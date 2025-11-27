# 🚀 Cyber IDS - How to Run (Step-by-Step Guide)

This guide provides complete instructions for running the Cyber IDS intrusion detection system, from installation to testing predictions.

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.11+** installed
- ✅ **Node.js 18+** and npm installed
- ✅ **Docker & Docker Compose** (optional, for containerized deployment)
- ✅ **8GB+ RAM** (16GB recommended for training)
- ✅ **10GB+ disk space** (for dataset and artifacts)

---

## 🎯 Quick Start (5 Minutes)

### Option A: Test API Without Dataset (Immediate)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Run Django migrations
python manage.py migrate

# 3. Start Django server
python manage.py runserver

# 4. Test health endpoint (in another terminal)
curl http://localhost:8000/app/v1/cyber/ml/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "model_loaded": false,
  "model_version": null,
  "n_features": null
}
```

### Option B: Full Setup with Frontend

```bash
# Backend (Terminal 1)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (Terminal 2)
cd cyber
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material axios
echo "REACT_APP_API_BASE_URL=http://localhost:8000/app/v1/cyber" > .env.local
npm start

# Open browser: http://localhost:3000/cyber-ids
```

---

## 📦 Detailed Setup Instructions

### Step 1: Backend Installation

#### 1.1 Clone or Navigate to Project
```bash
cd "D:\Dropbox\Universidades, educación y certificaciones\Universidades\NYU\CS-GY 6083 Database principles\Cyber"
```

#### 1.2 Install Python Dependencies
```bash
pip install -r requirements.txt
```

**This installs**:
- Django 5.1.7
- django-ninja 1.3.0
- numpy, pandas, scikit-learn, xgboost
- joblib, pyarrow (for Parquet)
- pytest, pytest-django, pytest-cov (for tests)

#### 1.3 Apply Database Migrations
```bash
python manage.py migrate
```

#### 1.4 Create Artifact Directories
```bash
mkdir -p artifacts/ids/models
mkdir -p artifacts/ids/metrics
mkdir -p artifacts/ids/pipeline
mkdir -p artifacts/ids/runs
```

#### 1.5 Verify Backend Installation
```bash
python -c "import cyber_ids; print('✅ Cyber IDS module loaded successfully')"
```

---

### Step 2: Dataset Setup (Optional for Training)

**Skip this step if you only want to test the API/UI without training**

#### 2.1 Download CSE-CIC-IDS2018

Download from: https://www.unb.ca/cic/datasets/ids-2018.html

Or use a subset for testing (recommended):
- Wednesday-14-02-2018 (2.7M rows, ~400MB CSV)
- Thursday-15-02-2018 (1.0M rows, ~150MB CSV)
- Wednesday-21-02-2018 (0.6M rows, ~90MB CSV)

#### 2.2 Organize Dataset
```bash
mkdir -p data/cse-cic-ids2018/raw

# Place CSV files in:
# data/cse-cic-ids2018/raw/Wednesday-14-02-2018/Wednesday-14-02-2018.csv
# data/cse-cic-ids2018/raw/Thursday-15-02-2018/Thursday-15-02-2018.csv
# data/cse-cic-ids2018/raw/Wednesday-21-02-2018/Wednesday-21-02-2018.csv
```

#### 2.3 Convert to Parquet (Recommended)
```bash
python -c "
from cyber_ids.data_pipeline.pipeline import convert_csv_to_parquet
from pathlib import Path

convert_csv_to_parquet(
    csv_dir=Path('data/cse-cic-ids2018/raw'),
    parquet_dir=Path('data/cse-cic-ids2018/parquet'),
    days=['Wednesday-14-02-2018', 'Thursday-15-02-2018', 'Wednesday-21-02-2018']
)
print('✅ Conversion complete')
"
```

#### 2.4 Verify Dataset
```bash
ls -lh data/cse-cic-ids2018/parquet/
```

---

### Step 3: Frontend Installation

#### 3.1 Navigate to Frontend Directory
```bash
cd cyber
```

#### 3.2 Install Node Dependencies
```bash
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material axios
```

**Alternatively, if you have package.json**:
```bash
npm install
```

#### 3.3 Configure API Base URL
```bash
# Create .env.local file
echo "REACT_APP_API_BASE_URL=http://localhost:8000/app/v1/cyber" > .env.local
```

Or manually create `.env.local`:
```
REACT_APP_API_BASE_URL=http://localhost:8000/app/v1/cyber
```

#### 3.4 Add CyberIDS Route to App.js

Edit `cyber/src/App.js` and add:

```javascript
import CyberIDS from './pages/CyberIDS';

