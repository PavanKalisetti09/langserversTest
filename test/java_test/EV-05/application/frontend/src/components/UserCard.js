import React from 'react';
import { Card, CardContent, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import api from '../services/api';

const UserCard = ({ user, onRefresh }) => {
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const { showNotification } = useNotification();
  const isCurrentUser = currentUser?.id === user.id;

  const handleFollow = async () => {
    try {
      await api.post(`/api/follow/${user.username}`);
      showNotification('Follow request sent', 'success');
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('Follow error:', error);
      showNotification(error.response?.data?.message || 'Failed to send follow request', 'error');
    }
  };

  const handleUnfollow = async () => {
    try {
      const response = await api.delete(`/api/follow/${user.username}`);
      console.log('Unfollow response:', response);
      showNotification('Unfollowed successfully', 'success');
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('Unfollow error:', {
        message: error.response?.data?.message,
        status: error.response?.status,
        error: error
      });
      showNotification(error.response?.data?.message || 'Failed to unfollow', 'error');
    }
  };

  const handleAcceptFollow = async () => {
    try {
      await api.post(`/api/follow/${user.username}/approve`);
      showNotification('Follow request accepted', 'success');
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('Accept follow error:', error);
      showNotification(error.response?.data?.message || 'Failed to accept follow request', 'error');
    }
  };

  const handleRejectFollow = async () => {
    try {
      await api.post(`/api/follow/${user.username}/reject`);
      showNotification('Follow request rejected', 'success');
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('Reject follow error:', error);
      showNotification(error.response?.data?.message || 'Failed to reject follow request', 'error');
    }
  };

  const getFollowButton = () => {
    if (isCurrentUser) return null;
    
    if (user.followRequestPending) {
      return (
        <Button variant="outlined" disabled>
          Request Pending
        </Button>
      );
    }

    if (user.hasRequestedToFollow) {
      return (
        <Box>
          <Button
            variant="contained"
            color="primary"
            onClick={handleAcceptFollow}
            sx={{ mr: 1 }}
          >
            Accept
          </Button>
          <Button
            variant="outlined"
            color="error"
            onClick={handleRejectFollow}
          >
            Reject
          </Button>
        </Box>
      );
    }

    return (
      <Button
        variant={user.isFollowing ? "outlined" : "contained"}
        onClick={user.isFollowing ? handleUnfollow : handleFollow}
      >
        {user.isFollowing ? 'Unfollow' : 'Follow'}
      </Button>
    );
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography
              variant="h6"
              sx={{ cursor: 'pointer' }}
              onClick={() => navigate(`/profile/${user.username}`)}
            >
              {user.username}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {user.bio}
            </Typography>
          </Box>
          {getFollowButton()}
        </Box>
      </CardContent>
    </Card>
  );
};

export default UserCard; 