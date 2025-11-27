# Cyber IDS Implementation Checklist

## Phase 1: Core Infrastructure ✅

- [x] Create `cyber_ids/` package structure
- [x] Create `config.py` with paths, hyperparameters, and seeds
- [x] Create data pipeline package (`data_pipeline/`)
- [x] Create models package (`models/`)
- [x] Create metrics package (`metrics/`)
- [x] Create service package (`service/`)
- [x] Add ML dependencies to `requirements.txt`
- [x] Update `settings.py` with Cyber IDS configuration
- [x] Create artifact directories (`artifacts/ids/`)

## Phase 2: Data Pipeline ✅

- [x] Implement `load_raw_data()` - CSV/Parquet loader
- [x] Implement `build_train_test_split_by_day()` - temporal split
- [x] Implement `derive_feature_list()` - leakage-safe feature selection
- [x] Implement `build_feature_matrix_and_labels()` - X, y extraction
- [x] Implement `preprocess_features()` - imputation, clipping
- [x] Implement `convert_csv_to_parquet()` - utility function
- [x] Add leakage guards (drop IPs, timestamps, flow IDs)
- [x] Add missing value handling
- [x] Add day-level split validation

## Phase 3: Modeling & Metrics ✅

- [x] Implement `train_baseline_models()` - majority, LogReg
- [x] Implement `train_ensemble_models()` - RF, XGBoost
- [x] Implement `evaluate_models()` - metrics computation
- [x] Implement `select_champion()` - PR-AUC-based selection
- [x] Implement `calibrate_model()` - isotonic/Platt scaling
- [x] Implement `persist_artifacts()` - save models, metrics, manifests
- [x] Implement `compute_pr_auc()` - PR-AUC metric
- [x] Implement `compute_recall_at_fpr()` - recall@1%FPR, recall@0.1%FPR
- [x] Implement `compute_metrics_bundle()` - comprehensive metrics
- [x] Implement `find_optimal_threshold_for_f1()` - threshold tuning
- [x] Implement `compare_models()` - model comparison table
- [x] Add class imbalance handling (balanced weights, scale_pos_weight)
- [x] Add reproducibility (fixed seeds, manifest tracking)

## Phase 4: API Integration ✅

- [x] Create `app/api/cyber_ids/` package
- [x] Implement Pydantic schemas (`schemas.py`)
  - [x] `TrainRequest`, `TrainResponse`
  - [x] `PredictRequest`, `PredictResponse`
  - [x] `MetricsResponse`, `HealthResponse`
- [x] Implement Django Ninja router (`router.py`)
  - [x] `POST /ml/train` endpoint
  - [x] `POST /ml/predict` endpoint
  - [x] `GET /ml/metrics` endpoint
  - [x] `GET /ml/health` endpoint
- [x] Implement `PredictorService` - model loading and inference
- [x] Add router to `app/api/api.py`
- [x] Add input validation (empty flows, >100 flows, threshold range)
- [x] Add latency tracking

## Phase 5: Testing ✅

- [x] Create `tests/cyber_ids/` package
- [x] Implement `test_data_pipeline.py`
  - [x] Test feature selection (leakage guards)
  - [x] Test feature matrix construction
  - [x] Test preprocessing (imputation, clipping)
  - [x] Test no leakage in preprocessing
  - [x] Test day-level split separation
- [x] Implement `test_metrics.py`
  - [x] Test PR-AUC computation
  - [x] Test recall@FPR computation
  - [x] Test metrics bundle completeness
  - [x] Test optimal threshold finding
  - [x] Test model comparison
- [x] Implement `test_api.py`
  - [x] Test train endpoint (mocked)
  - [x] Test predict endpoint (mocked)
  - [x] Test metrics endpoint
  - [x] Test health endpoint
  - [x] Test schema validation

## Phase 6: Documentation ✅

- [x] Create `CYBER_IDS_README.md` - comprehensive documentation
  - [x] Architecture diagram
  - [x] Directory structure
  - [x] Installation instructions
  - [x] Usage examples (CLI, API, Docker)
  - [x] Configuration reference
  - [x] Troubleshooting guide
  - [x] API reference
  - [x] Leakage guards explanation
  - [x] Performance tips
  - [x] Extension guide
- [x] Create `CYBER_IDS_QUICKSTART.md` - 5-minute setup guide
- [x] Add inline code comments and docstrings

---

## Remaining Tasks (To Be Done)

### Phase 7: Dataset Preparation

- [ ] Download CSE-CIC-IDS2018 dataset
- [ ] Extract and organize by day
- [ ] Convert CSVs to Parquet
- [ ] Verify feature names match CICFlowMeter format
- [ ] Create sample subset for testing (e.g., 10k rows per day)

### Phase 8: Initial Training & Validation

- [ ] Run first training on 2-3 days
- [ ] Verify artifacts are saved correctly
- [ ] Check model file size is reasonable (~10-100MB)
- [ ] Validate metrics (PR-AUC > 0.8 expected for decent model)
- [ ] Inspect calibration improvement (Brier score before/after)
- [ ] Check latency (p95 < 10ms for single prediction)

