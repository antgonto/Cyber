import React, { useState } from 'react';
import {
  EuiFlexGrid,
  EuiFlexItem,
  EuiCard,
  EuiIcon,
  EuiSpacer,
} from '@elastic/eui';
import axios from "axios";

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const actions = [
    {
      id: 'create-db',
      title: 'Create Database',
      url: '/app/v1/cyber/settings/create_database/',
      successMsg: 'Database created.',
      errorMsg: 'Failed to create the database: ',
      iconType: 'database',  // changed to a valid Elastic UI icon
    },
    {
      id: 'create-tables',
      title: 'Create Tables',
      url: '/app/v1/cyber/settings/create_tables/',
      successMsg: 'Tables procedure created.',
      errorMsg: 'Failed to create the tables procedure: ',
      iconType: 'tableDensityExpanded',
    },
    {
      id: 'fill-tables',
      title: 'Create Procedure to Fill Tables',
      url: '/app/v1/cyber/settings/create_fake_data_procedure/',
      successMsg: 'Fill tables procedure created.',
      errorMsg: 'Failed to create the fill tables procedure: ',
      iconType: 'importAction',
    },
    {
      id: 'execute-fill-tables',
      title: 'Execute Fill Tables Procedure',
      url: '/app/v1/cyber/settings/execute_fake_data_procedure/',
      successMsg: 'Execute procedure to fill the tables.',
      errorMsg: 'Failed to execute the procedure to fill the tables: ',
      iconType: 'playFilled',
    },
    {
      id: 'create-dashboard',
      title: 'Create Dashboard View',
      url: '/app/v1/cyber/dashboard/create_view/',
      successMsg: 'Dashboard View created successfully.',
      errorMsg: 'Failed to create the dashboard view: ',
      iconType: 'dashboardApp',
    },
    {
      id: 'create-truncate',
      title: 'Create Truncate Procedure',
      url: '/app/v1/cyber/settings/create_truncate_procedure/',
      successMsg: 'Truncate procedure created.',
      errorMsg: 'Failed to create the procedure: ',
      iconType: 'eraser',
    },
    {
      id: 'execute-truncate',
      title: 'Execute Truncate Procedure',
      url: '/app/v1/cyber/settings/execute_truncate_procedure/',
      successMsg: 'Truncate procedure executed.',
      errorMsg: 'Failed to execute the procedure: ',
      iconType: 'play',
    },
    {
      id: 'drop-db',
      title: 'Drop Database',
      url: '/app/v1/cyber/settings/drop_database/',
      successMsg: 'Database dropped.',
      errorMsg: 'Failed to drop the database: ',
      iconType: 'trash',
    },
];

// 5 columns x 4 rows = 20 tiles total
const GRID_SIZE = 5 * 4;

const SettingsMenu: React.FC = () => {
  const [selected, setSelected] = useState<string[]>([]);

  const handleAction = async (action: typeof actions[0]) => {
    try {
      console.log("url", action.url);
      const response = await api.post(action.url);
      const data = response.data;
      alert(data.detail || action.successMsg);
      setSelected(prev =>
        prev.includes(action.id)
          ? prev.filter(id => id !== action.id)
          : [...prev, action.id]
      );
    } catch (error) {
      alert(action.errorMsg + error);
    }
  };

  const blankCount = GRID_SIZE - actions.length;

  return (
    <>
      <EuiSpacer size="xl" />
      <EuiFlexGrid columns={4} gutterSize="l">
        {actions.map(action => (
          <EuiFlexItem key={action.id} style={{ minHeight: 200 }}>
            <EuiCard
              icon={<EuiIcon type={action.iconType} size="xxl" />}
              title={action.title}
              textAlign="center"
              paddingSize="l"
              selectable={{
                isSelected: selected.includes(action.id),
                onClick: () => handleAction(action),
              }}
            />
          </EuiFlexItem>
        ))}

        {Array.from({ length: blankCount }).map((_, idx) => (
          <EuiFlexItem key={`blank-${idx}`} style={{ minHeight: 200 }}>
            {/* empty space */}
          </EuiFlexItem>
        ))}
      </EuiFlexGrid>
    </>
  );
};

export default SettingsMenu;
