/**
 * Main App Component
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';

// Import pages (to be created)
// import Dashboard from './pages/Dashboard';
// import TaskManagement from './pages/TaskManagement';
// import TeamView from './pages/TeamView';
// import Analytics from './pages/Analytics';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<h1>B2P.AI - Dashboard</h1>} />
            <Route path="/tasks" element={<h1>Task Management</h1>} />
            <Route path="/team" element={<h1>Team View</h1>} />
            <Route path="/analytics" element={<h1>Analytics</h1>} />
            {/* Add more routes as pages are created */}
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
