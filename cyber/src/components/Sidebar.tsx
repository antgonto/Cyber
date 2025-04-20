import * as React from 'react';
import {
  EuiSideNav,
  EuiIcon,
  EuiSpacer,
  EuiFlexGroup,
  EuiFlexItem,
  EuiText
} from '@elastic/eui';
import { useNavigate, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const sideNavItems = [
    {
      name: 'Security Platform',
      id: 0,
      items: [
        {
          id: '1',
          name: 'Dashboard',
          onClick: () => navigate('/'),
          isSelected: location.pathname === '/',
          icon: <EuiIcon type="dashboardApp" />
        },
        {
          id: '2',
          name: 'Users',
          onClick: () => navigate('/users'),
          isSelected: location.pathname === '/users',
          icon: <EuiIcon type="usersRolesApp" />
        },
        {
          id: '3',
          name: 'Assets',
          onClick: () => navigate('/assets'),
          isSelected: location.pathname === '/assets',
          icon: <EuiIcon type="storage" />
        },
        {
          id: '4',
          name: 'Vulnerabilities',
          onClick: () => navigate('/vulnerabilities'),
          isSelected: location.pathname === '/vulnerabilities',
          icon: <EuiIcon type="securityApp" />
        },
        {
          id: '5',
          name: 'Alerts',
          onClick: () => navigate('/alerts'),
          isSelected: location.pathname === '/alerts',
          icon: <EuiIcon type="alert" />
        },
        {
          id: '6',
          name: 'Settings',
          onClick: () => navigate('/settings'),
          isSelected: location.pathname === '/settings',
          icon: <EuiIcon type="gear" />
        }
      ]
    }
  ];

  return (
    <div style={{ width: '240px', height: '100%', background: '#1a1c21', padding: '16px' }}>
      <EuiFlexGroup alignItems="center" gutterSize="s">
        <EuiFlexItem grow={false}>
          <EuiIcon type="securityApp" size="xl" />
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiText>
            <h2 style={{ margin: 0 }}>SecOps</h2>
          </EuiText>
        </EuiFlexItem>
      </EuiFlexGroup>
      <EuiSpacer size="l" />
      <EuiSideNav items={sideNavItems} />
    </div>
  );
};

export default Sidebar;