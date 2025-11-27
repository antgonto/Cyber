// Prediction Interface Component
import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Slider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Collapse,
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import cyberIDSAPI from '../services/api';

// Sample CICFlowMeter features for demo
const SAMPLE_FEATURES = {
  benign: {
    'Fwd Packet Length Mean': 100.5,
    'Bwd Packet Length Mean': 80.3,
    'Flow Duration': 5000,
    'Total Fwd Packets': 10,
    'Total Bwd Packets': 8,
    'Fwd Packet Length Max': 1500,
    'Bwd Packet Length Max': 1200,
    'Flow Bytes/s': 25000,
    'Flow Packets/s': 3.6,
  },
  attack: {
    'Fwd Packet Length Mean': 1200.0,
    'Bwd Packet Length Mean': 50.0,
    'Flow Duration': 100,
    'Total Fwd Packets': 500,
    'Total Bwd Packets': 2,
    'Fwd Packet Length Max': 1500,
    'Bwd Packet Length Max': 100,
    'Flow Bytes/s': 500000,
    'Flow Packets/s': 5000.0,
  },
};

export default function PredictionInterface() {
  const [flows, setFlows] = useState([{ ...SAMPLE_FEATURES.benign }]);
  const [threshold, setThreshold] = useState(0.5);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [showFeatureHelper, setShowFeatureHelper] = useState(false);

  const handleFeatureChange = (flowIndex, featureName, value) => {
    const newFlows = [...flows];
    newFlows[flowIndex][featureName] = parseFloat(value) || 0;
    setFlows(newFlows);
  };

  const addFlow = () => {
    if (flows.length < 10) {
      setFlows([...flows, { ...SAMPLE_FEATURES.benign }]);
    }
  };

  const removeFlow = (index) => {
    if (flows.length > 1) {
      setFlows(flows.filter((_, i) => i !== index));
    }
  };

  const loadSample = (type) => {
    setFlows([{ ...SAMPLE_FEATURES[type] }]);
  };

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await cyberIDSAPI.predict(flows, threshold);
      setResults(response);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Network Flow Prediction
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Enter CICFlowMeter features for network flows to predict if they are benign or attack traffic.
      </Typography>

      {/* Quick Actions */}
      <Box mb={3} display="flex" gap={2} flexWrap="wrap">
        <Button
          variant="outlined"
          size="small"
          onClick={() => loadSample('benign')}
          startIcon={<SecurityIcon />}
        >
          Load Benign Sample
        </Button>
        <Button
          variant="outlined"
          size="small"
          onClick={() => loadSample('attack')}
          startIcon={<WarningIcon />}
          color="error"
        >
          Load Attack Sample
        </Button>
        <Button
          variant="outlined"
          size="small"
          onClick={() => setShowFeatureHelper(!showFeatureHelper)}
          startIcon={<ExpandMoreIcon />}
        >
          Feature Guide
        </Button>
      </Box>

      {/* Feature Helper */}
      <Collapse in={showFeatureHelper}>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Common CICFlowMeter Features:
          </Typography>
          <Typography variant="body2" component="div">
            • <strong>Packet Length Mean/Max</strong>: Average/maximum packet size in bytes
            <br />
            • <strong>Flow Duration</strong>: Total duration of flow in microseconds
            <br />
            • <strong>Total Packets</strong>: Number of packets sent/received
            <br />
            • <strong>Flow Bytes/s</strong>: Data transfer rate
            <br />• <strong>Flow Packets/s</strong>: Packet rate
          </Typography>
        </Alert>
      </Collapse>

      {/* Threshold Slider */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography gutterBottom>Decision Threshold: {threshold.toFixed(2)}</Typography>
          <Slider
            value={threshold}
            onChange={(e, newValue) => setThreshold(newValue)}
            min={0}
            max={1}
            step={0.05}
            marks={[
              { value: 0, label: '0' },
              { value: 0.5, label: '0.5' },
              { value: 1, label: '1' },
            ]}
            valueLabelDisplay="auto"
          />
          <Typography variant="caption" color="text.secondary">
            Lower threshold = more sensitive (more detections, higher false alarms)
          </Typography>
        </CardContent>
      </Card>

      {/* Flow Input Forms */}
      {flows.map((flow, flowIndex) => (
        <Card key={flowIndex} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Flow {flowIndex + 1}</Typography>
              {flows.length > 1 && (
                <IconButton
                  onClick={() => removeFlow(flowIndex)}
                  color="error"
                  size="small"
                >
                  <DeleteIcon />
                </IconButton>
              )}
            </Box>
            <Grid container spacing={2}>
              {Object.entries(flow).map(([featureName, value]) => (
                <Grid item xs={12} sm={6} md={4} key={featureName}>
                  <TextField
                    fullWidth
                    label={featureName}
                    type="number"
                    value={value}
                    onChange={(e) =>
                      handleFeatureChange(flowIndex, featureName, e.target.value)
                    }
                    size="small"
                    inputProps={{ step: 0.1 }}
                  />
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      ))}

      {/* Add Flow Button */}
      {flows.length < 10 && (
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={addFlow}
          sx={{ mb: 3 }}
        >
          Add Another Flow (Max 10)
        </Button>
      )}

      {/* Predict Button */}
      <Box display="flex" justifyContent="center" mb={3}>
        <Button
          variant="contained"
          size="large"
          startIcon={loading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          onClick={handlePredict}
          disabled={loading || flows.length === 0}
        >
          {loading ? 'Predicting...' : 'Predict'}
        </Button>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results Display */}
      {results && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Prediction Results
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Flow #</TableCell>
                    <TableCell>Prediction</TableCell>
                    <TableCell align="right">Probability</TableCell>
                    <TableCell align="right">Confidence</TableCell>
                    <TableCell>Model Version</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.predictions.map((pred, idx) => (
                    <TableRow key={idx}>
                      <TableCell>{idx + 1}</TableCell>
                      <TableCell>
                        <Chip
                          label={pred.label === 1 ? '⚠️ ATTACK' : '✅ BENIGN'}
                          color={pred.label === 1 ? 'error' : 'success'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">{pred.prob.toFixed(4)}</TableCell>
                      <TableCell align="right">
                        <Chip
                          label={
                            pred.prob > 0.9 || pred.prob < 0.1
                              ? 'High'
                              : pred.prob > 0.7 || pred.prob < 0.3
                              ? 'Medium'
                              : 'Low'
                          }
                          color={
                            pred.prob > 0.9 || pred.prob < 0.1
                              ? 'success'
                              : pred.prob > 0.7 || pred.prob < 0.3
                              ? 'warning'
                              : 'default'
                          }
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{pred.model_version}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Summary Stats */}
            <Box mt={2} display="flex" gap={3} flexWrap="wrap">
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Total Flows
                </Typography>
                <Typography variant="h6">{results.count}</Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Attacks Detected
                </Typography>
                <Typography variant="h6" color="error.main">
                  {results.predictions.filter((p) => p.label === 1).length}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Benign Flows
                </Typography>
                <Typography variant="h6" color="success.main">
                  {results.predictions.filter((p) => p.label === 0).length}
                </Typography>
              </Box>
              {results.latency_ms && (
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Latency
                  </Typography>
                  <Typography variant="h6">{results.latency_ms.toFixed(2)} ms</Typography>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

