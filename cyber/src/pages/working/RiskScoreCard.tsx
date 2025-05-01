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
} from '@elastic/eui';

export interface RiskScore {
  incident_id: number;
  incident_type: string;
  severity: string;
  risk_score: number;
  risk_factors: {
    asset_factor: number;
    vulnerability_factor: number;
    threat_factor: number;
    alert_factor: number;
    time_factor: number;
  };
  recommended_action: string;
}

interface RiskScoreCardProps {
  riskScore: RiskScore;
  onClick: () => void;
}

const getSeverityColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'critical': return 'danger';
    case 'high': return 'warning';
    case 'medium': return 'primary';
    case 'low': return 'success';
    default: return 'subdued';
  }
};

const getRiskScoreColor = (score: number): string => {
  if (score >= 90) return '#ff4d4f';
  if (score >= 75) return '#fa8c16';
  if (score >= 50) return '#faad14';
  if (score >= 25) return '#1890ff';
  return '#52c41a';
};

const RiskScoreCard: React.FC<RiskScoreCardProps> = ({ riskScore, onClick }) => {
  const {
    incident_id,
    incident_type,
    severity,
    risk_score,
    risk_factors,
    recommended_action
  } = riskScore;

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
            <EuiBadge color={getSeverityColor(severity)}>{severity.toUpperCase()}</EuiBadge>
          </EuiFlexItem>
        </EuiFlexGroup>
      </EuiFlexItem>
      <EuiFlexItem grow={false}>
        <EuiFlexGroup alignItems="center">
          {risk_score >= 75 && <EuiIcon type="alert" color="danger" />}
          <EuiText size="s"><strong>{recommended_action}</strong></EuiText>
        </EuiFlexGroup>
      </EuiFlexItem>
    </EuiFlexGroup>
  );

  const cardContent = (
    <>
      <EuiFlexGroup alignItems="center">
        <EuiFlexItem grow={false}>
          <EuiTitle size="s">
            <h3>{Math.round(risk_score)}</h3>
          </EuiTitle>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiText color="subdued" size="s">Risk Score</EuiText>
        </EuiFlexItem>
        <EuiFlexItem grow={false}>
          <EuiToolTip content="Based on asset criticality, vulnerabilities, threats, alerts, and time factor">
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

      <EuiTitle size="xs">
        <h5>Risk Factors</h5>
      </EuiTitle>

      <EuiSpacer size="s" />

      <div className="risk-factors">
        <EuiFlexGroup direction="column" gutterSize="s">
          <EuiFlexItem>
            <EuiText size="xs">Assets</EuiText>
            <EuiProgress
              value={(risk_factors.asset_factor / 50) * 100}
              max={100}
              size="s"
              color="#1890ff"
            />
          </EuiFlexItem>

          <EuiFlexItem>
            <EuiText size="xs">Vulnerabilities</EuiText>
            <EuiProgress
              value={(risk_factors.vulnerability_factor / 40) * 100}
              max={100}
              size="s"
              color="#faad14"
            />
          </EuiFlexItem>

          <EuiFlexItem>
            <EuiText size="xs">Threats</EuiText>
            <EuiProgress
              value={(risk_factors.threat_factor / 30) * 100}
              max={100}
              size="s"
              color="#ff4d4f"
            />
          </EuiFlexItem>

          <EuiFlexItem>
            <EuiText size="xs">Alerts</EuiText>
            <EuiProgress
              value={(risk_factors.alert_factor / 30) * 100}
              max={100}
              size="s"
              color="#fa8c16"
            />
          </EuiFlexItem>

          <EuiFlexItem>
            <EuiText size="xs">Time Factor</EuiText>
            <EuiProgress
              value={(risk_factors.time_factor / 30) * 100}
              max={100}
              size="s"
              color="#722ed1"
            />
          </EuiFlexItem>
        </EuiFlexGroup>
      </div>
    </>
  );

return (
    <EuiCard
      title=""
      titleElement="span"
      description=""
      onClick={onClick}
      paddingSize="m"
      hasBorder
    >
      {cardHeader}
      {cardContent}
    </EuiCard>
  );
};

export default RiskScoreCard;
