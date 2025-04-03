import * as React from 'react';
import {
  EuiFlexGrid,
  EuiFlexItem,
  EuiPanel,
  EuiStat,
  EuiTitle,
  EuiText,
  EuiIcon,
  EuiPageHeader,
  EuiPageTemplate,
  EuiSpacer
} from '@elastic/eui';

const Dashboard = () => {
  // Using more modern ES2023 patterns
  const stats = {
    users: 24,
    assets: 156,
    incidents: 12,
    vulnerabilities: 47
  };

  const displayValue = (key) => stats?.[key] ?? 0;

  // Using array methods that are well supported in ES2023
  const statItems = [
    { key: 'users', icon: 'user', color: 'primary', description: 'Total Users' },
    { key: 'assets', icon: 'storage', color: 'success', description: 'Assets' },
    { key: 'incidents', icon: 'alert', color: 'danger', description: 'Security Incidents' },
    { key: 'vulnerabilities', icon: 'securitySignal', color: 'warning', description: 'Vulnerabilities' }
  ];

  return (
    <>
      <EuiPageHeader>
        <EuiTitle size="l">
          <h1>Dashboard</h1>
        </EuiTitle>
      </EuiPageHeader>

      <EuiPageTemplate>
        <EuiFlexGrid columns={4}>
          {statItems.map(item => (
            <EuiFlexItem key={item.key}>
              <EuiPanel>
                <EuiIcon type={item.icon} color={item.color} />
                <EuiStat
                  title={`${displayValue(item.key)}`}
                  description={item.description}
                  titleColor={item.color}
                  textAlign="center"
                />
              </EuiPanel>
            </EuiFlexItem>
          ))}
        </EuiFlexGrid>

        <EuiSpacer size="l" />

        <EuiPanel paddingSize="l" style={{ minHeight: '400px' }}>
          <EuiTitle size="s">
            <h2>Recent Activity</h2>
          </EuiTitle>
          <EuiSpacer size="m" />
          <EuiText>
            <p>This section will display recent system activities, logs, or events.
            Connect it to your backend API when those endpoints are available.</p>
          </EuiText>
        </EuiPanel>
      </EuiPageTemplate>
    </>
  );
};

export default Dashboard;