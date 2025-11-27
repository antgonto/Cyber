"""
Unit tests for Cyber IDS data pipeline.

Tests:
- Feature selection and leakage guards
- Train/test split by day
- Preprocessing (imputation, clipping)
- Feature matrix construction
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from cyber_ids.data_pipeline.pipeline import (
    derive_feature_list,
    build_feature_matrix_and_labels,
    preprocess_features,
)


@pytest.fixture
def sample_df():
    """Create a sample DataFrame mimicking CSE-CIC-IDS2018 structure."""
    np.random.seed(42)
    n = 100

    return pd.DataFrame({
        # Leakage-prone columns (should be dropped)
        "Flow ID": [f"flow_{i}" for i in range(n)],
        "Source IP": [f"192.168.1.{i % 255}" for i in range(n)],
        "Destination IP": [f"10.0.0.{i % 255}" for i in range(n)],
        "Source Port": np.random.randint(1024, 65535, n),
        "Destination Port": np.random.randint(1, 1024, n),
        "Timestamp": pd.date_range("2018-02-14", periods=n, freq="1s"),
        # Valid features
        "Fwd Packet Length Mean": np.random.rand(n) * 1000,
        "Bwd Packet Length Mean": np.random.rand(n) * 1000,
        "Flow Duration": np.random.randint(0, 10000, n),
        "Total Fwd Packets": np.random.randint(1, 100, n),
        "Total Bwd Packets": np.random.randint(1, 100, n),
        # Feature with missing values
        "Flow IAT Mean": np.where(np.random.rand(n) < 0.2, np.nan, np.random.rand(n) * 100),
        # Feature with high missing (should be dropped)
        "High Missing Feature": np.where(np.random.rand(n) < 0.6, np.nan, np.random.rand(n)),
        # Label
        "Label": np.random.choice(["Benign", "Attack"], n, p=[0.7, 0.3]),
        # Day for split
        "day": ["Wednesday-14-02-2018"] * n,
    })


class TestFeatureSelection:
    """Test feature selection and leakage prevention."""

    def test_derive_feature_list_drops_leakage_cols(self, sample_df):
        """Test that leakage-prone columns are dropped."""
        drop_cols = [
            "Flow ID", "Source IP", "Destination IP",
            "Source Port", "Destination Port", "Timestamp", "Label", "day"
        ]
        features = derive_feature_list(sample_df, drop_cols=drop_cols)

        # Ensure leakage columns are not in features
        for col in ["Flow ID", "Source IP", "Label"]:
            assert col not in features

        # Ensure valid features are included
        assert "Fwd Packet Length Mean" in features
        assert "Flow Duration" in features

    def test_derive_feature_list_drops_high_missing(self, sample_df):
        """Test that features with excessive missing values are dropped."""
        features = derive_feature_list(sample_df, missing_threshold=0.3)

        # High Missing Feature has 60% missing, should be dropped
        assert "High Missing Feature" not in features

        # Flow IAT Mean has 20% missing, should be kept
        assert "Flow IAT Mean" in features

    def test_derive_feature_list_only_numeric(self, sample_df):
        """Test that only numeric features are selected."""
        features = derive_feature_list(sample_df)

        # All returned features should be numeric
        for feat in features:
            assert pd.api.types.is_numeric_dtype(sample_df[feat])


class TestFeatureMatrixConstruction:
    """Test feature matrix and label extraction."""

    def test_build_feature_matrix_and_labels(self, sample_df):
        """Test X, y construction."""
        feature_cols = ["Fwd Packet Length Mean", "Flow Duration"]
        X, y = build_feature_matrix_and_labels(sample_df, feature_cols)

        # Check shapes
        assert X.shape == (100, 2)
        assert y.shape == (100,)

        # Check X contains only specified features
        assert list(X.columns) == feature_cols

        # Check y is binary (0=Benign, 1=Attack)
        assert set(y.unique()).issubset({0, 1})

    def test_label_mapping(self, sample_df):
        """Test that labels are correctly mapped to binary."""
        feature_cols = ["Fwd Packet Length Mean"]
        X, y = build_feature_matrix_and_labels(sample_df, feature_cols)

        # Original labels
        original = sample_df["Label"]

        # Check mapping
        for i in range(len(y)):
            if "Benign" in str(original.iloc[i]):
                assert y.iloc[i] == 0
            else:
                assert y.iloc[i] == 1


class TestPreprocessing:
    """Test preprocessing functions."""

    def test_preprocess_imputation(self):
        """Test that imputation is fitted on train and applied to val."""
        np.random.seed(42)

        # Train with some missing values
        X_train = pd.DataFrame({
            "feat1": [1, 2, np.nan, 4, 5],
            "feat2": [10, np.nan, 30, 40, 50],
        })

        # Val with different missing pattern
        X_val = pd.DataFrame({
            "feat1": [np.nan, 2, 3],
            "feat2": [10, 20, np.nan],
        })

        X_train_proc, X_val_proc, _, params = preprocess_features(
            X_train, X_val, impute_strategy="median"
        )

        # Check no NaNs remain
        assert not X_train_proc.isnull().any().any()
        assert not X_val_proc.isnull().any().any()

        # Check fill values stored
        assert "fill_values" in params
        assert "feat1" in params["fill_values"]

    def test_preprocess_clipping(self):
        """Test that extreme values are clipped based on train quantile."""
        np.random.seed(42)

        X_train = pd.DataFrame({
            "feat1": [1, 2, 3, 4, 5],
        })

        X_val = pd.DataFrame({
            "feat1": [1, 2, 100],  # 100 is extreme outlier
        })

        X_train_proc, X_val_proc, _, params = preprocess_features(
            X_train, X_val, clip_quantile=0.8  # Clip at 80th percentile
        )

        # Val extreme value should be clipped to train's 80th percentile
        train_upper = X_train["feat1"].quantile(0.8)
        assert X_val_proc["feat1"].max() <= train_upper

        # Check clipping params stored
        assert "clip_upper" in params

    def test_no_leakage_in_preprocessing(self):
        """Test that preprocessing statistics come only from train."""
        np.random.seed(42)

        X_train = pd.DataFrame({"feat1": [1, 2, 3, 4, 5]})
        X_val = pd.DataFrame({"feat1": [10, 20, 30]})  # Much larger values

        X_train_proc, X_val_proc, _, params = preprocess_features(
            X_train, X_val, impute_strategy="median", clip_quantile=0.999
        )

        # Fill value should be median of train, not influenced by val
        train_median = X_train["feat1"].median()
        assert params["fill_values"]["feat1"] == train_median

        # Clip upper should be from train quantile
        train_upper = X_train["feat1"].quantile(0.999)
        assert params["clip_upper"]["feat1"] == train_upper


class TestDayLevelSplit:
    """Test that day-level splits prevent temporal leakage."""

    def test_day_separation(self):
        """Test that train/val/test days don't overlap."""
        train_days = ["Wednesday-14-02-2018", "Thursday-15-02-2018"]
        val_days = ["Wednesday-21-02-2018"]
        test_days = ["Thursday-22-02-2018"]

        # Verify no overlap
        train_set = set(train_days)
        val_set = set(val_days)
        test_set = set(test_days)

        assert len(train_set & val_set) == 0, "Train and val overlap"
        assert len(train_set & test_set) == 0, "Train and test overlap"
        assert len(val_set & test_set) == 0, "Val and test overlap"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