// Inside your Routes component:
<Route path="/cyber-ids" element={<CyberIDS />} />
```

**Full example**:
```javascript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CyberIDS from './pages/CyberIDS';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/cyber-ids" element={<CyberIDS />} />
        {/* ...other routes */}
      </Routes>
    </Router>
  );
}

export default App;
```

---

## 🏃 Running the Application

### Method 1: Local Development (Recommended for Testing)

#### Terminal 1: Start Django Backend
```bash
# From project root
python manage.py runserver

# Server starts at: http://localhost:8000
```

#### Terminal 2: Start React Frontend
```bash
# From cyber/ directory
cd cyber
npm start

# App opens at: http://localhost:3000
```

#### Terminal 3: Test Backend API (Optional)
```bash
# Health check
curl http://localhost:8000/app/v1/cyber/ml/health

# Get metrics (will fail if model not trained yet)
curl http://localhost:8000/app/v1/cyber/ml/metrics
```

---

### Method 2: Docker (Production-like)

#### 2.1 Update docker-compose.yml

Add volume mounts:

```yaml
services:
  django:
    volumes:
      - .:/code
      - ./data:/code/data              # Dataset
      - ./artifacts:/code/artifacts    # Model artifacts
    # ...rest of config
```

#### 2.2 Build and Start Containers
```bash
docker-compose build
docker-compose up -d
```

#### 2.3 Access Services
- **Backend API**: http://localhost:8000/app/v1/cyber/ml/health
- **Frontend**: Configure separately or use nginx

---

## 🎓 Training Your First Model

### Option 1: Train via CLI

```bash
python -m cyber_ids.models.train
```

**Expected output**:
```
INFO - Loading data: train=['Wednesday-14-02-2018', 'Thursday-15-02-2018'], val=['Wednesday-21-02-2018']
INFO - Loaded 3700000 rows from 2 day(s)
INFO - Selected 76 features
INFO - Training majority class baseline...
INFO - Training logistic regression...
INFO - Training Random Forest...
INFO - Training XGBoost...
INFO - Evaluating models on validation set...
INFO - xgboost: PR-AUC=0.9234, Recall@1%FPR=0.8567, F1=0.8821
INFO - Champion model: xgboost
INFO - Calibrating model with method=isotonic...
INFO - Saved model: artifacts/ids/models/model_20231124T143022Z.joblib
INFO - Training complete in 142.3s

================================================================================
Training Summary
================================================================================
Champion: xgboost
PR-AUC: 0.9234
Recall@1%FPR: 0.8567
F1 (macro): 0.8821
Model path: artifacts/ids/models/model_20231124T143022Z.joblib
```

**Training time**: 2-5 minutes for 2 days, 10-20 minutes for 5+ days

### Option 2: Train via API (curl)

```bash
curl -X POST http://localhost:8000/app/v1/cyber/ml/train \
  -H "Content-Type: application/json" \
  -d '{
    "train_days": ["Wednesday-14-02-2018", "Thursday-15-02-2018"],
    "val_days": ["Wednesday-21-02-2018"],
    "calibration_method": "isotonic",
    "random_seed": 42
  }'
