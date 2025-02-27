import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Box, Typography, Button, Grid, Tabs, Tab, CircularProgress, Alert } from '@mui/material';
import Post from '../components/Post';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';

const Profile = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const { showNotification } = useNotification();
  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState(0);
  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);

  useEffect(() => {
    fetchProfile();
  }, [username]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const [profileRes, postsRes, followersRes, followingRes] = await Promise.all([
        api.get(`/api/users/${username}`),
        api.get(`/api/users/${username}/posts`),
        api.get(`/api/users/${username}/followers`),
        api.get(`/api/users/${username}/following`)
      ]);
      setProfile(profileRes.data);
      setPosts(postsRes.data);
      setFollowers(followersRes.data);
      setFollowing(followingRes.data);
    } catch (error) {
      setError(error.displayMessage);
      showNotification(error.displayMessage, 'error');
      if (error.response?.status === 404) {
        navigate('/');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async () => {
    try {
      await api.post(`/api/follow/${username}`);
      showNotification(`You are now following ${username}`, 'success');
      fetchProfile();
    } catch (error) {
      showNotification(error.displayMessage, 'error');
    }
  };

  const handleUnfollow = async () => {
    try {
      await api.delete(`/api/follow/${username}`);
      showNotification(`You have unfollowed ${username}`, 'success');
      fetchProfile();
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

  if (error) {
    return (
      <Container maxWidth="md">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h4">{profile.username}</Typography>
              {currentUser && currentUser.username !== username && (
                <Button
                  variant="contained"
                  onClick={profile.isFollowing ? handleUnfollow : handleFollow}
                >
                  {profile.isFollowing ? 'Unfollow' : 'Follow'}
                </Button>
              )}
            </Box>
            <Typography variant="body1" sx={{ mt: 2 }}>
              {profile.bio}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                {followers.length} followers · {following.length} following
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Tabs value={tab} onChange={(e, newValue) => setTab(newValue)}>
              <Tab label={`Posts (${posts.length})`} />
              <Tab label={`Followers (${followers.length})`} />
              <Tab label={`Following (${following.length})`} />
            </Tabs>
            <Box sx={{ mt: 2 }}>
              {tab === 0 && (
                posts.length > 0 ? (
                  posts.map(post => (
                    <Post key={post.id} post={post} />
                  ))
                ) : (
                  <Alert severity="info">No posts yet</Alert>
                )
              )}
              {tab === 1 && (
                followers.length > 0 ? (
                  followers.map(follower => (
                    <Typography
                      key={follower.id}
                      variant="body1"
                      sx={{ cursor: 'pointer', mb: 1 }}
                      onClick={() => navigate(`/profile/${follower.username}`)}
                    >
                      {follower.username}
                    </Typography>
                  ))
                ) : (
                  <Alert severity="info">No followers yet</Alert>
                )
              )}
              {tab === 2 && (
                following.length > 0 ? (
                  following.map(follow => (
                    <Typography
                      key={follow.id}
                      variant="body1"
                      sx={{ cursor: 'pointer', mb: 1 }}
                      onClick={() => navigate(`/profile/${follow.username}`)}
                    >
                      {follow.username}
                    </Typography>
                  ))
                ) : (
                  <Alert severity="info">Not following anyone yet</Alert>
                )
              )}
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Profile; 