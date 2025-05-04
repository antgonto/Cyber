// src/components/risk/RiskScoreCard.tsx
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
  EuiIcon, EuiPanel,
  EuiHorizontalRule
} from '@elastic/eui';

import {
  EuiDescriptionList,
  EuiDescriptionListDescription,
  EuiDescriptionListTitle
} from "@elastic/eui/src/components/description_list";
import {EuiHealth} from "@elastic/eui/src/components/health";

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
  onClick: () => void;
}

// Helpers
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

const getRecommendationIcon = (score: number): string => {
  if (score >= 90) return 'alert';
  if (score >= 75) return 'warning';
  if (score >= 50) return 'bell';
  return 'checkInCircleFilled';
};

const getRiskLabel = (score: number): string => {
  if (score >= 90) return 'CRITICAL RISK';
  if (score >= 75) return 'HIGH RISK';
  if (score >= 50) return 'MODERATE RISK';
  return 'LOW RISK';
};

const RiskScoreCard: React.FC<RiskScoreCardProps> = ({ riskScore, onClick }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const {
    incident_id,
    incident_type,
    severity,
    risk_score,
    risk_factors,
    recommended_action
  } = riskScore;

  // Summary header
  const cardHeader = (
      <EuiFlexGroup justifyContent="spaceBetween" alignItems="center">
        <EuiFlexItem>
          <EuiFlexGroup alignItems="center">
            <EuiFlexItem grow={false}>
              <EuiTitle size="s"><h4>#{incident_id}: {incident_type}</h4></EuiTitle>
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
            <EuiIcon type={getRecommendationIcon(risk_score)} color={risk_score >= 75 ? 'danger' : 'subdued'}/>
            <EuiText size="s"><strong>{recommended_action}</strong></EuiText>
          </EuiFlexGroup>
        </EuiFlexItem>
      </EuiFlexGroup>
  );

  // Summary content
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
              <EuiIcon type="iInCircle"/>
            </EuiToolTip>
          </EuiFlexItem>
        </EuiFlexGroup>

        <EuiProgress
            value={risk_score}
            max={100}
            size="s"
            color={getRiskScoreColor(risk_score)}
        />

        <EuiSpacer size="m"/>

        <EuiTitle size="s"><h5>Risk Factors</h5></EuiTitle>
        <EuiSpacer size="s"/>
        <div className="risk-factors">
          <EuiFlexGroup direction="column" gutterSize="s" alignItems="flexStart">
            <EuiFlexItem>
              <EuiText size="s">– Assets</EuiText>
              <EuiProgress
                  value={(risk_factors.asset_factor / 50) * 100}
                  max={100}
                  size="s"
                  color="#1890ff"
              />
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiText size="s">– Vulnerabilities</EuiText>
              <EuiProgress
                  value={(risk_factors.vulnerability_factor / 40) * 100}
                  max={100}
                  size="s"
                  color="#faad14"
              />
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiText size="s">– Threats</EuiText>
              <EuiProgress
                  value={(risk_factors.threat_factor / 30) * 100}
                  max={100}
                  size="s"
                  color="#ff4d4f"
              />
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiText size="s">– Alerts</EuiText>
              <EuiProgress
                  value={(risk_factors.alert_factor / 30) * 100}
                  max={100}
                  size="s"
                  color="#fa8c16"
              />
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiText size="s">– Time Factor</EuiText>
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
          onClick={() => setIsExpanded(!isExpanded)}
          paddingSize="m"
          hasBorder
      >
        {cardHeader}
        {cardContent}

        {isExpanded && (
            <>
              <EuiSpacer size="m"/>
              <EuiPanel paddingSize="l">
                <EuiTitle><h2>{incident_type} Risk Assessment</h2></EuiTitle>
                <EuiSpacer size="l"/>
                <EuiFlexGroup alignItems="center">
                  <EuiFlexItem grow={false}>
                    <EuiText><h3>{getRiskLabel(risk_score)}</h3></EuiText>
                  </EuiFlexItem>
                  <EuiFlexItem>
                    <EuiProgress
                        valueText={`${Math.round(risk_score)}%`}
                        value={risk_score}
                        max={100}
                        size="l"
                        color={getRiskScoreColor(risk_score)}
                    />
                  </EuiFlexItem>
                </EuiFlexGroup>
                <EuiHorizontalRule/>
                <EuiDescriptionList textStyle="reverse" style={{maxWidth: '800px'}}>
                  <EuiFlexGroup>
                    <EuiFlexItem>
                      <EuiDescriptionListTitle>ID</EuiDescriptionListTitle>
                      <EuiDescriptionListDescription>{incident_id}</EuiDescriptionListDescription>
                    </EuiFlexItem>
                    <EuiFlexItem>
                      <EuiDescriptionListTitle>Type</EuiDescriptionListTitle>
                      <EuiDescriptionListDescription>{incident_type}</EuiDescriptionListDescription>
                    </EuiFlexItem>
                    <EuiFlexItem>
                      <EuiDescriptionListTitle>Severity</EuiDescriptionListTitle>
                      <EuiDescriptionListDescription>
                        <EuiHealth color={
                          severity === 'critical' ? 'danger' :
                              severity === 'high' ? 'warning' :
                                  severity === 'medium' ? 'primary' : 'success'
                        }>
                          {severity.toUpperCase()}
                        </EuiHealth>
                      </EuiDescriptionListDescription>
                    </EuiFlexItem>
                  </EuiFlexGroup>
                </EuiDescriptionList>
              </EuiPanel>
            </>
        )}
      </EuiCard>
  );
};

export default RiskScoreCard;