```

### Option 3: Train via Frontend UI

1. Open http://localhost:3000/cyber-ids
2. Click **"Train Model"** tab
3. Enter training days: `Wednesday-14-02-2018, Thursday-15-02-2018`
4. Enter validation days: `Wednesday-21-02-2018`
5. Select calibration method: `Isotonic Regression`
6. Click **"Start Training"**
7. Wait for progress bar to complete (2-5 minutes)
8. View results with metrics cards

---

## 🔮 Making Predictions

### Option 1: Predict via API (curl)

```bash
curl -X POST http://localhost:8000/app/v1/cyber/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "flows": [
      {
        "Fwd Packet Length Mean": 500.0,
        "Bwd Packet Length Mean": 300.0,
        "Flow Duration": 10000.0,
        "Total Fwd Packets": 20,
        "Total Bwd Packets": 15,
        "Fwd Packet Length Max": 1500.0,
        "Bwd Packet Length Max": 1000.0,
        "Flow Bytes/s": 50000.0,
        "Flow Packets/s": 3.5
      }
    ],
    "threshold": 0.5
  }'
```

**Expected response**:
```json
{
  "predictions": [
    {
      "label": 0,
      "prob": 0.1234,
      "model_version": "20231124T143022Z"
    }
  ],
  "count": 1,
  "latency_ms": 2.34
}
```

### Option 2: Predict via Frontend UI

1. Open http://localhost:3000/cyber-ids
2. Click **"Predict"** tab
3. Click **"Load Benign Sample"** or **"Load Attack Sample"**
4. Adjust threshold slider if needed
5. Click **"Predict"**
6. View results in table with confidence levels

### Option 3: Predict via Python Script

```python
import requests

API_URL = "http://localhost:8000/app/v1/cyber"

# Single flow prediction
flow = {
    "Fwd Packet Length Mean": 500.0,
    "Bwd Packet Length Mean": 300.0,
    "Flow Duration": 10000.0,
    "Total Fwd Packets": 20,
    "Total Bwd Packets": 15,
    "Fwd Packet Length Max": 1500.0,
    "Bwd Packet Length Max": 1000.0,
    "Flow Bytes/s": 50000.0,
    "Flow Packets/s": 3.5
}

response = requests.post(
    f"{API_URL}/ml/predict",
    json={"flows": [flow], "threshold": 0.5}
)

result = response.json()
print(f"Prediction: {'ATTACK' if result['predictions'][0]['label'] == 1 else 'BENIGN'}")
print(f"Probability: {result['predictions'][0]['prob']:.4f}")
```

---

## 📊 Viewing Metrics

### Option 1: Metrics via API

```bash
curl http://localhost:8000/app/v1/cyber/ml/metrics
```

### Option 2: Metrics via Frontend UI

1. Open http://localhost:3000/cyber-ids
2. View **"Metrics Dashboard"** tab (default)
3. See real-time metrics:
   - PR-AUC, Recall@1%FPR, F1 Score
   - ROC-AUC, Brier Score
   - Latency statistics
4. Dashboard auto-refreshes every 30 seconds

### Option 3: Swagger UI (Interactive API Docs)

1. Open http://localhost:8000/app/v1/cyber/docs
2. Explore all endpoints
3. Test directly in browser

---

## 🧪 Running Tests

### Run All Tests
```bash
pytest tests/cyber_ids/ -v
```

### Run Specific Test Modules
```bash
# Data pipeline tests
pytest tests/cyber_ids/test_data_pipeline.py -v

# Metrics tests
pytest tests/cyber_ids/test_metrics.py -v

# API tests
pytest tests/cyber_ids/test_api.py -v
```

### Run with Coverage
```bash
pytest tests/cyber_ids/ --cov=cyber_ids --cov-report=html

# View coverage report
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html  # Windows
```

---

## 🐛 Troubleshooting

### Issue 1: "Model not found" when predicting

**Cause**: No model has been trained yet

**Solution**:
```bash
# Train a model first
python -m cyber_ids.models.train

# Or via API/UI
```

### Issue 2: "Data file not found" during training

**Cause**: Dataset not in expected location

**Solution**:
```bash
# Check data directory
ls data/cse-cic-ids2018/parquet/

# Update config if needed
# Edit cyber_ids/config.py: DATA_DIR = Path("your/path")
```

### Issue 3: CORS errors in frontend

**Cause**: Django not allowing frontend origin

**Solution**:
```python
# In app/settings.py (already configured)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
```

### Issue 4: "ModuleNotFoundError: No module named 'xgboost'"

**Cause**: XGBoost not installed

**Solution**:
```bash
pip install xgboost
```

### Issue 5: Frontend not connecting to backend

**Cause**: Wrong API URL or backend not running

**Solution**:
```bash
# 1. Check backend is running
curl http://localhost:8000/app/v1/cyber/ml/health

