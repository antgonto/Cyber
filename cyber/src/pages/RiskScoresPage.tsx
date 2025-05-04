import React, { useState, useEffect } from 'react';
import {
  EuiBasicTable,
  EuiBadge,
  EuiPageHeader,
  EuiSpacer,
  EuiPanel, EuiButton,
} from '@elastic/eui';
import { riskService } from '../services/api';

interface RiskScore {
  incident_id: number;
  incident_type: string;
  severity: string;
  risk_score: number;
  risk_factors: number
  recommended_action: string;
}

const RiskScoresPage: React.FC = () => {
  const [risks, setData] = useState<RiskScore[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchRiskScore = async () => {
    setIsLoading(true);
    try {
      const response = await riskService.getOpenRiskScores();
      const responseData = response.data.map((risk: RiskScore) => ({
        incident_id: risk.incident_id,
        incident_type: risk.incident_type,
        severity: risk.severity,
        risk_score: risk.risk_score,
        risk_factors: risk.risk_factors,
        recommended_action: risk.recommended_action
      }));
      setData(responseData);
    } catch (error) {
      console.error('Error fetching risk scores:', error);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
      fetchRiskScore();
  }, []);

  console.log(risks);

  const columns = [
    {
      field: 'incident_id',
      name: 'ID',
      sortable: true
    },
    {
      field: 'incident_type',
      name: 'Type'
    },
    {
      field: 'severity',
      name: 'Severity',
      sortable: true,
      render: (severity: string) => {
        const key = severity.toLowerCase();
        const colors: Record<string, 'danger' | 'warning' | 'accent' | 'success'> = {
          critical: 'danger',
          high: 'warning',
          medium: 'accent',
          low: 'success',
        };
        const color = colors[key] || 'accent';
        return (
          <EuiButton size="s" color={color} fill>
            {severity.charAt(0).toUpperCase() + severity.slice(1)}
          </EuiButton>
        );
      },
    },
    {
      field: 'risk_score',
      name: 'Score',
      render: (score: number) => Math.round(score)
    },
    {
      field: 'risk_factors',
      name: 'Risk Factors',
      render: (factors: any) => {
        if (typeof factors === 'number') {
          return Math.round(factors);
        } else {
          return (
            <div>
              <div>Time: {factors.time_factor}</div>
              <div>Alert: {factors.alert_factor}</div>
              <div>Asset: {factors.asset_factor}</div>
              <div>Threat: {factors.threat_factor}</div>
              <div>Vulnerability: {factors.vulnerability_factor}</div>
            </div>
          );
        }
      }
    },
    {
      field: 'recommended_action',
      name: 'Action',
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <EuiPageHeader
          pageTitle="Open Incident Risk Scores"
      />

      <EuiSpacer size="l" />

      <EuiPanel>
        <EuiBasicTable
          items={risks}
          columns={columns}
          loading={isLoading}
          noItemsMessage="No risk scores to display"
        />
      </EuiPanel>
    </div>
  );
};

export default RiskScoresPage;