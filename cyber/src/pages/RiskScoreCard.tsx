// src/components/risk/RiskScoreCard.tsx
import React from 'react';
import {
  EuiCard,
  EuiFlexGroup,
  EuiFlexItem,
  EuiProgress,
  EuiBadge,
  EuiText,
  EuiTitle,
  EuiSpacer,
  EuiToolTip,
  EuiIcon,
  EuiPanel,
} from '@elastic/eui';
import {string} from "yup";

  export interface RiskScore {
    incident_id: number;
    incident_type: string;
    severity: string;
    risk_score: number;
    // risk_factors may come as a JSON string from the API
    risk_factors: string | {
      asset_factor: number;
      vulnerability_factor: number;
      threat_factor: number;
      alert_factor: number;
      time_factor: number;
    };
    recommended_action: string;
  }

  export interface RiskScoreCardProps {
    riskScore: RiskScore;
    onClick?: () => void;
  }

  // Helpers to color code severity and score
  const getSeverityColor = (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'danger';
      case 'high':     return 'warning';
      case 'medium':   return 'primary';
      case 'low':      return 'success';
      default:         return 'subdued';
    }
  };
  const getRiskScoreColor = (score: number): string => {
    if (score >= 90) return '#ff4d4f';
    if (score >= 75) return '#fa8c16';
    if (score >= 50) return '#faad14';
    if (score >= 25) return '#1890ff';
    return '#52c41a';
  };
  const getRecommendationIcon = (score: number): string => {
    if (score >= 90) return 'alert';
    if (score >= 75) return 'warning';
    if (score >= 50) return 'bell';
    return 'checkInCircleFilled';
  };

  const RiskScoreCard: React.FC<RiskScoreCardProps> = ({ riskScore, onClick }) => {
    const {
      incident_id,
      incident_type,
      severity,
      risk_score,
      risk_factors,
      recommended_action,
    } = riskScore;

    // Parse JSON string if needed
    const factors = typeof risk_factors === 'string'
      ? JSON.parse(risk_factors)
      : risk_factors;


  const cardHeader = (
    <EuiFlexGroup justifyContent="spaceBetween" alignItems="center">
      <EuiFlexItem>
        <EuiFlexGroup alignItems="center">
          <EuiFlexItem grow={false}>
            <EuiTitle size="s">
              <h4>#{incident_id}: {incident_type}</h4>
            </EuiTitle>
          </EuiFlexItem>
          <EuiFlexItem grow={false}>
            <EuiBadge color={getSeverityColor(severity)}>
              {severity.charAt(0).toUpperCase() + severity.slice(1)}
            </EuiBadge>
          </EuiFlexItem>
        </EuiFlexGroup>
      </EuiFlexItem>
      <EuiFlexItem grow={false}>
        <EuiFlexGroup alignItems="center">
          <EuiIcon
            type={getRecommendationIcon(risk_score)}
            color={risk_score >= 75 ? 'danger' : 'subdued'}
          />
          <EuiText size="s" style={{ marginLeft: '4px' }}>
            <strong>{recommended_action}</strong>
          </EuiText>
        </EuiFlexGroup>
      </EuiFlexItem>
    </EuiFlexGroup>
  );

  const summarySection = (
    <>
      <EuiFlexGroup alignItems="center">
        <EuiFlexItem grow={false}>
          <EuiTitle size="m"><h3>{Math.round(risk_score)}</h3></EuiTitle>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiText color="subdued" size="s">Risk Score</EuiText>
        </EuiFlexItem>
        <EuiFlexItem grow={false}>
          <EuiToolTip content="Aggregated risk factors and base score">
            <EuiIcon type="iInCircle" />
          </EuiToolTip>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiProgress
        value={risk_score}
        max={100}
        size="s"
        color={getRiskScoreColor(risk_score)}
      />

      <EuiSpacer size="m" />
    </>
  );


  const metricsSection = (
    <>
      <EuiTitle size="s"><h5>Risk Factors Breakdown</h5></EuiTitle>
      <EuiSpacer size="s" />
      <EuiFlexGroup direction="column" gutterSize="s">
        {/* Asset Factor */}
        <EuiFlexItem>

          <EuiText size="s">Assets: {factors.asset_factor}</EuiText>
          <EuiProgress
            value={(factors.asset_factor / 50) * 100}
            max={100}
            size="s"
            color="#1890ff"
            valueText={`${factors.asset_factor}`}
          />
        </EuiFlexItem>

        {/* Vulnerability Factor */}
        <EuiFlexItem>
          <EuiText size="s">Vulnerabilities: {factors.vulnerability_factor}</EuiText>
          <EuiProgress
            value={(factors.vulnerability_factor / 40) * 100}
            max={100}
            size="s"
            color="#faad14"
            valueText={`${factors.vulnerability_factor}`}
          />
        </EuiFlexItem>

        {/* Threat Factor */}
        <EuiFlexItem>
          <EuiText size="s">Threats: {factors.threat_factor}</EuiText>
          <EuiProgress
            value={(factors.threat_factor / 30) * 100}
            max={100}
            size="s"
            color="#ff4d4f"
            valueText={`${factors.threat_factor}`}
          />
        </EuiFlexItem>

        {/* Alert Factor */}
        <EuiFlexItem>
          <EuiText size="s">Alerts: {factors.alert_factor}</EuiText>
          <EuiProgress
            value={(factors.alert_factor / 30) * 100}
            max={100}
            size="s"
            color="#fa8c16"
            valueText={`${factors.alert_factor}`}
          />
        </EuiFlexItem>

        {/* Time Factor */}
        <EuiFlexItem>
          <EuiText size="s">Time (days): {factors.time_factor}</EuiText>
          <EuiProgress
            value={(factors.time_factor / 30) * 100}
            max={100}
            size="s"
            color="#722ed1"
            valueText={`${factors.time_factor}`}
          />
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />
    </>
  );

  const actionSection = (
    <EuiPanel paddingSize="s">
      <EuiTitle size="s"><h5>Recommended Action</h5></EuiTitle>
      <EuiSpacer size="xs" />
      <EuiText size="s">{recommended_action}</EuiText>
    </EuiPanel>
  );

  return (
    <EuiCard
      title={cardHeader}
      paddingSize="m"
      onClick={onClick}
    >
      {summarySection}
      {metricsSection}
      {actionSection}
    </EuiCard>
  );
};

export default RiskScoreCard;