# 2. Verify .env.local in cyber/
cat cyber/.env.local
# Should show: REACT_APP_API_BASE_URL=http://localhost:8000/app/v1/cyber

# 3. Restart frontend
cd cyber
npm start
```

### Issue 6: Training takes too long

**Cause**: Large dataset

**Solution**:
```python
# Start with smaller subset (1-2 days)
# Edit cyber_ids/config.py:
DEFAULT_TRAIN_DAYS = ["Wednesday-14-02-2018"]  # Just 1 day
DEFAULT_VAL_DAYS = ["Wednesday-21-02-2018"]
```

---

## 📈 Performance Tips

### Faster Training
1. **Use Parquet instead of CSV** (10-100x faster loading)
2. **Reduce n_estimators** for prototyping (RF: 100, XGBoost: 200)
3. **Use fewer days** (1-2 days for testing)
4. **Ensure adequate RAM** (8GB minimum, 16GB recommended)

### Faster Inference
1. **Batch predictions** (up to 100 flows per request)
2. **Model is cached** after first load (subsequent calls are faster)
3. **Use Parquet for faster feature loading**

---

## 🚀 Production Deployment

### Using Docker

1. **Update docker-compose.yml** with volume mounts
2. **Build image**: `docker-compose build`
3. **Start services**: `docker-compose up -d`
4. **Train model**: `docker exec -it django python -m cyber_ids.models.train`
5. **Test API**: `curl http://localhost:8000/app/v1/cyber/ml/health`

### Environment Variables

```bash
# .env file
POSTGRES_USERNAME=cyber_user
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=cyber_db
POSTGRES_HOST=cyber_db
POSTGRES_PORT=5432
REDIS_PASSWORD=your_redis_password
REDIS_PORT=6379

# Frontend .env.local
REACT_APP_API_BASE_URL=http://your-domain.com/app/v1/cyber
```

---

## 📋 Quick Reference

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ml/health` | GET | Model status |
| `/ml/metrics` | GET | Performance metrics |
| `/ml/train` | POST | Trigger training |
| `/ml/predict` | POST | Predict on flows |

### Frontend Routes
| Route | Purpose |
|-------|---------|
| `/cyber-ids` | Main dashboard |
| `/cyber-ids` → Metrics Dashboard | View metrics |
| `/cyber-ids` → Predict | Test predictions |
| `/cyber-ids` → Train Model | Train new model |

### Key Files
| File | Purpose |
|------|---------|
| `cyber_ids/config.py` | Configuration |
| `cyber_ids/models/train.py` | Training script |
| `app/api/cyber_ids/router.py` | API endpoints |
| `cyber/src/pages/CyberIDS/CyberIDS.js` | Frontend main |

---

## ✅ Success Checklist

Before considering setup complete:

- [ ] Backend starts without errors (`python manage.py runserver`)
- [ ] Frontend starts without errors (`npm start`)
- [ ] Health endpoint returns 200 (`curl .../ml/health`)
- [ ] Can access frontend UI (`http://localhost:3000/cyber-ids`)
- [ ] Dataset is organized (if training)
- [ ] Can train model successfully (CLI or UI)
- [ ] Can make predictions (API or UI)
- [ ] Metrics dashboard loads

---

## 🎯 Next Steps

1. ✅ **Complete setup** (follow this guide)
2. ✅ **Train first model** (2-5 minutes)
3. ✅ **Test predictions** via UI
4. ✅ **Monitor metrics** dashboard
5. ⏩ **Integrate with your app** (add custom flows)
6. ⏩ **Deploy to production** (Docker)
7. ⏩ **Set up monitoring** (Prometheus/Grafana)

---

## 📞 Support

**Issues**: Open a GitHub issue  
**Questions**: Email antonio.gonto@nyu.edu  
**Documentation**: See [CYBER_IDS_INDEX.md](./CYBER_IDS_INDEX.md)

---

*Last updated: November 24, 2025*  
*Ready to run! 🚀*

