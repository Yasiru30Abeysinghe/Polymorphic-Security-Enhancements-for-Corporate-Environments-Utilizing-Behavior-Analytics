import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Box, Typography } from '@mui/material';

// Register the necessary Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState({
    tppCount: 0,
    dlpCount: 0,
  });

  useEffect(() => {
    const fetchLogData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/logs');  // Replace with actual API endpoint
        const logData = await response.json();
        
        console.log("Fetched log data:", logData);  // Add this line to see the fetched data
  
        if (Array.isArray(logData) && logData.length > 0) {
          let tppCount = 0;
          let dlpCount = 0;
  
          logData.forEach(logFile => {    
            const fileName = logFile.replace('.json', '');
  
            // Check if the filename starts with 'Threat_Prevention' or 'Data_Leakage_Prevention'
            if (fileName.startsWith('Threat_Prevention')) {
              tppCount += 1;
            } else if (fileName.startsWith('Data_Leakage_Prevention')) {
              dlpCount += 1;
            }
          });
  
          // Set the counts for TPP and DLP policies
          setMetrics({
            tppCount: tppCount,
            dlpCount: dlpCount,
          });
        } else {
          // Reset counts if no logs are found
          setMetrics({
            tppCount: 0,
            dlpCount: 0,
          });
        }
      } catch (error) {
        console.error('Error fetching logs:', error);
      }
    };
  
    fetchLogData();
  }, []);

  const handleDashboardClick = () => {
    navigate('/policy-details'); // Navigate to the detailed view page
  };
  

  // Data for the bar chart
  const chartData = {
    labels: ['TPP', 'DLP'],
    datasets: [
      {
        label: 'Number of Policies Applied',
        data: [metrics.tppCount, metrics.dlpCount],
        backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)'],
        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)'],
        borderWidth: 1,
      },
    ],
  };

  return (
    <Box sx={{ padding: 2 }}>
      <Typography variant="h6">Policy Trends</Typography>
      <Box sx={{ marginTop: 4 }} onClick={handleDashboardClick} style={{ cursor: 'pointer' }}>
        <Bar data={chartData} />
      </Box>
    </Box>
  );
};

export default Dashboard;
