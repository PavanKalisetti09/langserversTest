import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  Button, 
  Paper 
} from '@mui/material';
import { useNotification } from '../contexts/NotificationContext';
import api from '../services/api';

const FollowRequests = () => {
  const [requests, setRequests] = useState([]);
  const { showNotification } = useNotification();

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const response = await api.get('/api/follow/requests');
      setRequests(response.data);
    } catch (error) {
      showNotification('Failed to fetch follow requests', 'error');
    }
  };

  const handleAccept = async (username) => {
    try {
      await api.post(`/api/follow/${username}/approve`);
      showNotification('Follow request accepted', 'success');
      fetchRequests(); // Refresh the list
    } catch (error) {
      showNotification('Failed to accept follow request', 'error');
    }
  };

  const handleReject = async (username) => {
    try {
      await api.post(`/api/follow/${username}/reject`);
      showNotification('Follow request rejected', 'success');
      fetchRequests(); // Refresh the list
    } catch (error) {
      showNotification('Failed to reject follow request', 'error');
    }
  };

  if (requests.length === 0) {
    return null;
  }

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        Follow Requests
      </Typography>
      <List>
        {requests.map((request) => (
          <ListItem
            key={request.id}
            secondaryAction={
              <Box>
                <Button
                  onClick={() => handleAccept(request.username)}
                  variant="contained"
                  color="primary"
                  size="small"
                  sx={{ mr: 1 }}
                >
                  Accept
                </Button>
                <Button
                  onClick={() => handleReject(request.username)}
                  variant="outlined"
                  color="error"
                  size="small"
                >
                  Reject
                </Button>
              </Box>
            }
          >
            <ListItemText primary={request.username} />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default FollowRequests; 