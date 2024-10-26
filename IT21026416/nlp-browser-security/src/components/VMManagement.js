import React, { useState, useEffect } from 'react';
import { 
  Box, Button, TextField, Typography, Paper, IconButton, 
  Snackbar, Alert, Tooltip, Dialog, DialogTitle, DialogActions 
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';

const VMManagement = () => {
  const [ipAddress, setIpAddress] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [vmList, setVmList] = useState([]);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [editIndex, setEditIndex] = useState(null); // Track which VM is being edited
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false); // Track delete confirmation
  const [selectedVM, setSelectedVM] = useState(null); // VM to delete

  // Fetch saved VMs on component mount
  useEffect(() => {
    fetchVMs();
  }, []);

  const fetchVMs = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/vms');
      if (!response.ok) throw new Error('Failed to fetch VMs.');
      const data = await response.json();
      setVmList(data);
    } catch (error) {
      console.error('Error fetching VMs:', error);
      setError('Failed to fetch VMs.');
    }
  };
  

  const handleAddOrEditVM = async () => {
    const newVM = { ip: ipAddress, username, password };
    const method = editIndex !== null ? 'PUT' : 'POST'; 
    const endpoint = editIndex !== null 
      ? `http://127.0.0.1:5000/vms/${editIndex}` 
      : 'http://127.0.0.1:5000/vms';
  
    try {
      const response = await fetch(endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newVM),
      });
  
      if (response.ok) {
        await fetchVMs(); // Refresh VM list
        resetForm();
        setSnackbarOpen(true);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to add/update VM. Please try again.');
      }
    } catch (error) {
      console.error('Error adding/editing VM:', error);
      setError('Failed to add/update VM. Please try again.');
    }
  };
  

  const handleDeleteVM = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/vms/${selectedVM}`, {
        method: 'DELETE',
      });
  
      if (response.ok) {
        await fetchVMs();
        setDeleteConfirmOpen(false);
      } else {
        setError('Failed to delete VM. Please try again.');
      }
    } catch (error) {
      console.error('Error deleting VM:', error);
      setError('Failed to delete VM. Please try again.');
    }
  };
  
  

  const validateInputs = () => {
    if (!ipAddress || !username || !password) {
      setError('All fields are required.');
      return false;
    }
    const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    if (!ipRegex.test(ipAddress)) {
      setError('Invalid IP address format.');
      return false;
    }
    return true;
  };

  const resetForm = () => {
    setIpAddress('');
    setUsername('');
    setPassword('');
    setEditIndex(null);
    setError(null);
  };

  const handleEditVM = (index) => {
    const vm = vmList[index];
    setIpAddress(vm.ip);
    setUsername(vm.username);
    setPassword(vm.password);
    setEditIndex(index);
  };

  const openDeleteDialog = (index) => {
    setSelectedVM(index);
    setDeleteConfirmOpen(true);
  };

  const handleSnackbarClose = () => setSnackbarOpen(false);

  const handleExportVMs = () => {
    const dataStr = JSON.stringify(vmList, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'vms.json';
    link.click();
    URL.revokeObjectURL(url); // Clean up URL object
  };

  return (
    
    <Box sx={{ padding: '20px' }}>
      <Typography variant="h4" gutterBottom>
        Manage Virtual Machines
      </Typography>

      <Paper sx={{ padding: '20px', marginBottom: '20px' }}>
        <Typography variant="h6">
          {editIndex !== null ? 'Edit VM' : 'Add a New VM'}
        </Typography>
        <TextField
          label="IP Address"
          fullWidth
          value={ipAddress}
          onChange={(e) => setIpAddress(e.target.value)}
          margin="normal"
        />
        <TextField
          label="Username"
          fullWidth
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          margin="normal"
        />
        <TextField
          label="Password"
          type="password"
          fullWidth
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          margin="normal"
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleAddOrEditVM}
          sx={{ marginTop: '10px' }}
        >
          {editIndex !== null ? 'Update VM' : 'Add VM'}
        </Button>

        {error && <Typography color="error" sx={{ marginTop: '10px' }}>{error}</Typography>}
      </Paper>

      <Typography variant="h6">Saved VMs</Typography>
      <Paper sx={{ padding: '20px' }}>
        {vmList.length > 0 ? (
          vmList.map((vm, index) => (
            <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <Typography>{vm.ip} - {vm.username}</Typography>
              <Box>
                <Tooltip title="Edit VM">
                  <IconButton onClick={() => handleEditVM(index)} color="primary">
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete VM">
                  <IconButton onClick={() => openDeleteDialog(index)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          ))
        ) : (
          <Typography>No VMs saved.</Typography>
        )}
      </Paper>

      <Box sx={{ marginTop: '20px' }}>
        <Button
          variant="contained"
          color="secondary"
          onClick={handleExportVMs}
        >
          Export VMs as JSON
        </Button>
      </Box>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
      >
        <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
          VM {editIndex !== null ? 'updated' : 'added'} successfully!
        </Alert>
      </Snackbar>

      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
      >
        <DialogTitle>Are you sure you want to delete this VM?</DialogTitle>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteVM} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default VMManagement;
