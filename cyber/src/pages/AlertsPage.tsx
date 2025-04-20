import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import moment from 'moment';

// Interfaces based on the Alert model
interface Alert {
  alert_id: number;
  source: string;
  name: string;
  alert_type: string;
  alert_time: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'new' | 'acknowledged' | 'resolved' | 'closed';
  incident_id: number | null;
}
import {alertService, assetService} from '../services/api';

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [openCreateDialog, setOpenCreateDialog] = useState<boolean>(false);
  const [openViewDialog, setOpenViewDialog] = useState<boolean>(false);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await alertService.getAlerts();
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAlert = async (values: Omit<Alert, 'alert_id' | 'alert_time'>) => {
    try {
      const response = await fetch('/api/alerts/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        const newAlert = await response.json();
        setAlerts([newAlert, ...alerts]);
        setOpenCreateDialog(false);
        formik.resetForm();
      } else {
        const errorData = await response.json();
        console.error('Error creating alert:', errorData);
      }
    } catch (error) {
      console.error('Error submitting alert:', error);
    }
  };

  const handleViewAlert = (alert: Alert) => {
    setSelectedAlert(alert);
    setOpenViewDialog(true);
  };

  const formik = useFormik({
    initialValues: {
      source: '',
      name: '',
      alert_type: '',
      severity: 'low' as const,
      status: 'new' as const,
      incident_id: null as number | null,
    },
    validationSchema: Yup.object({
      source: Yup.string().required('Source is required'),
      name: Yup.string().required('Name is required'),
      alert_type: Yup.string().required('Alert type is required'),
      severity: Yup.string().oneOf(['low', 'medium', 'high', 'critical']).required('Severity is required'),
      status: Yup.string().oneOf(['new', 'acknowledged', 'resolved', 'closed']),
      incident_id: Yup.number().nullable(),
    }),
    onSubmit: handleCreateAlert,
  });

  // Get severity color for visual indication
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      default:
        return 'success';
    }
  };

  return (
    <Box sx={{ padding: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Security Alerts
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => setOpenCreateDialog(true)}
        >
          Create New Alert
        </Button>
      </Box>

      {loading ? (
        <Typography>Loading alerts...</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {alerts.map((alert) => (
                <TableRow key={alert.alert_id}>
                  <TableCell>{alert.alert_id}</TableCell>
                  <TableCell>{alert.name}</TableCell>
                  <TableCell>{alert.source}</TableCell>
                  <TableCell>{alert.alert_type}</TableCell>
                  <TableCell>{moment(alert.alert_time).format('YYYY-MM-DD HH:mm:ss')}</TableCell>
                  <TableCell>
                    <Chip
                      label={alert.severity.toUpperCase()}
                      color={getSeverityColor(alert.severity) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={alert.status.toUpperCase()}
                      color={alert.status === 'new' ? 'error' :
                             alert.status === 'acknowledged' ? 'warning' :
                             alert.status === 'resolved' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      onClick={() => handleViewAlert(alert)}
                    >
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Alert Dialog */}
      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
        <form onSubmit={formik.handleSubmit}>
          <DialogTitle>Create New Alert</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'grid', gap: 2, my: 2 }}>
              <TextField
                fullWidth
                id="name"
                name="name"
                label="Alert Name"
                value={formik.values.name}
                onChange={formik.handleChange}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
              />

              <TextField
                fullWidth
                id="source"
                name="source"
                label="Alert Source"
                value={formik.values.source}
                onChange={formik.handleChange}
                error={formik.touched.source && Boolean(formik.errors.source)}
                helperText={formik.touched.source && formik.errors.source}
              />

              <TextField
                fullWidth
                id="alert_type"
                name="alert_type"
                label="Alert Type"
                value={formik.values.alert_type}
                onChange={formik.handleChange}
                error={formik.touched.alert_type && Boolean(formik.errors.alert_type)}
                helperText={formik.touched.alert_type && formik.errors.alert_type}
              />

              <FormControl fullWidth>
                <InputLabel id="severity-label">Severity</InputLabel>
                <Select
                  labelId="severity-label"
                  id="severity"
                  name="severity"
                  value={formik.values.severity}
                  onChange={formik.handleChange}
                  label="Severity"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                id="incident_id"
                name="incident_id"
                label="Incident ID (Optional)"
                type="number"
                value={formik.values.incident_id || ''}
                onChange={(e) => {
                  const value = e.target.value === '' ? null : Number(e.target.value);
                  formik.setFieldValue('incident_id', value);
                }}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenCreateDialog(false)}>Cancel</Button>
            <Button type="submit" color="primary" variant="contained">Create</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* View Alert Dialog */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="md" fullWidth>
        {selectedAlert && (
          <>
            <DialogTitle>
              Alert Details: {selectedAlert.name}
              <Chip
                label={selectedAlert.severity.toUpperCase()}
                color={getSeverityColor(selectedAlert.severity) as any}
                sx={{ ml: 2 }}
              />
            </DialogTitle>
            <DialogContent>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, my: 2 }}>
                <Typography variant="body1"><strong>ID:</strong> {selectedAlert.alert_id}</Typography>
                <Typography variant="body1"><strong>Source:</strong> {selectedAlert.source}</Typography>
                <Typography variant="body1"><strong>Type:</strong> {selectedAlert.alert_type}</Typography>
                <Typography variant="body1">
                  <strong>Time:</strong> {moment(selectedAlert.alert_time).format('YYYY-MM-DD HH:mm:ss')}
                </Typography>
                <Typography variant="body1">
                  <strong>Status:</strong> {selectedAlert.status.toUpperCase()}
                </Typography>
                <Typography variant="body1">
                  <strong>Incident ID:</strong> {selectedAlert.incident_id || 'Not assigned'}
                </Typography>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
              <Button color="primary" variant="contained">
                Update Status
              </Button>
              {!selectedAlert.incident_id && (
                <Button color="secondary" variant="contained">
                  Create Incident
                </Button>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default AlertsPage;