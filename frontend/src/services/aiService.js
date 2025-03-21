import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Send a query to the AI assistant
 * @param {Object} queryData - Query data
 * @param {string} queryData.query - User's question
 * @param {Object} [queryData.user_context] - User context information
 * @param {string} [queryData.user_id] - User ID for retrieving user-specific data
 * @returns {Promise<Object>} - AI response
 */
export const sendQuery = async (queryData) => {
  try {
    const response = await api.post('/ai/query', queryData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get spending advice based on user profile
 * @param {Object} userProfile - User profile information
 * @param {string} userProfile.year_in_school - Year in school
 * @param {string} userProfile.major - Student's major
 * @param {number} userProfile.monthly_income - Monthly income
 * @param {number} userProfile.financial_aid - Financial aid amount
 * @param {Object} [userProfile.financial_data] - Additional financial data from the app
 * @param {string} [userProfile.user_id] - User ID for retrieving user-specific data
 * @returns {Promise<Object>} - Spending advice
 */
export const getSpendingAdvice = async (userProfile) => {
  try {
    const response = await api.post('/ai/spending-advice', userProfile);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get personalized budget template based on user profile and financial data
 * @param {Object} userProfile - User profile information
 * @param {string} userProfile.year_in_school - Year in school
 * @param {string} userProfile.major - Student's major
 * @param {string} [userProfile.user_id] - User ID for retrieving user-specific data
 * @param {Object} financialData - User's current financial data
 * @returns {Promise<Object>} - Budget template
 */
export const getBudgetTemplate = async (userProfile, financialData) => {
  try {
    const requestData = {
      ...userProfile,
      financial_data: financialData,
      user_id: userProfile.user_id
    };
    
    const response = await api.post('/ai/budget-template', requestData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Analyze financial goals and provide recommendations
 * @param {Object} goalsData - Goals and financial context
 * @param {Array} goalsData.goals - List of financial goals
 * @param {Object} goalsData.financial_data - User's financial data
 * @param {string} [goalsData.user_id] - User ID for retrieving user-specific data
 * @returns {Promise<Object>} - Goals analysis
 */
export const analyzeFinancialGoals = async (goalsData) => {
  try {
    const response = await api.post('/ai/analyze-goals', goalsData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default {
  sendQuery,
  getSpendingAdvice,
  getBudgetTemplate,
  analyzeFinancialGoals
}; 