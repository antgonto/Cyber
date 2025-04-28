# SQL View Explanation: Incident Management Dashboard
# This SQL file creates a comprehensive database view called incident_management_dashboard that aggregates data from multiple tables related to security incidents. This view is likely used for reporting and visualization in a security incident management system.
# Key Components:
# Line 8. Core Incident Information
# Line 17. Assignment Information
# Line 25. Related Assets, Vulnerabilities and Threats. The view aggregates counts and details using functions like COUNT, STRING_AGG, and MAX:
# Line 48. Time and Resolution Metrics
# Line 58. Table Joins. The view joins multiple tables to gather all necessary information.

view = """
CREATE OR REPLACE VIEW incident_management_dashboard AS
SELECT 
    i.incident_id,
    i.incident_type,
    i.description AS incident_description,
    i.severity AS incident_severity,
    i.status AS incident_status,
    i.reported_date,
    i.resolved_date,
    u.user_id AS assigned_user_id,
    u.username AS assigned_username,
    u.email AS assigned_email,
    u.role AS assigned_user_role,
    
    -- Asset information
    COUNT(DISTINCT ia.asset_id) AS affected_assets_count,
    STRING_AGG(DISTINCT a.asset_name, ', ') AS affected_asset_names,
    MAX(a.criticality_level) AS highest_asset_criticality,
    
    -- Vulnerability information
    COUNT(DISTINCT av.vulnerability_id) AS related_vulnerabilities_count,
    STRING_AGG(DISTINCT v.title, ', ') AS vulnerability_titles,
    STRING_AGG(DISTINCT v.cve_reference, ', ') AS related_cves,
    
    -- Threat intelligence
    COUNT(DISTINCT tia.threat_id) AS related_threats_count,
    STRING_AGG(DISTINCT ti.threat_actor_name, ', ') AS threat_actors,
    MAX(ti.confidence_level) AS highest_threat_confidence,
    
    -- Alert information
    COUNT(DISTINCT al.alert_id) AS related_alerts_count,
    MAX(al.severity) AS highest_alert_severity,
    COUNT(DISTINCT CASE WHEN al.status = 'new' THEN al.alert_id END) AS unacknowledged_alerts_count,
    
    -- Activity metrics
    MAX(ual.timestamp) AS last_activity_time,
    COUNT(DISTINCT ual.log_id) AS activity_count,
    
    -- Time metrics
    CASE 
        WHEN i.status = 'resolved' OR i.status = 'closed' THEN 
            EXTRACT(EPOCH FROM (i.resolved_date - i.reported_date))/3600
        ELSE 
            EXTRACT(EPOCH FROM (NOW() - i.reported_date))/3600
    END AS resolution_time_hours
    
FROM api_incident i
LEFT JOIN api_user u ON i.assigned_to_id = u.user_id
LEFT JOIN incident_assets ia ON ia.incident_id = i.incident_id
LEFT JOIN api_asset a ON a.asset_id = ia.asset_id
LEFT JOIN asset_vulnerabilities av ON av.asset_id = a.asset_id
LEFT JOIN api_vulnerability v ON v.vulnerability_id = av.vulnerability_id
LEFT JOIN threat_incident_association tia ON tia.incident_id = i.incident_id
LEFT JOIN api_threatintelligence ti ON ti.threat_id = tia.threat_id
LEFT JOIN api_alert al ON al.incident_id = i.incident_id
LEFT JOIN user_activity_logs ual ON ual.resource_type = 'incident' AND ual.resource_id = i.incident_id

GROUP BY 
    i.incident_id,
    i.incident_type,
    i.description,
    i.severity,
    i.status,
    i.reported_date,
    i.resolved_date,
    u.user_id,
    u.username,
    u.email,
    u.role

ORDER BY 
    CASE 
        WHEN i.status = 'open' THEN 1
        WHEN i.status = 'investigating' THEN 2
        WHEN i.status = 'resolved' THEN 3
        WHEN i.status = 'closed' THEN 4
    END,
    CASE 
        WHEN i.severity = 'critical' THEN 1
        WHEN i.severity = 'high' THEN 2
        WHEN i.severity = 'medium' THEN 3
        WHEN i.severity = 'low' THEN 4
    END,
    i.reported_date DESC;
"""

