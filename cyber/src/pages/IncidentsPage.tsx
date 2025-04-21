import React, { useEffect, useState } from 'react';
import {
  EuiPanel, EuiTitle, EuiSpacer, EuiButton, EuiFieldText,
  EuiFormRow, EuiSelect, EuiTextArea,
  EuiCallOut, EuiTable, EuiTableBody, EuiTableRow,
  EuiTableRowCell, EuiTableHeader, EuiTableHeaderCell
} from '@elastic/eui';

import { incidentService, userService } from '../services/api';

interface Incident {
  id: string | number;
  incident_type: string;
  description: string;
  severity: string;
  status: string;
  created_at: string;
  assigned_to?: { username: string };
}

interface User {
  id: string | number;
  username: string;
}

interface FormData {
  incident_type: string;
  description: string;
  severity: string;
  status: string;
  resolved_date: string;
  assigned_to_id: string | number;
}

const severityOptions = ['Low', 'Medium', 'High', 'Critical'].map(v => ({ value: v, text: v }));
const statusOptions = ['open', 'acknowledged', 'resolved', 'closed'].map(v => ({ value: v, text: v }));

const IncidentsPage = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [formData, setFormData] = useState<FormData>({
    incident_type: '',
    description: '',
    severity: 'Medium',
    status: 'open',
    resolved_date: '',
    assigned_to_id: ''
  });
  const [users, setUsers] = useState<User[]>([]);
  const [successMessage, setSuccessMessage] = useState<string>('');

  useEffect(() => {
    loadIncidents();
    userService.getUsers().then(res => setUsers(res.data));
  }, []);

  const loadIncidents = () => {
    incidentService.getIncidents({}).then(res => setIncidents(res.data));
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCreate = () => {
    incidentService.createIncident(formData).then(() => {
      setSuccessMessage('Incident created successfully.');
      setFormData({ incident_type: '', description: '', severity: 'Medium', status: 'open', resolved_date: '', assigned_to_id: '' });
      loadIncidents();
    });
  };

  return (
    <EuiPanel paddingSize="l">
      <EuiTitle size="l"><h1>Incident Management</h1></EuiTitle>
      <EuiSpacer size="l" />

      {successMessage && (
        <EuiCallOut title={successMessage} color="success" iconType="check" />
      )}

      <EuiFormRow label="Incident Type">
        <EuiFieldText
          value={formData.incident_type}
          onChange={e => handleChange('incident_type', e.target.value)}
        />
      </EuiFormRow>

      <EuiFormRow label="Description">
        <EuiTextArea
          value={formData.description}
          onChange={e => handleChange('description', e.target.value)}
        />
      </EuiFormRow>

      <EuiFormRow label="Severity">
        <EuiSelect
          options={severityOptions}
          value={formData.severity}
          onChange={e => handleChange('severity', e.target.value)}
        />
      </EuiFormRow>

      <EuiFormRow label="Status">
        <EuiSelect
          options={statusOptions}
          value={formData.status}
          onChange={e => handleChange('status', e.target.value)}
        />
      </EuiFormRow>

      <EuiFormRow label="Assigned To">
        <EuiSelect
          options={users.map(user => ({ value: user.id, text: user.username }))}
          value={formData.assigned_to_id}
          onChange={e => handleChange('assigned_to_id', e.target.value)}
        />
      </EuiFormRow>

      <EuiSpacer size="m" />
      <EuiButton fill onClick={handleCreate}>Create Incident</EuiButton>

      <EuiSpacer size="l" />
      <EuiTitle size="s"><h2>Incident List</h2></EuiTitle>
      <EuiSpacer size="m" />

      <EuiTable>
        <EuiTableHeader>
          <EuiTableHeaderCell>Type</EuiTableHeaderCell>
          <EuiTableHeaderCell>Severity</EuiTableHeaderCell>
          <EuiTableHeaderCell>Status</EuiTableHeaderCell>
          <EuiTableHeaderCell>Description</EuiTableHeaderCell>
          <EuiTableHeaderCell>Created</EuiTableHeaderCell>
          <EuiTableHeaderCell>Assigned To</EuiTableHeaderCell>
        </EuiTableHeader>
        <EuiTableBody>
          {incidents.map(incident => (
            <EuiTableRow key={incident.id}>
              <EuiTableRowCell>{incident.incident_type}</EuiTableRowCell>
              <EuiTableRowCell>{incident.severity}</EuiTableRowCell>
              <EuiTableRowCell>{incident.status}</EuiTableRowCell>
              <EuiTableRowCell>{incident.description}</EuiTableRowCell>
              <EuiTableRowCell>{new Date(incident.created_at).toLocaleString()}</EuiTableRowCell>
              <EuiTableRowCell>{incident.assigned_to?.username || 'Unassigned'}</EuiTableRowCell>
            </EuiTableRow>
          ))}
        </EuiTableBody>
      </EuiTable>
    </EuiPanel>
  );
};

export default IncidentsPage;