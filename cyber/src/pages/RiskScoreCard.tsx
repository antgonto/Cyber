import React, { useState } from 'react';
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
  EuiButtonIcon,
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

export interface RiskScoreCardProps {
  riskScore: RiskScore;
  onClick?: () => void;
}

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
  const [isExpanded, setIsExpanded] = useState(false);
  const toggleExpand = () => setIsExpanded(prev => !prev);

  const {
    incident_id,
    incident_type,
    severity,
    risk_score,
    risk_factors,
    recommended_action,
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
          <EuiText size="s">
            <strong>{recommended_action}</strong>
          </EuiText>
        </EuiFlexGroup>
      </EuiFlexItem>
    </EuiFlexGroup>
  );

  const cardContent = (
    <>
      <EuiFlexGroup alignItems="center">
        <EuiFlexItem grow={false}>
          <EuiTitle size="s"><h3>{Math.round(risk_score)}</h3></EuiTitle>
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
      <EuiTitle size="s"><h5>Risk Factors</h5></EuiTitle>
      <EuiSpacer size="s" />
      <EuiPanel paddingSize="none">
        <EuiFlexGroup direction="column" gutterSize="s" alignItems="flexStart">
          <EuiFlexItem>
            <EuiText size="s">– Assets</EuiText>
            <EuiProgress value={(risk_factors.asset_factor / 50) * 100} max={100} size="s" color="#1890ff" />
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiText size="s">– Vulnerabilities</EuiText>
            <EuiProgress value={(risk_factors.vulnerability_factor / 40) * 100} max={100} size="s" color="#faad14" />
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiText size="s">– Threats</EuiText>
            <EuiProgress value={(risk_factors.threat_factor / 30) * 100} max={100} size="s" color="#ff4d4f" />
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiText size="s">– Alerts</EuiText>
            <EuiProgress value={(risk_factors.alert_factor / 20) * 100} max={100} size="s" color="#d36086" />
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiText size="s">– Time</EuiText>
            <EuiProgress value={(risk_factors.time_factor / 10) * 100} max={100} size="s" color="#54b399" />
          </EuiFlexItem>
        </EuiFlexGroup>
      </EuiPanel>

      <EuiSpacer size="m" />
      <EuiTitle size="s"><h5>Recommended Action</h5></EuiTitle>
      <EuiSpacer size="s" />
      <EuiText size="s">{recommended_action}</EuiText>
    </>
  );

  return (
    <EuiCard
      title={cardHeader}
      paddingSize="m"
      onClick={toggleExpand}
    >
      <EuiButtonIcon
        iconType={isExpanded ? 'arrowUp' : 'arrowDown'}
        onClick={e => {
          e.stopPropagation();
          toggleExpand();
        }}
        aria-label="Toggle details"
      />
      {isExpanded && <EuiPanel paddingSize="m">{cardContent}</EuiPanel>}
    </EuiCard>
  );
};

export default RiskScoreCard;