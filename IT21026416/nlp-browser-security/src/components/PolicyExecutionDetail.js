import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Tooltip, Modal, List, ListItem, ListItemText } from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';

const PolicyExecutionDetail = () => {
  const [policyData, setPolicyData] = useState([]);
  const [openLogModal, setOpenLogModal] = useState(false);
  const [selectedLog, setSelectedLog] = useState(null);

  // Function to generate a sequential Policy ID from the index
  const generatePolicyID = (index) => {
    return `Policy-${index + 1}`;
  };

  useEffect(() => {
    const fetchPolicyDetails = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/logs");  // Fetch log filenames
        const data = await response.json();
        console.log("Fetched log data:", data);

        // Ensure the data is an array and process each filename
        const parsedData = Array.isArray(data)
          ? data.map((logFile, index) => {
              const fileNameParts = logFile.replace('.json', '').split('_');
              const category = fileNameParts.slice(0, -2).join(' ') || 'Unknown';  // Extract category correctly
              const timestamp = fileNameParts.slice(-2).join('_') || 'Unknown';  // Extract full timestamp
              return {
                id: generatePolicyID(index),  // Generate sequential policy ID
                category: category || 'Unknown',
                executedAt: timestamp || 'N/A',
                status: 'Success'  // Assuming 'Success' for all logs
              };
            })
          : [];

        setPolicyData(parsedData);  // Set the parsed data
      } catch (error) {
        console.error('Error fetching policy details:', error);
      }
    };

    fetchPolicyDetails();
  }, []);

  // Fetch and display a specific log file
  const handleViewLog = async (category, fullTimestamp) => {
    if (!category || !fullTimestamp) {
      console.error("Category or timestamp is undefined");
      return;
    }
  
    const logFileName = `${category.replace(/ /g, '_')}_${fullTimestamp}.json`; // Correct filename construction
    
    console.log(`Fetching log file: ${logFileName}`);
  
    try {
      const response = await fetch(`http://127.0.0.1:5000/logs/${logFileName}`);
      const logData = await response.json();
  
      if (logData.error) {
        throw new Error(logData.error);
      }
  
      console.log('Log data received:', logData);
      setSelectedLog(logData);
      setOpenLogModal(true);
    } catch (error) {
      console.error('Error fetching log file:', error.message);
      setSelectedLog({ error: `Log file not found: ${logFileName}` });
      setOpenLogModal(true);
    }
  };

  // Function to display relevant log data in a structured way
  const renderLogDetails = (logData) => {
    if (!logData) return 'Loading...';
    
    const fieldsToDisplay = [
      "data_type", "time_to_live_in_hours", "PrintWebpage", "AutomaticBrowserSync",
      "SaveBrowserHistory", "Autofill", "CaptureScreenshots", "RememberPasswords",
      "SitePerProcess", "SearchSuggestions", "MetricsReporting", "PromptDownloadLocation",
      "BrowserHistoryDeletion", "BackgroundProcessing", "NetworkPredictions", "ThirdPartyCookies",
      "BlockURLs", "AllowURLs",    "SafeBrowsingProtectionLevel", "BlockObstructiveWebsites", "OverrideCertificateErrors",
      "BlockExcessiveAds", "BlockInjectedCode", "WhitelistExtensions", "BlacklistExtensions",
      "geolocation", "camera", "sensor", "notifications", "js", "popups", "usb"
    ];

    // Filter and format logData for display
    const filteredData = fieldsToDisplay.reduce((result, key) => {
      if (logData[key] !== undefined) {
        result[key] = logData[key];
      }
      return result;
    }, {});

    const renderStatusIcon = (value) => {
      if (['allow', 'enable', 'enabled', 'yes'].includes(value.toLowerCase())) {
        return <CheckIcon color="success" />;
      } else if (['block', 'restrict', 'disable', 'no'].includes(value.toLowerCase())) {
        return <CloseIcon color="error" />;
      } else {
        return 'Not Configured';
      }
    };

    return (
      <List>
        {Object.entries(filteredData).map(([key, value], index) => (
          <ListItem key={index} sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <ListItemText primary={key.replace(/([A-Z])/g, ' $1').trim()} />
            {renderStatusIcon(value)}
          </ListItem>
        ))}
      </List>
    );
  };

  // Close modal handler
  const handleCloseModal = () => {
    setOpenLogModal(false);
    setSelectedLog(null);
  };

  return (
    <Box sx={{ padding: 2 }}>
      <Typography variant="h4" gutterBottom>Detailed Policy Execution Overview</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Policy ID</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Date Executed</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {policyData.length > 0 ? (
              policyData.map((policy, index) => (
                <TableRow key={index}>
                  <TableCell>{policy.id || 'Unknown'}</TableCell>
                  <TableCell>{policy.category || 'Unknown'}</TableCell>
                  <TableCell>{policy.executedAt || 'N/A'}</TableCell>
                  <TableCell>{policy.status || 'N/A'}</TableCell>
                  <TableCell>
                    <Tooltip title="View full log" arrow>
                      <Button
                        variant="outlined"
                        onClick={() => handleViewLog(policy.category || 'Unknown', policy.executedAt || 'Unknown')}
                        sx={{ marginRight: 1 }}
                      >
                        View Log
                      </Button>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5}>No policy data available.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

    {/* Modal to display log details */}
    <Modal open={openLogModal} onClose={handleCloseModal} aria-labelledby="modal-modal-title" aria-describedby="modal-modal-description">
      <Box sx={{ 
          position: 'absolute', 
          top: '50%', 
          left: '50%', 
          transform: 'translate(-50%, -50%)', 
          width: '700px', // Set width to make it rectangular and smaller
          maxHeight: '400px', // Set a maximum height
          padding: '50px', // Adjust padding
          bgcolor: 'background.paper', 
          border: '1px solid #000', 
          boxShadow: 24, 
          borderRadius: 2, // Slight border-radius to make it neat
          overflowY: 'auto'  // Add vertical scroll when content exceeds height

        }}>
        <Typography variant="h6" component="h2">
          Policy Log Details
        </Typography>
        {/* Render the log data or an error message */}
        {selectedLog && selectedLog.error ? (
          <Typography sx={{ mt: 2 }}>{selectedLog.error}</Typography>
        ) : (
          <Box sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>
            
            {selectedLog ? renderLogDetails(selectedLog) : 'Loading...'}
          </Box>
        )}
        <Button onClick={handleCloseModal} sx={{ mt: 2 }}>Close</Button>
      </Box>
    </Modal>
  </Box>
  );
};

export default PolicyExecutionDetail;
