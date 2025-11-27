# Cyber IDS Module - Complete Documentation Index

## 📖 Quick Navigation

### **Start Here**
1. **[HOW_TO_RUN.md](./HOW_TO_RUN.md)** ⭐ **NEW!** - Complete step-by-step running guide
2. **[CYBER_IDS_SUMMARY.md](./CYBER_IDS_SUMMARY.md)** - Executive summary, design principles, success metrics
3. **[CYBER_IDS_QUICKSTART.md](./CYBER_IDS_QUICKSTART.md)** - 5-minute setup guide for first-time users

### **Detailed Documentation**
4. **[CYBER_IDS_README.md](./CYBER_IDS_README.md)** - Comprehensive documentation (600+ lines)
5. **[CYBER_IDS_ARCHITECTURE.md](./CYBER_IDS_ARCHITECTURE.md)** - Visual architecture diagrams and workflows
6. **[CYBER_IDS_CHECKLIST.md](./CYBER_IDS_CHECKLIST.md)** - Implementation progress tracker
7. **[CYBER_IDS_FRONTEND_SUMMARY.md](./CYBER_IDS_FRONTEND_SUMMARY.md)** - React frontend implementation guide

---

## 🎯 What to Read When

### **"I'm new to this project"**
→ Start with **CYBER_IDS_SUMMARY.md** (Overview, design principles)  
→ Then **CYBER_IDS_QUICKSTART.md** (5-minute setup)  
→ Then **CYBER_IDS_ARCHITECTURE.md** (Visual diagrams)

### **"I want to train my first model"**
→ **CYBER_IDS_QUICKSTART.md** (Steps 1-4)  
→ **CYBER_IDS_README.md** → "Usage" section  
→ **CYBER_IDS_README.md** → "Troubleshooting" if issues

### **"I want to use the API"**
→ **CYBER_IDS_README.md** → "API Reference"  
→ **CYBER_IDS_ARCHITECTURE.md** → "Prediction Workflow"  
→ Interactive docs: `http://localhost:8000/app/v1/cyber/docs`

### **"I want to understand the code"**
→ **CYBER_IDS_ARCHITECTURE.md** → "Training Workflow (Detailed)"  
→ **CYBER_IDS_README.md** → "Configuration Reference"  
→ Inline docstrings in `cyber_ids/` modules

### **"I want to use the frontend UI"**
→ **CYBER_IDS_FRONTEND_SUMMARY.md** (Complete frontend guide)  
→ `cyber/src/pages/CyberIDS/README.md` (Setup instructions)  
→ Navigate to `http://localhost:3000/cyber-ids`

### **"I want to extend the module"**
→ **CYBER_IDS_README.md** → "Extending the Module"  
→ **CYBER_IDS_CHECKLIST.md** → "Phase 11: Advanced Features"  
→ Code examples in test files

### **"I want to deploy to production"**
→ **CYBER_IDS_README.md** → "Docker Deployment"  
→ **CYBER_IDS_CHECKLIST.md** → "Phase 13: Production Hardening"  
→ **CYBER_IDS_SUMMARY.md** → "Success Criteria"

### **"I have a specific error"**
→ **CYBER_IDS_README.md** → "Troubleshooting"  
→ **CYBER_IDS_QUICKSTART.md** → "Common First-Run Issues"  
→ GitHub Issues: https://github.com/antgonto/Cyber/issues

---

## 📊 Documentation by Purpose

### **Architecture & Design**
- [CYBER_IDS_SUMMARY.md](./CYBER_IDS_SUMMARY.md)
  - Design principles (leakage prevention, imbalance handling)
  - Technology stack
  - Expected performance benchmarks
  
- [CYBER_IDS_ARCHITECTURE.md](./CYBER_IDS_ARCHITECTURE.md)
  - High-level system diagram
  - Training workflow (step-by-step)
  - Prediction workflow
  - Data flow with leakage guards
  - Model selection logic
  - Calibration process

### **User Guides**
- [CYBER_IDS_QUICKSTART.md](./CYBER_IDS_QUICKSTART.md)
  - 5-minute setup
  - First training run
  - Testing endpoints
  - Common first-run issues
  
- [CYBER_IDS_README.md](./CYBER_IDS_README.md)
  - Comprehensive guide (600+ lines)
  - Installation, configuration, usage
  - CLI training, API usage, Docker deployment
  - API reference with curl examples
  - Configuration reference
  - Troubleshooting guide
  - Extension guide

### **Project Management**
- [CYBER_IDS_CHECKLIST.md](./CYBER_IDS_CHECKLIST.md)
  - Implementation phases (1-14)
  - ✅ Completed tasks
  - [ ] Remaining tasks
  - Priority ordering
  - Time estimates
  - Success criteria

