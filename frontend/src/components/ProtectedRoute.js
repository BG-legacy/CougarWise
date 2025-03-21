import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import { CircularProgress, Box } from '@mui/material';

/**
 * ProtectedRoute component to protect routes that require authentication
 * If user is not authenticated, redirect to login page
 * If authentication is still loading, show a loading indicator
 */
const ProtectedRoute = ({ children }) => {
  const { currentUser, loading } = useContext(AuthContext);

  // Show loading indicator while auth state is being determined
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // Redirect to login if not authenticated
  if (!currentUser) {
    return <Navigate to="/login" />;
  }

  // Render children if authenticated
  return children;
};

export default ProtectedRoute; 