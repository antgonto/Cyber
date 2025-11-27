"""
Cyber IDS Module - Network Intrusion Detection System

A production-ready binary intrusion detector (Attack vs Benign) built on the
CSE-CIC-IDS2018 dataset, exposing classical ML models via Django Ninja APIs.

Key features:
- Temporal train/test split by day (prevents data leakage)
- Class imbalance handling (balanced weights, optional SMOTE)
- Probability calibration (Platt scaling, Isotonic regression)
- Reproducible experiments (fixed seeds, artifact manifests)
- CPU-friendly tabular ML (LogReg, Random Forest, XGBoost)
"""

__version__ = "1.0.0"

