import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Box, CircularProgress, Typography } from '@mui/material';
import Post from '../components/Post';
import api from '../services/api';
import { useNotification } from '../contexts/NotificationContext';

const PostPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showNotification } = useNotification();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPost();
  }, [id]);

  const fetchPost = async () => {
    try {
      const response = await api.get(`/api/posts/${id}`);
      setPost(response.data);
    } catch (error) {
      showNotification(error.response?.data?.message || 'Failed to load post', 'error');
      navigate('/');
    } finally {
      setLoading(false);
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
      <Box mt={4}>
        {post ? (
          <Post post={post} />
        ) : (
          <Typography>Post not found</Typography>
        )}
      </Box>
    </Container>
  );
};

export default PostPage; 