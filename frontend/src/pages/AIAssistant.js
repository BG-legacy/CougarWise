import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  CircularProgress,
  Divider,
  Card,
  IconButton,
  InputAdornment,
  Grid
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import CalculateIcon from '@mui/icons-material/Calculate';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SavingsIcon from '@mui/icons-material/Savings';
import { styled } from '@mui/material/styles';
import transactionService from '../services/transactionService';
import budgetService from '../services/budgetService';
import goalService from '../services/goalService';
import aiService from '../services/aiService';
import { useAuth } from '../context/AuthContext'; // Import auth context
import authService from '../services/authService';

// Styled components
const MessageBubble = styled(Paper)(({ theme, sender }) => ({
  padding: theme.spacing(1.5),
  borderRadius: sender === 'user' ? '18px 18px 0 18px' : '18px 18px 18px 0',
  backgroundColor: sender === 'user' ? theme.palette.primary.main : theme.palette.grey[100],
  color: sender === 'user' ? theme.palette.primary.contrastText : theme.palette.text.primary,
  maxWidth: '80%',
  marginBottom: theme.spacing(1),
  wordBreak: 'break-word'
}));

const SuggestionCard = styled(Card)(({ theme }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(1),
  cursor: 'pointer',
  transition: 'transform 0.2s',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[3]
  }
}));