### Phase 9: Integration Testing

- [ ] Start Django server
- [ ] Test `/ml/health` endpoint
- [ ] Trigger `/ml/train` via API
- [ ] Test `/ml/predict` with sample flows
- [ ] Retrieve metrics via `/ml/metrics`
- [ ] Test batch prediction (50-100 flows)
- [ ] Verify CORS works with React frontend
- [ ] Test error handling (missing features, invalid threshold)

### Phase 10: Docker Deployment

- [ ] Update `docker-compose.yml` with volume mounts
- [ ] Build Docker image with ML dependencies
- [ ] Test training inside Docker container
- [ ] Test API serving inside Docker container
- [ ] Verify artifacts persist across container restarts
- [ ] Test health checks in Docker Compose

### Phase 11: Advanced Features (Optional)

- [ ] Implement per-family metrics loading
- [ ] Add threshold tuning endpoint (`/ml/tune_threshold`)
- [ ] Add model retraining scheduler (cron job)
- [ ] Add prediction logging to database
- [ ] Add model drift detection
- [ ] Add feature importance endpoint
- [ ] Add SHAP explanations for predictions
- [ ] Add support for streaming predictions (Celery/Redis)

### Phase 12: React Frontend Integration ✅

- [x] Create `cyber/src/pages/CyberIDS/` components
- [x] Add training dashboard (trigger training, view progress)
- [x] Add prediction UI (input flow features, show result)
- [x] Add metrics dashboard (charts for PR-AUC, F1, latency)
- [x] Add API service layer (cyberIDSAPI.js)
- [x] Add tabbed interface with MUI components
- [ ] Add model version selector (future enhancement)
- [ ] Add real-time prediction feed (WebSocket - future enhancement)

### Phase 13: Production Hardening

- [ ] Add authentication/authorization to ML endpoints
- [ ] Add rate limiting (e.g., 100 predictions/minute)
- [ ] Add request logging and audit trail
- [ ] Add Prometheus metrics export
- [ ] Add Grafana dashboard for monitoring
- [ ] Set up alerting (model drift, high latency, low accuracy)
- [ ] Add backup/restore for artifacts
- [ ] Document disaster recovery procedures

### Phase 14: CI/CD Integration

- [ ] Add pytest to CI pipeline
- [ ] Add linting (black, flake8, mypy)
- [ ] Add security scanning (Bandit, Safety)
- [ ] Add code coverage reporting
- [ ] Set up automated testing on PR
- [ ] Add model versioning (MLflow/W&B integration)
- [ ] Add automated artifact uploading to S3/GCS

---

## Priority Order for Remaining Tasks

**Immediate (Must Do)**:
1. Phase 7: Dataset Preparation
2. Phase 8: Initial Training & Validation
3. Phase 9: Integration Testing

**Short-Term (Should Do)**:
4. Phase 10: Docker Deployment
5. Phase 13: Production Hardening (basic auth, rate limiting)

**Long-Term (Nice to Have)**:
6. Phase 11: Advanced Features
7. Phase 12: React Frontend Integration
8. Phase 14: CI/CD Integration

---

## Estimated Time to Complete

| Phase | Estimated Time |
|-------|----------------|
| 7. Dataset Preparation | 1-2 hours |
| 8. Initial Training | 2-4 hours (depending on dataset size) |
| 9. Integration Testing | 1-2 hours |
| 10. Docker Deployment | 1 hour |
| 13. Production Hardening (basic) | 2-3 hours |
| **Total MVP** | **7-12 hours** |

---

## Success Criteria

✅ **MVP Complete When**:
- [ ] Model trains successfully on CSE-CIC-IDS2018 (at least 2 days)
- [ ] PR-AUC > 0.80 on validation set
- [ ] Recall@1%FPR > 0.70
- [ ] All API endpoints return 200 OK
- [ ] Predictions return in < 10ms (p95)
- [ ] Artifacts persist and reload correctly
- [ ] Tests pass with >80% coverage
- [ ] Documentation is complete and accurate

✅ **Production-Ready When**:
- [ ] Docker deployment works end-to-end
- [ ] Authentication/authorization in place
- [ ] Monitoring and alerting configured
- [ ] Load testing shows stable performance (>100 req/s)
- [ ] Disaster recovery plan documented
- [ ] Frontend integration complete

---

## Notes

- **Leakage Prevention**: Always verify day-level splits; never use validation/test data for preprocessing stats
- **Class Imbalance**: CSE-CIC-IDS2018 is highly imbalanced; PR-AUC is more informative than ROC-AUC
- **Calibration**: Essential for trustworthy probabilities; always calibrate before deployment
- **Performance**: Parquet is 10-100x faster than CSV; convert early
- **Testing**: Use small synthetic fixtures for unit tests; save real dataset tests for integration

---

## Contact

Questions or issues? Open a GitHub issue or contact: antonio.gonto@nyu.edu

