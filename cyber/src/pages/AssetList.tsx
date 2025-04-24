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
} from '@elastic/eui';
import { assetService } from '../services/api';

// Define asset interface
interface Asset {
  id: string;
  asset_name: string;
  assetType: string;
  criticality_level: 'low' | 'medium' | 'high' | 'critical';
  location: string;
  owner: string;
}

// Backend asset interface
interface BackendAsset {
  asset_id: number;
  asset_name: string;
  asset_type: string;
  criticality_level: string;
  location: string;
  owner: string;
}

const AssetList: React.FC = () => {
  // State for assets data
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // State for modal and form
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
  const [isDeleteModalVisible, setIsDeleteModalVisible] = useState<boolean>(false);
  const [currentAsset, setCurrentAsset] = useState<Asset | null>(null);
  const [formData, setFormData] = useState<Omit<Asset, 'id'>>({
    asset_name: '',
    assetType: '',
    criticality_level: 'medium',
    location: '',
    owner: '',
  });

  // Fetch assets data
  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    setIsLoading(true);
    try {
      const response = await assetService.getAssets();
      // Transform backend data format to match frontend Asset interface
      const transformedData = response.data.map((asset: BackendAsset) => ({
        id: asset.asset_id.toString(),
        asset_name: asset.asset_name,
        assetType: asset.asset_type,
        criticality: asset.criticality_level as 'low' | 'medium' | 'high' | 'critical',
        location: asset.location,
        owner: asset.owner
      }));
      setAssets(transformedData);
    } catch (error) {
      console.error('Failed to fetch assets:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Create new asset
  const createAsset = async () => {
    try {
      const assetData = {
        name: formData.asset_name,
        asset_type: formData.assetType,
        criticality: formData.criticality_level,
        location: formData.location,
        owner: formData.owner
      };

      const response = await assetService.createAsset(assetData);

      // Add the new asset to the list
      const newAsset: Asset = {
        id: response.data.asset_id.toString(),
        asset_name: response.data.asset_name,
        assetType: response.data.asset_type,
        criticality_level: response.data.criticality_level,
        location: response.data.location,
        owner: response.data.owner
      };

      setAssets([...assets, newAsset]);
      closeModal();
    } catch (error) {
      console.error('Failed to create asset:', error);
    }
  };

  // Update existing asset
  const updateAsset = async () => {
    if (!currentAsset) return;

    try {
      const assetData = {
        asset_name: formData.asset_name,
        asset_type: formData.assetType,
        criticality: formData.criticality_level,
        location: formData.location,
        owner: formData.owner
      };

      await assetService.updateAsset(currentAsset.id, assetData);

      // Update the asset in the list
      const updatedAssets = assets.map(asset =>
        asset.id === currentAsset.id
          ? { ...asset, ...formData }
          : asset
      );

      setAssets(updatedAssets);
      closeModal();
    } catch (error) {
      console.error('Failed to update asset:', error);
    }
  };

  // Delete asset
  const deleteAsset = async () => {
    if (!currentAsset) return;

    try {
      await assetService.deleteAsset(currentAsset.id);

      // Remove the asset from the list
      const filteredAssets = assets.filter(
        asset => asset.id !== currentAsset.id
      );

      setAssets(filteredAssets);
      closeDeleteModal();
    } catch (error) {
      console.error('Failed to delete asset:', error);
    }
  };

  // Handle form input changes
  const handleInputChange = (field: string, value: any) => {
    setFormData({
      ...formData,
      [field]: value,
    });
  };

  // Open modal for creating new asset
  const openCreateModal = () => {
    setCurrentAsset(null);
    setFormData({
      asset_name: '',
      assetType: '',
      criticality_level: 'medium',
      location: '',
      owner: ''
    });
    setIsModalVisible(true);
  };

  // Open modal for editing existing asset
  const openEditModal = (asset: Asset) => {
    setCurrentAsset(asset);
    setFormData({
      asset_name: asset.asset_name,
      assetType: asset.assetType,
      criticality_level: asset.criticality_level,
      location: asset.location,
      owner: asset.owner
    });
    setIsModalVisible(true);
  };

  // Open delete confirmation modal
  const openDeleteModal = (asset: Asset) => {
    setCurrentAsset(asset);
    setIsDeleteModalVisible(true);
  };

  // Close modals
  const closeModal = () => {
    setIsModalVisible(false);
    setCurrentAsset(null);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalVisible(false);
    setCurrentAsset(null);
  };

  // Table columns configuration
  const columns = [
    {
      field: 'id',
      name: 'ID',
      sortable: true,
      width: '70px',
    },
    {
      field: 'asset_name',
      name: 'Asset Name',
      sortable: true,
      truncateText: true,
    },
    {
      field: 'assetType',
      name: 'Asset Type',
      sortable: true,
    },
    {
      field: 'criticality',
      name: 'Criticality',
      sortable: true,
      render: (criticality: Asset['criticality_level']) => {
        const colors = {
          low: 'success' as 'success',
          medium: 'primary' as 'primary',
          high: 'warning' as 'warning',
          critical: 'danger' as 'danger',
        };
        return (
          <EuiButton
            size="s"
            color={colors[criticality]}
            fill
          >
            {/*{criticality ? criticality.charAt(0).toUpperCase() + criticality.slice(1) : ''}*/}
            {criticality.charAt(0).toUpperCase() + criticality.slice(1)}
          </EuiButton>
        );
      },
    },
    {
      field: 'location',
      name: 'Location',
      sortable: true,
    },
    {
      field: 'owner',
      name: 'Owner',
      sortable: true,
    },
    {
      name: 'Actions',
      actions: [
        {
          name: 'Edit',
          description: 'Edit this asset',
          icon: 'pencil',
          type: 'icon',
          onClick: (asset: Asset) => openEditModal(asset),
        },
        {
          name: 'Delete',
          description: 'Delete this asset',
          icon: 'trash',
          type: 'icon',
          color: 'danger' as 'danger',
          onClick: (asset: Asset) => openDeleteModal(asset),
        },
      ],
    } as any,
  ];

  return (
    <div style={{ padding: '24px' }}>
      <EuiPageHeader
        pageTitle="Assets Management"
        rightSideItems={[
          <EuiButton
            fill
            iconType="plusInCircle"
            onClick={openCreateModal}
          >
            Create Asset
          </EuiButton>,
        ]}
      />

      <EuiSpacer size="l" />

      <EuiPanel>
        <EuiBasicTable
          items={assets}
          columns={columns}
          loading={isLoading}
          noItemsMessage="No assets found"
        />
      </EuiPanel>

      {/* Create/Edit Modal */}
      {isModalVisible && (
        <EuiModal onClose={closeModal}>
          <EuiModalHeader>
            <EuiModalHeaderTitle>
              {currentAsset ? 'Edit Asset' : 'Create New Asset'}
            </EuiModalHeaderTitle>
          </EuiModalHeader>

          <EuiModalBody>
            <EuiFormRow label="Name" labelType="label">
              <EuiFieldText
                placeholder="Enter asset name"
                value={formData.asset_name}
                onChange={(e) => handleInputChange('asset_name', e.target.value)}
                required
              />
            </EuiFormRow>

            <EuiFormRow label="Asset Type" labelType="label">
              <EuiFieldText
                placeholder="Type of asset (e.g., Server, Database, Network Device)"
                value={formData.assetType}
                onChange={(e) => handleInputChange('assetType', e.target.value)}
              />
            </EuiFormRow>

            <EuiFormRow label="Criticality" labelType="label">
              <EuiSelect
                options={[
                  { value: 'Low', text: 'Low' },
                  { value: 'Medium', text: 'Medium' },
                  { value: 'High', text: 'High' },
                  { value: 'Critical', text: 'Critical' },
                ]}
                value={formData.criticality_level}
                onChange={(e) => handleInputChange('criticality', e.target.value)}
              />
            </EuiFormRow>

            <EuiFormRow label="Location" labelType="label">
              <EuiFieldText
                placeholder="Physical or virtual location"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
              />
            </EuiFormRow>

            <EuiFormRow label="Owner" labelType="label">
              <EuiFieldText
                placeholder="Person or team responsible for this asset"
                value={formData.owner}
                onChange={(e) => handleInputChange('owner', e.target.value)}
              />
            </EuiFormRow>
          </EuiModalBody>

          <EuiModalFooter>
            <EuiButton onClick={closeModal}>Cancel</EuiButton>
            <EuiButton
              fill
              onClick={currentAsset ? updateAsset : createAsset}
            >
              {currentAsset ? 'Update' : 'Create'}
            </EuiButton>
          </EuiModalFooter>
        </EuiModal>
      )}

      {/* Delete Confirmation Modal */}
      {isDeleteModalVisible && (
        <EuiConfirmModal
          title="Delete Asset"
          onCancel={closeDeleteModal}
          onConfirm={deleteAsset}
          cancelButtonText="Cancel"
          confirmButtonText="Delete"
          buttonColor="danger"
        >
          <p>Are you sure you want to delete asset "{currentAsset?.asset_name}"?</p>
          <p>This action cannot be undone.</p>
        </EuiConfirmModal>
      )}
    </div>
  );
};

export default AssetList;