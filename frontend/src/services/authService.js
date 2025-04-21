import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Login user
 * @param {string} username - User's username
 * @param {string} password - User's password
 * @returns {Promise<Object>} - Server response object
 */
export const login = async (username, password) => {
  try {
    const response = await api.post('/api/auth/login', { username, password });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Register new user
 * @param {Object} userData - User registration data
 * @param {string} userData.username - Username
 * @param {string} userData.email - Email address
 * @param {string} userData.password - Password
 * @param {string} userData.name - Full name
 * @returns {Promise<Object>} - Server response object
 */
export const register = async (userData) => {
  try {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get current user profile
 * @param {string} userId - User ID
 * @returns {Promise<Object>} - User profile data
 */
export const getUserProfile = async (userId) => {
  try {
    const response = await api.get(`/api/users/${userId}/profile`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};

/**
 * Update user profile
 * @param {string} userId - User ID
 * @param {Object} profileData - Updated profile data
 * @returns {Promise<Object>} - Updated user profile
 */
export const updateProfile = async (userId, profileData) => {
  try {
    const response = await api.put(`/api/users/${userId}/profile`, profileData);
    return response.data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

/**
 * Update user password
 * @param {string} userId - User ID
 * @param {string} currentPassword - Current password
 * @param {string} newPassword - New password
 * @returns {Promise<Object>} - Response data
 */
export const updatePassword = async (userId, currentPassword, newPassword) => {
  try {
    const response = await api.put(`/api/users/${userId}/password`, { 
      currentPassword, 
      newPassword 
    });
    return response.data;
  } catch (error) {
    console.error('Error updating password:', error);
    throw error;
  }
};

const authService = {
  login,
  register,
  getUserProfile,
  updateProfile,
  updatePassword
};

export default authService; 