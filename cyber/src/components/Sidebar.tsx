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
  const [isConfirmModalVisible, setIsConfirmModalVisible] = React.useState(false);

  const handleConfirmDropDatabase = async () => {
    try {
      const response = await fetch('/settings/execute-drop-database-procedure/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      alert(data.message);
      setIsConfirmModalVisible(false);
    } catch (error) {
      alert('Failed to drop the database: ' + error);
    }
  };

  const showConfirmModal = () => setIsConfirmModalVisible(true);
  const closeConfirmModal = () => setIsConfirmModalVisible(false);

  const handleCreateProcedure = async () => {
    try {
      const response = await fetch('/settings/create-truncate-procedure/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert('Failed to create the procedure: ' + error);
    }
  };

  const handleExecuteProcedure = async () => {
    try {
      const response = await fetch('/settings/execute-truncate-procedure/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert('Failed to execute the procedure: ' + error);
    }
  };

  const handleCreateDatabaseProcedure = async () => {
    try {
      const response = await fetch('/settings/create-database-procedure/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert('Failed to create the database procedure: ' + error);
    }
  };

  const handleExecuteDatabaseProcedure = async () => {
    try {
      const response = await fetch('/settings/execute-database-procedure/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert('Failed to execute the database procedure: ' + error);
    }
  };

  const handleCreateTablesProcedure = async () => {
    try {
      const response = await fetch('/settings/create-tables-procedure/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert('Failed to create the tables procedure: ' + error);
    }
  };

  const handleExecuteTablesProcedure = async () => {
    try {
      const response = await fetch('/settings/execute-tables-procedure/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert('Failed to execute the tables procedure: ' + error);
    }
  };

  const handleCreateDropDatabaseProcedure = async () => {
    try {
      const response = await fetch('/settings/create-drop-database-procedure/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert('Failed to create the drop database procedure: ' + error);
    }
  };

  const handleExecuteDropDatabaseProcedure = () => {
    showConfirmModal();
  };

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
          name: 'Incidents',
          onClick: () => navigate('/incidents'),
          isSelected: location.pathname === '/incidents',
          icon: <EuiIcon type="bolt" />
        },
        {
          id: '7',
          name: 'Threat Intelligence',
          onClick: () => navigate('/threat_intelligence'),
          isSelected: location.pathname === '/threat_intelligence',
          icon: <EuiIcon type="globe" />
        },
        {
          id: '8',
          name: 'View',
          onClick: () => navigate('/dashboard'),
          isSelected: location.pathname === '/dashboard',
          icon: <EuiIcon type="visLine" />
        },
        {
          id: '9',
          name: 'Settings',
          icon: <EuiIcon type="gear" />,
          items: [
            {
              id: '9-1',
              name: 'Create Truncate Procedure',
              onClick: handleCreateProcedure
            },
            {
              id: '9-2',
              name: 'Execute Truncate Procedure',
              onClick: handleExecuteProcedure
            },
            {
              id: '9-3',
              name: 'Create Database Procedure',
              onClick: handleCreateDatabaseProcedure
            },
            {
              id: '9-4',
              name: 'Execute Database Procedure',
              onClick: handleExecuteDatabaseProcedure
            },
            {
              id: '9-5',
              name: 'Create Tables Procedure',
              onClick: handleCreateTablesProcedure
            },
            {
              id: '9-6',
              name: 'Execute Tables Procedure',
              onClick: handleExecuteTablesProcedure
            },
            {
              id: '9-7',
              name: 'Create Drop Database Procedure',
              onClick: handleCreateDropDatabaseProcedure
            },
            {
              id: '9-8',
              name: 'Execute Drop Database Procedure',
              onClick: handleExecuteDropDatabaseProcedure
            }
          ]
        }
      ]
    }
  ];

  return (
    <div style={{ width: '280px', height: '100%', background: '#1a1c21', padding: '16px' }}>
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

      {isConfirmModalVisible && (
        <div className="confirm-modal" style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: '#fff',
            padding: '20px',
            borderRadius: '4px',
            maxWidth: '400px'
          }}>
            <p>Are you sure you want to drop the cyber_db database? This action cannot be undone.</p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button
                style={{ marginRight: '10px', padding: '5px 10px' }}
                onClick={closeConfirmModal}
              >
                Cancel
              </button>
              <button
                style={{ padding: '5px 10px' }}
                onClick={handleConfirmDropDatabase}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;