import React, { useState, useEffect } from 'react';
import {
  EuiBasicTable,
  EuiButton,
  EuiFormRow,
  EuiFieldText,
  EuiTextArea,
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
} from '@elastic/eui';
import { incidentService } from '../services/api';

// Define incident interface
interface Incident {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  dateCreated: string;
  assignedTo?: string;
}

// Backend incident interface
interface BackendIncident {
  incident_id: number;
  incident_type: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  reported_date: string;
  resolved_date: string | null;
  assigned_to_id: number | null;
  assigned_to_username: string | null;
  alerts: any[];
  threats: any[];
  assets: any[];
}

const IncidentsPage: React.FC = () => {
  // State for incidents data
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // State for modal and form
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
  const [isDeleteModalVisible, setIsDeleteModalVisible] = useState<boolean>(false);
  const [currentIncident, setCurrentIncident] = useState<Incident | null>(null);
  const [formData, setFormData] = useState<Omit<Incident, 'id' | 'dateCreated'>>({
    title: '',
    description: '',
    severity: 'medium',
    status: 'open',
  });

  // Fetch incidents data
  useEffect(() => {
    fetchIncidents();
  }, []);

  const fetchIncidents = async () => {
    setIsLoading(true);
    try {
      const response = await incidentService.getIncidents({});
      // Transform backend data format to match frontend Incident interface
      const transformedData = response.data.map((incident: BackendIncident) => ({
        id: incident.incident_id.toString(),
        title: incident.incident_type,
        description: incident.description,
        severity: incident.severity,
        status: incident.status,
        dateCreated: incident.reported_date,
        assignedTo: incident.assigned_to_username || undefined
      }));
      setIncidents(transformedData);
    } catch (error) {
      console.error('Failed to fetch incidents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Create new incident
  const createIncident = async () => {
    try {
      const incidentData = {
        incident_type: formData.title,
        description: formData.description,
        severity: formData.severity,
        status: formData.status,
        assigned_to_username: formData.assignedTo || null
      };

      const response = await incidentService.createIncident(incidentData);

      // Add the new incident to the list
      const newIncident: Incident = {
        id: response.data.incident_id.toString(),
        title: response.data.incident_type,
        description: response.data.description,
        severity: response.data.severity,
        status: response.data.status,
        dateCreated: response.data.reported_date,
        assignedTo: response.data.assigned_to_username || undefined
      };

      setIncidents([...incidents, newIncident]);
      closeModal();
    } catch (error) {
      console.error('Failed to create incident:', error);
    }
  };

  // Update existing incident
  const updateIncident = async () => {
    if (!currentIncident) return;

    try {
      const incidentData = {
        incident_type: formData.title,
        description: formData.description,
        severity: formData.severity,
        status: formData.status,
        assigned_to_username: formData.assignedTo || null
      };

      await incidentService.updateIncident(currentIncident.id, incidentData);

      // Update the incident in the list
      const updatedIncidents = incidents.map(incident =>
        incident.id === currentIncident.id
          ? { ...incident, ...formData, dateCreated: incident.dateCreated }
          : incident
      );

      setIncidents(updatedIncidents);
      closeModal();
    } catch (error) {
      console.error('Failed to update incident:', error);
    }
  };

  // Delete incident
  const deleteIncident = async () => {
    if (!currentIncident) return;

    try {
      await incidentService.deleteIncident(currentIncident.id);

      // Remove the incident from the list
      const filteredIncidents = incidents.filter(
        incident => incident.id !== currentIncident.id
      );

      setIncidents(filteredIncidents);
      closeDeleteModal();
    } catch (error) {
      console.error('Failed to delete incident:', error);
    }
  };

  // Handle form input changes
  const handleInputChange = (field: string, value: any) => {
    setFormData({
      ...formData,
      [field]: value,
    });
  };

  // Open modal for creating new incident
  const openCreateModal = () => {
    setCurrentIncident(null);
    setFormData({
      title: '',
      description: '',
      severity: 'medium',
      status: 'open',
    });
    setIsModalVisible(true);
  };

  // Open modal for editing existing incident
  const openEditModal = (incident: Incident) => {
    setCurrentIncident(incident);
    setFormData({
      title: incident.title,
      description: incident.description,
      severity: incident.severity,
      status: incident.status,
      assignedTo: incident.assignedTo,
    });
    setIsModalVisible(true);
  };

  // Open delete confirmation modal
  const openDeleteModal = (incident: Incident) => {
    setCurrentIncident(incident);
    setIsDeleteModalVisible(true);
  };

  // Close modals
  const closeModal = () => {
    setIsModalVisible(false);
    setCurrentIncident(null);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalVisible(false);
    setCurrentIncident(null);
  };

  // Table columns configuration
  const columns = [
    {
      field: 'title',
      name: 'Title',
      sortable: true,
      truncateText: true,
    },
    {
      field: 'severity',
      name: 'Severity',
      sortable: true,
      render: (severity: Incident['severity']) => {
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
      field: 'dateCreated',
      name: 'Date Created',
      sortable: true,
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      field: 'assignedTo',
      name: 'Assigned To',
      sortable: true,
    },
    {
      name: 'Actions',
      actions: [
        {
          name: 'Edit',
          description: 'Edit this incident',
          icon: 'pencil',
          type: 'icon',
          onClick: (incident: Incident) => openEditModal(incident),
        },
        {
          name: 'Delete',
          description: 'Delete this incident',
          icon: 'trash',
          type: 'icon',
          color: 'danger' as 'danger',
          onClick: (incident: Incident) => openDeleteModal(incident),
        },
      ],
    } as any,
  ];

  return (
    <div style={{ padding: '24px' }}>
      <EuiPageHeader
        pageTitle="Incidents Management"
        rightSideItems={[
          <EuiButton
            fill
            iconType="plusInCircle"
            onClick={openCreateModal}
          >
            Create Incident
          </EuiButton>,
        ]}
      />

      <EuiSpacer size="l" />

      <EuiPanel>
        <EuiBasicTable
          items={incidents}
          columns={columns}
          loading={isLoading}
          noItemsMessage="No incidents found"
        />
      </EuiPanel>

      {/* Create/Edit Modal */}
      {isModalVisible && (
        <EuiModal onClose={closeModal}>
          <EuiModalHeader>
            <EuiModalHeaderTitle>
              {currentIncident ? 'Edit Incident' : 'Create New Incident'}
            </EuiModalHeaderTitle>
          </EuiModalHeader>

          <EuiModalBody>
            <EuiFormRow label="Title">
              <EuiFieldText
                placeholder="Enter incident title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                required
              />
            </EuiFormRow>

            <EuiFormRow label="Description">
              <EuiTextArea
                placeholder="Describe the incident"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
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
                  { value: 'open', text: 'Open' },
                  { value: 'investigating', text: 'Investigating' },
                  { value: 'resolved', text: 'Resolved' },
                  { value: 'closed', text: 'Closed' },
                ]}
                value={formData.status}
                onChange={(e) => handleInputChange('status', e.target.value)}
              />
            </EuiFormRow>

            <EuiFormRow label="Assigned To">
              <EuiFieldText
                placeholder="Username of assignee"
                value={formData.assignedTo || ''}
                onChange={(e) => handleInputChange('assignedTo', e.target.value)}
              />
            </EuiFormRow>
          </EuiModalBody>

          <EuiModalFooter>
            <EuiButton onClick={closeModal}>Cancel</EuiButton>
            <EuiButton
              fill
              onClick={currentIncident ? updateIncident : createIncident}
            >
              {currentIncident ? 'Update' : 'Create'}
            </EuiButton>
          </EuiModalFooter>
        </EuiModal>
      )}

      {/* Delete Confirmation Modal */}
      {isDeleteModalVisible && (
        <EuiConfirmModal
          title="Delete Incident"
          onCancel={closeDeleteModal}
          onConfirm={deleteIncident}
          cancelButtonText="Cancel"
          confirmButtonText="Delete"
          buttonColor="danger"
        >
          <p>Are you sure you want to delete incident "{currentIncident?.title}"?</p>
          <p>This action cannot be undone.</p>
        </EuiConfirmModal>
      )}
    </div>
  );
};

export default IncidentsPage;