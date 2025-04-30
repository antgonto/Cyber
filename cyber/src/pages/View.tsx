import React, { useState, useEffect, useCallback } from 'react';
import {
  EuiBasicTable,
  EuiBadge,
  EuiButton,
  EuiCard,
  EuiFieldNumber,
  EuiSelect,
  EuiFlexGroup,
  EuiFlexItem,
  EuiFormRow,
  EuiSpacer,
  EuiToolTip,
  EuiModal,
  EuiModalHeader,
  EuiModalHeaderTitle,
  EuiModalBody,
  EuiModalFooter,
  EuiLoadingSpinner,
} from '@elastic/eui';
import { dashboardService } from '../services/api';

interface IncidentDashboardItem {
  incident_id: number;
  incident_type: string;
  incident_description: string;
  incident_severity: string;
  incident_status: string;
  reported_date: string;
  resolved_date: string | null;
  assigned_user_id: number | null;
  assigned_username: string | null;
  assigned_email: string | null;
  assigned_user_role: string | null;
  affected_assets_count: number;
  affected_asset_names: string | null;
  related_alerts_count: number;
  unacknowledged_alerts_count: number;
  resolution_time_hours: number | null;
}

interface FilterParams {
  incident_status?: string;
  incident_severity?: string;
  assigned_user_id?: number;
  min_resolution_time_hours?: number;
  max_resolution_time_hours?: number;
  page?: number;
  per_page?: number;
}

