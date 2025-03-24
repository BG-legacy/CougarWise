// Import React and hooks needed for context creation and management
import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
// Import authentication API service functions for interacting with the backend
import { 
  login as apiLogin, // API function to authenticate users
  register as apiRegister, // API function to create new users 
  getUserProfile as apiGetUserProfile, // API function to retrieve user profile data
  updateProfile as apiUpdateProfile, // API function to modify user profile
  updatePassword as apiUpdatePassword // API function to change user password
} from '../services/authService';

// Create a context for authentication data and functions
const AuthContext = createContext();

// Custom hook to easily access auth context from any component
export const useAuth = () => {
  // Get the context value
  const context = useContext(AuthContext);
  // Throw error if hook is used outside of AuthProvider
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  // Return the context so components can access auth data and functions
  return context;
};

// Provider component that wraps the application to provide auth context
export const AuthProvider = ({ children }) => {
  // State to store the authenticated user's data
  const [currentUser, setCurrentUser] = useState(null);
  // State to track loading status during async operations
  const [loading, setLoading] = useState(true);
  // State to store error messages from auth operations
  const [error, setError] = useState(null);

  // Function to fetch user profile data from the backend
  // useCallback prevents recreation of this function on each render
  const fetchUserProfile = useCallback(async (userId) => {
    try {
      // Set loading state to show progress indicators
      setLoading(true);
      // Call API to get user profile data
      const userData = await apiGetUserProfile(userId);
      
      if (userData) {
        // Update user state with data from backend
        // Using functional update pattern to avoid dependency on currentUser
        setCurrentUser(prevUser => {
          // Create updated user object with new data
          const updatedUser = {
            ...prevUser, // Keep existing user data
            firstName: userData.firstName || prevUser?.firstName || '',
            lastName: userData.lastName || prevUser?.lastName || '',
            email: userData.email || prevUser?.email || '', 
            phone: userData.phone || prevUser?.phone || '',
            // Additional fields would be added here
          };
          
          // Store updated user in localStorage for persistence across page reloads
          localStorage.setItem('user', JSON.stringify(updatedUser));
          // Return updated user object to update state
          return updatedUser;
        });
      }
    } catch (error) {
      // Log error for debugging
      console.error('Error fetching user profile:', error);
      // Set error state for UI error messages
      setError('Failed to fetch user profile data');
    } finally {
      // Set loading to false whether request succeeds or fails
      setLoading(false);
    }
  }, []); // Empty dependency array prevents recreation of function

  // Effect to initialize user on app load
  useEffect(() => {
    // Function to load user from localStorage and fetch latest data
    const initializeUser = () => {
      // Check if user is stored in localStorage (persisted from previous session)
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        // Parse the stored JSON user data
        const parsedUser = JSON.parse(storedUser);
        // Update current user state with stored data
        setCurrentUser(parsedUser);
        
        // If we have a user ID, fetch the latest profile data
        if (parsedUser.id) {
          // Create controller to handle request cancellation if component unmounts
          const controller = new AbortController();
          // Call function to fetch updated profile data
          fetchUserProfile(parsedUser.id);
          
          // Return cleanup function to prevent memory leaks
          return () => controller.abort();
        }
      }
      // If no stored user, set loading to false
      setLoading(false);
    };
    
    // Call initialization function
    initializeUser();
    
    // Disable ESLint warning about missing dependencies
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only on component mount

  // Function to authenticate a user with username and password
  const login = async (username, password) => {
    try {
      // Reset any previous errors
      setError(null);
      // Set loading state for UI indicators
      setLoading(true);
      // Call API login function with credentials
      const response = await apiLogin(username, password);
      
      if (response.success) {
        // Get any temporary user data stored during registration
        let tempUserData = {};
        // Check for temporary data in session storage
        const storedTempData = sessionStorage.getItem('tempUserData');
        if (storedTempData) {
          // Parse stored JSON data
          tempUserData = JSON.parse(storedTempData);
          // Clear temporary data after it's been used
          sessionStorage.removeItem('tempUserData');
        }
        
        // Create user object with data from API response and temp data
        const user = {
          id: response.user_id, // User ID from backend
          username: response.username, // Username from backend
          firstName: response.firstName || tempUserData.firstName || '', // Use backend data or temp data
          lastName: response.lastName || tempUserData.lastName || '', // Use backend data or temp data
          email: response.email || tempUserData.email || '', // Use backend data or temp data
          phone: response.phone || '', // Phone from backend or empty string
          // Additional user properties would be added here
        };
        
        // Update current user state with new user object
        setCurrentUser(user);
        // Save user to localStorage for persistence
        localStorage.setItem('user', JSON.stringify(user));
        // Return success object
        return { success: true };
      } else {
        // Set error state with message from API response
        setError(response.message || 'Login failed');
        // Return failure object with error message
        return { success: false, message: response.message };
      }
    } catch (error) {
      // Extract error message from API response or use default message
      const message = error.response?.data?.message || 'An error occurred during login';
      // Set error state for UI display
      setError(message);
      // Return failure object with error message
      return { success: false, message };
    } finally {
      // Set loading to false whether request succeeds or fails
      setLoading(false);
    }
  };

  // Function to register a new user
  const register = async (userData) => {
    try {
      // Reset any previous errors
      setError(null);
      // Set loading state for UI indicators
      setLoading(true);
      // Call API register function with user data
      const response = await apiRegister(userData);
      
      if (response.success) {
        // Extract user information to preserve between register and login
        const { firstName, lastName, email } = userData;
        // Store this data temporarily to be used during login
        const tempUserData = { firstName, lastName, email };
        // Save in session storage for use in login function
        sessionStorage.setItem('tempUserData', JSON.stringify(tempUserData));
        
        // Automatically log in the user after successful registration
        return login(userData.username, userData.password);
      } else {
        // Set error state with message from API response
        setError(response.message || 'Registration failed');
        // Return failure object with error message
        return { success: false, message: response.message };
      }
    } catch (error) {
      // Extract error message from API response or use default message
      const message = error.response?.data?.message || 'An error occurred during registration';
      // Set error state for UI display
      setError(message);
      // Return failure object with error message
      return { success: false, message };
    } finally {
      // Set loading to false whether request succeeds or fails
      setLoading(false);
    }
  };

  // Function to log out the current user
  const logout = () => {
    // Clear current user from state
    setCurrentUser(null);
    // Remove user from localStorage
    localStorage.removeItem('user');
    // Note: No backend call since we're using token-based auth
  };

  // Function to update the user's profile information
  const updateUserProfile = async (profileData) => {
    try {
      // Reset any previous errors
      setError(null);
      // Set loading state for UI indicators
      setLoading(true);
      
      // Verify user is logged in before proceeding
      if (!currentUser || !currentUser.id) {
        throw new Error('User not logged in');
      }
      
      // Call API to update profile with user ID and new data
      const response = await apiUpdateProfile(currentUser.id, profileData);
      
      if (response && response.success) {
        // Update user data in state with new profile information
        // Using functional update to avoid dependency on currentUser
        setCurrentUser(prevUser => {
          // Create updated user with new profile data
          const updatedUser = {
            ...prevUser, // Keep existing user data
            ...profileData // Override with new profile data
          };
          // Update localStorage with new user data
          localStorage.setItem('user', JSON.stringify(updatedUser));
          // Return updated user object to update state
          return updatedUser;
        });
        // Return success object
        return { success: true };
      } else {
        // Throw error if API response indicates failure
        throw new Error(response.message || 'Failed to update profile');
      }
    } catch (error) {
      // Extract error message from error object or API response
      const message = error.response?.data?.message || error.message || 'Failed to update profile';
      // Set error state for UI display
      setError(message);
      // Return failure object with error message
      return { success: false, message };
    } finally {
      // Set loading to false whether request succeeds or fails
      setLoading(false);
    }
  };

  // Function to update the user's password
  const updateUserPassword = async (currentPassword, newPassword) => {
    try {
      // Reset any previous errors
      setError(null);
      // Set loading state for UI indicators
      setLoading(true);
      
      // Verify user is logged in before proceeding
      if (!currentUser || !currentUser.id) {
        throw new Error('User not logged in');
      }
      
      // Call API to update password with user ID and password data
      const response = await apiUpdatePassword(currentUser.id, currentPassword, newPassword);
      
      if (response && response.success) {
        // Return success object - no need to update state for password change
        return { success: true };
      } else {
        // Throw error if API response indicates failure
        throw new Error(response.message || 'Failed to update password');
      }
    } catch (error) {
      // Extract error message from error object or API response
      const message = error.response?.data?.message || error.message || 'Failed to update password';
      // Set error state for UI display
      setError(message);
      // Return failure object with error message
      return { success: false, message };
    } finally {
      // Set loading to false whether request succeeds or fails
      setLoading(false);
    }
  };

  // Create object with all values and functions to be provided by context
  const value = {
    currentUser, // Current authenticated user data
    loading, // Loading state for async operations
    error, // Error messages
    login, // Function to authenticate user
    register, // Function to create new user
    logout, // Function to log out user
    updateUserProfile, // Function to update user profile
    updateUserPassword, // Function to update user password
    fetchUserProfile // Function to refresh user data
  };

  // Return provider component with context value, wrapping children
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Export the context for direct usage with useContext if needed
export default AuthContext;