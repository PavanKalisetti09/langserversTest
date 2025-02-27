import React from 'react';
import { Card, CardContent, CardHeader, Typography, IconButton, Box, Link } from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Link as RouterLink } from 'react-router-dom';
import { formatDistance } from 'date-fns';
import Markdown from 'markdown-to-jsx';
import DOMPurify from 'dompurify';

const Post = ({ post, onDelete }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const isAuthor = user?.id === post.user.id;

  const handleUserClick = () => {
    navigate(`/profile/${post.user.username}`);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      onDelete(post.id);
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
    <Card sx={{ mb: 2 }}>
      <CardHeader
        title={
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Link
              component={RouterLink}
              to={`/profile/${post.user.username}`}
              color="inherit"
              underline="hover"
            >
              <Typography variant="h6">{post.user.username}</Typography>
            </Link>
            <Link
              component={RouterLink}
              to={`/post/${post.id}`}
              color="textSecondary"
              underline="hover"
            >
              <Typography variant="body2">
                {formatDistance(new Date(post.createdAt), new Date(), { addSuffix: true })}
              </Typography>
            </Link>
          </Box>
        }
        subheader={new Date(post.createdAt).toLocaleDateString()}
        action={
          isAuthor && (
            <IconButton onClick={handleDelete} size="small">
              <DeleteIcon />
            </IconButton>
          )
        }
      />
      <CardContent>
        <Box sx={{ 
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
          },
          '& blockquote': {
            borderLeft: 4,
            borderColor: 'grey.300',
            pl: 2,
            my: 2,
            color: 'text.secondary'
          },
          '& table': {
            borderCollapse: 'collapse',
            width: '100%',
            '& th, & td': {
              border: 1,
              borderColor: 'grey.300',
              p: 1
            }
          }
        }}>
          <Markdown options={options}>
            {post.content}
          </Markdown>
        </Box>
        {post.isPrivate && (
          <Typography variant="caption" color="text.secondary">
            Private post
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default Post; 