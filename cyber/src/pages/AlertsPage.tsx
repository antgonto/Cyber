import React, { useState, useEffect } from 'react';
import {
  EuiBasicTable,
  EuiButton,
  EuiFormRow,
  EuiFieldText,
  EuiSpacer,
  EuiModal,
  EuiModalBody,
  EuiModalFooter,
  EuiModalHeader,
  EuiModalHeaderTitle,
  EuiPageHeader,
  EuiPanel,
  EuiSelect,
  EuiConfirmModal,
  EuiDatePicker,
} from '@elastic/eui';
import { alertService, incidentService } from '../services/api';
import moment from 'moment';

// Define alert interface
interface Alert {
  id: string;
  source: string;
  name: string;
  alertType: string;
  alertTime: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'new' | 'acknowledged' | 'resolved' | 'closed';
  incidentId?: string;
}

// Backend alert interface
interface BackendAlert {
  alert_id: number;
  source: string;
  name: string;
  alert_type: string;
  alert_time: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'new' | 'acknowledged' | 'resolved' | 'closed';
  incident_id?: number;
}

const AlertsPage: React.FC = () => {
  // State for alerts data
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [incidents, setIncidents] = useState<any[]>([]);

  // State for modal and form
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
  const [isDeleteModalVisible, setIsDeleteModalVisible] = useState<boolean>(false);
  const [currentAlert, setCurrentAlert] = useState<Alert | null>(null);
  const [formData, setFormData] = useState<Omit<Alert, 'id'>>({
    source: '',
    name: '',
    alertType: '',
    alertTime: new Date().toISOString(),
    severity: 'medium',
    status: 'new',
  });

  // Fetch alerts data
  useEffect(() => {
    fetchAlerts();
    fetchIncidents();
  }, []);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const response = await alertService.getAlerts({});
      // Transform backend data format to match frontend Alert interface
      const transformedData = response.data.alerts.map((alert: BackendAlert) => ({
        id: alert.alert_id.toString(),
        source: alert.source,
        name: alert.name,
        alertType: alert.alert_type,
        alertTime: alert.alert_time,
        severity: alert.severity,
        status: alert.status,
        incidentId: alert.incident_id ? alert.incident_id.toString() : undefined
      }));
      setAlerts(transformedData);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchIncidents = async () => {
    try {
      const response = await incidentService.getIncidents({});
      setIncidents(response.data);
    } catch (error) {
      console.error('Failed to fetch incidents:', error);
    }
  };

  // Create new alert
  const createAlert = async () => {
    try {
      const alertData = {
        source: formData.source,
        name: formData.name,
        alert_type: formData.alertType,
        alert_time: moment(formData.alertTime).toISOString(),
        severity: formData.severity,
        status: formData.status,
        incident_id: formData.incidentId ? parseInt(formData.incidentId) : null
      };

      const response = await alertService.createAlert(alertData);

      // Add the new alert to the list
      const newAlert: Alert = {
        id: response.data.alert_id.toString(),
        source: response.data.source,
        name: response.data.name,
        alertType: response.data.alert_type,
        alertTime: response.data.alert_time,
        severity: response.data.severity,
        status: response.data.status,
        incidentId: response.data.incident_id ? response.data.incident_id.toString() : undefined
      };

      setAlerts([...alerts, newAlert]);
      closeModal();
    } catch (error) {
      console.error('Failed to create alert:', error);
    }
  };

  // Update existing alert
  const updateAlert = async () => {
    if (!currentAlert) return;

    try {
      const alertData = {
        source: formData.source,
        name: formData.name,
        alert_type: formData.alertType,
        alert_time: moment(formData.alertTime).toISOString(),
        severity: formData.severity,
        status: formData.status,
        incident_id: formData.incidentId ? parseInt(formData.incidentId) : null
      };

      await alertService.updateAlert(currentAlert.id, alertData);

      // Update the alert in the list
      const updatedAlerts = alerts.map(alert =>
        alert.id === currentAlert.id
          ? { ...alert, ...formData }
          : alert
      );

      setAlerts(updatedAlerts);
      closeModal();
    } catch (error) {
      console.error('Failed to update alert:', error);
    }
  };

  // Delete alert
  const deleteAlert = async () => {
    if (!currentAlert) return;

    try {
      await alertService.deleteAlert(currentAlert.id);

      // Remove the alert from the list
      const filteredAlerts = alerts.filter(
        alert => alert.id !== currentAlert.id
      );

      setAlerts(filteredAlerts);
      closeDeleteModal();
    } catch (error) {
      console.error('Failed to delete alert:', error);
    }
  };

  // Handle form input changes
  const handleInputChange = (field: string, value: any) => {
    setFormData({
      ...formData,
      [field]: value,
    });
  };

  // Open modal for creating new alert
  const openCreateModal = () => {
    setCurrentAlert(null);
    setFormData({
      source: '',
      name: '',
      alertType: '',
      alertTime: new Date().toISOString(),
      severity: 'medium',
      status: 'new',
    });
    setIsModalVisible(true);
  };

  // Open modal for editing existing alert
  const openEditModal = (alert: Alert) => {
    setCurrentAlert(alert);
    setFormData({
      source: alert.source,
      name: alert.name,
      alertType: alert.alertType,
      alertTime: alert.alertTime,
      severity: alert.severity,
      status: alert.status,
      incidentId: alert.incidentId,
    });
    setIsModalVisible(true);
  };

  // Open delete confirmation modal
  const openDeleteModal = (alert: Alert) => {
    setCurrentAlert(alert);
    setIsDeleteModalVisible(true);
  };

  // Close modals
  const closeModal = () => {
    setIsModalVisible(false);
    setCurrentAlert(null);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalVisible(false);
    setCurrentAlert(null);
  };

  // Table columns configuration
  const columns = [
    {
      field: 'name',
      name: 'Name',
      sortable: true,
      truncateText: true,
    },
    {
      field: 'source',
      name: 'Source',
      sortable: true,
    },
    {
      field: 'alertType',
      name: 'Type',
      sortable: true,
    },
    {
      field: 'severity',
      name: 'Severity',
      sortable: true,
      render: (severity: Alert['severity']) => {
        const colors = {
          low: 'success' as 'success',
          medium: 'primary' as 'primary',
          high: 'warning' as 'warning',
          critical: 'danger' as 'danger',
        };
        return (
          <EuiButton
            size="s"
            color={colors[severity]}
            fill
          >
            {severity.charAt(0).toUpperCase() + severity.slice(1)}
          </EuiButton>
        );
      },
    },
    {
      field: 'status',
      name: 'Status',
      sortable: true,
    },
    {
      field: 'alertTime',
      name: 'Alert Time',
      sortable: true,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      field: 'incidentId',
      name: 'Linked Incident',
      sortable: true,
      render: (incidentId: string | undefined) => {
        if (!incidentId) return 'None';
        const incident = incidents.find(inc => inc.incident_id.toString() === incidentId);
        return incident ? `${incident.incident_type} (#${incidentId})` : incidentId;
      },
    },
    {
      name: 'Actions',
      actions: [
        {
          name: 'Edit',
          description: 'Edit this alert',
          icon: 'pencil',
          type: 'icon',
          onClick: (alert: Alert) => openEditModal(alert),
        },
        {
          name: 'Delete',
          description: 'Delete this alert',
          icon: 'trash',
          type: 'icon',
          color: 'danger' as 'danger',
          onClick: (alert: Alert) => openDeleteModal(alert),
        },
      ],
    } as any,
  ];

  return (
    <div style={{ padding: '24px' }}>
      <EuiPageHeader
        pageTitle="Alerts Management"
        rightSideItems={[
          <EuiButton
            fill
            iconType="plusInCircle"
            onClick={openCreateModal}
          >
            Create Alert
          </EuiButton>,
        ]}
      />

      <EuiSpacer size="l" />

      <EuiPanel>
        <EuiBasicTable
          items={alerts}
          columns={columns}
          loading={isLoading}
          noItemsMessage="No alerts found"
        />
      </EuiPanel>

      {/* Create/Edit Modal */}
      {isModalVisible && (
        <EuiModal onClose={closeModal}>
          <EuiModalHeader>
            <EuiModalHeaderTitle>
              {currentAlert ? 'Edit Alert' : 'Create New Alert'}
            </EuiModalHeaderTitle>
          </EuiModalHeader>

          <EuiModalBody>
            <EuiFormRow label="Name">
              <EuiFieldText
                placeholder="Enter alert name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                required
              />
            </EuiFormRow>

            <EuiFormRow label="Source">
              <EuiFieldText
                placeholder="Alert source"
                value={formData.source}
                onChange={(e) => handleInputChange('source', e.target.value)}
              />
            </EuiFormRow>

            <EuiFormRow label="Alert Type">
              <EuiFieldText
                placeholder="Type of alert"
                value={formData.alertType}
                onChange={(e) => handleInputChange('alertType', e.target.value)}
              />
            </EuiFormRow>

            <EuiFormRow label="Alert Time">
              <EuiDatePicker
                selected={moment(formData.alertTime)}
                onChange={(date) => handleInputChange('alertTime', date ? date.toISOString() : '')}
                showTimeSelect
              />
            </EuiFormRow>

            <EuiFormRow label="Severity">
              <EuiSelect
                options={[
                  { value: 'low', text: 'Low' },
                  { value: 'medium', text: 'Medium' },
                  { value: 'high', text: 'High' },
                  { value: 'critical', text: 'Critical' },
                ]}
                value={formData.severity}
                onChange={(e) => handleInputChange('severity', e.target.value)}
              />
            </EuiFormRow>

            <EuiFormRow label="Status">
              <EuiSelect
                options={[
                  { value: 'new', text: 'New' },
                  { value: 'acknowledged', text: 'Acknowledged' },
                  { value: 'resolved', text: 'Resolved' },
                  { value: 'closed', text: 'Closed' },
                ]}
                value={formData.status}
                onChange={(e) => handleInputChange('status', e.target.value)}
              />
            </EuiFormRow>

            <EuiFormRow label="Linked Incident">
              <EuiSelect
                options={[
                  { value: '', text: 'None' },
                  ...incidents.map(incident => ({
                    value: incident.incident_id.toString(),
                    text: `${incident.incident_type} (${incident.severity})`
                  }))
                ]}
                value={formData.incidentId || ''}
                onChange={(e) => handleInputChange('incidentId', e.target.value)}
              />
            </EuiFormRow>
          </EuiModalBody>

          <EuiModalFooter>
            <EuiButton onClick={closeModal}>Cancel</EuiButton>
            <EuiButton
              fill
              onClick={currentAlert ? updateAlert : createAlert}
            >
              {currentAlert ? 'Update' : 'Create'}
            </EuiButton>
          </EuiModalFooter>
        </EuiModal>
      )}

      {/* Delete Confirmation Modal */}
      {isDeleteModalVisible && (
        <EuiConfirmModal
          title="Delete Alert"
          onCancel={closeDeleteModal}
          onConfirm={deleteAlert}
          cancelButtonText="Cancel"
          confirmButtonText="Delete"
          buttonColor="danger"
        >
          <p>Are you sure you want to delete alert "{currentAlert?.name}"?</p>
          <p>This action cannot be undone.</p>
        </EuiConfirmModal>
      )}
    </div>
  );
};

export default AlertsPage;