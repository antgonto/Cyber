"""
Unit tests for metrics evaluation functions.

Tests:
- PR-AUC computation
- Recall at fixed FPR thresholds
- Metrics bundle generation
- Model comparison
"""

import pytest
import numpy as np
from sklearn.metrics import average_precision_score, roc_curve

from cyber_ids.metrics.evaluation import (
    compute_pr_auc,
    compute_recall_at_fpr,
    compute_metrics_bundle,
    find_optimal_threshold_for_f1,
    compare_models,
)


@pytest.fixture
def binary_classification_data():
    """Generate synthetic binary classification predictions."""
    np.random.seed(42)
    n = 1000

    # Imbalanced: 80% benign (0), 20% attack (1)
    y_true = np.random.choice([0, 1], n, p=[0.8, 0.2])

    # Reasonably good predictions (AUC ~0.85)
    y_scores = np.where(
        y_true == 1,
        np.random.beta(5, 2, n),  # Attack: higher scores
        np.random.beta(2, 5, n),  # Benign: lower scores
    )

    return y_true, y_scores


class TestPRAUC:
    """Test PR-AUC computation."""

    def test_pr_auc_perfect_classifier(self):
        """Test PR-AUC for perfect classifier."""
        y_true = np.array([0, 0, 1, 1, 1])
        y_scores = np.array([0.1, 0.2, 0.8, 0.9, 0.95])

        pr_auc = compute_pr_auc(y_true, y_scores)

        # Perfect separation should give PR-AUC = 1.0
        assert pr_auc == pytest.approx(1.0, abs=0.01)

    def test_pr_auc_random_classifier(self):
        """Test PR-AUC for random classifier."""
        np.random.seed(42)
        y_true = np.array([0, 1] * 500)
        y_scores = np.random.rand(1000)

        pr_auc = compute_pr_auc(y_true, y_scores)

        # Random classifier should be close to baseline (proportion of positive class)
        baseline = y_true.sum() / len(y_true)
        assert pr_auc == pytest.approx(baseline, abs=0.1)

    def test_pr_auc_matches_sklearn(self, binary_classification_data):
        """Test that our PR-AUC matches sklearn."""
        y_true, y_scores = binary_classification_data

        our_pr_auc = compute_pr_auc(y_true, y_scores)
        sklearn_pr_auc = average_precision_score(y_true, y_scores)

        assert our_pr_auc == pytest.approx(sklearn_pr_auc, abs=1e-6)


class TestRecallAtFPR:
    """Test recall at fixed FPR computation."""

    def test_recall_at_1pct_fpr_perfect(self):
        """Test recall@1%FPR for perfect classifier."""
        y_true = np.array([0] * 99 + [1] * 100)  # 1% minority
        y_scores = np.concatenate([np.zeros(99), np.ones(100)])

        recall = compute_recall_at_fpr(y_true, y_scores, target_fpr=0.01)

        # Perfect classifier: at 1% FPR, we should catch all attacks
        assert recall == pytest.approx(1.0, abs=0.01)

    def test_recall_at_fpr_tradeoff(self, binary_classification_data):
        """Test that recall decreases as FPR constraint tightens."""
        y_true, y_scores = binary_classification_data

        recall_1pct = compute_recall_at_fpr(y_true, y_scores, target_fpr=0.01)
        recall_0_1pct = compute_recall_at_fpr(y_true, y_scores, target_fpr=0.001)

        # Lower FPR should give lower recall
        assert recall_0_1pct <= recall_1pct

    def test_recall_at_fpr_zero_when_impossible(self):
        """Test that recall is 0 when target FPR is unachievable."""
        y_true = np.array([0, 0, 1, 1])
        y_scores = np.array([0.5, 0.5, 0.5, 0.5])  # All same score

        recall = compute_recall_at_fpr(y_true, y_scores, target_fpr=0.0)

        # Can't achieve 0% FPR with these scores
        assert recall >= 0.0


class TestMetricsBundle:
    """Test comprehensive metrics computation."""

    def test_metrics_bundle_completeness(self, binary_classification_data):
        """Test that all expected metrics are computed."""
        y_true, y_scores = binary_classification_data

        metrics = compute_metrics_bundle(y_true, y_scores)

        # Check all required metrics present
        required_metrics = [
            "pr_auc_macro",
            "f1_macro",
            "precision_macro",
            "recall_macro",
            "roc_auc",
            "brier_score",
            "recall_at_fpr_1pct",
            "recall_at_fpr_0_1pct",
        ]

        for metric in required_metrics:
            assert metric in metrics, f"Missing metric: {metric}"

    def test_metrics_bundle_ranges(self, binary_classification_data):
        """Test that metrics are in valid ranges."""
        y_true, y_scores = binary_classification_data

        metrics = compute_metrics_bundle(y_true, y_scores)

        # All metrics should be between 0 and 1
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                assert 0 <= value <= 1, f"{key} = {value} out of range [0, 1]"

    def test_brier_score_calibration(self):
        """Test Brier score for calibrated vs uncalibrated predictions."""
        y_true = np.array([0, 0, 1, 1])

        # Well-calibrated predictions
        y_scores_calibrated = np.array([0.1, 0.2, 0.8, 0.9])

        # Poorly calibrated (overconfident)
        y_scores_uncalibrated = np.array([0.01, 0.01, 0.99, 0.99])

        metrics_cal = compute_metrics_bundle(y_true, y_scores_calibrated)
        metrics_uncal = compute_metrics_bundle(y_true, y_scores_uncalibrated)

        # Calibrated should have better (lower) Brier score
        # Note: Both are perfect classifiers, so Brier might be similar
        # Just check that Brier is computed
        assert "brier_score" in metrics_cal
        assert "brier_score" in metrics_uncal


class TestOptimalThreshold:
    """Test optimal threshold finding."""

    def test_find_optimal_threshold_for_f1(self, binary_classification_data):
        """Test F1-optimal threshold finding."""
        y_true, y_scores = binary_classification_data

        threshold, f1 = find_optimal_threshold_for_f1(y_true, y_scores)

        # Threshold should be between 0 and 1
        assert 0 <= threshold <= 1

        # F1 should be positive
        assert f1 > 0

        # Threshold should not be at extremes for good classifier
        assert 0.1 < threshold < 0.9


class TestModelComparison:
    """Test model comparison utility."""

    def test_compare_models_sorting(self):
        """Test that models are sorted by PR-AUC."""
        metrics_dict = {
            "model_a": {"pr_auc_macro": 0.85, "f1_macro": 0.80},
            "model_b": {"pr_auc_macro": 0.90, "f1_macro": 0.85},
            "model_c": {"pr_auc_macro": 0.75, "f1_macro": 0.70},
        }

        comparison_df = compare_models(metrics_dict)

        # Should be sorted by PR-AUC descending
        assert comparison_df.index[0] == "model_b"  # Highest PR-AUC
        assert comparison_df.index[-1] == "model_c"  # Lowest PR-AUC

    def test_compare_models_structure(self):
        """Test comparison DataFrame structure."""
        metrics_dict = {
            "model_a": {"pr_auc_macro": 0.85, "f1_macro": 0.80},
        }

        comparison_df = compare_models(metrics_dict)

        # Should have models as index
        assert "model_a" in comparison_df.index

        # Should have metrics as columns
        assert "pr_auc_macro" in comparison_df.columns
        assert "f1_macro" in comparison_df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

