# Cyber IDS Frontend - React Integration

## Overview

This directory contains the React frontend components for the Cyber IDS intrusion detection system. The UI provides three main interfaces:

1. **Metrics Dashboard** - Real-time model performance monitoring
2. **Prediction Interface** - Interactive flow prediction with custom features
3. **Training Dashboard** - Model training configuration and execution

## Components

```
cyber/src/pages/CyberIDS/
├── index.js                    # Main export
├── CyberIDS.js                 # Main dashboard with tabs
├── MetricsDashboard.js         # Metrics visualization (PR-AUC, F1, latency)
├── PredictionInterface.js      # Predict on network flows
└── TrainingDashboard.js        # Trigger training with config

cyber/src/services/
└── cyberIDSAPI.js              # API client for backend
```

## Installation

The components use Material-UI (MUI) for styling. Install dependencies:

```bash
cd cyber
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material axios
```

## Usage

### 1. Add to Router

In your main App.js or router configuration:

```javascript
import CyberIDS from './pages/CyberIDS';

// In your routes
<Route path="/cyber-ids" element={<CyberIDS />} />
```

### 2. Configure API Base URL

Set the environment variable for the API endpoint:

```bash
# .env.local
REACT_APP_API_BASE_URL=http://localhost:8000/app/v1/cyber
```

Or update `cyber/src/services/cyberIDSAPI.js` directly.

### 3. Navigate to Dashboard

```
http://localhost:3000/cyber-ids
```

## Features

### Metrics Dashboard

- **Real-time metrics**: PR-AUC, Recall@1% FPR, F1 score
- **Model health status**: Model loaded, version, feature count
- **Performance tracking**: Latency stats (p50, p95, mean)
- **Auto-refresh**: Updates every 30 seconds
- **Secondary metrics**: ROC-AUC, Brier score, precision, recall
- **Attack class metrics**: Dedicated attack performance indicators

### Prediction Interface

- **Flow input**: Enter CICFlowMeter features manually
- **Sample data**: Load benign or attack samples with one click
- **Batch prediction**: Predict up to 10 flows at once
- **Threshold control**: Adjust decision threshold (0-1)
- **Feature guide**: Tooltip help for common features
- **Results table**: Detailed prediction with confidence levels
- **Visual feedback**: Color-coded chips for attack/benign

### Training Dashboard

- **Day configuration**: Specify train/val/test days
- **Calibration method**: Choose isotonic or sigmoid (Platt scaling)
- **Random seed**: Set for reproducibility
- **Progress tracking**: Real-time training status
- **Results summary**: Champion model, metrics, elapsed time
- **Artifact paths**: View saved model and metric locations
- **Expandable metrics**: Detailed metric breakdown

## Screenshots

### Metrics Dashboard
```
┌────────────────────────────────────────────────────┐
│ 🛡️ Cyber IDS - Intrusion Detection System         │
├────────────────────────────────────────────────────┤
│ [ 📊 Metrics Dashboard ] [ 🔮 Predict ] [ 🎓 Train ]│
├────────────────────────────────────────────────────┤
│                                                    │
│  Status: Healthy ✓  Model: v20231120T123456Z      │
│                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ PR-AUC   │  │ Recall@  │  │ F1 Score │        │
│  │  0.9234  │  │  0.8567  │  │  0.8821  │        │
│  │ Excellent│  │ Excellent│  │ Excellent│        │
│  └──────────┘  └──────────┘  └──────────┘        │
│                                                    │
│  Secondary Metrics Table                          │
│  Latency Stats: p50=2.1ms, p95=3.8ms             │
└────────────────────────────────────────────────────┘
```

