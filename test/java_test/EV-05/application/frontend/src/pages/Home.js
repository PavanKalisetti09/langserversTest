import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, CircularProgress, Alert } from '@mui/material';
import Post from '../components/Post';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import PostList from '../components/PostList';
import FollowRequests from '../components/FollowRequests';

const Home = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { showNotification } = useNotification();

  useEffect(() => {
    fetchPosts();
  }, [user]);

  const fetchPosts = async () => {
    try {
      const response = await api.get(user ? '/api/posts' : '/api/posts/public');
      setPosts(response.data);
    } catch (error) {
      showNotification(error.displayMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePost = async (postId) => {
    try {
      await api.delete(`/api/posts/${postId}`);
      setPosts(posts.filter(post => post.id !== postId));
      showNotification('Post deleted successfully', 'success');
    } catch (error) {
      showNotification(error.displayMessage, 'error');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" mt={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <FollowRequests />
        <PostList />
      </Box>
    </Container>
  );
};

export default Home; 