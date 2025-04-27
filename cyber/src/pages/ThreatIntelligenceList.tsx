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
  EuiComboBox,
  EuiConfirmModal,
  EuiTextArea,
} from '@elastic/eui';
import {
  threatsService,
  assetService,
  vulnerabilityService,
  incidentService,
} from '../services/api';

// Define the Threat interface used in UI
interface Threat {
  threat_id: string;
  threat_actor_name: string;
  indicator_type: string;
  indicator_value: string;
  confidence_level: string;
  description: string;
  related_cve: string;
  date_identified: string;
  last_updated: string;
}

// Backend shape
interface BackendThreat {
  threat_id: number;
  threat_actor_name: string;
  indicator_type: string;
  indicator_value: string;
  confidence_level: string;
  description: string;
  related_cve: string;
  date_identified: string;
  last_updated: string;
}

// Option shape for ComboBox
interface Option {
  label: string;
  value: number;
}

const ThreatIntelligenceList: React.FC = () => {
  const [threats, setThreats] = useState<Threat[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
  const [isDeleteModalVisible, setIsDeleteModalVisible] = useState<boolean>(false);
  const [currentThreat, setCurrentThreat] = useState<Threat | null>(null);

  // form data
  const [formData, setFormData] = useState<Omit<Threat, 'threat_id'>>({
    threat_actor_name: '',
    indicator_type: '',
    indicator_value: '',
    confidence_level: '',
    description: '',
    related_cve: '',
    date_identified: '',
    last_updated: '',
  });

  // Options
  const [assetOptions, setAssetOptions] = useState<Option[]>([]);
  const [vulnOptions, setVulnOptions] = useState<Option[]>([]);
  const [incidentOptions, setIncidentOptions] = useState<Option[]>([]);

  useEffect(() => {
    fetchThreats();
    fetchOptions();
  }, []);

  const fetchThreats = async () => {
    setIsLoading(true);
    try {
      const res = await threatsService.getThreats({});
      const data: BackendThreat[] = res.data.threats;
      const transformed = data.map(t => ({
        ...t,
        threat_id: t.threat_id.toString(),
      }));
      setThreats(transformed);
    } catch (err) {
      console.error('Failed to fetch threats:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchOptions = async () => {
    try {
      const [assetsRes, vulnsRes, incidentsRes] = await Promise.all([
        assetService.getAssets(),
        vulnerabilityService.getVulnerabilities(),
        incidentService.getIncidents({}),
      ]);
      setAssetOptions(
        assetsRes.data.map((a: any) => ({ value: a.asset_id, label: a.name || a.asset_id.toString() }))
      );
      setVulnOptions(
        vulnsRes.data.map((v: any) => ({ value: v.vulnerability_id, label: v.title || v.vulnerability_id.toString() }))
      );
      setIncidentOptions(
        incidentsRes.data.map((i: any) => ({ value: i.incident_id, label: `#${i.incident_id}: ${i.type}` }))
      );
    } catch (err) {
      console.error('Failed to load options:', err);
    }
  };

  const openCreateModal = () => {
    const currentDate = new Date().toISOString().split('T')[0];
    setCurrentThreat(null);
    setFormData({
      threat_actor_name: '',
      indicator_type: '',
      indicator_value: '',
      confidence_level: '',
      description: '',
      related_cve: '',
      date_identified: currentDate,
      last_updated: currentDate,
    });
    setIsModalVisible(true);
  };

  const openEditModal = (threat: Threat) => {
    setCurrentThreat(threat);
    setFormData({
      threat_actor_name: threat.threat_actor_name,
      indicator_type: threat.indicator_type,
      indicator_value: threat.indicator_value,
      confidence_level: threat.confidence_level,
      description: threat.description,
      related_cve: threat.related_cve,
      date_identified: threat.date_identified,
      last_updated: threat.last_updated,
    });
    setIsModalVisible(true);
  };

  const closeModal = () => {
    setIsModalVisible(false);
    setCurrentThreat(null);
  };

  const openDeleteModal = (threat: Threat) => {
    setCurrentThreat(threat);
    setIsDeleteModalVisible(true);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalVisible(false);
    setCurrentThreat(null);
  };

  const handleInputChange = (field: keyof Omit<Threat, 'threat_id' | 'assets' | 'vulnerabilities' | 'incidents'>, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleComboChange = (field: 'assets' | 'vulnerabilities' | 'incidents', selected: any[]) => {
    const ids = selected.map(opt => opt.value || 0);
    setFormData({ ...formData, [field]: ids });
  };

  const createThreat = async () => {
    try {
      const payload = { ...formData };
      await threatsService.createThreat(payload);
      fetchThreats();
      closeModal();
    } catch (err) {
      console.error('Failed to create threat:', err);
    }
  };

  const updateThreat = async () => {
    if (!currentThreat) return;
    try {
      // Convert string ID to number for backend
      const threatId = parseInt(currentThreat.threat_id, 10);
      const updatedFormData = {
        ...formData,
        last_updated: new Date().toISOString().split('T')[0]
      };
      await threatsService.updateThreat(threatId, updatedFormData);
      fetchThreats();
      closeModal();
    } catch (err) {
      console.error('Failed to update threat:', err);
    }
  };

  const deleteThreat = async () => {
    if (!currentThreat) return;
    try {
      // Convert string ID to number for backend
      const threatId = parseInt(currentThreat.threat_id, 10);
      await threatsService.deleteThreat(threatId);
      fetchThreats();
      closeDeleteModal();
    } catch (err) {
      console.error('Failed to delete threat:', err);
    }
  };

  const columns = [
    { field: 'threat_id', name: 'ID', sortable: true, width: '80px' },
    { field: 'threat_actor_name', name: 'Actor', sortable: true },
    { field: 'indicator_type', name: 'Type', sortable: true },
    { field: 'indicator_value', name: 'Value', sortable: true },
    { field: 'confidence_level', name: 'Confidence', sortable: true },
    { field: 'related_cve', name: 'CVE', render: (cve: string) => cve || '-' },
    {
      field: 'assets', name: 'Assets', render: (list: number[]) => list.length,
    },
    {
      field: 'vulnerabilities', name: 'Vulns', render: (list: number[]) => list.length,
    },
    {
      field: 'incidents', name: 'Incidents', render: (list: number[]) => list.length,
    },
    { name: 'Actions', actions: [
        { name: 'Edit', icon: 'pencil', type: 'icon', onClick: openEditModal },
        { name: 'Delete', icon: 'trash', type: 'icon', color: 'danger', onClick: openDeleteModal },
      ] as any,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <EuiPageHeader
        pageTitle="Threat Intelligence"
        rightSideItems={[<EuiButton fill iconType="plusInCircle" onClick={openCreateModal}>Create Threat</EuiButton>]} />
      <EuiSpacer size="l" />
      <EuiPanel>
        <EuiBasicTable items={threats} columns={columns} loading={isLoading} noItemsMessage="No threats found" />
      </EuiPanel>

      {/* Create / Edit Modal */}
      {isModalVisible && (
        <EuiModal onClose={closeModal}>
          <EuiModalHeader>
            <EuiModalHeaderTitle>{currentThreat ? 'Edit Threat' : 'Create Threat'}</EuiModalHeaderTitle>
          </EuiModalHeader>
          <EuiModalBody>
            <EuiFormRow label="Actor Name">
              <EuiFieldText value={formData.threat_actor_name} onChange={e => handleInputChange('threat_actor_name', e.target.value)} />
            </EuiFormRow>
            <EuiFormRow label="Indicator Type">
              <EuiFieldText value={formData.indicator_type} onChange={e => handleInputChange('indicator_type', e.target.value)} />
            </EuiFormRow>
            <EuiFormRow label="Indicator Value">
              <EuiFieldText value={formData.indicator_value} onChange={e => handleInputChange('indicator_value', e.target.value)} />
            </EuiFormRow>
            <EuiFormRow label="Confidence Level">
              <EuiFieldText value={formData.confidence_level} onChange={e => handleInputChange('confidence_level', e.target.value)} />
            </EuiFormRow>
            <EuiFormRow label="Related CVE">
              <EuiFieldText value={formData.related_cve} onChange={e => handleInputChange('related_cve', e.target.value)} />
            </EuiFormRow>
            <EuiFormRow label="Description">
              <EuiTextArea value={formData.description} onChange={e => handleInputChange('description', e.target.value)} />
            </EuiFormRow>

            <EuiFormRow label="Assets">
              <EuiComboBox
                options={assetOptions}
                selectedOptions={assetOptions.filter(o => formData.assets.includes(o.value))}
                onChange={selected => handleComboChange('assets', selected)}
                isClearable
              />
            </EuiFormRow>
            <EuiFormRow label="Vulnerabilities">
              <EuiComboBox
                options={vulnOptions}
                selectedOptions={vulnOptions.filter(o => formData.vulnerabilities.includes(o.value))}
                onChange={selected => handleComboChange('vulnerabilities', selected)}
                isClearable
              />
            </EuiFormRow>
            <EuiFormRow label="Incidents">
              <EuiComboBox
                options={incidentOptions}
                selectedOptions={incidentOptions.filter(o => formData.incidents.includes(o.value))}
                onChange={selected => handleComboChange('incidents', selected)}
                isClearable
              />
            </EuiFormRow>
          </EuiModalBody>
          <EuiModalFooter>
            <EuiButton onClick={closeModal}>Cancel</EuiButton>
            <EuiButton fill onClick={currentThreat ? updateThreat : createThreat}>
              {currentThreat ? 'Update' : 'Create'}
            </EuiButton>
          </EuiModalFooter>
        </EuiModal>
      )}

      {/* Delete Confirmation */}
      {isDeleteModalVisible && (
        <EuiConfirmModal
          title="Delete Threat"
          onCancel={closeDeleteModal}
          onConfirm={deleteThreat}
          cancelButtonText="Cancel"
          confirmButtonText="Delete"
          buttonColor="danger"
        >
          <p>Are you sure you want to delete threat "{currentThreat?.threat_actor_name}"?</p>
        </EuiConfirmModal>
      )}
    </div>
  );
};

export default ThreatIntelligenceList;