### Prediction Interface
```
┌────────────────────────────────────────────────────┐
│ Network Flow Prediction                           │
├────────────────────────────────────────────────────┤
│ [ Load Benign Sample ] [ Load Attack Sample ]     │
│                                                    │
│ Decision Threshold: [========•=====] 0.50         │
│                                                    │
│ Flow 1                                   [ × ]    │
│ ┌──────────────────────────────────────────────┐ │
│ │ Fwd Packet Length Mean: [  100.5  ]         │ │
│ │ Flow Duration:          [ 5000    ]         │ │
│ │ Total Fwd Packets:      [   10    ]         │ │
│ └──────────────────────────────────────────────┘ │
│                                                    │
│          [ ▶ Predict ]                             │
│                                                    │
│ Results:                                          │
│ ┌──────────────────────────────────────────────┐ │
│ │ Flow #1: ✅ BENIGN (prob: 0.12, High conf)  │ │
│ └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

### Training Dashboard
```
┌────────────────────────────────────────────────────┐
│ Model Training                                    │
├────────────────────────────────────────────────────┤
│ Training Configuration                            │
│                                                    │
│ Training Days: [Wednesday-14-02-2018, ...]       │
│ Validation Days: [Wednesday-21-02-2018]          │
│ Calibration Method: [ Isotonic Regression ▼ ]    │
│ Random Seed: [ 42 ]                               │
│                                                    │
│     [ 🎓 Start Training ]                         │
│                                                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Training...       │
│                                                    │
│ Results: Champion: xgboost                        │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│ │ PR-AUC   │  │ Recall@  │  │ F1 Score │        │
│ │  0.9234  │  │  0.8567  │  │  0.8821  │        │
│ └──────────┘  └──────────┘  └──────────┘        │
└────────────────────────────────────────────────────┘
```

## API Integration

The frontend communicates with the backend via REST API:

```javascript
// cyberIDSAPI.js

// GET /ml/health
getHealth() → { status, model_loaded, model_version, n_features }

// GET /ml/metrics
getMetrics() → { latest_version, metrics, latency_stats }

// POST /ml/train
trainModel(config) → { success, champion, model_version, metrics, artifact_paths }

// POST /ml/predict
predict(flows, threshold) → { predictions, count, latency_ms }
```

## Customization

### Change Color Theme

Edit the Chip/Alert colors in each component:

```javascript
// In MetricsDashboard.js
<Chip
  color={value >= 0.85 ? 'success' : 'warning'}  // Adjust thresholds
  ...
/>
```

### Add New Features

To add a new feature input field:

```javascript
// In PredictionInterface.js
const SAMPLE_FEATURES = {
  benign: {
    'Fwd Packet Length Mean': 100.5,
    'Your New Feature': 0.0,  // Add here
    ...
  }
};
```

### Change Auto-Refresh Interval

```javascript
// In MetricsDashboard.js
const interval = setInterval(fetchData, 30000);  // 30 seconds → change to 60000 for 1 minute
```

## Troubleshooting

### CORS Errors

Ensure Django settings allow your frontend origin:

```python
# app/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
```

### API Connection Refused

1. Check backend is running: `http://localhost:8000/app/v1/cyber/ml/health`
2. Verify `REACT_APP_API_BASE_URL` in `.env.local`
3. Check browser console for specific errors

### Prediction Fails

- Ensure all required features are provided
- Check feature names match CICFlowMeter output
- Verify threshold is between 0 and 1
- Model must be trained first

### Training Stuck

- Training can take 2-10 minutes depending on dataset size
- Check Django logs for errors
- Ensure CSE-CIC-IDS2018 dataset is mounted/accessible

## Performance

- **Metrics Dashboard**: ~500ms initial load, 30s auto-refresh
- **Prediction**: <100ms for single flow, <500ms for 10 flows
- **Training**: 2-10 minutes (backend, not frontend)

## Future Enhancements

- [ ] Real-time prediction feed (WebSocket)
- [ ] Charts/graphs for metric trends over time
- [ ] Model comparison view (compare multiple versions)
- [ ] Feature importance visualization
- [ ] SHAP explanation plots
- [ ] Dark mode toggle
- [ ] Export predictions to CSV
- [ ] Training progress bar with ETA
- [ ] Notification system for training completion

## Dependencies

```json
{
  "@mui/material": "^5.14.0",
  "@mui/icons-material": "^5.14.0",
  "@emotion/react": "^11.11.0",
  "@emotion/styled": "^11.11.0",
  "axios": "^1.5.0",
  "react": "^18.2.0"
}
```

## License

Part of the Cyber project. See main repository LICENSE.

## Support

For issues or questions:
- GitHub Issues: https://github.com/antgonto/Cyber/issues
- Email: antonio.gonto@nyu.edu

