import React, { useState, useEffect } from 'react';
import { Typography, Alert, CircularProgress, Box } from '@mui/material';
import Post from './Post';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';

const PostList = () => {
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
      showNotification(error.response?.data?.message || 'Failed to fetch posts', 'error');
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
      showNotification(error.response?.data?.message || 'Failed to delete post', 'error');
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
    <>
      <Typography variant="h4" gutterBottom>
        {user ? 'Your Feed' : 'Public Posts'}
      </Typography>
      {posts.map(post => (
        <Post
          key={post.id}
          post={post}
          onDelete={handleDeletePost}
        />
      ))}
      {posts.length === 0 && (
        <Alert severity="info">
          No posts to display
        </Alert>
      )}
    </>
  );
};

export default PostList; 