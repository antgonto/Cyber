import React, { useEffect, useState } from 'react';
import {
  EuiForm, EuiFormRow, EuiFieldText, EuiSelect,
  EuiDatePicker, EuiButton, EuiSpacer, EuiTitle, EuiText,
  EuiFlexGroup, EuiFlexItem
} from '@elastic/eui';
import moment from 'moment';
import { incidentService, alertService } from '../services/api';

const AlertForm = () => {
  const [alerts, setAlerts] = useState([]);
  const [selectedAlertId, setSelectedAlertId] = useState('');
  const [incidents, setIncidents] = useState([]);
  const [incidentDetails, setIncidentDetails] = useState({ assets: [], threats: [], vulnerabilities: [] });

  const defaultFormData = {
    source: '',
    name: '',
    alert_type: '',
    alert_time: moment(),
    severity: 'Medium',
    status: 'Active',
    incident_id: ''
  };
  const [formData, setFormData] = useState(defaultFormData);

  const severityOptions = ['Critical', 'High', 'Medium', 'Low'].map(val => ({ value: val, text: val }));
  const statusOptions = ['Active', 'Closed'].map(val => ({ value: val, text: val }));

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async() => {
    try {
      const alertParams = {}; // Adding empty params object as required argument
      const incidents = await incidentService.getIncidents({});
      const alertsResponse = await alertService.getAlerts(alertParams);
      setIncidents(incidents.data);
      setAlerts(alertsResponse.data.alerts);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const handleAlertSelect = (alertId) => {
    setSelectedAlertId(alertId);
    if (alertId) {
      alertService.getAlert(alertId).then(res => {
        console.log(alertId)
        const alert = res.data;
        setFormData({
          source: alert.source,
          name: alert.name,
          alert_type: alert.alert_type,
          alert_time: moment(alert.alert_time),
          severity: alert.severity,
          status: alert.status,
          incident_id: alert.incident_id || ''
        });
      });
    } else {
      setFormData(defaultFormData);
    }
  };

  useEffect(() => {
    if (formData.incident_id) {
      incidentService.getIncidentById(formData.incident_id).then(res => {
        const { assets, threats } = res.data;
        const vulnSet = new Set();
        threats.forEach(t => t.related_cve && vulnSet.add(t.related_cve));
        setIncidentDetails({
          assets: assets.map(a => a.asset_name),
          threats: threats.map(t => t.threat_actor_name),
          vulnerabilities: [...vulnSet]
        });
      });
    } else {
      setIncidentDetails({ assets: [], threats: [], vulnerabilities: [] });
    }
  }, [formData.incident_id]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCreate = () => {
    alertService.createAlert({ ...formData, alert_time: formData.alert_time.toISOString() }).then(() => {
      alert('Alert created');
      setFormData(defaultFormData);
      setSelectedAlertId('');
      loadAlerts();
    });
  };

  const handleUpdate = () => {
    alertService.updateAlert(selectedAlertId, { ...formData, alert_time: formData.alert_time.toISOString() }).then(() => {
      alert('Alert updated');
      loadAlerts();
    });
  };

  const handleDelete = () => {
    alertService.deleteAlert(selectedAlertId).then(() => {
      alert('Alert deleted');
      setFormData(defaultFormData);
      setSelectedAlertId('');
      loadAlerts();
    });
  };

  return (
    <>
      <EuiTitle><h2>Manage Cybersecurity Alerts</h2></EuiTitle>
      <EuiSpacer />

      <EuiFormRow label="Select Existing Alert">
        <EuiSelect
          options={[{ value: '', text: 'Create New Alert' }, ...alerts.map(a => ({ value: a.alert_id, text: a.name }))]}
          value={selectedAlertId}
          onChange={e => handleAlertSelect(e.target.value)}
        />
      </EuiFormRow>

      <EuiForm component="form">
        <EuiFormRow label="Source">
          <EuiFieldText value={formData.source} onChange={e => handleChange('source', e.target.value)} />
        </EuiFormRow>
        <EuiFormRow label="Name">
          <EuiFieldText value={formData.name} onChange={e => handleChange('name', e.target.value)} />
        </EuiFormRow>
        <EuiFormRow label="Alert Type">
          <EuiFieldText value={formData.alert_type} onChange={e => handleChange('alert_type', e.target.value)} />
        </EuiFormRow>
        <EuiFormRow label="Alert Time">
          <EuiDatePicker selected={formData.alert_time} onChange={date => handleChange('alert_time', date)} showTimeSelect />
        </EuiFormRow>
        <EuiFormRow label="Severity">
          <EuiSelect options={severityOptions} value={formData.severity} onChange={e => handleChange('severity', e.target.value)} />
        </EuiFormRow>
        <EuiFormRow label="Status">
          <EuiSelect options={statusOptions} value={formData.status} onChange={e => handleChange('status', e.target.value)} />
        </EuiFormRow>
        <EuiFormRow label="Linked Incident">
          <EuiSelect
            options={[{ value: '', text: 'None' }, ...incidents.map(i => ({ value: i.incident_id, text: `${i.incident_type} (${i.severity})` }))]}
            value={formData.incident_id}
            onChange={e => handleChange('incident_id', e.target.value)}
          />
        </EuiFormRow>

        {formData.incident_id && (
          <>
            <EuiSpacer />
            <EuiTitle size="xs"><h4>Incident Context</h4></EuiTitle>
            <EuiText><strong>Assets:</strong> {incidentDetails.assets.join(', ') || 'None'}</EuiText>
            <EuiText><strong>Threats:</strong> {incidentDetails.threats.join(', ') || 'None'}</EuiText>
            <EuiText><strong>Vulnerabilities:</strong> {incidentDetails.vulnerabilities.join(', ') || 'None'}</EuiText>
          </>
        )}

        <EuiSpacer size="l" />
        <EuiFlexGroup>
          <EuiFlexItem grow={false}>
            <EuiButton fill onClick={handleCreate} isDisabled={!!selectedAlertId}>Create</EuiButton>
          </EuiFlexItem>
          <EuiFlexItem grow={false}>
            <EuiButton color="primary" onClick={handleUpdate} isDisabled={!selectedAlertId}>Update</EuiButton>
          </EuiFlexItem>
          <EuiFlexItem grow={false}>
            <EuiButton color="danger" onClick={handleDelete} isDisabled={!selectedAlertId}>Delete</EuiButton>
          </EuiFlexItem>
        </EuiFlexGroup>
      </EuiForm>
    </>
  );
};

export default AlertForm;