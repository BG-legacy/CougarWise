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
 * Get all budgets for a user
 * @param {string} userId - User ID
 * @returns {Promise<Array>} - Array of budgets
 */
export const getUserBudgets = async (userId) => {
  try {
    const response = await api.get(`/api/budgets/user/${userId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get all budgets (requires user to be authenticated)
 * @returns {Promise<Array>} - Array of budgets for the current user
 */
export const getBudgets = async () => {
  try {
    // Get user ID from localStorage
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || !user.id) {
      throw new Error('User not authenticated');
    }
    // Use the existing getUserBudgets method
    return await getUserBudgets(user.id);
  } catch (error) {
    console.error('Error getting budgets:', error);
    // Format error message for display
    if (error.response) {
      throw new Error(error.response.data?.detail || 'Failed to get budgets');
    } else if (error.request) {
      throw new Error('No response from server. Please check your connection.');
    } else {
      throw error;
    }
  }
};

/**
 * Create a new budget
 * @param {Object} budgetData - Budget data
 * @param {string} budgetData.category - Budget category
 * @param {number} budgetData.amount - Budget amount
 * @param {string} budgetData.period - Budget period (monthly, weekly)
 * @returns {Promise<Object>} - Created budget
 */
export const createBudget = async (budgetData) => {
  try {
    // Get user ID from localStorage
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || !user.id) {
      throw new Error('User not authenticated');
    }
    
    // Add user_id to the budgetData
    const budgetWithUserId = {
      ...budgetData,
      user_id: user.id
    };
    
    const response = await api.post('/api/budgets', budgetWithUserId);
    return response.data;
  } catch (error) {
    console.error('Error creating budget:', error);
    // Format error message for display
    if (error.response) {
      throw new Error(error.response.data?.detail || 'Failed to create budget');
    } else if (error.request) {
      throw new Error('No response from server. Please check your connection.');
    } else {
      throw error;
    }
  }
};

/**
 * Update an existing budget
 * @param {string} budgetId - Budget ID
 * @param {Object} budgetData - Budget data to update
 * @returns {Promise<Object>} - Updated budget
 */
export const updateBudget = async (budgetId, budgetData) => {
  try {
    // Get user ID from localStorage
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || !user.id) {
      throw new Error('User not authenticated');
    }
    
    // Add user_id to the budgetData
    const budgetWithUserId = {
      ...budgetData,
      user_id: user.id
    };
    
    const response = await api.put(`/api/budgets/${budgetId}`, budgetWithUserId);
    return response.data;
  } catch (error) {
    console.error('Error updating budget:', error);
    // Format error message for display
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      throw new Error(error.response.data?.detail || 'Failed to update budget');
    } else if (error.request) {
      // The request was made but no response was received
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Something happened in setting up the request that triggered an Error
      throw error;
    }
  }
};

/**
 * Delete a budget
 * @param {string} budgetId - Budget ID
 * @returns {Promise<Object>} - Deletion result
 */
export const deleteBudget = async (budgetId) => {
  try {
    const response = await api.delete(`/api/budgets/${budgetId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting budget:', error);
    // Format error message for display
    if (error.response) {
      throw new Error(error.response.data?.detail || 'Failed to delete budget');
    } else if (error.request) {
      throw new Error('No response from server. Please check your connection.');
    } else {
      throw error;
    }
  }
};

/**
 * Get a budget template based on user profile
 * @param {Object} userProfile - User profile information
 * @param {string} userProfile.year_in_school - Year in school
 * @param {string} userProfile.major - Student's major
 * @param {number} userProfile.monthly_income - Monthly income
 * @param {number} userProfile.financial_aid - Financial aid amount
 * @returns {Promise<Object>} - Budget template
 */
export const getBudgetTemplate = async (userProfile) => {
  try {
    const response = await api.post('/ai/budget-template', userProfile);
    return response.data;
  } catch (error) {
    throw error;
  }
};

const budgetService = {
  getUserBudgets,
  getBudgets,
  createBudget,
  updateBudget,
  deleteBudget,
  getBudgetTemplate
};

export default budgetService; 