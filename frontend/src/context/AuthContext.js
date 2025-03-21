import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import { 
  login as apiLogin, 
  register as apiRegister, 
  getUserProfile as apiGetUserProfile,
  updateProfile as apiUpdateProfile,
  updatePassword as apiUpdatePassword 
} from '../services/authService';

const AuthContext = createContext();

// Custom hook for using the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to fetch user profile from backend - wrapped in useCallback to prevent infinite loops
  const fetchUserProfile = useCallback(async (userId) => {
    try {
      setLoading(true);
      const userData = await apiGetUserProfile(userId);
      
      if (userData) {
        // Update user with data from backend - don't reference currentUser here
        setCurrentUser(prevUser => {
          // Use functional update pattern to avoid dependency on currentUser
          const updatedUser = {
            ...prevUser,
            firstName: userData.firstName || prevUser?.firstName || '',
            lastName: userData.lastName || prevUser?.lastName || '',
            email: userData.email || prevUser?.email || '',
            phone: userData.phone || prevUser?.phone || '',
            // Add any other fields from backend response
          };
          
          localStorage.setItem('user', JSON.stringify(updatedUser));
          return updatedUser;
        });
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
      setError('Failed to fetch user profile data');
    } finally {
      setLoading(false);
    }
  }, []); // Remove currentUser from dependencies

  // Initial load effect
  useEffect(() => {
    const initializeUser = () => {
      // Check if user is stored in localStorage on initial load
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const parsedUser = JSON.parse(storedUser);
        setCurrentUser(parsedUser);
        
        // Only fetch the profile if we have a user ID and haven't already fetched it
        if (parsedUser.id) {
          // Use a ref to track if this is the first load to prevent repeated calls
          const controller = new AbortController();
          fetchUserProfile(parsedUser.id);
          
          // Clean up function to abort any pending requests
          return () => controller.abort();
        }
      }
      setLoading(false);
    };
    
    initializeUser();
    
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Explicitly include fetchUserProfile in the dependencies

  const login = async (username, password) => {
    try {
      setError(null);
      setLoading(true);
      const response = await apiLogin(username, password);
      
      if (response.success) {
        // Get any temporary user data stored during registration
        let tempUserData = {};
        const storedTempData = sessionStorage.getItem('tempUserData');
        if (storedTempData) {
          tempUserData = JSON.parse(storedTempData);
          // Clear the temporary data
          sessionStorage.removeItem('tempUserData');
        }
        
        // Create a user object with relevant data
        const user = {
          id: response.user_id,
          username: response.username,
          firstName: response.firstName || tempUserData.firstName || '',
          lastName: response.lastName || tempUserData.lastName || '',
          email: response.email || tempUserData.email || '',
          phone: response.phone || '',
          // Add other user properties as needed
        };
        
        // Save user to state and localStorage
        setCurrentUser(user);
        localStorage.setItem('user', JSON.stringify(user));
        return { success: true };
      } else {
        setError(response.message || 'Login failed');
        return { success: false, message: response.message };
      }
    } catch (error) {
      const message = error.response?.data?.message || 'An error occurred during login';
      setError(message);
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      setLoading(true);
      const response = await apiRegister(userData);
      
      if (response.success) {
        // When registering, we already have the user's first and last name
        // Store them in a temporary variable to be added to the user object during login
        const { firstName, lastName, email } = userData;
        const tempUserData = { firstName, lastName, email };
        sessionStorage.setItem('tempUserData', JSON.stringify(tempUserData));
        
        // Login the user after successful registration
        return login(userData.username, userData.password);
      } else {
        setError(response.message || 'Registration failed');
        return { success: false, message: response.message };
      }
    } catch (error) {
      const message = error.response?.data?.message || 'An error occurred during registration';
      setError(message);
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('user');
  };

  const updateUserProfile = async (profileData) => {
    try {
      setError(null);
      setLoading(true);
      
      if (!currentUser || !currentUser.id) {
        throw new Error('User not logged in');
      }
      
      // Call the API to update profile
      const response = await apiUpdateProfile(currentUser.id, profileData);
      
      if (response && response.success) {
        // Use functional update to avoid dependency on currentUser
        setCurrentUser(prevUser => {
          const updatedUser = {
            ...prevUser,
            ...profileData
          };
          localStorage.setItem('user', JSON.stringify(updatedUser));
          return updatedUser;
        });
        return { success: true };
      } else {
        throw new Error(response.message || 'Failed to update profile');
      }
    } catch (error) {
      const message = error.response?.data?.message || error.message || 'Failed to update profile';
      setError(message);
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const updateUserPassword = async (currentPassword, newPassword) => {
    try {
      setError(null);
      setLoading(true);
      
      if (!currentUser || !currentUser.id) {
        throw new Error('User not logged in');
      }
      
      // Call the API to update password
      const response = await apiUpdatePassword(currentUser.id, currentPassword, newPassword);
      
      if (response && response.success) {
        return { success: true };
      } else {
        throw new Error(response.message || 'Failed to update password');
      }
    } catch (error) {
      const message = error.response?.data?.message || error.message || 'Failed to update password';
      setError(message);
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout,
    updateUserProfile,
    updateUserPassword,
    fetchUserProfile
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext; 