const IncidentDashboard: React.FC = () => {
  const [incidents, setIncidents] = useState<IncidentDashboardItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filters, setFilters] = useState<FilterParams>({});
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
    totalItemCount: 0,
  });
  const [showErrorModal, setShowErrorModal] = useState<boolean>(false);

  const fetchIncidents = useCallback(
    async (params: FilterParams = {}) => {
      setLoading(true);
      try {
        // Merge current filters with new params
        const queryParams = {
          ...filters,
          ...params,
          page: params.page ?? pagination.pageIndex + 1,
          per_page: params.per_page ?? pagination.pageSize
        };

        // Remove any undefined/null values
        Object.keys(queryParams).forEach(key => {
          if (queryParams[key] === undefined || queryParams[key] === null) {
            delete queryParams[key];
          }
        });

        const response = await dashboardService.getDashboard(queryParams);
        const data = response.data;

        setIncidents(data.items || []);
        setPagination({
          pageIndex: (params.page ?? pagination.pageIndex + 1) - 1,
          pageSize: params.per_page ?? pagination.pageSize,
          totalItemCount: data.count || 0
        });
      } catch (error) {
        console.error('Error fetching incidents:', error);
        setShowErrorModal(true);
      } finally {
        setLoading(false);
      }
    },
    [filters, pagination.pageIndex, pagination.pageSize]
  );

  useEffect(() => {
    fetchIncidents({
      page: pagination.pageIndex + 1,
      per_page: pagination.pageSize,
    });
  }, [fetchIncidents, pagination.pageIndex, pagination.pageSize]);

  const handleTableChange = ({ page }: { page: { index: number; size: number } }) => {
    setPagination({
      ...pagination,
      pageIndex: page.index,
      pageSize: page.size,
    });
  };

  const handleFilterChange = <K extends keyof FilterParams>(key: K, value: FilterParams[K] | null) => {
    console.log('filter: ', key, value);
    setFilters((prev) => {
      const val = value == null || value === '' ? undefined : value;
      const updated = { ...prev };
      if (val === undefined) {
        delete updated[key];
      } else {
        updated[key] = val;
      }
      return updated;
    });
    setPagination((prev) => ({ ...prev, pageIndex: 0 }));
  };

  const applyFilters = () => {
    setPagination((prev) => ({ ...prev, pageIndex: 0 }));
    fetchIncidents({
      ...filters,
      page: 1,
      per_page: pagination.pageSize,
    });
  };

  const resetFilters = () => {
    setFilters({});
    setPagination((prev) => ({ ...prev, pageIndex: 0 }));
    fetchIncidents({
      page: 1,
      per_page: pagination.pageSize,
    });
  };

  const getSeverityColor = (
    severity: string
  ): 'danger' | 'warning' | 'accent' | 'success' => {
    const colors: Record<string, 'danger' | 'warning' | 'accent' | 'success'> = {
      critical: 'danger',
      high: 'warning',
      medium: 'accent',
      low: 'success',
    };
    return colors[severity] || 'accent';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      open: 'primary',
      investigating: 'accent',
      resolved: 'success',
      closed: 'subdued',
    };
    return colors[status] || 'default';
  };

  const columns = [
    { field: 'incident_id', name: 'ID', width: '80px' },
    { field: 'incident_type', name: 'Type', width: '150px' },
    {
      field: 'incident_status',
      name: 'Status',
      width: '120px',
      render: (status: string) => (
        <EuiBadge color={getStatusColor(status)}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </EuiBadge>
      ),
    },
    {
      field: 'incident_severity',
      name: 'Severity',
      width: '100px',
      render: (severity: string) => (
        <EuiBadge color={getSeverityColor(severity)}>
          {severity.charAt(0).toUpperCase() + severity.slice(1)}
        </EuiBadge>
      ),
    },
    { field: 'incident_description', name: 'Description', truncateText: true },
    {
      field: 'assigned_username',
      name: 'Assigned To',
      width: '150px',
      render: (username: string, record: IncidentDashboardItem) =>
        username ? (
          <EuiToolTip content={`${record.assigned_email} (${record.assigned_user_role})`}>
            <span>{username}</span>
          </EuiToolTip>
        ) : (
          <span style={{ color: '#999' }}>Unassigned</span>
        ),
    },
    {
      field: 'related_alerts_count',
      name: 'Alerts',
      width: '100px',
      render: (count: number, record: IncidentDashboardItem) => (
        <EuiToolTip
          content={`${record.unacknowledged_alerts_count} unacknowledged of ${count}`}
        >
          <EuiBadge
            color={
              record.unacknowledged_alerts_count > 0 ? 'danger' : 'success'
            }
          >
            {count}
          </EuiBadge>
        </EuiToolTip>
      ),
    },
    {
      field: 'affected_assets_count',
      name: 'Assets',
      width: '80px',
      render: (count: number, record: IncidentDashboardItem) => (
        <EuiToolTip content={record.affected_asset_names || 'No assets'}>
          <EuiBadge color="primary">{count}</EuiBadge>
        </EuiToolTip>
      ),
    },
    {
      field: 'reported_date',
      name: 'Reported',
      width: '170px',
      render: (date: string) =>
        new Date(date).toLocaleString('en-US', { hour12: true }).toLowerCase(),
    },
    {
      field: 'resolution_time_hours',
      name: 'Resolution Time',
      width: '120px',
      render: (hours: number | null) =>
        hours !== null ? `${Math.round(hours)}h` : '-',
    },
  ];

  return (
    <div className="incident-dashboard">
      <EuiCard title="Incident Management Dashboard">
        {/* Filters */}
        <EuiFlexGroup gutterSize="m">
          <EuiFlexItem>
            <EuiFormRow label="Filter by Status">
              <EuiSelect
                options={[
                  { value: '', text: 'All' },
                  { value: 'open', text: 'Open' },
                  { value: 'investigating', text: 'Investigating' },
                  { value: 'resolved', text: 'Resolved' },
                  { value: 'closed', text: 'Closed' },
                ]}
                value={filters.incident_status || ''}
                onChange={(e) =>
                  handleFilterChange('incident_status', e.target.value)
                }
              />
            </EuiFormRow>
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiFormRow label="Filter by Severity">
              <EuiSelect
                options={[
                  { value: '', text: 'All' },
                  { value: 'critical', text: 'Critical' },
                  { value: 'high', text: 'High' },
                  { value: 'medium', text: 'Medium' },
                  { value: 'low', text: 'Low' },
                ]}
                value={filters.incident_severity || ''}
                onChange={(e) =>
                  handleFilterChange('incident_severity', e.target.value)
                }
              />
            </EuiFormRow>
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiFormRow label="Assigned User ID">
              <EuiFieldNumber
                placeholder="User ID"
                value={
                  filters.assigned_user_id !== undefined
                    ? filters.assigned_user_id
                    : ''
                }
                onChange={(e) =>
                  handleFilterChange(
                    'assigned_user_id',
                    e.target.value ? parseInt(e.target.value, 10) : null
                  )
                }
              />
            </EuiFormRow>
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiFormRow label="Resolution Time (Hours)">
              <EuiFlexGroup gutterSize="s">
                <EuiFlexItem>
                  <EuiFieldNumber
                    placeholder="Min"
                    value={filters.min_resolution_time_hours ?? ''}
                    onChange={(e) =>
                      handleFilterChange(
                        'min_resolution_time_hours',
                        e.target.value ? parseFloat(e.target.value) : null
                      )
                    }
                  />
                </EuiFlexItem>
                <EuiFlexItem>
                  <EuiFieldNumber
                    placeholder="Max"
                    value={
                      filters.max_resolution_time_hours ?? ''}
                    onChange={(e) =>
                      handleFilterChange(
                        'max_resolution_time_hours',
                        e.target.value ? parseFloat(e.target.value) : null
                      )
                    }
                  />
                </EuiFlexItem>
              </EuiFlexGroup>
            </EuiFormRow>
          </EuiFlexItem>
          <EuiFlexItem grow={false}>
            <EuiFormRow hasEmptyLabelSpace>
              <EuiButton onClick={applyFilters} fill>
                Apply Filters
              </EuiButton>
            </EuiFormRow>
          </EuiFlexItem>
        </EuiFlexGroup>

        <EuiSpacer size="m" />

        <EuiButton onClick={resetFilters} color="warning">
          Reset Filters
        </EuiButton>

        <EuiSpacer size="m" />

        {loading ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <EuiLoadingSpinner size="xl" />
          </div>
        ) : (
          <EuiBasicTable
            items={incidents}
            columns={columns}
            pagination={{
              pageIndex: pagination.pageIndex,
              pageSize: pagination.pageSize,
              totalItemCount: pagination.totalItemCount,
              showPerPageOptions: true,
            }}
            onChange={handleTableChange}
          />
        )}
      </EuiCard>

      {showErrorModal && (
        <EuiModal onClose={() => setShowErrorModal(false)}>
          <EuiModalHeader>
            <EuiModalHeaderTitle>Error</EuiModalHeaderTitle>
          </EuiModalHeader>
          <EuiModalBody>
            <p>Failed to fetch incidents. Please try again later.</p>
          </EuiModalBody>
          <EuiModalFooter>
            <EuiButton onClick={() => setShowErrorModal(false)} fill>
              Close
            </EuiButton>
          </EuiModalFooter>
        </EuiModal>
      )}
    </div>
  );
};

export default IncidentDashboard;