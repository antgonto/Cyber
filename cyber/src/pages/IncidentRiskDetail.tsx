// src/components/risk/IncidentRiskDetail.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  EuiLoadingSpinner,
  EuiCallOut,
  EuiTitle,
  EuiText,
  EuiSpacer,
  EuiProgress,
  EuiFlexGroup,
  EuiFlexItem,
  EuiStat,
  EuiIcon,
  EuiHorizontalRule,
  EuiPanel,
  EuiDescriptionList,
  EuiDescriptionListTitle,
  EuiDescriptionListDescription,
  EuiButton,
  EuiTextColor,
  EuiHealth
} from '@elastic/eui';
import axios from 'axios';
import { RiskScore } from './RiskScoreCard';
import {riskService} from "../services/api";

const getRiskScoreColor = (score: number): string => {
  if (score >= 90) return '#ff4d4f';
  if (score >= 75) return '#fa8c16';
  if (score >= 50) return '#faad14';
  if (score >= 25) return '#1890ff';
  return '#52c41a';
};

const IncidentRiskDetail: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [riskScore, setRiskScore] = useState<{
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
  } | null>(null);


  const fetchRiskScore = async () => {
    // setLoading(true);
    try {
        if (!incidentId) {
          throw new Error('Incident ID is required');
        }
        const id = parseInt(incidentId, 10);
        const response = await riskService.getRiskScoreById(id);
        console.log("Details: ", response.data);
        const responseData = response.data.map((risk: RiskScore) => ({
          incident_type: risk.incident_type,
          severity: risk.severity,
          risk_score: risk.risk_score,
          risk_factors: {
            asset_factor: risk.risk_factors.asset_factor,
            vulnerability_factor: risk.risk_factors.vulnerability_factor,
            threat_factor: risk.risk_factors.threat_factor,
            alert_factor: risk.risk_factors.alert_factor,
            time_factor: risk.risk_factors.time_factor
          },
          recommended_action: risk.recommended_action
        }));

        setRiskScore(responseData);
    } catch (err) {
      setError('Failed to load risk score data. Please try again later.');
      console.error(err);
    }finally {
      // setLoading(false);
    }
  }

    useEffect(() => {
      if (incidentId) {
        fetchRiskScore();
      }
    }, []);

  const handleTriggerEscalation = async () => {
    if (!incidentId) return;

    try {
      await axios.post(`/api/incidents/${incidentId}/escalate/`);
      // Refresh the risk score data
      const response = await axios.get(`/api/risk/${incidentId}/`);
      setRiskScore(response.data);
    } catch (err) {
      console.error('Failed to escalate incident:', err);
    }
  };

  // if (loading) {
  //   return (
  //     <EuiFlexGroup alignItems="center" justifyContent="center" style={{ height: '100vh' }}>
  //       <EuiFlexItem grow={false}>
  //         <EuiLoadingSpinner size="xl" />
  //         <EuiSpacer size="s" />
  //         <EuiText>Loading risk assessment...</EuiText>
  //       </EuiFlexItem>
  //     </EuiFlexGroup>
  //   );
  // }

  if (error || !riskScore) {
    return (
      <EuiCallOut title="Error" color="danger" iconType="alert">
        {error || 'Could not find risk score for this incident'}
      </EuiCallOut>
    );
  }

  const {
    incident_type,
    severity,
    risk_score,
    risk_factors,
    recommended_action
  } = riskScore;

  const getRecommendationIcon = () => {
    if (risk_score >= 90) return 'alert';
    if (risk_score >= 75) return 'warning';
    if (risk_score >= 50) return 'bell';
    return 'checkInCircleFilled';
  };

  const getRiskLabel = () => {
    if (risk_score >= 90) return 'CRITICAL RISK';
    if (risk_score >= 75) return 'HIGH RISK';
    if (risk_score >= 50) return 'MODERATE RISK';
    return 'LOW RISK';
  };

  return (
    <div className="incident-risk-detail">
      <EuiPanel paddingSize="l">
        <EuiFlexGroup>
          <EuiFlexItem>
            <EuiTitle>
              <h2>{incident_type} Risk Assessment</h2>
            </EuiTitle>
          </EuiFlexItem>
        </EuiFlexGroup>

        <EuiSpacer size="l" />

        {/* Risk Score Overview */}
        <EuiFlexGroup>
          <EuiFlexItem grow={false}>
            <EuiStat
              title={`${Math.round(risk_score)}/100`}
              description="Risk Score"
              titleColor={risk_score >= 75 ? 'danger' : risk_score >= 50 ? 'warning' : 'success'}
              titleSize="l"
            />
          </EuiFlexItem>
          <EuiFlexItem grow={false}>
            <EuiProgress
              valueText={`${Math.round(risk_score)}%`}
              value={risk_score}
              max={100}
              size="l"
              color={getRiskScoreColor(risk_score)}
            />
          </EuiFlexItem>

          <EuiFlexItem>
            <EuiText>
              <h4>Recommendation</h4>
              <p>
                <EuiIcon type={getRecommendationIcon()} color={risk_score >= 75 ? 'danger' : risk_score >= 50 ? 'warning' : 'success'} /> {recommended_action}
              </p>
            </EuiText>
            {risk_score >= 75 && (
              <EuiButton
                color="danger"
                iconType="alert"
                onClick={handleTriggerEscalation}
                fill
              >
                Trigger Escalation Process
              </EuiButton>
            )}
          </EuiFlexItem>
        </EuiFlexGroup>

        <EuiHorizontalRule />

        {/* Risk Factors Breakdown */}
        <EuiTitle size="s">
          <h3>Risk Factors Breakdown</h3>
        </EuiTitle>

        <EuiSpacer size="m" />

        <EuiFlexGroup direction="column">
          <EuiFlexItem>
            <EuiFlexGroup gutterSize="s" alignItems="center">
              <EuiFlexItem grow={false}>
                <EuiIcon type="storage" color="#1890ff" />
              </EuiFlexItem>
              <EuiFlexItem>
                <EuiText size="s"><strong>Asset Risk Factor: {risk_factors.asset_factor.toFixed(1)}/50</strong></EuiText>
              </EuiFlexItem>
            </EuiFlexGroup>
            <EuiSpacer size="xs" />
            <EuiProgress
              value={(risk_factors.asset_factor / 50) * 100}
              max={100}
              size="s"
              color="#1890ff"
            />
            <EuiSpacer size="xs" />
            <EuiText size="xs" color="subdued">Based on number and criticality of affected assets</EuiText>
            <EuiSpacer size="m" />
          </EuiFlexItem>

          <EuiFlexItem>
            <EuiFlexGroup gutterSize="s" alignItems="center">
              <EuiFlexItem grow={false}>
                <EuiIcon type="bug" color="#faad14" />
              </EuiFlexItem>
              <EuiFlexItem>
                <EuiText size="s"><strong>Vulnerability Factor: {risk_factors.vulnerability_factor.toFixed(1)}/40</strong></EuiText>
              </EuiFlexItem>
            </EuiFlexGroup>
            <EuiSpacer size="xs" />
            <EuiProgress
              value={(risk_factors.vulnerability_factor / 40) * 100}
              max={100}
              size="s"
              color="#faad14"
            />
            <EuiSpacer size="xs" />
            <EuiText size="xs" color="subdued">Based on number and severity of related vulnerabilities</EuiText>
            <EuiSpacer size="m" />
          </EuiFlexItem>

          <EuiFlexItem>
            <EuiFlexGroup gutterSize="s" alignItems="center">
              <EuiFlexItem grow={false}>
                <EuiIcon type="warning" color="#ff4d4f" />
              </EuiFlexItem>
              <EuiFlexItem>
                <EuiText size="s"><strong>Threat Intelligence Factor: {risk_factors.threat_factor.toFixed(1)}/30</strong></EuiText>
              </EuiFlexItem>
            </EuiFlexGroup>
            <EuiSpacer size="xs" />
            <EuiProgress
              value={(risk_factors.threat_factor / 30) * 100}
              max={100}
              size="s"
              color="#ff4d4f"
            />
            <EuiSpacer size="xs" />
            <EuiText size="xs" color="subdued">Based on related threat actors and confidence levels</EuiText>
            <EuiSpacer size="m" />
          </EuiFlexItem>

          <EuiFlexItem>
            <EuiFlexGroup gutterSize="s" alignItems="center">
              <EuiFlexItem grow={false}>
                <EuiIcon type="bell" color="#fa8c16" />
              </EuiFlexItem>
              <EuiFlexItem>
                <EuiText size="s"><strong>Alert Factor: {risk_factors.alert_factor.toFixed(1)}/30</strong></EuiText>
              </EuiFlexItem>
            </EuiFlexGroup>
            <EuiSpacer size="xs" />
            <EuiProgress
              value={(risk_factors.alert_factor / 30) * 100}
              max={100}
              size="s"
              color="#fa8c16"
            />
            <EuiSpacer size="xs" />
            <EuiText size="xs" color="subdued">Based on number and severity of related alerts</EuiText>
            <EuiSpacer size="m" />
          </EuiFlexItem>

          <EuiFlexItem>
            <EuiFlexGroup gutterSize="s" alignItems="center">
              <EuiFlexItem grow={false}>
                <EuiIcon type="clock" color="#722ed1" />
              </EuiFlexItem>
              <EuiFlexItem>
                <EuiText size="s"><strong>Time Factor: {risk_factors.time_factor.toFixed(1)}/30</strong></EuiText>
              </EuiFlexItem>
            </EuiFlexGroup>
            <EuiSpacer size="xs" />
            <EuiProgress
              value={(risk_factors.time_factor / 30) * 100}
              max={100}
              size="s"
              color="#722ed1"
            />
            <EuiSpacer size="xs" />
            <EuiText size="xs" color="subdued">Based on how long the incident has been open</EuiText>
          </EuiFlexItem>
        </EuiFlexGroup>

        <EuiHorizontalRule />

        {/* Incident Details */}
        <EuiTitle size="s">
          <h3>Incident Information</h3>
        </EuiTitle>

        <EuiSpacer size="m" />

        <EuiDescriptionList textStyle="reverse" style={{ maxWidth: '800px' }}>
          <EuiFlexGroup>
            <EuiFlexItem>
              <EuiDescriptionListTitle>ID</EuiDescriptionListTitle>
              <EuiDescriptionListDescription>{incidentId}</EuiDescriptionListDescription>
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiDescriptionListTitle>Type</EuiDescriptionListTitle>
              <EuiDescriptionListDescription>{incident_type}</EuiDescriptionListDescription>
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiDescriptionListTitle>Severity</EuiDescriptionListTitle>
              <EuiDescriptionListDescription>
                <EuiHealth color={severity === 'critical' ? 'danger' :
                            severity === 'high' ? 'warning' :
                            severity === 'medium' ? 'primary' : 'success'}>
                  {severity.toUpperCase()}
                </EuiHealth>
              </EuiDescriptionListDescription>
            </EuiFlexItem>
          </EuiFlexGroup>

          <EuiSpacer size="s" />

          <EuiFlexGroup>
            <EuiFlexItem>
              <EuiDescriptionListTitle>Overall Risk</EuiDescriptionListTitle>
              <EuiDescriptionListDescription>
                <EuiTextColor color={risk_score >= 75 ? 'danger' : risk_score >= 50 ? 'warning' : 'success'}>
                  <strong>{getRiskLabel()}</strong>
                </EuiTextColor>
              </EuiDescriptionListDescription>
            </EuiFlexItem>
          </EuiFlexGroup>
        </EuiDescriptionList>
      </EuiPanel>
    </div>
  );
};

export default IncidentRiskDetail;