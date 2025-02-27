import React, { useState } from 'react';
import { 
  Container, 
  Box, 
  TextField, 
  Button, 
  Typography,
  Switch,
  FormControlLabel,
  Paper,
  Tabs,
  Tab
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../contexts/NotificationContext';
import api from '../services/api';
import Markdown from 'markdown-to-jsx';
import DOMPurify from 'dompurify';

const CreatePost = () => {
  const navigate = useNavigate();
  const { showNotification } = useNotification();
  const [formData, setFormData] = useState({
    content: '',
    isPrivate: false
  });
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.content.trim()) {
      showNotification('Post content cannot be empty', 'error');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/posts', {
        content: formData.content,
        private: formData.isPrivate
      });
      showNotification('Post created successfully', 'success');
      navigate('/');
    } catch (error) {
      showNotification(error.response?.data?.message || 'Failed to create post', 'error');
    } finally {
      setLoading(false);
    }
  };

  const options = {
    overrides: {
      h1: { component: Typography, props: { variant: 'h4', gutterBottom: true } },
      h2: { component: Typography, props: { variant: 'h5', gutterBottom: true } },
      h3: { component: Typography, props: { variant: 'h6', gutterBottom: true } },
      p: { component: Typography, props: { paragraph: true } },
      a: { component: 'a', props: { target: '_blank', rel: 'noopener noreferrer' } },
    },
    forceBlock: true,
    forceWrapper: true,
    wrapper: 'div',
    preprocessMarkdown: (markdown) => {
      return DOMPurify.sanitize(markdown, {
        ALLOWED_TAGS: [
          'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'img',
          'strong', 'em', 'del', 'blockquote', 'ul', 'ol', 'li',
          'code', 'pre', 'hr', 'br', 'div', 'span', 'table',
          'thead', 'tbody', 'tr', 'th', 'td'
        ],
        ALLOWED_ATTR: [
          'href', 'src', 'alt', 'title', 'class', 'target', 'rel',
          'style'
        ],
        ALLOWED_STYLES: {
          '*': ['color', 'background-color', 'text-align']
        }
      });
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" component="h1" gutterBottom>
            Create Post
          </Typography>
          <Tabs value={tab} onChange={(e, newValue) => setTab(newValue)} sx={{ mb: 2 }}>
            <Tab label="Write" />
            <Tab label="Preview" />
          </Tabs>
          <Box component="form" onSubmit={handleSubmit}>
            {tab === 0 ? (
              <TextField
                fullWidth
                multiline
                rows={8}
                label="What's on your mind? (Supports Markdown)"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                margin="normal"
                required
                disabled={loading}
              />
            ) : (
              <Box sx={{ 
                minHeight: '200px', 
                p: 2, 
                border: 1, 
                borderColor: 'grey.300',
                borderRadius: 1,
                '& a': { color: 'primary.main' },
                '& img': { maxWidth: '100%', height: 'auto' },
                '& pre': { 
                  bgcolor: 'grey.100', 
                  p: 2, 
                  borderRadius: 1,
                  overflow: 'auto'
                },
                '& code': { 
                  bgcolor: 'grey.100', 
                  p: 0.5, 
                  borderRadius: 0.5 
                }
              }}>
                <Markdown options={options}>
                  {formData.content}
                </Markdown>
              </Box>
            )}
            <FormControlLabel
              control={
                <Switch
                  checked={formData.isPrivate}
                  onChange={(e) => setFormData({ ...formData, isPrivate: e.target.checked })}
                  disabled={loading}
                />
              }
              label="Private Post"
            />
            <Box sx={{ mt: 2 }}>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                disabled={loading}
              >
                {loading ? 'Creating...' : 'Create Post'}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default CreatePost; 