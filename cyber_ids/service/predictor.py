"""
Predictor service for Cyber IDS.

Handles:
- Lazy loading of trained models and feature lists
- Batch prediction with latency tracking
- Model version management
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import joblib
import numpy as np
import pandas as pd

from cyber_ids.config import ARTIFACT_DIR, DEFAULT_DECISION_THRESHOLD

logger = logging.getLogger(__name__)


class PredictorService:
    """
    Singleton-like service for model inference.

    Usage:
        predictor = PredictorService()
        predictor.ensure_loaded()
        results = predictor.predict([{"feat1": 1.0, "feat2": 2.0}])
    """

    def __init__(self, artifact_dir: Optional[Path] = None):
        self.artifact_dir = artifact_dir or Path(ARTIFACT_DIR)
        self.model = None
        self.feature_order: List[str] = []
        self.preprocess_params: Dict = {}
        self.version: Optional[str] = None
        self.decision_threshold = DEFAULT_DECISION_THRESHOLD
        self.latencies: List[float] = []

    def ensure_loaded(self, model_path: Optional[str] = None) -> None:
        """
        Load model artifacts if not already loaded.

        Args:
            model_path: Optional explicit path; if None, loads 'latest.joblib'
        """
        if self.model is not None:
            return  # Already loaded

        # Resolve model path
        if model_path is None:
            model_path = self.artifact_dir / "models" / "latest.joblib"
        else:
            model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        logger.info(f"Loading model from {model_path}")

        # Load model
        self.model = joblib.load(model_path)

        # Extract version from filename (e.g., model_20231120T123456Z.joblib)
        self.version = self._extract_version(model_path)

        # Load feature list
        features_path = self._find_matching_artifact(model_path, "features", ".json")
        with open(features_path, "r") as f:
            self.feature_order = json.load(f)

        # Load preprocessing parameters
        preprocess_path = self._find_matching_artifact(model_path, "preprocess", ".json")
        if preprocess_path.exists():
            with open(preprocess_path, "r") as f:
                self.preprocess_params = json.load(f)

        logger.info(
            f"Model loaded: version={self.version}, "
            f"n_features={len(self.feature_order)}"
        )

    def _extract_version(self, model_path: Path) -> str:
        """Extract version timestamp from model filename."""
        stem = model_path.stem  # e.g., "model_20231120T123456Z" or "latest"
        if stem == "latest":
            return "latest"
        # Extract timestamp portion
        parts = stem.split("_")
        return parts[-1] if len(parts) > 1 else "unknown"

    def _find_matching_artifact(
        self, model_path: Path, artifact_type: str, extension: str
    ) -> Path:
        """
        Find matching artifact (features, preprocess) for a model.

        Args:
            model_path: Path to model file
            artifact_type: 'features' or 'preprocess'
            extension: '.json'

        Returns:
            Path to artifact file
        """
        # If model is "latest", try to find latest artifact
        if model_path.stem == "latest":
            # Look for most recent artifact
            artifact_dir = self.artifact_dir / "pipeline"
            pattern = f"{artifact_type}_*{extension}"
            candidates = sorted(artifact_dir.glob(pattern), reverse=True)
            if candidates:
                return candidates[0]
            raise FileNotFoundError(f"No {artifact_type} artifact found")

        # Otherwise, replace model_ with artifact_type_ and .joblib with extension
        version = self._extract_version(model_path)
        artifact_path = (
            self.artifact_dir / "pipeline" / f"{artifact_type}_{version}{extension}"
        )

        if not artifact_path.exists():
            raise FileNotFoundError(f"Artifact not found: {artifact_path}")

        return artifact_path

    def preprocess_input(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Apply preprocessing to input features.

        Args:
            X: Raw input features

        Returns:
            Preprocessed features
        """
        # Align with expected features
        X = X[self.feature_order].copy()

        # Apply imputation
        if "fill_values" in self.preprocess_params:
            fill_values = pd.Series(self.preprocess_params["fill_values"])
            X = X.fillna(fill_values)

        # Apply clipping
        if "clip_upper" in self.preprocess_params:
            clip_upper = pd.Series(self.preprocess_params["clip_upper"])
            X = X.clip(upper=clip_upper, axis=1)

        return X

    def predict(
        self, flows: List[Dict[str, float]], threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Predict on a batch of network flows.

        Args:
            flows: List of flow feature dictionaries
            threshold: Optional decision threshold override

        Returns:
            List of predictions with label, probability, and model version

        Example:
            >>> flows = [{"Fwd Packet Length Mean": 123.4, ...}]
            >>> predictor.predict(flows)
            [{"label": 1, "prob": 0.87, "model_version": "20231120T123456Z"}]
        """
        self.ensure_loaded()

        threshold = threshold or self.decision_threshold

        # Convert to DataFrame
        X = pd.DataFrame(flows)

        # Preprocess
        X = self.preprocess_input(X)

        # Time prediction
        start = time.perf_counter()

        # Predict probabilities
        probs = self.model.predict_proba(X)[:, 1]

        # Hard predictions
        labels = (probs >= threshold).astype(int)

        elapsed = time.perf_counter() - start
        self.latencies.append(elapsed)

        # Format results
        results = [
            {
                "label": int(label),
                "prob": float(prob),
                "model_version": self.version,
            }
            for label, prob in zip(labels, probs)
        ]

        return results

    def get_latency_stats(self) -> Dict[str, float]:
        """
        Get prediction latency statistics.

        Returns:
            Dictionary with p50, p95, mean latency in milliseconds
        """
        if not self.latencies:
            return {"p50_ms": 0, "p95_ms": 0, "mean_ms": 0, "count": 0}

        latencies_ms = np.array(self.latencies) * 1000  # Convert to ms

        return {
            "p50_ms": float(np.percentile(latencies_ms, 50)),
            "p95_ms": float(np.percentile(latencies_ms, 95)),
            "mean_ms": float(np.mean(latencies_ms)),
            "count": len(self.latencies),
        }

    def reload(self) -> None:
        """Force reload of model (useful after retraining)."""
        self.model = None
        self.feature_order = []
        self.preprocess_params = {}
        self.version = None
        self.latencies = []
        self.ensure_loaded()


# Global singleton instance
_predictor_instance: Optional[PredictorService] = None


def get_predictor() -> PredictorService:
    """Get or create global predictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = PredictorService()
    return _predictor_instance