# from ninja import Router, Schema
# from ninja.pagination import paginate
# from typing import List, Optional
# from django.db import connection
# from datetime import datetime
#
#
# # Schema definitions
# class IncidentDashboardItem(Schema):
#     incident_id: int
#     incident_type: str
#     incident_description: str
#     incident_severity: str
#     incident_status: str
#     reported_date: datetime
#     resolved_date: Optional[datetime] = None
#     assigned_user_id: Optional[int] = None
#     assigned_username: Optional[str] = None
#     assigned_email: Optional[str] = None
#     assigned_user_role: Optional[str] = None
#     affected_assets_count: int
#     affected_asset_names: Optional[str] = None
#     highest_asset_criticality: Optional[str] = None
#     related_vulnerabilities_count: int
#     vulnerability_titles: Optional[str] = None
#     related_cves: Optional[str] = None
#     related_threats_count: int
#     threat_actors: Optional[str] = None
#     highest_threat_confidence: Optional[str] = None
#     related_alerts_count: int
#     highest_alert_severity: Optional[str] = None
#     unacknowledged_alerts_count: int
#     last_activity_time: Optional[datetime] = None
#     activity_count: int
#     resolution_time_hours: Optional[float] = None
#
#
# class IncidentDashboardFilters(Schema):
#     incident_status: Optional[str] = None
#     incident_severity: Optional[str] = None
#     assigned_user_id: Optional[int] = None
#     min_resolution_time: Optional[float] = None
#     max_resolution_time: Optional[float] = None
#
#
# # Router definition
# router = Router()
#
#
# @router.get("/dashboard", response=List[IncidentDashboardItem])
# @paginate
# def get_incident_dashboard(request, filters: IncidentDashboardFilters = None):
#     """
#     Get incidents data from the incident_management_dashboard view with optional filtering
#     """
#     query = "SELECT * FROM incident_management_dashboard"
#     params = []
#
#     # Apply filters if provided
#     if filters:
#         conditions = []
#         if filters.incident_status:
#             conditions.append("incident_status = %s")
#             params.append(filters.incident_status)
#         if filters.incident_severity:
#             conditions.append("incident_severity = %s")
#             params.append(filters.incident_severity)
#         if filters.assigned_user_id:
#             conditions.append("assigned_user_id = %s")
#             params.append(filters.assigned_user_id)
#         if filters.min_resolution_time is not None:
#             conditions.append("resolution_time_hours >= %s")
#             params.append(filters.min_resolution_time)
#         if filters.max_resolution_time is not None:
#             conditions.append("resolution_time_hours <= %s")
#             params.append(filters.max_resolution_time)
#
#         if conditions:
#             query += " WHERE " + " AND ".join(conditions)
#
#     # Execute the query
#     with connection.cursor() as cursor:
#         cursor.execute(query, params)
#         columns = [col[0] for col in cursor.description]
#         results = [
#             dict(zip(columns, row))
#             for row in cursor.fetchall()
#         ]
#
#     return results



