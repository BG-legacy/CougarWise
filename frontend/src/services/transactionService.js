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
 * Get all transactions for a user
 * @param {string} userId - User ID
 * @returns {Promise<Array>} - Array of transactions
 */
export const getUserTransactions = async (userId) => {
  try {
    const response = await api.get(`/api/transactions/user/${userId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get all transactions for the current user
 * @returns {Promise<Array>} - Array of transactions for the current user
 */
export const getTransactions = async () => {
  try {
    // Get user ID from localStorage
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || !user.id) {
      throw new Error('User not authenticated');
    }
    // Use the existing getUserTransactions method
    return await getUserTransactions(user.id);
  } catch (error) {
    console.error('Error getting transactions:', error);
    // Format error message for display
    if (error.response) {
      throw new Error(error.response.data?.detail || 'Failed to get transactions');
    } else if (error.request) {
      throw new Error('No response from server. Please check your connection.');
    } else {
      throw error;
    }
  }
};

/**
 * Create a new transaction
 * @param {Object} transactionData - Transaction data
 * @param {string} transactionData.user_id - User ID
 * @param {number} transactionData.amount - Transaction amount
 * @param {string} transactionData.category - Transaction category
 * @param {string} transactionData.description - Transaction description
 * @param {string} [transactionData.date] - Transaction date (optional)
 * @returns {Promise<Object>} - Created transaction
 */
export const createTransaction = async (transactionData) => {
  try {
    const response = await api.post('/api/transactions', transactionData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get spending analysis for a user
 * @param {string} userId - User ID
 * @param {string} [period='monthly'] - Analysis period (monthly, weekly, etc.)
 * @param {string} [startDate] - Start date for analysis
 * @param {string} [endDate] - End date for analysis
 * @returns {Promise<Object>} - Spending analysis data
 */
export const getSpendingAnalysis = async (userId, period = 'monthly', startDate = null, endDate = null) => {
  try {
    let url = `/api/analysis/spending/${userId}?period=${period}`;
    
    if (startDate) {
      url += `&start_date=${startDate}`;
    }
    
    if (endDate) {
      url += `&end_date=${endDate}`;
    }
    
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error getting spending analysis:', error);
    // Return a default structure instead of throwing the error
    return {
      total_spending: 0,
      category_breakdown: {},
      period: period,
      start_date: new Date().toISOString(),
      end_date: new Date().toISOString()
    };
  }
};

/**
 * Get spending insights for a user
 * @param {string} userId - User ID
 * @returns {Promise<Object>} - Spending insights data
 */
export const getSpendingInsights = async (userId) => {
  try {
    const response = await api.get(`/api/analysis/insights/${userId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

const transactionService = {
  getUserTransactions,
  getTransactions,
  createTransaction,
  getSpendingAnalysis,
  getSpendingInsights
};

export default transactionService; 