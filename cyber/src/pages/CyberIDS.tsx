// Cyber IDS - Main Dashboard Component
import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Paper
} from '@mui/material';
import TrainingDashboard from './TrainingDashboard';
import PredictionInterface from './PredictionInterface';
import MetricsDashboard from './MetricsDashboard';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`cyberids-tabpanel-${index}`}
      aria-labelledby={`cyberids-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function CyberIDS() {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          🛡️ Cyber IDS - Intrusion Detection System
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Binary intrusion detector powered by XGBoost on CSE-CIC-IDS2018
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 3 }}>
          <Tabs value={currentTab} onChange={handleTabChange} aria-label="Cyber IDS tabs">
            <Tab label="📊 Metrics Dashboard" id="cyberids-tab-0" />
            <Tab label="🔮 Predict" id="cyberids-tab-1" />
            <Tab label="🎓 Train Model" id="cyberids-tab-2" />
          </Tabs>
        </Box>

        <TabPanel value={currentTab} index={0}>
          <MetricsDashboard />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <PredictionInterface />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <TrainingDashboard />
        </TabPanel>
      </Paper>
    </Container>
  );
}

