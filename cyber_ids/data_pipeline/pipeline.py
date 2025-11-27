"""
Data pipeline for CSE-CIC-IDS2018 dataset.

Handles:
- Loading raw CSVs and converting to Parquet
- Train/validation/test split by day (prevents temporal leakage)
- Feature matrix construction with leakage guards
- Reproducible preprocessing
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from cyber_ids.config import (
    DATA_DIR,
    LABEL_COL,
    DROP_COLS,
    LABEL_MAP,
    RANDOM_SEED,
    MISSING_THRESHOLD,
)

logger = logging.getLogger(__name__)


def load_raw_data(
    days: List[str],
    use_parquet: bool = True,
    data_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Load selected days into a single DataFrame.

    Args:
        days: List of day identifiers (e.g., ["Wednesday-14-02-2018"])
        use_parquet: If True, load from parquet/ subfolder; else from raw/ CSVs
        data_dir: Override default data directory

    Returns:
        Concatenated DataFrame with 'day' column tracking provenance

    Raises:
        FileNotFoundError: If data files don't exist
    """
    data_dir = data_dir or DATA_DIR
    frames = []

    for day in days:
        if use_parquet:
            path = data_dir / "parquet" / f"{day}.parquet"
            if not path.exists():
                logger.warning(f"Parquet not found: {path}. Attempting CSV fallback.")
                path = data_dir / "raw" / day / f"{day}.csv"
                use_parquet = False

        else:
            # CSV might be in day subdirectory or flat
            path = data_dir / "raw" / day / f"{day}.csv"
            if not path.exists():
                path = data_dir / "raw" / f"{day}.csv"

        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")

        logger.info(f"Loading {day} from {path}")

        if use_parquet:
            df = pd.read_parquet(path)
        else:
            df = pd.read_csv(path, low_memory=False)

        # Track day for split validation and debugging
        df["day"] = day
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    logger.info(f"Loaded {len(combined)} rows from {len(days)} day(s)")

    return combined


