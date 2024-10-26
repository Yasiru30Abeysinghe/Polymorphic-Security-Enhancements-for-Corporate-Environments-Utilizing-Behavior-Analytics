import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Container, Button, Typography, Paper, Box, Grid, TextField, Tooltip, IconButton } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { Route, Routes, useNavigate, Link } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import PolicyForm from './components/PolicyForm';
import Dashboard from './components/Dashboard';
import ErrorBoundary from './components/ErrorBoundary';
import PolicyExecutionDetail from './components/PolicyExecutionDetail';
import VMManagement from './components/VMManagement'; // Import VMManagement component
import QuickLinks from './components/QuickLinks';


const theme = createTheme({
  palette: {
    primary: {
      main: '#0078D4',
    },
    secondary: {
      main: '#D83B01',
    },
    background: {
      default: '#F3F2F1',
    },
  },
  typography: {
    fontFamily: 'Segoe UI, sans-serif',
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
  },
  shape: {
    borderRadius: 8,
  },
});



function App() {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState([]);
  const [policyCategory, setPolicyCategory] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    appliedPolicies: 0,
    vulnerabilities: 0,
    threatLevel: 'Unknown',
  });
  const [logData, setLogData] = useState([]);
  const [appliedConfigurations, setAppliedConfigurations] = useState(null);
  const navigate = useNavigate();

  const fetchUpdatedLogs = async () => {
    try {
      const logResponse = await fetch('http://127.0.0.1:5000/logs');
      const logs = await logResponse.json();
      setLogData(logs);

      setDashboardData({
        appliedPolicies: logs.length,
        vulnerabilities: logs.reduce((acc, log) => acc + (log.vulnerabilities || 0), 0),
        threatLevel: logs.length ? logs[logs.length - 1].threatLevel : 'Low',
      });
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  const renderWithBoldText = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  useEffect(() => {
    fetchUpdatedLogs();
  }, []);
  
  // Enhanced sanitization function to remove malicious patterns
  const sanitizeInput = (input) => {
    const unsafePattern = /<.*?>|on\w+=['"].*?['"]/gi; // Detect <tags> or event handlers
    return input.replace(unsafePattern, ''); // Remove malicious content
  };

  // Function to validate the input after sanitization
  const isInputSafe = (input) => {
    const unsafePattern = /<|>|script|alert|onerror|onload/i; // Detect unsafe patterns
    return !unsafePattern.test(input); // Return false if any malicious pattern is found
  };

  const handleInputChange = (e) => {
    const rawInput = e.target.value;
    const sanitizedInput = sanitizeInput(rawInput); // Sanitize input immediately
    setInputText(sanitizedInput);
  };


  
  const handleSubmit = async (e) => {
    e.preventDefault();
  
    const sanitizedText = sanitizeInput(inputText.trim());
  
    if (!isInputSafe(inputText)) {
      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'Invalid input detected. Please try again with a valid security requirement.', sender: 'system' }
      ]);
      return; // Stop if input is malicious
    }
  
    if (inputText.trim() !== '') {
      try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ inputText }), // Send the sanitized input
        });
  
        const data = await response.json();
        setMessages([{ text: `${data.justification}`, sender: 'system' }]);
        setPolicyCategory(data.label);
      } catch (error) {
        setMessages(prevMessages => [
          ...prevMessages,
          { text: 'An error occurred while processing your request.', sender: 'system' }
        ]);
      }
    }
  };

  const handleApplyPolicies = async (formData) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      setDashboardData({
        appliedPolicies: data.appliedPoliciesCount,
        vulnerabilities: data.vulnerabilitiesDetected,
        threatLevel: data.threatLevel,
      });

      setAppliedConfigurations(formData);

      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'Policies applied successfully!', sender: 'system' }
      ]);

      await fetchUpdatedLogs();
    } catch (error) {
      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'An error occurred while applying policies.', sender: 'system' }
      ]);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg">
        <Paper elevation={3} sx={{ padding: '20px', marginTop: '20px', backgroundColor: '#fff' }}>
          <Header />
          <Sidebar />

          <Routes>

            {/* Main Page Route */}
            <Route path="/" element={
              <>
                <Typography variant="h4" gutterBottom align="center">
                  NLP Policy Generator
                </Typography>

                {/* Examples, Capabilities, and Limitations Section */}
                <Box display="flex" justifyContent="space-between" sx={{ marginBottom: '20px' }}>
                  <Box>
                    <Typography variant="h6" align="center">Examples</Typography>
                    <Paper sx={{ padding: '10px', marginBottom: '10px' }}>
                      <Typography>"Help to comply with NIST 800-53" -&gt;</Typography>
                    </Paper>
                    <Paper sx={{ padding: '10px', marginBottom: '10px' }}>
                      <Typography>"How do I make my Browser Secure?" -&gt;</Typography>
                    </Paper>
                  </Box>

                  <Box>
                    <Typography variant="h6" align="center">Capabilities</Typography>
                    <Paper sx={{ padding: '10px', marginBottom: '10px' }}>
                      <Typography>Explains the user requested security requirements</Typography>
                    </Paper>
                    <Paper sx={{ padding: '10px', marginBottom: '10px' }}>
                      <Typography>Provides browser configurable settings</Typography>
                    </Paper>
                  </Box>

                  <Box>
                    <Typography variant="h6" align="center">Limitations</Typography>
                    <Paper sx={{ padding: '10px', marginBottom: '10px' }}>
                      <Typography>Only Supports limited browser configurations</Typography>
                    </Paper>
                  </Box>
                </Box>
                

                {/* Search Bar Section */}
                <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
                  <TextField
                    variant="outlined"
                    fullWidth
                    value={inputText}
                    onChange={handleInputChange}
                    placeholder="Search"
                    sx={{ marginRight: '10px' }}
                  />
                  <IconButton type="submit" color="primary">
                    <SearchIcon />
                  </IconButton>
                </Box>

                {/* "Find Logs Here" Button */}
                <Box display="flex" justifyContent="right" sx={{ marginBottom: '20px' }}>
                  <Link to="/policy-details" style={{ textDecoration: 'none' }}>
                    <Button variant="contained" color="primary">
                      Find Logs Here
                    </Button>
                  </Link>

                    {/* Button to Navigate to VM Management */}
                    <Link to="/manage-vms" style={{ textDecoration: 'none' }}>
                      <Button variant="outlined" color="secondary">
                        Manage VMs
                      </Button>
                    </Link>
                </Box>

                {/* Conditional Rendering */}
                {messages.length > 0 && (
                  <Box className="chat-area" sx={{ marginBottom: '20px', backgroundColor: '#F3F2F1', padding: '10px' }}>
                    {messages.map((msg, index) => (
                      <Paper key={index} sx={{ padding: '10px', backgroundColor: '#f5f5f5', marginBottom: '10px' }}>
                        <Typography>{renderWithBoldText(msg.text)}</Typography>
                      </Paper>
                    ))}
                  </Box>
                )}

                {policyCategory && (
                  <ErrorBoundary>
                    <PolicyForm policyCategory={policyCategory} onApply={handleApplyPolicies} />
                  </ErrorBoundary>
                )}

                {/* Display applied configurations */}
                {appliedConfigurations && (
                  <Box sx={{ marginTop: '20px' }}>
                    <Typography variant="h6">Applied Configurations</Typography>
                    <pre>{JSON.stringify(appliedConfigurations, null, 2)}</pre>
                  </Box>
                )}
              </>
            } />

            {/* Policy Details Page */}
            <Route path="/policy-details" element={
              <>
                <Typography variant="h4" gutterBottom align="center">
                  Policy Execution Details
                </Typography>
                
                {/* Smaller Dashboard */}
                <Grid container justifyContent="center" sx={{ marginBottom: '20px' }}>
                  <Grid item xs={6}>
                    <ErrorBoundary>
                      <Dashboard data={dashboardData} onlyGraph={true} />
                    </ErrorBoundary>
                  </Grid>
                </Grid>

                {/* Display Policy Execution Details */}
                <Box className="chat-area" sx={{ marginBottom: '20px', backgroundColor: '#F3F2F1', padding: '10px' }}>
                  <PolicyExecutionDetail logData={logData} />
                </Box>
              </>
            } />

            <Route path="/manage-vms" element={<VMManagement />} />

          </Routes>
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App;