# # TypeScript React component for this endpoint:
# // """
# // // src/components/incidents/IncidentDashboard.tsx
# // import React, { useState, useEffect } from 'react';
# // import axios from 'axios';
# // import {
# //   Table,
# //   Tag,
# //   Spin,
# //   Input,
# //   Select,
# //   DatePicker,
# //   Button,
# //   Card,
# //   Row,
# //   Col,
# //   Badge,
# //   Tooltip,
# //   Pagination
# // } from 'antd';
# // import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
# //
# // interface IncidentDashboardItem {
# //   incident_id: number;
# //   incident_type: string;
# //   incident_description: string;
# //   incident_severity: string;
# //   incident_status: string;
# //   reported_date: string;
# //   resolved_date: string | null;
# //   assigned_user_id: number | null;
# //   assigned_username: string | null;
# //   assigned_email: string | null;
# //   assigned_user_role: string | null;
# //   affected_assets_count: number;
# //   affected_asset_names: string | null;
# //   highest_asset_criticality: string | null;
# //   related_vulnerabilities_count: number;
# //   vulnerability_titles: string | null;
# //   related_cves: string | null;
# //   related_threats_count: number;
# //   threat_actors: string | null;
# //   highest_threat_confidence: string | null;
# //   related_alerts_count: number;
# //   highest_alert_severity: string | null;
# //   unacknowledged_alerts_count: number;
# //   last_activity_time: string | null;
# //   activity_count: number;
# //   resolution_time_hours: number | null;
# // }
# //
# // interface FilterParams {
# //   incident_status?: string;
# //   incident_severity?: string;
# //   assigned_user_id?: number;
# //   min_resolution_time?: number;
# //   max_resolution_time?: number;
# //   page?: number;
# //   per_page?: number;
# // }
# //
# // const { Option } = Select;
# //
# // const IncidentDashboard: React.FC = () => {
# //   const [incidents, setIncidents] = useState<IncidentDashboardItem[]>([]);
# //   const [loading, setLoading] = useState<boolean>(true);
# //   const [filters, setFilters] = useState<FilterParams>({});
# //   const [pagination, setPagination] = useState({
# //     current: 1,
# //     pageSize: 10,
# //     total: 0
# //   });
# //
# //   const fetchIncidents = async (params: FilterParams = {}) => {
# //     setLoading(true);
# //     try {
# //       const { data } = await axios.get('/api/dashboard', { params });
# //       setIncidents(data.items);
# //       setPagination({
# //         ...pagination,
# //         current: data.pagination.page,
# //         total: data.pagination.total
# //       });
# //     } catch (error) {
# //       console.error('Error fetching incidents:', error);
# //     } finally {
# //       setLoading(false);
# //     }
# //   };
# //
# //   useEffect(() => {
# //     fetchIncidents({
# //       page: pagination.current,
# //       per_page: pagination.pageSize
# //     });
# //   }, []);
# //
# //   const handleTableChange = (paginationConfig: any) => {
# //     const newPagination = {
# //       ...pagination,
# //       current: paginationConfig.current
# //     };
# //     setPagination(newPagination);
# //
# //     fetchIncidents({
# //       ...filters,
# //       page: paginationConfig.current,
# //       per_page: pagination.pageSize
# //     });
# //   };
# //
# //   const handleFilterChange = (key: string, value: any) => {
# //     const newFilters = { ...filters, [key]: value };
# //     if (!value && value !== 0) {
# //       delete newFilters[key];
# //     }
# //     setFilters(newFilters);
# //   };
# //
# //   const applyFilters = () => {
# //     setPagination({ ...pagination, current: 1 });
# //     fetchIncidents({
# //       ...filters,
# //       page: 1,
# //       per_page: pagination.pageSize
# //     });
# //   };
# //
# //   const resetFilters = () => {
# //     setFilters({});
# //     setPagination({ ...pagination, current: 1 });
# //     fetchIncidents({
# //       page: 1,
# //       per_page: pagination.pageSize
# //     });
# //   };
# //
# //   const getSeverityColor = (severity: string) => {
# //     const colors: Record<string, string> = {
# //       critical: 'red',
# //       high: 'orange',
# //       medium: 'gold',
# //       low: 'green'
# //     };
# //     return colors[severity] || 'blue';
# //   };
# //
# //   const getStatusColor = (status: string) => {
# //     const colors: Record<string, string> = {
# //       open: 'blue',
# //       investigating: 'purple',
# //       resolved: 'green',
# //       closed: 'gray'
# //     };
# //     return colors[status] || 'default';
# //   };
# //
# //   const columns = [
# //     {
# //       title: 'ID',
# //       dataIndex: 'incident_id',
# //       key: 'incident_id',
# //       width: 80,
# //     },
# //     {
# //       title: 'Type',
# //       dataIndex: 'incident_type',
# //       key: 'incident_type',
# //       width: 120,
# //     },
# //     {
# //       title: 'Status',
# //       dataIndex: 'incident_status',
# //       key: 'incident_status',
# //       width: 120,
# //       render: (status: string) => (
# //         <Tag color={getStatusColor(status)}>
# //           {status.toUpperCase()}
# //         </Tag>
# //       ),
# //     },
# //     {
# //       title: 'Severity',
# //       dataIndex: 'incident_severity',
# //       key: 'incident_severity',
# //       width: 100,
# //       render: (severity: string) => (
# //         <Tag color={getSeverityColor(severity)}>
# //           {severity.toUpperCase()}
# //         </Tag>
# //       ),
# //     },
# //     {
# //       title: 'Description',
# //       dataIndex: 'incident_description',
# //       key: 'incident_description',
# //       ellipsis: true,
# //     },
# //     {
# //       title: 'Assigned To',
# //       dataIndex: 'assigned_username',
# //       key: 'assigned_username',
# //       width: 150,
# //       render: (username: string, record: IncidentDashboardItem) => (
# //         username ? (
# //           <Tooltip title={`${record.assigned_email} (${record.assigned_user_role})`}>
# //             {username}
# //           </Tooltip>
# //         ) : <span style={{ color: '#999' }}>Unassigned</span>
# //       )
# //     },
# //     {
# //       title: 'Alerts',
# //       key: 'alerts',
# //       width: 100,
# //       render: (record: IncidentDashboardItem) => (
# //         <Tooltip title={`${record.unacknowledged_alerts_count} unacknowledged of ${record.related_alerts_count} total`}>
# //           <Badge
# //             count={record.unacknowledged_alerts_count}
# //             style={{ backgroundColor: record.unacknowledged_alerts_count > 0 ? '#f5222d' : '#52c41a' }}
# //           >
# //             <Tag color="blue">{record.related_alerts_count} total</Tag>
# //           </Badge>
# //         </Tooltip>
# //       )
# //     },
# //     {
# //       title: 'Assets',
# //       dataIndex: 'affected_assets_count',
# //       key: 'affected_assets_count',
# //       width: 80,
# //       render: (count: number, record: IncidentDashboardItem) => (
# //         <Tooltip title={record.affected_asset_names || 'No assets'}>
# //           <Tag color="blue">{count}</Tag>
# //         </Tooltip>
# //       )
# //     },
# //     {
# //       title: 'Reported',
# //       dataIndex: 'reported_date',
# //       key: 'reported_date',
# //       width: 150,
# //       render: (date: string) => new Date(date).toLocaleString()
# //     },
# //     {
# //       title: 'Resolution Time',
# //       dataIndex: 'resolution_time_hours',
# //       key: 'resolution_time_hours',
# //       width: 120,
# //       render: (hours: number) => hours ? `${Math.round(hours)}h` : '-'
# //     }
# //   ];
# //
# //   return (
# //     <div className="incident-dashboard">
# //       <Card title="Incident Management Dashboard">
# //         <Row gutter={16} style={{ marginBottom: 16 }}>
# //           <Col span={5}>
# //             <Select
# //               placeholder="Filter by Status"
# //               style={{ width: '100%' }}
# //               allowClear
# //               onChange={(value) => handleFilterChange('incident_status', value)}
# //               value={filters.incident_status}
# //             >
# //               <Option value="open">Open</Option>
# //               <Option value="investigating">Investigating</Option>
# //               <Option value="resolved">Resolved</Option>
# //               <Option value="closed">Closed</Option>
# //             </Select>
# //           </Col>
# //
# //           <Col span={5}>
# //             <Select
# //               placeholder="Filter by Severity"
# //               style={{ width: '100%' }}
# //               allowClear
# //               onChange={(value) => handleFilterChange('incident_severity', value)}
# //               value={filters.incident_severity}
# //             >
# //               <Option value="critical">Critical</Option>
# //               <Option value="high">High</Option>
# //               <Option value="medium">Medium</Option>
# //               <Option value="low">Low</Option>
# //             </Select>
# //           </Col>
# //
# //           <Col span={5}>
# //             <Input
# //               placeholder="Assigned User ID"
# //               type="number"
# //               onChange={(e) => handleFilterChange('assigned_user_id', e.target.value ? parseInt(e.target.value) : null)}
# //               value={filters.assigned_user_id || ''}
# //             />
# //           </Col>
# //
# //           <Col span={7}>
# //             <Input.Group compact>
# //               <Input
# //                 style={{ width: '50%' }}
# //                 placeholder="Min Hours"
# //                 type="number"
# //                 onChange={(e) => handleFilterChange('min_resolution_time', e.target.value ? parseFloat(e.target.value) : null)}
# //                 value={filters.min_resolution_time || ''}
# //               />
# //               <Input
# //                 style={{ width: '50%' }}
# //                 placeholder="Max Hours"
# //                 type="number"
# //                 onChange={(e) => handleFilterChange('max_resolution_time', e.target.value ? parseFloat(e.target.value) : null)}
# //                 value={filters.max_resolution_time || ''}
# //               />
# //             </Input.Group>
# //           </Col>
# //
# //           <Col span={2}>
# //             <Button type="primary" icon={<SearchOutlined />} onClick={applyFilters}>
# //               Filter
# //             </Button>
# //           </Col>
# //         </Row>
# //
# //         <Button
# //           icon={<ReloadOutlined />}
# //           onClick={resetFilters}
# //           style={{ marginBottom: 16 }}
# //         >
# //           Reset Filters
# //         </Button>
# //
# //         <Table
# //           columns={columns}
# //           dataSource={incidents}
# //           rowKey="incident_id"
# //           pagination={pagination}
# //           loading={loading}
# //           onChange={handleTableChange}
# //           scroll={{ x: 1300 }}
# //         />
# //       </Card>
# //     </div>
# //   );
# // };
# //
# // export default IncidentDashboard;
# // """