def build_train_test_split_by_day(
    train_days: List[str],
    val_days: List[str],
    test_days: Optional[List[str]] = None,
    use_parquet: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Load data with strict day-level separation to prevent temporal leakage.

    Args:
        train_days: Days for training
        val_days: Days for validation (used for calibration)
        test_days: Optional days for final test evaluation
        use_parquet: Load from Parquet or CSV

    Returns:
        (train_df, val_df, test_df) where test_df is None if test_days not provided

    Leakage guard:
        Entire days are held out; no row-level shuffling across days.
    """
    logger.info(f"Building splits: train={train_days}, val={val_days}, test={test_days}")

    train_df = load_raw_data(train_days, use_parquet=use_parquet)
    val_df = load_raw_data(val_days, use_parquet=use_parquet)
    test_df = load_raw_data(test_days, use_parquet=use_parquet) if test_days else None

    # Verify no day overlap
    train_set = set(train_days)
    val_set = set(val_days)
    test_set = set(test_days) if test_days else set()

    assert not (train_set & val_set), "Train and val days overlap!"
    assert not (train_set & test_set), "Train and test days overlap!"
    assert not (val_set & test_set), "Val and test days overlap!"

    return train_df, val_df, test_df


def derive_feature_list(
    df: pd.DataFrame,
    drop_cols: Optional[List[str]] = None,
    missing_threshold: float = MISSING_THRESHOLD,
) -> List[str]:
    """
    Determine usable feature columns based on heuristics.

    Args:
        df: Input DataFrame
        drop_cols: Columns to explicitly drop (IDs, IPs, timestamps)
        missing_threshold: Drop features with missing > this fraction

    Returns:
        List of feature column names

    Leakage guards:
        - Drops timestamp, IP, port, flow ID columns
        - Drops label column itself
        - Drops columns with excessive missing values (computed on train only)
    """
    drop_cols = drop_cols or DROP_COLS

    # Start with all columns
    candidate_cols = [c for c in df.columns if c not in drop_cols]

    # Keep only numeric columns (CICFlowMeter features are numeric)
    numeric_cols = [c for c in candidate_cols if pd.api.types.is_numeric_dtype(df[c])]

    # Drop columns with excessive missing values
    missing_frac = df[numeric_cols].isnull().mean()
    valid_cols = missing_frac[missing_frac <= missing_threshold].index.tolist()

    logger.info(
        f"Feature selection: {len(df.columns)} total → "
        f"{len(numeric_cols)} numeric → "
        f"{len(valid_cols)} after missing filter"
    )

    return valid_cols


def build_feature_matrix_and_labels(
    df: pd.DataFrame,
    feature_cols: List[str],
    label_col: str = LABEL_COL,
    label_map: Optional[Dict[str, int]] = None,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Extract feature matrix X and binary labels y.

    Args:
        df: Input DataFrame
        feature_cols: List of feature column names
        label_col: Name of label column
        label_map: Mapping from label strings to integers

    Returns:
        (X, y) where X is feature DataFrame and y is binary Series (0=Benign, 1=Attack)

    Leakage guard:
        - Only specified feature_cols are used (no accidental label inclusion)
    """
    label_map = label_map or LABEL_MAP

    # Feature matrix
    X = df[feature_cols].copy()

    # Binary labels
    if label_col not in df.columns:
        raise ValueError(f"Label column '{label_col}' not found in DataFrame")

    # Map labels to binary (0=Benign, 1=Attack)
    # If dataset has specific attack names, map them all to 1
    y = df[label_col].apply(lambda x: 0 if "Benign" in str(x) else 1)

    logger.info(f"Built feature matrix: X={X.shape}, y={y.shape}")
    logger.info(f"Class distribution: {y.value_counts().to_dict()}")

    return X, y


def preprocess_features(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    X_test: Optional[pd.DataFrame] = None,
    impute_strategy: str = "median",
    clip_quantile: float = 0.999,
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame], Dict]:
    """
    Apply preprocessing: imputation, clipping, optional scaling.

    Args:
        X_train: Training features
        X_val: Validation features
        X_test: Optional test features
        impute_strategy: 'median', 'mean', or 'zero'
        clip_quantile: Clip extreme values at this quantile (reduces outliers)

    Returns:
        (X_train_proc, X_val_proc, X_test_proc, preprocess_params)

    Leakage guard:
        - All statistics (median, quantiles) computed ONLY on training set
        - Applied consistently to val/test
    """
    preprocess_params = {}

    # 1. Imputation (fit on train only)
    if impute_strategy == "median":
        fill_values = X_train.median()
    elif impute_strategy == "mean":
        fill_values = X_train.mean()
    elif impute_strategy == "zero":
        fill_values = pd.Series(0, index=X_train.columns)
    else:
        raise ValueError(f"Unknown impute_strategy: {impute_strategy}")

    preprocess_params["fill_values"] = fill_values.to_dict()

    X_train = X_train.fillna(fill_values)
    X_val = X_val.fillna(fill_values)
    if X_test is not None:
        X_test = X_test.fillna(fill_values)

    # 2. Clip extreme values (fit quantiles on train only)
    if clip_quantile < 1.0:
        upper_bounds = X_train.quantile(clip_quantile)
        preprocess_params["clip_upper"] = upper_bounds.to_dict()

        X_train = X_train.clip(upper=upper_bounds, axis=1)
        X_val = X_val.clip(upper=upper_bounds, axis=1)
        if X_test is not None:
            X_test = X_test.clip(upper=upper_bounds, axis=1)

    # 3. Optional: StandardScaler (not needed for tree models, but useful for LogReg)
    # For simplicity, we skip scaling here; tree models handle raw features well.
    # If LogReg underperforms, add StandardScaler here.

    logger.info("Preprocessing complete")

    return X_train, X_val, X_test, preprocess_params


def convert_csv_to_parquet(
    csv_dir: Path,
    parquet_dir: Path,
    days: Optional[List[str]] = None,
) -> None:
    """
    Utility to convert CSV files to Parquet for faster loading.

    Args:
        csv_dir: Directory containing raw CSVs (e.g., data/cse-cic-ids2018/raw/)
        parquet_dir: Output directory for Parquet files
        days: Optional list of specific days to convert; if None, convert all
    """
    parquet_dir.mkdir(parents=True, exist_ok=True)

    if days is None:
        # Auto-discover day folders
        days = [d.name for d in csv_dir.iterdir() if d.is_dir()]

    for day in days:
        csv_path = csv_dir / day / f"{day}.csv"
        if not csv_path.exists():
            csv_path = csv_dir / f"{day}.csv"

        if not csv_path.exists():
            logger.warning(f"CSV not found: {csv_path}")
            continue

        parquet_path = parquet_dir / f"{day}.parquet"

        logger.info(f"Converting {csv_path} → {parquet_path}")
        df = pd.read_csv(csv_path, low_memory=False)
        df.to_parquet(parquet_path, index=False, compression="snappy")

    logger.info(f"Conversion complete: {len(days)} day(s)")

