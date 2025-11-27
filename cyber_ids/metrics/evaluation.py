"""
Metrics evaluation module for Cyber IDS.

Provides comprehensive evaluation metrics focused on imbalanced classification:
- PR-AUC (Precision-Recall Area Under Curve)
- Recall at fixed FPR thresholds (1%, 0.1%)
- F1, Precision, Recall (macro-averaged)
- ROC-AUC
- Brier score (calibration quality)
- Per-family metrics for attack categories
"""

from __future__ import annotations

import logging
from typing import Dict, List, Sequence, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    precision_recall_curve,
    roc_curve,
    brier_score_loss,
    classification_report,
)

logger = logging.getLogger(__name__)


def compute_pr_auc(y_true: Sequence[int], y_scores: Sequence[float]) -> float:
    """
    Compute Precision-Recall Area Under Curve.

    PR-AUC is preferred over ROC-AUC for imbalanced datasets because it focuses
    on the minority (attack) class performance.

    Args:
        y_true: Ground truth binary labels
        y_scores: Predicted probabilities for positive class

    Returns:
        PR-AUC score (0.0 to 1.0)
    """
    return average_precision_score(y_true, y_scores)


def compute_recall_at_fpr(
    y_true: Sequence[int],
    y_scores: Sequence[float],
    target_fpr: float = 0.01,
) -> float:
    """
    Compute recall (TPR) at a fixed false positive rate threshold.

    This metric is critical for security applications where we want to maximize
    attack detection (recall) while keeping false alarms (FPR) below a threshold.

    Args:
        y_true: Ground truth binary labels
        y_scores: Predicted probabilities
        target_fpr: Maximum acceptable FPR (e.g., 0.01 = 1%)

    Returns:
        Maximum recall achievable at target_fpr

    Example:
        At FPR=1%, what's the best recall we can achieve?
        If recall@1%FPR = 0.85, we catch 85% of attacks with 1% false alarms.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)

    # Find all points where FPR <= target
    mask = fpr <= target_fpr

    if not mask.any():
        logger.warning(f"No thresholds achieve FPR <= {target_fpr}")
        return 0.0

    # Return maximum TPR (recall) at this FPR constraint
    return float(tpr[mask].max())


def compute_threshold_for_target_fpr(
    y_true: Sequence[int],
    y_scores: Sequence[float],
    target_fpr: float = 0.01,
) -> float:
    """
    Find decision threshold that achieves target FPR.

    Args:
        y_true: Ground truth binary labels
        y_scores: Predicted probabilities
        target_fpr: Desired FPR

    Returns:
        Threshold value
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    mask = fpr <= target_fpr

    if not mask.any():
        return 1.0  # No valid threshold

    # Return threshold at target FPR
    idx = np.where(mask)[0][-1]  # Last index where FPR <= target
    return float(thresholds[idx])


def compute_metrics_bundle(
    y_true: Sequence[int],
    y_scores: Sequence[float],
    fpr_targets: Optional[List[float]] = None,
    threshold: float = 0.5,
) -> Dict[str, float]:
    """
    Compute comprehensive metrics bundle.

    Args:
        y_true: Ground truth binary labels
        y_scores: Predicted probabilities
        fpr_targets: FPR levels for recall computation (e.g., [0.01, 0.001])
        threshold: Decision threshold for hard predictions

    Returns:
        Dictionary of metric name → value
    """
    fpr_targets = fpr_targets or [0.01, 0.001]

    # Hard predictions at threshold
    y_pred = (np.array(y_scores) >= threshold).astype(int)

    # Compute all metrics
    metrics = {
        # Primary metrics
        "pr_auc_macro": compute_pr_auc(y_true, y_scores),
        "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "precision_macro": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=0),
        # Secondary metrics
        "roc_auc": roc_auc_score(y_true, y_scores),
        "brier_score": brier_score_loss(y_true, y_scores),
        # Per-class at threshold
        "f1_attack": f1_score(y_true, y_pred, pos_label=1, zero_division=0),
        "precision_attack": precision_score(y_true, y_pred, pos_label=1, zero_division=0),
        "recall_attack": recall_score(y_true, y_pred, pos_label=1, zero_division=0),
    }

    # Recall at fixed FPR thresholds
    for fpr_target in fpr_targets:
        key = f"recall_at_fpr_{fpr_target:.1%}".replace(".", "_").replace("%", "pct")
        metrics[key] = compute_recall_at_fpr(y_true, y_scores, fpr_target)

    return metrics


def compute_classification_report_dict(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    target_names: Optional[List[str]] = None,
) -> Dict:
    """
    Generate sklearn classification report as dictionary.

    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        target_names: Class names (e.g., ["Benign", "Attack"])

    Returns:
        Dictionary with per-class and aggregate metrics
    """
    target_names = target_names or ["Benign", "Attack"]
    return classification_report(
        y_true, y_pred, target_names=target_names, output_dict=True, zero_division=0
    )


def compute_per_family_metrics(
    y_true: pd.Series,
    y_scores: pd.Series,
    attack_labels: pd.Series,
    family_map: Dict[str, List[str]],
    threshold: float = 0.5,
) -> Dict[str, Dict[str, float]]:
    """
    Compute metrics for specific attack families (DoS, Brute Force, Web, etc.).

    Args:
        y_true: Ground truth binary labels (0=Benign, 1=Attack)
        y_scores: Predicted probabilities
        attack_labels: Original attack category labels (e.g., "DoS Hulk")
        family_map: Mapping from family name to list of attack labels
        threshold: Decision threshold

    Returns:
        Dictionary: family_name → {precision, recall, f1, count}

    Example:
        family_map = {
            "DoS/DDoS": ["DoS slowloris", "DDoS"],
            "Brute Force": ["SSH-Bruteforce", "FTP-BruteForce"],
        }
    """
    y_pred = (y_scores >= threshold).astype(int)
    per_family = {}

    for family_name, attack_types in family_map.items():
        # Filter to this family
        mask = attack_labels.isin(attack_types)

        if mask.sum() == 0:
            continue  # No samples for this family

        y_true_family = y_true[mask]
        y_pred_family = y_pred[mask]

        per_family[family_name] = {
            "precision": precision_score(y_true_family, y_pred_family, zero_division=0),
            "recall": recall_score(y_true_family, y_pred_family, zero_division=0),
            "f1": f1_score(y_true_family, y_pred_family, zero_division=0),
            "count": int(mask.sum()),
        }

    return per_family


def find_optimal_threshold_for_f1(
    y_true: Sequence[int], y_scores: Sequence[float]
) -> Tuple[float, float]:
    """
    Find threshold that maximizes F1 score.

    Args:
        y_true: Ground truth labels
        y_scores: Predicted probabilities

    Returns:
        (optimal_threshold, best_f1)
    """
    precision, recall, thresholds = precision_recall_curve(y_true, y_scores)

    # Compute F1 for each threshold
    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)

    # Find best
    best_idx = np.argmax(f1_scores)
    best_f1 = f1_scores[best_idx]

    # thresholds array is 1 element shorter than precision/recall
    if best_idx < len(thresholds):
        best_threshold = thresholds[best_idx]
    else:
        best_threshold = 0.5

    return float(best_threshold), float(best_f1)


def compare_models(metrics_dict: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Compare multiple models in a summary table.

    Args:
        metrics_dict: model_name → metrics_bundle

    Returns:
        DataFrame with models as rows and metrics as columns
    """
    df = pd.DataFrame(metrics_dict).T
    # Sort by PR-AUC descending
    if "pr_auc_macro" in df.columns:
        df = df.sort_values("pr_auc_macro", ascending=False)
    return df