const AIAssistant = () => {
  const { currentUser } = useAuth(); // Get current user from auth context
  const [messages, setMessages] = useState([
    { 
      sender: 'assistant', 
      text: "Hi there! I'm your financial assistant. I'll use your profile information to provide personalized advice. Feel free to ask me anything about your finances."
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [financialData, setFinancialData] = useState({
    totalIncome: 0,
    totalExpenses: 0,
    topCategory: 'Food',
    topCategoryAmount: 0,
    goalProgress: 0,
    goalTimeRemaining: 0
  });
  const messagesEndRef = useRef(null);
  const [userProfile, setUserProfile] = useState({
    year_in_school: '',
    major: '',
    monthly_income: 0,
    financial_aid: 0
  });

  // Fetch user profile data when component mounts
  useEffect(() => {
    if (currentUser) {
      // Try to load user profile from auth context
      fetchUserProfile();
    }
  }, [currentUser]);

  useEffect(() => {
    fetchFinancialData();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check if we have financial data
    const hasFinancialData = financialData.totalIncome > 0 || financialData.totalExpenses > 0;
    
    // If no financial data and no profile data yet, show a message that we're loading profile data
    if (!hasFinancialData) {
      // Check if we also don't have user profile data
      const hasProfileData = userProfile.year_in_school && userProfile.major && userProfile.monthly_income > 0;
      
      if (!hasProfileData && currentUser && currentUser.userId) {
        setTimeout(() => {
          setMessages(prev => [
            ...prev,
            { 
              sender: 'assistant', 
              text: "I'll fetch your profile information from your account to provide personalized advice."
            }
          ]);
          // Try to fetch profile data
          fetchUserProfile();
        }, 1000);
      }
    }
  }, [financialData, userProfile, currentUser]);

  // Function to fetch user profile data from the database
  const fetchUserProfile = async () => {
    try {
      // Use currentUser from auth context to fetch profile data
      if (currentUser && currentUser.userId) {
        const profileData = await authService.getUserProfile(currentUser.userId);
        
        // Update the userProfile state with data from the database
        if (profileData) {
          setMessages(prev => [
            ...prev,
            { 
              sender: 'assistant', 
              text: `I've loaded your profile data. I can see you're a ${profileData.year_in_school || 'student'} studying ${profileData.major || 'at college'}. How can I help with your finances today?`
            }
          ]);
          
          setUserProfile({
            year_in_school: profileData.year_in_school || 'Sophomore',
            major: profileData.major || 'Computer Science',
            monthly_income: profileData.monthly_income || 1200,
            financial_aid: profileData.financial_aid || 5000
          });
          return true; // We successfully loaded profile data
        }
      }
      return false; // We couldn't load profile data
    } catch (error) {
      console.error('Error fetching user profile:', error);
      // Use default values if profile fetch fails
      setUserProfile({
        year_in_school: 'Sophomore',
        major: 'Computer Science',
        monthly_income: 1200,
        financial_aid: 5000
      });
      return false;
    }
  };

  const fetchFinancialData = async () => {
    try {
      // Fetch transactions, budgets, and goals data in parallel for efficiency
      const [transactions, budgets, goals] = await Promise.all([
        transactionService.getTransactions(),
        budgetService.getBudgets(),
        goalService.getGoals()
      ]);

      // Calculate financial metrics
      // Income calculations
      const income = transactions
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
      
      // Expense calculations
      const expenses = transactions
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);
      
      // Calculate monthly savings
      const monthlySavings = income - expenses;
      const savingsRate = income > 0 ? (monthlySavings / income) * 100 : 0;
      
      // Find top spending categories
      const categorySpendings = transactions
        .filter(t => t.type === 'expense')
        .reduce((acc, t) => {
          const category = t.category || 'Uncategorized';
          if (!acc[category]) acc[category] = 0;
          acc[category] += t.amount;
          return acc;
        }, {});
      
      // Sort categories by spending amount
      const sortedCategories = Object.entries(categorySpendings)
        .sort((a, b) => b[1] - a[1]);
      
      // Get top 3 categories
      const topCategories = sortedCategories.slice(0, 3).map(([category, amount]) => ({
        category,
        amount,
        percentage: expenses > 0 ? (amount / expenses) * 100 : 0
      }));
      
      // Default if no categories found
      const topCategoryEntry = sortedCategories.length > 0 
        ? sortedCategories[0] 
        : ['Uncategorized', 0];
      
      // Budget utilization - compare spending against budgets
      const budgetUtilization = budgets.map(budget => {
        const spent = categorySpendings[budget.category] || 0;
        const percentage = budget.amount > 0 ? (spent / budget.amount) * 100 : 0;
        return {
          category: budget.category,
          budgeted: budget.amount,
          spent,
          percentage,
          remaining: budget.amount - spent
        };
      });
      
      // Calculate overall budget status
      const totalBudgeted = budgets.reduce((sum, b) => sum + b.amount, 0);
      const budgetStatus = totalBudgeted > 0 
        ? { 
            totalBudgeted,
            totalSpent: expenses,
            percentage: (expenses / totalBudgeted) * 100,
            underBudget: totalBudgeted > expenses
          }
        : null;
      
      // Goal progress and timeline
      let goalProgress = 0;
      let goalTimeRemaining = 0;
      let goalDetails = [];
      
      if (goals.length > 0) {
        // Calculate progress for all goals
        goalDetails = goals.map(goal => {
          const progress = Math.round((goal.currentAmount / goal.targetAmount) * 100);
          const timeRemaining = monthlySavings > 0 
            ? Math.ceil((goal.targetAmount - goal.currentAmount) / monthlySavings)
            : Infinity;
          
          return {
            name: goal.name,
            category: goal.category,
            targetAmount: goal.targetAmount,
            currentAmount: goal.currentAmount,
            progress,
            timeRemaining: isFinite(timeRemaining) ? timeRemaining : 'unknown'
          };
        });
        
        // Use primary goal for main display
        const primaryGoal = goals[0];
        goalProgress = Math.round((primaryGoal.currentAmount / primaryGoal.targetAmount) * 100);
        
        if (monthlySavings > 0) {
          const remaining = primaryGoal.targetAmount - primaryGoal.currentAmount;
          goalTimeRemaining = Math.ceil(remaining / monthlySavings);
        } else {
          goalTimeRemaining = Infinity;
        }
      }

      // Set comprehensive financial data
      setFinancialData({
        // Basic metrics
        totalIncome: income,
        totalExpenses: expenses,
        monthlySavings,
        savingsRate,
        
        // Spending breakdown
        topCategory: topCategoryEntry[0],
        topCategoryAmount: topCategoryEntry[1],
        topCategories,
        categorySpendings,
        
        // Budget information
        budgetUtilization,
        budgetStatus,
        
        // Goals information
        goalProgress,
        goalTimeRemaining: isFinite(goalTimeRemaining) ? goalTimeRemaining : 'unknown',
        goalDetails
      });
    } catch (error) {
      console.error('Error fetching financial data:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message to chat
    setMessages(prev => [
      ...prev,
      { sender: 'user', text: userMessage }
    ]);
    
    setLoading(true);
    
    try {
      // Create query data with user context including userId if available
      const queryData = {
        query: userMessage,
        user_context: {
          year_in_school: userProfile.year_in_school,
          major: userProfile.major,
          financial_data: financialData,
          user_id: currentUser?.userId // Include user ID for retrieving accurate transaction data from database
        }
      };
      
      // Send the query to the AI service
      const response = await aiService.sendQuery(queryData);
      
      if (response.status === 'success') {
        // Add AI response to chat
        setMessages(prev => [
          ...prev,
          { sender: 'assistant', text: response.response }
        ]);
        
        // Generate relevant suggestions based on the query
        addRelevantSuggestion(userMessage);
      } else {
        // Handle error response
        setMessages(prev => [
          ...prev,
          { sender: 'assistant', text: "I'm sorry, I couldn't process your request. Please try again." }
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        { sender: 'assistant', text: "I'm sorry, something went wrong. Please try again later." }
      ]);
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  // Helper function to categorize the query
  const categorizeQuery = (query) => {
    const lowerQuery = query.toLowerCase();
    if (lowerQuery.includes('budget') || lowerQuery.includes('spend')) {
      return 'budget';
    } else if (lowerQuery.includes('save') || lowerQuery.includes('saving')) {
      return 'savings';
    } else if (lowerQuery.includes('goal') || lowerQuery.includes('target')) {
      return 'goals';
    } else if (lowerQuery.includes('invest') || lowerQuery.includes('investment')) {
      return 'investment';
    } else {
      return 'general';
    }
  };

  // Helper function to add a relevant suggestion based on query
  const addRelevantSuggestion = (query) => {
    const queryType = categorizeQuery(query);
    
    let suggestion = "";
    switch (queryType) {
      case 'budget':
        suggestion = "Would you like to see your budget breakdown?";
        break;
      case 'savings':
        suggestion = "Would you like some specific strategies to save in your highest expense category?";
        break;
      case 'goals':
        suggestion = "Would you like tips to reach your goals faster?";
        break;
      case 'investment':
        suggestion = "Would you like to learn about beginning investment strategies?";
        break;
      default:
        return; // No suggestion for general queries
    }
    
    setMessages(prev => [
      ...prev, 
      { sender: 'assistant', suggestion }
    ]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    // Auto-send the suggestion
    handleSuggestionInput(suggestion);
  };

  const handleSuggestionInput = async (suggestionText) => {
    if (!suggestionText.trim()) return;
    
    const newUserMessage = { sender: 'user', text: suggestionText };
    setMessages(prev => [...prev, newUserMessage]);
    setLoading(true);
    
    try {
      // Enhanced context with more comprehensive financial data
      const userContext = {
        // Basic financial metrics
        totalIncome: financialData.totalIncome,
        totalExpenses: financialData.totalExpenses,
        monthlySavings: financialData.totalIncome - financialData.totalExpenses,
        savingsRate: financialData.totalIncome > 0 
          ? ((financialData.totalIncome - financialData.totalExpenses) / financialData.totalIncome * 100).toFixed(2) 
          : 0,
        
        // Spending breakdown
        topCategory: financialData.topCategory,
        topCategoryAmount: financialData.topCategoryAmount,
        topCategoryPercentage: financialData.totalExpenses > 0 
          ? ((financialData.topCategoryAmount / financialData.totalExpenses) * 100).toFixed(2)
          : 0,
        
        // Goals information
        goalProgress: financialData.goalProgress,
        goalTimeRemaining: financialData.goalTimeRemaining,
        
        // Query context
        queryType: categorizeQuery(suggestionText)
      };

      // Call the AI service with enhanced context
      const aiResponse = await aiService.sendQuery({
        query: suggestionText,
        user_context: userContext
      });
      
      // Add AI response message
      setMessages(prev => [
        ...prev, 
        { sender: 'assistant', text: aiResponse.response }
      ]);
      
      // Add suggestion based on query
      addRelevantSuggestion(suggestionText);
    } catch (error) {
      console.error('Error getting AI response:', error);
      setMessages(prev => [
        ...prev, 
        { sender: 'assistant', text: "I'm sorry, I encountered an error. Please try again later." }
      ]);
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  const handleClearChat = () => {
    setMessages([
      { sender: 'assistant', text: "Chat history cleared. How can I help you today?" }
    ]);
  };

  // Function to get personalized spending advice
  const getPersonalizedAdvice = async () => {
    setLoading(true);
    try {
      // Use the userProfile state that's populated from the database
      const userProfileData = {
        year_in_school: userProfile.year_in_school,
        major: userProfile.major,
        monthly_income: userProfile.monthly_income || financialData.totalIncome,
        financial_aid: userProfile.financial_aid,
        user_id: currentUser?.userId, // Include user ID if available
        financial_data: {
          income: financialData.totalIncome,
          expenses: financialData.totalExpenses,
          topCategory: financialData.topCategory,
          topCategoryAmount: financialData.topCategoryAmount,
          savingsRate: financialData.savingsRate,
          budgetStatus: financialData.budgetStatus,
          goalProgress: financialData.goalProgress
        }
      };

      // Get spending advice from AI using real profile data
      const advice = await aiService.getSpendingAdvice(userProfileData);
      
      // Display advice to user
      if (advice.status === 'success') {
        // Add message showing what profile data was used
        setMessages(prev => [
          ...prev,
          { sender: 'assistant', text: `Based on your profile (${userProfile.year_in_school} studying ${userProfile.major}), here's some personalized advice:` }
        ]);
        
        // Add advice points
        if (advice.advice && advice.advice.length > 0) {
          advice.advice.forEach((tip, index) => {
            setTimeout(() => {
              setMessages(prev => [
                ...prev,
                { sender: 'assistant', text: `${index + 1}. ${tip}` }
              ]);
            }, index * 500); // Stagger the messages for better UX
          });
        }
        
        // Add predictions after advice with a delay
        if (advice.predictions && advice.predictions.length > 0) {
          setTimeout(() => {
            setMessages(prev => [
              ...prev,
              { sender: 'assistant', text: "Financial predictions based on your data:" }
            ]);
            
            advice.predictions.forEach((prediction, index) => {
              setTimeout(() => {
                setMessages(prev => [
                  ...prev,
                  { sender: 'assistant', text: `• ${prediction}` }
                ]);
              }, index * 500);
            });
          }, (advice.advice?.length || 0) * 500 + 1000);
        }
      } else {
        setMessages(prev => [
          ...prev,
          { sender: 'assistant', text: "I couldn't generate personalized advice at this time. Please try again later." }
        ]);
      }
    } catch (error) {
      console.error('Error getting spending advice:', error);
      setMessages(prev => [
        ...prev,
        { sender: 'assistant', text: "I'm sorry, I encountered an error getting personalized advice. Please try again later." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Function to analyze financial goals
  const analyzeFinancialGoals = async () => {
    setLoading(true);
    try {
      // Format goals data for analysis
      const goalsData = {
        goals: financialData.goalDetails?.map(goal => goal.name) || [],
        user_id: currentUser?.userId, // Include user ID if available
        user_context: {
          user_id: currentUser?.userId, // Include user ID in context as well
          monthly_income: financialData.totalIncome,
          monthly_expenses: financialData.totalExpenses,
          savings_rate: financialData.savingsRate,
          budget_status: financialData.budgetStatus,
          current_goals: financialData.goalDetails || []
        }
      };

      // Only proceed if there are goals to analyze
      if (goalsData.goals.length === 0) {
        setMessages(prev => [
          ...prev,
          { sender: 'assistant', text: "You don't have any financial goals set up yet. Would you like to create one?" }
        ]);
        setLoading(false);
        return;
      }

      // Get goals analysis from AI
      const analysis = await aiService.analyzeFinancialGoals(goalsData);
      
      if (analysis) {
        setMessages(prev => [
          ...prev,
          { sender: 'assistant', text: analysis.analysis || "Here's an analysis of your financial goals:" }
        ]);
        
        // Add recommendations if available
        if (analysis.recommendations && analysis.recommendations.length > 0) {
          setTimeout(() => {
            setMessages(prev => [
              ...prev,
              { sender: 'assistant', text: "Recommendations to reach your goals faster:" }
            ]);
            
            analysis.recommendations.forEach((recommendation, index) => {
              setTimeout(() => {
                setMessages(prev => [
                  ...prev,
                  { sender: 'assistant', text: `• ${recommendation}` }
                ]);
              }, index * 500);
            });
          }, 1000);
        }
      } else {
        setMessages(prev => [
          ...prev,
          { sender: 'assistant', text: "I couldn't analyze your goals at this time. Please try again later." }
        ]);
      }
    } catch (error) {
      console.error('Error analyzing financial goals:', error);
      setMessages(prev => [
        ...prev,
        { sender: 'assistant', text: "I'm sorry, I encountered an error analyzing your goals. Please try again later." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Function to show user profile information
  const showProfileForm = () => {
    if (currentUser && currentUser.userId) {
      setMessages(prev => [
        ...prev,
        { 
          sender: 'assistant', 
          text: "I'm accessing your profile data from your account. If you'd like to update your information, please visit the Profile page."
        }
      ]);
      fetchUserProfile();
    } else {
      setMessages(prev => [
        ...prev,
        { 
          sender: 'assistant', 
          text: "I don't see an account associated with this session. Please log in to access your profile information for personalized advice."
        }
      ]);
    }
    scrollToBottom();
  };

  // Update quick suggestions to include a profile data option
  const quickSuggestions = [
    { 
      text: "How's my budget this month?", 
      icon: <AccountBalanceWalletIcon />,
      action: () => handleSuggestionClick("How's my budget this month?")
    },
    { 
      text: "Help me save more money", 
      icon: <SavingsIcon />,
      action: getPersonalizedAdvice
    },
    { 
      text: "Analyze my financial goals", 
      icon: <CalculateIcon />,
      action: analyzeFinancialGoals
    },
    { 
      text: "View my profile", 
      icon: <TrendingUpIcon />,
      action: showProfileForm
    }
  ];

  // Add a handler for user profile input changes
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setUserProfile(prev => ({
      ...prev,
      [name]: name === 'monthly_income' || name === 'financial_aid' ? Number(value) : value
    }));
  };

  // Add a handler to submit the profile data
  const handleProfileSubmit = async () => {
    setLoading(true);
    try {
      // Create a user message to show what was submitted
      const userMessage = `My profile: ${userProfile.year_in_school} student studying ${userProfile.major} with monthly income of $${userProfile.monthly_income} and financial aid of $${userProfile.financial_aid}.`;
      
      setMessages(prev => [
        ...prev,
        { sender: 'user', text: userMessage }
      ]);

      // If user is logged in, save this profile data to the database
      if (currentUser && currentUser.userId) {
        try {
          // Save profile data to the database using authService
          await authService.updateProfile(currentUser.userId, {
            year_in_school: userProfile.year_in_school,
            major: userProfile.major,
            monthly_income: userProfile.monthly_income,
            financial_aid: userProfile.financial_aid
          });
        } catch (saveError) {
          console.error('Error saving profile data:', saveError);
          // Continue with advice even if save fails
        }
      }

      // Get advice based on profile
      const advice = await aiService.getSpendingAdvice(userProfile);
      
      // Process and display advice
      if (advice.status === 'success') {
        setMessages(prev => [
          ...prev,
          { sender: 'assistant', text: "Based on your profile, here's some financial advice:" }
        ]);
        
        if (advice.advice && advice.advice.length > 0) {
          advice.advice.forEach((tip, index) => {
            setTimeout(() => {
              setMessages(prev => [
                ...prev,
                { sender: 'assistant', text: `${index + 1}. ${tip}` }
              ]);
            }, index * 500);
          });
        }
      } else {
        setMessages(prev => [
          ...prev,
          { sender: 'assistant', text: "Thank you for providing your information. Is there anything specific you'd like to know about managing your finances?" }
        ]);
      }
    } catch (error) {
      console.error('Error processing profile data:', error);
      setMessages(prev => [
        ...prev,
        { sender: 'assistant', text: "I had trouble processing your information. Let's try something else. What would you like to know about managing your finances?" }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Financial Assistant
          </Typography>
          <IconButton onClick={handleClearChat} aria-label="clear chat">
            <DeleteOutlineIcon />
          </IconButton>
        </Box>

        <Paper 
          elevation={3} 
          sx={{ 
            height: '60vh', 
            display: 'flex', 
            flexDirection: 'column',
            overflow: 'hidden'
          }}
        >
          {/* Messages Area */}
          <Box 
            sx={{ 
              p: 2, 
              flexGrow: 1, 
              overflow: 'auto',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {messages.map((message, index) => (
              <Box 
                key={index} 
                sx={{ 
                  alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 1.5
                }}
              >
                {message.text ? (
                  <MessageBubble sender={message.sender} elevation={1}>
                    <Typography variant="body1">
                      {message.text}
                    </Typography>
                  </MessageBubble>
                ) : message.suggestion ? (
                  <SuggestionCard 
                    onClick={() => handleSuggestionClick(message.suggestion)}
                    variant="outlined"
                  >
                    <Typography variant="body2" color="text.secondary">
                      Suggestion: {message.suggestion}
                    </Typography>
                  </SuggestionCard>
                ) : null}
              </Box>
            ))}
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                <CircularProgress size={24} />
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>

          <Divider />

          {/* Quick Suggestions */}
          <Box sx={{ p: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {quickSuggestions.map((suggestion, index) => (
              <Button 
                key={index}
                size="small"
                variant="outlined"
                startIcon={suggestion.icon}
                onClick={suggestion.action}
                sx={{ mb: 1 }}
              >
                {suggestion.text}
              </Button>
            ))}
          </Box>

          <Divider />

          {/* Input Area */}
          <Box sx={{ p: 2, backgroundColor: 'background.paper' }}>
            <TextField
              fullWidth
              placeholder="Ask me anything about your finances..."
              value={input}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              multiline
              maxRows={4}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton 
                      onClick={handleSendMessage}
                      disabled={!input.trim() || loading}
                      color="primary"
                    >
                      <SendIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default AIAssistant; 