---

## 🔍 Finding Specific Information

### **Dataset**
- Where to download: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Prepare Dataset"
- How to organize: [CYBER_IDS_QUICKSTART.md](./CYBER_IDS_QUICKSTART.md) → Step 2
- CSV to Parquet: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Prepare Dataset"

### **Training**
- CLI training: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Training via CLI"
- API training: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Training via API"
- Docker training: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Docker Deployment"
- Training workflow: [CYBER_IDS_ARCHITECTURE.md](./CYBER_IDS_ARCHITECTURE.md) → "Training Workflow"

### **Prediction**
- API prediction: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Prediction via API"
- Batch prediction: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Prediction via API"
- Prediction workflow: [CYBER_IDS_ARCHITECTURE.md](./CYBER_IDS_ARCHITECTURE.md) → "Prediction Workflow"

### **Metrics**
- Metrics explanation: [CYBER_IDS_SUMMARY.md](./CYBER_IDS_SUMMARY.md) → "Why These Design Choices?"
- API retrieval: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Retrieve Metrics"
- Expected performance: [CYBER_IDS_SUMMARY.md](./CYBER_IDS_SUMMARY.md) → "Expected Performance"

### **Configuration**
- Config file: `cyber_ids/config.py`
- Django settings: `app/settings.py` → "Cyber IDS Configuration"
- Configuration reference: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Configuration Reference"

### **Testing**
- Unit tests: `tests/cyber_ids/test_*.py`
- Running tests: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Testing"
- Test coverage: [CYBER_IDS_CHECKLIST.md](./CYBER_IDS_CHECKLIST.md) → "Phase 5: Testing"

### **Docker**
- Docker setup: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Docker Deployment"
- Volume mounts: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Update docker-compose.yml"
- Training in Docker: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Training in Docker"

### **Troubleshooting**
- Common issues: [CYBER_IDS_QUICKSTART.md](./CYBER_IDS_QUICKSTART.md) → "Common First-Run Issues"
- Detailed guide: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Troubleshooting"
- Error messages: Search in documentation

