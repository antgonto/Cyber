// Training Dashboard Component
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import cyberIDSAPI from '../services/api';

// Default day configurations
const DEFAULT_DAYS = {
  train: ['Wednesday-14-02-2018', 'Thursday-15-02-2018'],
  val: ['Wednesday-21-02-2018'],
  test: [],
};

export default function TrainingDashboard() {
  const [trainDays, setTrainDays] = useState(DEFAULT_DAYS.train.join(', '));
  const [valDays, setValDays] = useState(DEFAULT_DAYS.val.join(', '));
  const [testDays, setTestDays] = useState('');
  const [calibrationMethod, setCalibrationMethod] = useState('isotonic');
  const [randomSeed, setRandomSeed] = useState(42);

  const [training, setTraining] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const parseDays = (daysString) => {
    return daysString
      .split(',')
      .map((d) => d.trim())
      .filter((d) => d.length > 0);
  };

  const handleTrain = async () => {
    setTraining(true);
    setError(null);
    setResults(null);

    const config = {
      train_days: parseDays(trainDays),
      val_days: parseDays(valDays),
      calibration_method: calibrationMethod,
      random_seed: parseInt(randomSeed),
    };

    if (testDays.trim()) {
      config.test_days = parseDays(testDays);
    }

    try {
      const response = await cyberIDSAPI.trainModel(config);
      setResults(response);
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Training failed');
    } finally {
      setTraining(false);
    }
  };

  const canTrain = trainDays.trim() && valDays.trim() && !training;

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Model Training
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Train a new intrusion detection model on the CSE-CIC-IDS2018 dataset.
      </Typography>

      {/* Training Configuration */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Training Configuration
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <Grid container spacing={3}>
            {/* Train Days */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Training Days"
                value={trainDays}
                onChange={(e) => setTrainDays(e.target.value)}
                helperText="Comma-separated day identifiers (e.g., Wednesday-14-02-2018, Thursday-15-02-2018)"
                placeholder="Wednesday-14-02-2018, Thursday-15-02-2018"
              />
            </Grid>

            {/* Validation Days */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Validation Days"
                value={valDays}
                onChange={(e) => setValDays(e.target.value)}
                helperText="Used for model selection and calibration"
                placeholder="Wednesday-21-02-2018"
              />
            </Grid>

            {/* Test Days (Optional) */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Test Days (Optional)"
                value={testDays}
                onChange={(e) => setTestDays(e.target.value)}
                helperText="Optional held-out test set"
                placeholder="Thursday-22-02-2018"
              />
            </Grid>

            {/* Calibration Method */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Calibration Method</InputLabel>
                <Select
                  value={calibrationMethod}
                  onChange={(e) => setCalibrationMethod(e.target.value)}
                  label="Calibration Method"
                >
                  <MenuItem value="isotonic">Isotonic Regression</MenuItem>
                  <MenuItem value="sigmoid">Platt Scaling (Sigmoid)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Random Seed */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Random Seed"
                value={randomSeed}
                onChange={(e) => setRandomSeed(e.target.value)}
                helperText="For reproducibility"
              />
            </Grid>
          </Grid>

          {/* Training Info */}
          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="body2">
              <strong>Training process:</strong>
              <br />
              1. Load data by day (temporal split to prevent leakage)
              <br />
              2. Train baselines (Majority, LogReg) and ensembles (RF, XGBoost)
              <br />
              3. Select champion by PR-AUC → Recall@1%FPR → F1
              <br />
              4. Calibrate probabilities with {calibrationMethod}
              <br />
              5. Save artifacts (model, metrics, manifest)
            </Typography>
          </Alert>

          {/* Train Button */}
          <Box display="flex" justifyContent="center" mt={3}>
            <Button
              variant="contained"
              size="large"
              startIcon={training ? <CircularProgress size={20} /> : <SchoolIcon />}
              onClick={handleTrain}
              disabled={!canTrain}
            >
              {training ? 'Training...' : 'Start Training'}
            </Button>
          </Box>

          {training && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="caption" display="block" textAlign="center" sx={{ mt: 1 }}>
                Training in progress... This may take 2-10 minutes depending on dataset size.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results Display */}
      {results && (
        <>
          {/* Success Alert */}
          {results.success && (
            <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 3 }}>
              Training completed successfully! Champion model: <strong>{results.champion}</strong>
            </Alert>
          )}

          {/* Metrics Summary */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Training Results
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Champion Model
                  </Typography>
                  <Typography variant="h5">{results.champion}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Model Version
                  </Typography>
                  <Typography variant="h5">{results.model_version}</Typography>
                </Grid>
              </Grid>

              {/* Primary Metrics */}
              <Box mt={3}>
                <Typography variant="subtitle1" gutterBottom>
                  Primary Metrics (Validation Set)
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" variant="body2">
                          PR-AUC (Macro)
                        </Typography>
                        <Typography variant="h4">
                          {results.metrics.pr_auc_macro.toFixed(4)}
                        </Typography>
                        <Chip
                          label={results.metrics.pr_auc_macro >= 0.85 ? 'Excellent' : 'Good'}
                          color={results.metrics.pr_auc_macro >= 0.85 ? 'success' : 'warning'}
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" variant="body2">
                          Recall @ 1% FPR
                        </Typography>
                        <Typography variant="h4">
                          {results.metrics.recall_at_fpr_1pct.toFixed(4)}
                        </Typography>
                        <Chip
                          label={results.metrics.recall_at_fpr_1pct >= 0.75 ? 'Excellent' : 'Good'}
                          color={results.metrics.recall_at_fpr_1pct >= 0.75 ? 'success' : 'warning'}
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" variant="body2">
                          F1 Score (Macro)
                        </Typography>
                        <Typography variant="h4">
                          {results.metrics.f1_macro.toFixed(4)}
                        </Typography>
                        <Chip
                          label={results.metrics.f1_macro >= 0.80 ? 'Excellent' : 'Good'}
                          color={results.metrics.f1_macro >= 0.80 ? 'success' : 'warning'}
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Box>

              {/* Additional Metrics */}
              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Additional Metrics</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Metric</TableCell>
                          <TableCell align="right">Value</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        <TableRow>
                          <TableCell>ROC-AUC</TableCell>
                          <TableCell align="right">
                            {results.metrics.roc_auc.toFixed(4)}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Brier Score</TableCell>
                          <TableCell align="right">
                            {results.metrics.brier_score.toFixed(4)}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Precision (Macro)</TableCell>
                          <TableCell align="right">
                            {results.metrics.precision_macro.toFixed(4)}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Recall (Macro)</TableCell>
                          <TableCell align="right">
                            {results.metrics.recall_macro.toFixed(4)}
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </AccordionDetails>
              </Accordion>

              {/* Training Time */}
              <Box mt={2} textAlign="center">
                <Typography variant="body2" color="text.secondary">
                  Training completed in {results.elapsed_seconds.toFixed(1)} seconds
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Artifact Paths */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Saved Artifacts
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box component="pre" sx={{ fontSize: '0.875rem', overflow: 'auto' }}>
                {JSON.stringify(results.artifact_paths, null, 2)}
              </Box>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
}

