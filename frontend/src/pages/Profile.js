import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  TextField,
  Button,
  Avatar,
  Divider,
  Switch,
  FormControlLabel,
  Snackbar,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import LockIcon from '@mui/icons-material/Lock';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const { currentUser, updateUserProfile, updateUserPassword, logout } = useAuth();
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', severity: 'success' });
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [openPasswordDialog, setOpenPasswordDialog] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    avatar: ''
  });
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    darkMode: false,
    budgetAlerts: true
  });

  // Initialize the fetch tracking ref outside the effect
  const profileFetchedRef = useRef(false);

  useEffect(() => {
    // We no longer need to fetch the profile here as it's handled in AuthContext
    // Just update the ref to prevent future fetches
    profileFetchedRef.current = true;
  }, []); // Empty dependency array - this only runs once on mount

  useEffect(() => {
    if (currentUser) {
      setProfileData({
        firstName: currentUser.firstName || '',
        lastName: currentUser.lastName || '',
        email: currentUser.email || '',
        phone: currentUser.phone || '',
        avatar: currentUser.avatar || ''
      });
    }
  }, [currentUser]);

  const handleProfileInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData({
      ...profileData,
      [name]: value
    });
  };

  const handlePasswordInputChange = (e) => {
    const { name, value } = e.target;
    setPasswordData({
      ...passwordData,
      [name]: value
    });
  };

  const handlePreferenceChange = (e) => {
    const { name, checked } = e.target;
    setPreferences({
      ...preferences,
      [name]: checked
    });
  };

  const toggleEditMode = () => {
    setEditMode(!editMode);
    if (editMode) {
      // Reset form when cancelling edit
      setProfileData({
        firstName: currentUser.firstName || '',
        lastName: currentUser.lastName || '',
        email: currentUser.email || '',
        phone: currentUser.phone || '',
        avatar: currentUser.avatar || ''
      });
    }
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    try {
      await updateUserProfile(profileData);
      setEditMode(false);
      showMessage('Profile updated successfully', 'success');
    } catch (error) {
      showMessage(error.message || 'Failed to update profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreferences = async () => {
    setLoading(true);
    try {
      // Here you would call an API to save user preferences
      // For now, just simulate success
      await new Promise(resolve => setTimeout(resolve, 500));
      showMessage('Preferences saved successfully', 'success');
    } catch (error) {
      showMessage('Failed to save preferences', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenPasswordDialog = () => {
    setOpenPasswordDialog(true);
  };

  const handleClosePasswordDialog = () => {
    setOpenPasswordDialog(false);
    setPasswordData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
  };

  const handleUpdatePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      showMessage('New passwords do not match', 'error');
      return;
    }

    setLoading(true);
    try {
      await updateUserPassword(
        passwordData.currentPassword,
        passwordData.newPassword
      );
      handleClosePasswordDialog();
      showMessage('Password updated successfully', 'success');
    } catch (error) {
      showMessage(error.message || 'Failed to update password', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      // Redirect handled by AuthContext/ProtectedRoute
    } catch (error) {
      showMessage('Failed to log out', 'error');
    }
  };

  const showMessage = (text, severity) => {
    setMessage({ text, severity });
    setOpenSnackbar(true);
  };

  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Profile
        </Typography>

        <Grid container spacing={4}>
          {/* Profile Information */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Profile Information
                </Typography>
                <Button 
                  startIcon={editMode ? null : <EditIcon />} 
                  onClick={toggleEditMode}
                  color={editMode ? "error" : "primary"}
                >
                  {editMode ? "Cancel" : "Edit"}
                </Button>
              </Box>
              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    name="firstName"
                    value={profileData.firstName}
                    onChange={handleProfileInputChange}
                    disabled={!editMode}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    name="lastName"
                    value={profileData.lastName}
                    onChange={handleProfileInputChange}
                    disabled={!editMode}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    name="email"
                    type="email"
                    value={profileData.email}
                    onChange={handleProfileInputChange}
                    disabled={!editMode}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    name="phone"
                    value={profileData.phone}
                    onChange={handleProfileInputChange}
                    disabled={!editMode}
                    margin="normal"
                  />
                </Grid>
              </Grid>

              {editMode && (
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    variant="contained" 
                    onClick={handleSaveProfile} 
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : "Save Changes"}
                  </Button>
                </Box>
              )}
            </Paper>

            {/* Security Settings */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Security
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box>
                  <Typography variant="subtitle1">
                    Password
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Last changed: 30 days ago
                  </Typography>
                </Box>
                <Button 
                  startIcon={<LockIcon />} 
                  onClick={handleOpenPasswordDialog}
                >
                  Change
                </Button>
              </Box>

              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Two-Factor Authentication
                </Typography>
                <FormControlLabel
                  control={<Switch color="primary" />}
                  label="Enable two-factor authentication"
                />
              </Box>
            </Paper>

            {/* Preferences */}
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Preferences
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Notifications
                </Typography>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={preferences.emailNotifications} 
                      onChange={handlePreferenceChange} 
                      name="emailNotifications" 
                      color="primary" 
                    />
                  }
                  label="Email notifications"
                />
                <FormControlLabel
                  control={
                    <Switch 
                      checked={preferences.budgetAlerts} 
                      onChange={handlePreferenceChange} 
                      name="budgetAlerts" 
                      color="primary" 
                    />
                  }
                  label="Budget alerts"
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Appearance
                </Typography>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={preferences.darkMode} 
                      onChange={handlePreferenceChange} 
                      name="darkMode" 
                      color="primary" 
                    />
                  }
                  label="Dark mode"
                />
              </Box>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                <Button 
                  variant="contained" 
                  onClick={handleSavePreferences} 
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : "Save Preferences"}
                </Button>
              </Box>
            </Paper>
          </Grid>

          {/* Profile Sidebar */}
          <Grid item xs={12} md={4}>
            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Box sx={{ position: 'relative' }}>
                  <Avatar 
                    src={profileData.avatar || ""}
                    alt={`${profileData.firstName} ${profileData.lastName}`}
                    sx={{ width: 120, height: 120, mb: 2 }}
                  />
                  <IconButton 
                    sx={{ 
                      position: 'absolute', 
                      bottom: 0, 
                      right: 0, 
                      backgroundColor: 'primary.main',
                      color: 'white',
                      '&:hover': {
                        backgroundColor: 'primary.dark'
                      }
                    }}
                    size="small"
                  >
                    <PhotoCameraIcon fontSize="small" />
                  </IconButton>
                </Box>
                <Typography variant="h6" align="center">
                  {profileData.firstName} {profileData.lastName}
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center" gutterBottom>
                  {profileData.email}
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center">
                  Member since: January 2023
                </Typography>
              </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>
                  Account Actions
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Button 
                  fullWidth 
                  variant="outlined" 
                  color="error" 
                  onClick={handleLogout}
                  sx={{ mb: 1 }}
                >
                  Log Out
                </Button>
                <Button 
                  fullWidth 
                  variant="outlined" 
                  color="error"
                >
                  Delete Account
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>
                  Connected Accounts
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body2">
                    Google
                  </Typography>
                  <Button size="small" variant="outlined">
                    Connect
                  </Button>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">
                    Apple
                  </Typography>
                  <Button size="small" variant="outlined">
                    Connect
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Password Change Dialog */}
      <Dialog open={openPasswordDialog} onClose={handleClosePasswordDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <TextField
            margin="normal"
            label="Current Password"
            name="currentPassword"
            type="password"
            value={passwordData.currentPassword}
            onChange={handlePasswordInputChange}
            fullWidth
            required
          />
          <TextField
            margin="normal"
            label="New Password"
            name="newPassword"
            type="password"
            value={passwordData.newPassword}
            onChange={handlePasswordInputChange}
            fullWidth
            required
          />
          <TextField
            margin="normal"
            label="Confirm New Password"
            name="confirmPassword"
            type="password"
            value={passwordData.confirmPassword}
            onChange={handlePasswordInputChange}
            fullWidth
            required
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePasswordDialog}>Cancel</Button>
          <Button 
            onClick={handleUpdatePassword} 
            variant="contained" 
            disabled={loading || !passwordData.currentPassword || !passwordData.newPassword || !passwordData.confirmPassword}
          >
            {loading ? <CircularProgress size={24} /> : "Update Password"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={message.severity} sx={{ width: '100%' }}>
          {message.text}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Profile; 