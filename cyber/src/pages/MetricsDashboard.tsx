// Metrics Dashboard Component
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import SpeedIcon from '@mui/icons-material/Speed';
import cyberIDSAPI from '../services/api';

export default function MetricsDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [healthData, metricsData] = await Promise.all([
        cyberIDSAPI.getHealth(),
        cyberIDSAPI.getMetrics(),
      ]);

      setHealth(healthData);
      setMetrics(metricsData);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !metrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  const formatMetric = (value, decimals = 4) => {
    if (value === null || value === undefined) return 'N/A';
    return typeof value === 'number' ? value.toFixed(decimals) : value;
  };

  const getScoreColor = (value, thresholds = { good: 0.85, warning: 0.70 }) => {
    if (value >= thresholds.good) return 'success';
    if (value >= thresholds.warning) return 'warning';
    return 'error';
  };

  return (
    <Box>
      {/* Header with Refresh */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Model Performance Metrics</Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchData} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Health Status */}
      {health && (
        <Card sx={{ mb: 3, bgcolor: health.model_loaded ? 'success.light' : 'warning.light' }}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              {health.model_loaded ? (
                <CheckCircleIcon color="success" fontSize="large" />
              ) : (
                <ErrorIcon color="warning" fontSize="large" />
              )}
              <Box>
                <Typography variant="h6">
                  Status: {health.status === 'healthy' ? 'Healthy' : 'Unhealthy'}
                </Typography>
                <Typography variant="body2">
                  Model: {health.model_loaded ? `Loaded (v${health.model_version})` : 'Not Loaded'}
                </Typography>
                {health.n_features && (
                  <Typography variant="body2">Features: {health.n_features}</Typography>
                )}
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {metrics && (
        <>
          {/* Primary Metrics Cards */}
          <Grid container spacing={3} mb={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    PR-AUC (Macro)
                  </Typography>
                  <Typography variant="h3" component="div">
                    {formatMetric(metrics.metrics.pr_auc_macro)}
                  </Typography>
                  <Chip
                    label={
                      metrics.metrics.pr_auc_macro >= 0.85
                        ? 'Excellent'
                        : metrics.metrics.pr_auc_macro >= 0.70
                        ? 'Good'
                        : 'Needs Improvement'
                    }
                    color={getScoreColor(metrics.metrics.pr_auc_macro)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Primary metric for imbalanced data
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Recall @ 1% FPR
                  </Typography>
                  <Typography variant="h3" component="div">
                    {formatMetric(metrics.metrics.recall_at_fpr_1pct)}
                  </Typography>
                  <Chip
                    label={
                      metrics.metrics.recall_at_fpr_1pct >= 0.80
                        ? 'Excellent'
                        : metrics.metrics.recall_at_fpr_1pct >= 0.65
                        ? 'Good'
                        : 'Needs Improvement'
                    }
                    color={getScoreColor(metrics.metrics.recall_at_fpr_1pct, {
                      good: 0.80,
                      warning: 0.65,
                    })}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Detection rate at 1% false alarm rate
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    F1 Score (Macro)
                  </Typography>
                  <Typography variant="h3" component="div">
                    {formatMetric(metrics.metrics.f1_macro)}
                  </Typography>
                  <Chip
                    label={
                      metrics.metrics.f1_macro >= 0.85
                        ? 'Excellent'
                        : metrics.metrics.f1_macro >= 0.70
                        ? 'Good'
                        : 'Needs Improvement'
                    }
                    color={getScoreColor(metrics.metrics.f1_macro)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Harmonic mean of precision and recall
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Secondary Metrics Table */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Secondary Metrics
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Metric</TableCell>
                      <TableCell align="right">Value</TableCell>
                      <TableCell>Description</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>ROC-AUC</TableCell>
                      <TableCell align="right">
                        {formatMetric(metrics.metrics.roc_auc)}
                      </TableCell>
                      <TableCell>Area under ROC curve</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Brier Score</TableCell>
                      <TableCell align="right">
                        {formatMetric(metrics.metrics.brier_score)}
                      </TableCell>
                      <TableCell>Calibration quality (lower is better)</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Precision (Macro)</TableCell>
                      <TableCell align="right">
                        {formatMetric(metrics.metrics.precision_macro)}
                      </TableCell>
                      <TableCell>Average precision across classes</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Recall (Macro)</TableCell>
                      <TableCell align="right">
                        {formatMetric(metrics.metrics.recall_macro)}
                      </TableCell>
                      <TableCell>Average recall across classes</TableCell>
                    </TableRow>
                    {metrics.metrics.recall_at_fpr_0_1pct && (
                      <TableRow>
                        <TableCell>Recall @ 0.1% FPR</TableCell>
                        <TableCell align="right">
                          {formatMetric(metrics.metrics.recall_at_fpr_0_1pct)}
                        </TableCell>
                        <TableCell>Detection at very low false alarm rate</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* Attack Class Metrics */}
          {metrics.metrics.f1_attack && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Attack Class Performance
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="text.secondary">
                      Precision (Attack)
                    </Typography>
                    <Typography variant="h5">
                      {formatMetric(metrics.metrics.precision_attack)}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="text.secondary">
                      Recall (Attack)
                    </Typography>
                    <Typography variant="h5">
                      {formatMetric(metrics.metrics.recall_attack)}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="text.secondary">
                      F1 (Attack)
                    </Typography>
                    <Typography variant="h5">
                      {formatMetric(metrics.metrics.f1_attack)}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}

          {/* Latency Stats */}
          {metrics.latency_stats && metrics.latency_stats.count > 0 && (
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <SpeedIcon color="primary" />
                  <Typography variant="h6">Prediction Latency</Typography>
                </Box>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      P50 (Median)
                    </Typography>
                    <Typography variant="h6">
                      {formatMetric(metrics.latency_stats.p50_ms, 2)} ms
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      P95
                    </Typography>
                    <Typography variant="h6">
                      {formatMetric(metrics.latency_stats.p95_ms, 2)} ms
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Mean
                    </Typography>
                    <Typography variant="h6">
                      {formatMetric(metrics.latency_stats.mean_ms, 2)} ms
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Predictions
                    </Typography>
                    <Typography variant="h6">{metrics.latency_stats.count}</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}

          {/* Model Version Info */}
          <Box mt={3} textAlign="center">
            <Typography variant="caption" color="text.secondary">
              Model Version: {metrics.latest_version} | Last Updated: {new Date().toLocaleString()}
            </Typography>
          </Box>
        </>
      )}
    </Box>
  );
}

