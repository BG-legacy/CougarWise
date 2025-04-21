import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      // Set auth header
      config.headers.Authorization = `Bearer ${JSON.stringify(user)}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Get all financial goals for the current user
 * @returns {Promise<Array>} - Array of financial goals
 */
export const getGoals = async () => {
  try {
    const response = await api.get('/api/goals');
    return response.data;
  } catch (error) {
    console.error('Error getting goals:', error);
    return [];
  }
};

/**
 * Create a new financial goal
 * @param {Object} goalData - Goal data
 * @param {string} goalData.name - Goal name
 * @param {string} goalData.category - Goal category
 * @param {number} goalData.targetAmount - Target amount
 * @param {number} goalData.currentAmount - Current amount
 * @param {Date} goalData.targetDate - Goal target date
 * @returns {Promise<Object>} - Created goal
 */
export const createGoal = async (goalData) => {
  try {
    const response = await api.post('/api/goals', goalData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Update a financial goal
 * @param {string} goalId - Goal ID
 * @param {Object} goalData - Updated goal data
 * @returns {Promise<Object>} - Updated goal
 */
export const updateGoal = async (goalId, goalData) => {
  try {
    const response = await api.put(`/api/goals/${goalId}`, goalData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Delete a financial goal
 * @param {string} goalId - Goal ID
 * @returns {Promise<Object>} - Delete result
 */
export const deleteGoal = async (goalId) => {
  try {
    const response = await api.delete(`/api/goals/${goalId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Analyze financial goals with AI assistant
 * @param {Object} goalsData - Goals data
 * @param {Array<string>} goalsData.goals - List of financial goals
 * @param {Object} goalsData.user_context - User context information
 * @returns {Promise<Object>} - Analysis response
 */
export const analyzeFinancialGoals = async (goalsData) => {
  try {
    const response = await api.post('/ai/analyze-goals', goalsData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get financial goals for a specific user
 * @param {string} userId - User ID
 * @returns {Promise<Array>} - Array of financial goals
 */
export const getUserGoals = async (userId) => {
  try {
    if (!userId) {
      console.warn('getUserGoals called without userId');
      return [];
    }
    
    const response = await api.get(`/api/goals/user/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting user goals:', error);
    
    // Log detailed error information
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      console.error('Error response headers:', error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received from server');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error message:', error.message);
    }
    
    // Return empty array instead of throwing
    return [];
  }
};

const goalService = {
  getGoals,
  createGoal,
  updateGoal,
  deleteGoal,
  analyzeFinancialGoals,
  getUserGoals
};

export default goalService; 