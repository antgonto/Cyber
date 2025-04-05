import * as React from 'react';
import { useState, useEffect } from 'react';
import {
  EuiBasicTable,
  EuiButton,
  EuiButtonIcon,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPage,
  EuiPageBody,
  EuiPageHeader,
  EuiTitle,
  EuiModal,
  EuiModalHeader,
  EuiModalHeaderTitle,
  EuiModalBody,
  EuiModalFooter,
  EuiForm,
  EuiFormRow,
  EuiFieldText,
  EuiFieldPassword,
  EuiSpacer
} from '@elastic/eui';
import { assetService } from '../services/api';

const AssetsList = () => {
  const [assets, setAssets] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentAsset, setCurrentAsset] = useState({ asset_id: '', asset_name: '', asset_type: '', location: '', owner: '', criticality_level: '' });
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await assetService.getAssets();
      setAssets(response.data);
    } catch (error) {
      console.error('Error fetching assets:', error);
    }
  };

  const handleOpenModal = (asset = null) => {
    if (asset) {
      setCurrentAsset({ ...asset, password: '' });
      setIsEditing(true);
    } else {
      setCurrentAsset({ asset_id: '', asset_name: '', asset_type: '', location: '', owner: '', criticality_level: '' });
      setIsEditing(false);
    }
    setIsModalVisible(true);
  };

  const handleCloseModal = () => {
    setIsModalVisible(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentAsset({ ...currentAsset, [name]: value });
  };

  const handleSubmit = async () => {
    try {
      if (isEditing) {
        const { asset_id, ...assetData } = currentAsset;
        await assetService.updateAsset(asset_id, assetData);
      } else {
        await assetService.createAsset(currentAsset);
      }
      handleCloseModal();
      fetchAssets();
    } catch (error) {
      console.error('Error saving asset:', error);
    }
  };

  const handleDeleteAsset = async (assetId) => {
    try {
      await assetService.deleteAsset(assetId);
      fetchAssets();
    } catch (error) {
      console.error('Error deleting asset:', error);
    }
  };

  const columns = [
    {
      field: 'asset_id',
      name: 'ID',
      sortable: true,
      width: '50px',
    },
    {
      field: 'asset_name',
      name: 'Asset Name',
      sortable: true,
    },
    {
      field: 'asset_type',
      name: 'Asset Type',
      sortable: true,
    },
    {
      field: 'location',
      name: 'Location',
    },
    {
      field: 'owner',
      name: 'Owner',
    },
    {
      field: 'criticality_level',
      name: 'Criticality Level',
    },
    {
      field: 'asset_id',
      name: 'Actions',
      render: (asset_id, asset) => (
        <div>
          <EuiButtonIcon
            iconType="pencil"
            aria-label="Edit"
            onClick={() => handleOpenModal(asset)}
          />
          &nbsp;
          <EuiButtonIcon
            iconType="trash"
            color="danger"
            aria-label="Delete"
            onClick={() => {
              if (window.confirm('Are you sure you want to delete this asset?')) {
                handleDeleteAsset(asset.asset_id);
              }
            }}
          />
        </div>
      ),
    },
  ];

  const modal = isModalVisible ? (
    <EuiModal onClose={handleCloseModal} style={{ width: '500px' }}>
      <EuiModalHeader>
        <EuiModalHeaderTitle>
          {isEditing ? 'Edit Asset' : 'Add New Asset'}
        </EuiModalHeaderTitle>
      </EuiModalHeader>

      <EuiModalBody>
        <EuiForm>
          <EuiFormRow label="Asset Name">
            <EuiFieldText
              name="asset_name"
              value={currentAsset.asset_name}
              onChange={(e) => handleInputChange(e)}
            />
          </EuiFormRow>

          <EuiFormRow label="Asset Type">
            <EuiFieldText
              name="asset_type"
              value={currentAsset.asset_type}
              onChange={(e) => handleInputChange(e)}
            />
          </EuiFormRow>

          <EuiFormRow label="Location">
            <EuiFieldText
              name="location"
              value={currentAsset.location || ''}
              onChange={(e) => handleInputChange(e)}
            />
          </EuiFormRow>

          <EuiFormRow label="Owner">
            <EuiFieldPassword
              name="owner"
              value={currentAsset.owner || ''}
              onChange={(e) => handleInputChange(e)}
            />
          </EuiFormRow>
          <EuiFormRow label="Criticality Level">
            <EuiFieldPassword
              name="criticality_level"
              value={currentAsset.criticality_level || ''}
              onChange={(e) => handleInputChange(e)}
            />
          </EuiFormRow>
        </EuiForm>
      </EuiModalBody>

      <EuiModalFooter>
        <EuiButton onClick={handleCloseModal} fill={false}>
          Cancel
        </EuiButton>

        <EuiButton onClick={handleSubmit} fill>
          {isEditing ? 'Update' : 'Create'}
        </EuiButton>
      </EuiModalFooter>
    </EuiModal>
  ) : null;

  return (
    <EuiPage>
      <EuiPageBody>
        <EuiPageHeader>
          <EuiFlexGroup justifyContent="spaceBetween" alignItems="center">
            <EuiFlexItem grow={false}>
              <EuiTitle>
                <h1>Assets Management</h1>
              </EuiTitle>
            </EuiFlexItem>
            <EuiFlexItem grow={false}>
              <EuiButton
                iconType="plusInCircle"
                onClick={() => handleOpenModal()}
                fill
              >
                Add New Asset
              </EuiButton>
            </EuiFlexItem>
          </EuiFlexGroup>
        </EuiPageHeader>

        <EuiSpacer size="l" />

        <EuiBasicTable
          items={assets}
          columns={columns}
          tableLayout="fixed"
        />

        {modal}
      </EuiPageBody>
    </EuiPage>
  );
};

export default AssetsList;