### **Extension & Customization**
- Add new model: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Add New Model"
- Add metrics: [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Add Per-Family Metrics"
- Advanced features: [CYBER_IDS_CHECKLIST.md](./CYBER_IDS_CHECKLIST.md) → "Phase 11"

---

## 📂 File Structure Reference

```
Documentation Files (This Directory):
├── CYBER_IDS_INDEX.md          ← You are here
├── CYBER_IDS_SUMMARY.md        (Executive summary, 400 lines)
├── CYBER_IDS_QUICKSTART.md     (5-minute guide, 200 lines)
├── CYBER_IDS_README.md         (Comprehensive, 600+ lines)
├── CYBER_IDS_ARCHITECTURE.md   (Visual diagrams, 500 lines)
└── CYBER_IDS_CHECKLIST.md      (Implementation tracker, 300 lines)

Code Modules:
├── cyber_ids/                  (Core ML module)
│   ├── config.py               (Configuration)
│   ├── data_pipeline/          (Data loading, preprocessing)
│   ├── models/                 (Training orchestrator)
│   ├── metrics/                (Evaluation metrics)
│   └── service/                (Model serving)
│
├── app/api/cyber_ids/          (Django Ninja API)
│   ├── schemas.py              (Pydantic models)
│   └── router.py               (Endpoints)
│
├── cyber/src/pages/CyberIDS/   (React Frontend - NEW!)
│   ├── index.js                (Main export)
│   ├── CyberIDS.js             (Main dashboard)
│   ├── MetricsDashboard.js     (Metrics monitoring)
│   ├── PredictionInterface.js  (Flow prediction)
│   ├── TrainingDashboard.js    (Model training)
│   └── README.md               (Frontend setup guide)
│
├── cyber/src/services/         (API Services)
│   └── cyberIDSAPI.js          (Backend API client)
│
└── tests/cyber_ids/            (Unit & integration tests)
    ├── test_data_pipeline.py
    ├── test_metrics.py
    └── test_api.py
```

---

## 🎓 Learning Path

### **Beginner** (First-Time User)
1. Read [CYBER_IDS_SUMMARY.md](./CYBER_IDS_SUMMARY.md) → "What Was Built"
2. Read [CYBER_IDS_SUMMARY.md](./CYBER_IDS_SUMMARY.md) → "Design Principles"
3. Follow [CYBER_IDS_QUICKSTART.md](./CYBER_IDS_QUICKSTART.md) (all steps)
4. Review [CYBER_IDS_ARCHITECTURE.md](./CYBER_IDS_ARCHITECTURE.md) → "High-Level System Architecture"

### **Intermediate** (Ready to Experiment)
1. Read [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Configuration Reference"
2. Modify `cyber_ids/config.py` (change hyperparameters)
3. Read [CYBER_IDS_ARCHITECTURE.md](./CYBER_IDS_ARCHITECTURE.md) → "Training Workflow (Detailed)"
4. Review inline docstrings in `cyber_ids/models/train.py`
5. Run training with different days/config

### **Advanced** (Extending the Module)
1. Read [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Extending the Module"
2. Review test files in `tests/cyber_ids/`
3. Read [CYBER_IDS_CHECKLIST.md](./CYBER_IDS_CHECKLIST.md) → "Phase 11: Advanced Features"
4. Implement custom features (new models, metrics, endpoints)
5. Write tests and update documentation

---

## 🔗 External Resources

### **Dataset**
- **CSE-CIC-IDS2018**: https://www.unb.ca/cic/datasets/ids-2018.html
- **Paper**: Sharafaldin et al., "Toward Generating a New Intrusion Detection Dataset" (ICISSP 2018)

### **Libraries**
- **scikit-learn**: https://scikit-learn.org/
- **XGBoost**: https://xgboost.readthedocs.io/
- **Django Ninja**: https://django-ninja.rest-framework.com/
- **Pydantic**: https://docs.pydantic.dev/

### **Concepts**
- **PR-AUC vs ROC-AUC**: https://machinelearningmastery.com/roc-curves-and-precision-recall-curves-for-imbalanced-classification/
- **Probability Calibration**: https://scikit-learn.org/stable/modules/calibration.html
- **Class Imbalance**: https://machinelearningmastery.com/tactics-to-combat-imbalanced-classes-in-your-machine-learning-dataset/

---

## ❓ FAQ

### **Q: Where do I start?**
**A:** Read [CYBER_IDS_SUMMARY.md](./CYBER_IDS_SUMMARY.md) for overview, then follow [CYBER_IDS_QUICKSTART.md](./CYBER_IDS_QUICKSTART.md).

### **Q: How do I train a model?**
**A:** See [CYBER_IDS_QUICKSTART.md](./CYBER_IDS_QUICKSTART.md) → Step 4 (CLI) or [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Training via API".

### **Q: What metrics should I look at?**
**A:** Primary: **PR-AUC** (>0.80), **Recall@1%FPR** (>0.70), **F1** (>0.80). See [CYBER_IDS_SUMMARY.md](./CYBER_IDS_SUMMARY.md) → "Expected Performance".

### **Q: Why is training slow?**
**A:** CSV parsing is slow. Convert to Parquet (see [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Prepare Dataset").

### **Q: How do I deploy to Docker?**
**A:** See [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Docker Deployment" section.

### **Q: Can I add a new model (e.g., LightGBM)?**
**A:** Yes! See [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Add New Model" section.

### **Q: How do I prevent data leakage?**
**A:** Day-level split is enforced. See [CYBER_IDS_ARCHITECTURE.md](./CYBER_IDS_ARCHITECTURE.md) → "Data Flow (Leakage Prevention)".

### **Q: What if my dataset has different column names?**
**A:** Update `DROP_COLS` in `cyber_ids/config.py` to match your dataset.

### **Q: How do I run tests?**
**A:** `pytest tests/cyber_ids/ -v`. See [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Testing".

### **Q: Where are model artifacts saved?**
**A:** `artifacts/ids/models/`. See [CYBER_IDS_ARCHITECTURE.md](./CYBER_IDS_ARCHITECTURE.md) → "File Organization".

---

## 📧 Support

**GitHub Issues**: https://github.com/antgonto/Cyber/issues  
**Email**: antonio.gonto@nyu.edu (project-specific questions)

---

## ✅ Quick Reference

| Task | Documentation |
|------|---------------|
| **Setup** | [CYBER_IDS_QUICKSTART.md](./CYBER_IDS_QUICKSTART.md) |
| **Train** | [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Training via CLI" |
| **Predict** | [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Prediction via API" |
| **Metrics** | [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Retrieve Metrics" |
| **Docker** | [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Docker Deployment" |
| **Test** | [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Testing" |
| **Config** | [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Configuration Reference" |
| **Troubleshoot** | [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Troubleshooting" |
| **Extend** | [CYBER_IDS_README.md](./CYBER_IDS_README.md) → "Extending the Module" |

---

*Last Updated: November 24, 2025*  
*Created by: GitHub Copilot (Senior ML + MLOps Engineer)*

