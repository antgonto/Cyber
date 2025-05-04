import React, { useState, useEffect } from 'react';
import {
  EuiPage,
  EuiPageBody,
  EuiPageHeader,
  EuiTitle,
  EuiFlexGroup,
  EuiFlexItem,
  EuiSpacer,
  EuiSelect,
  EuiLoadingSpinner,
  EuiCallOut,
  EuiEmptyPrompt,
} from '@elastic/eui';
import { useNavigate } from 'react-router-dom';
import { riskService } from '../services/api';
import RiskScoreCard, { RiskScore } from './RiskScoreCard';

const IncidentRiskDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [riskScores, setRiskScores] = useState<RiskScore[]>([]);
  const [filteredScores, setFilteredScores] = useState<RiskScore[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRiskScores = async () => {
      try {
        setLoading(true);
        const response = await riskService.getRiskScores();
        setRiskScores(response.data);
        setFilteredScores(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load risk scores. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRiskScores();
  }, []);

  useEffect(() => {
    setFilteredScores(
      severityFilter === 'all'
        ? riskScores
        : riskScores.filter(s => s.severity === severityFilter)
    );
  }, [severityFilter, riskScores]);

  const handleCardClick = (id: number) => navigate(`/app/v1/cyber/incidents/${id}`);

  if (loading) {
    return (
      <EuiFlexGroup alignItems="center" justifyContent="center" style={{ height: '100vh' }}>
        <EuiFlexItem grow={false}>
          <EuiLoadingSpinner size="xl" />
        </EuiFlexItem>
      </EuiFlexGroup>
    );
  }

  if (error) {
    return <EuiCallOut title="Error" color="danger" iconType="alert">{error}</EuiCallOut>;
  }

  return (
    <EuiPage paddingSize="l">
      <EuiPageBody>
        <EuiPageHeader>
          <EuiFlexGroup justifyContent="spaceBetween" alignItems="center">
            <EuiFlexItem>
              <EuiTitle size="l"><h1>Incident Risk Dashboard</h1></EuiTitle>
            </EuiFlexItem>
            <EuiFlexItem grow={false}>
              <EuiFlexGroup alignItems="center">
                <EuiFlexItem grow={false}>Filter by severity:</EuiFlexItem>
                <EuiFlexItem grow={false}>
                  <EuiSelect
                    options={[
                      { value: 'all', text: 'All Severities' },
                      { value: 'critical', text: 'Critical' },
                      { value: 'high', text: 'High' },
                      { value: 'medium', text: 'Medium' },
                      { value: 'low', text: 'Low' },
                    ]}
                    value={severityFilter}
                    onChange={e => setSeverityFilter(e.target.value)}
                    aria-label="Filter by severity"
                  />
                </EuiFlexItem>
              </EuiFlexGroup>
            </EuiFlexItem>
          </EuiFlexGroup>
        </EuiPageHeader>

        <EuiSpacer size="l" />

        {filteredScores.length === 0 ? (
          <EuiEmptyPrompt
            iconType="securityApp"
            title={<h2>No incidents match your filter criteria</h2>}
            titleSize="s"
          />
        ) : (
          <EuiFlexGroup wrap gutterSize="m">
            {filteredScores.map(score => (
              <EuiFlexItem key={score.incident_id} style={{ minWidth: '350px', maxWidth: '500px' }}>
                <RiskScoreCard
                  riskScore={score}
                  onClick={() => handleCardClick(score.incident_id)}
                />
              </EuiFlexItem>
            ))}
          </EuiFlexGroup>
        )}
      </EuiPageBody>
    </EuiPage>
  );
};

export default IncidentRiskDashboard;