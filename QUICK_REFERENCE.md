# 🚀 Cyber IDS - Quick Reference Card

## ⚡ Ultra-Quick Start (Copy & Paste)

```bash
# 1. Install backend deps
pip install -r requirements.txt

# 2. Setup Django
python manage.py migrate

# 3. Install frontend deps
cd cyber
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material axios
echo "REACT_APP_API_BASE_URL=http://localhost:8000/app/v1/cyber" > .env.local
cd ..

# 4. Run backend (Terminal 1)
python manage.py runserver

# 5. Run frontend (Terminal 2 - from cyber/)
cd cyber && npm start

# 6. Open browser
# http://localhost:3000/cyber-ids
```

---

## 📍 Key URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend UI** | http://localhost:3000/cyber-ids | Interactive dashboards |
| **Backend API** | http://localhost:8000/app/v1/cyber/ml/ | REST endpoints |
| **Swagger Docs** | http://localhost:8000/app/v1/cyber/docs | API documentation |
| **Django Admin** | http://localhost:8000/admin | Django admin panel |

---

## 🎯 Common Commands

### Training
```bash
# CLI training
python -m cyber_ids.models.train

# API training
curl -X POST http://localhost:8000/app/v1/cyber/ml/train \
  -H "Content-Type: application/json" \
  -d '{"train_days": ["Wednesday-14-02-2018"], "val_days": ["Wednesday-21-02-2018"]}'
```

### Prediction
```bash
# API prediction
curl -X POST http://localhost:8000/app/v1/cyber/ml/predict \
  -H "Content-Type: application/json" \
  -d '{"flows": [{"Fwd Packet Length Mean": 500.0, "Flow Duration": 10000}]}'
```

### Metrics
```bash
# Get metrics
curl http://localhost:8000/app/v1/cyber/ml/metrics

# Health check
curl http://localhost:8000/app/v1/cyber/ml/health
```

### Testing
```bash
# Run all tests
pytest tests/cyber_ids/ -v

# Run with coverage
pytest tests/cyber_ids/ --cov=cyber_ids --cov-report=html
```

---

## 📂 File Locations

```
Project Root/
├── cyber_ids/              # ML module
├── app/api/cyber_ids/      # Django API
├── cyber/src/pages/CyberIDS/  # React UI
├── tests/cyber_ids/        # Tests
├── artifacts/ids/          # Trained models
├── data/cse-cic-ids2018/   # Dataset
└── HOW_TO_RUN.md          # Full guide ⭐
```

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| "Model not found" | Train model: `python -m cyber_ids.models.train` |
| "Data file not found" | Check: `ls data/cse-cic-ids2018/parquet/` |
| CORS errors | Already configured in `settings.py` |
| Module not found | Run: `pip install -r requirements.txt` |
| Frontend can't connect | Check backend running: `curl localhost:8000/app/v1/cyber/ml/health` |

---

## 📊 Expected Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Training (2 days) | 2-5 min | On 8-core CPU, 16GB RAM |
| Training (5+ days) | 10-20 min | Larger dataset |
| Single prediction | <10ms | p95 latency |
| Batch (10 flows) | <50ms | p95 latency |
| Frontend load | ~500ms | Initial dashboard load |

---

## ✅ Success Checklist

- [ ] Backend starts: `python manage.py runserver` ✓
- [ ] Frontend starts: `npm start` ✓
- [ ] Health check passes: `curl .../ml/health` returns 200 ✓
- [ ] UI loads: http://localhost:3000/cyber-ids ✓
- [ ] Can train model (if dataset available) ✓
- [ ] Can make predictions ✓

---

## 📖 Full Documentation

**Complete Guide**: [HOW_TO_RUN.md](./HOW_TO_RUN.md)  
**Navigation**: [CYBER_IDS_INDEX.md](./CYBER_IDS_INDEX.md)  
**Summary**: [CYBER_IDS_COMPLETE.md](./CYBER_IDS_COMPLETE.md)

---

*Quick reference for Cyber IDS v1.0*  
*For detailed instructions, see HOW_TO_RUN.md*

