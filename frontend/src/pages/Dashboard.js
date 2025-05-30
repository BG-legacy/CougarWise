import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Divider,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Card,
  CardContent,
  Avatar
} from '@mui/material';
import {
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AttachMoney as AttachMoneyIcon,
  AccountBalance as AccountBalanceIcon,
  EmojiEvents as EmojiEventsIcon,
  Receipt as ReceiptIcon
} from '@mui/icons-material';
import { Bar } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale
} from 'chart.js';
import AuthContext from '../context/AuthContext';
import { getUserTransactions } from '../services/transactionService';
import { getUserBudgets } from '../services/budgetService';
import { getUserGoals } from '../services/goalService';
import { getSpendingAnalysis } from '../services/transactionService';

// Register ChartJS components
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale
);

const Dashboard = () => {
  const navigate = useNavigate();
  const { currentUser } = useContext(AuthContext);
  
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [goals, setGoals] = useState([]);
  const [analysisData, setAnalysisData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!currentUser) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // Fetch user's transactions, budgets, goals, and spending analysis
        const [transactionsData, budgetsData, goalsData, analysisData] = await Promise.all([
          getUserTransactions(currentUser.id).catch(err => {
            console.error('Error fetching transactions:', err);
            return [];
          }),
          getUserBudgets(currentUser.id).catch(err => {
            console.error('Error fetching budgets:', err);
            return [];
          }),
          getUserGoals(currentUser.id).catch(err => {
            console.error('Error fetching goals:', err);
            return [];
          }),
          getSpendingAnalysis(currentUser.id).catch(err => {
            console.error('Error fetching spending analysis:', err);
            return null;
          })
        ]);
        
        console.log('Transaction Data:', transactionsData);
        console.log('Analysis Data:', analysisData);
        
        // Store the analysis data for later use in filtering income categories
        setAnalysisData(analysisData);
        
        // Check if we have transactions but no spending data
        const hasTransactions = transactionsData && transactionsData.length > 0;
        const hasSpendingData = analysisData?.category_breakdown && 
          Object.keys(analysisData.category_breakdown).length > 0;
        
        console.log('Has Transactions:', hasTransactions);
        console.log('Has Spending Data:', hasSpendingData);
        
        setTransactions(transactionsData);
        setBudgets(budgetsData);
        setGoals(goalsData || []);
        
        // First check: Do we have transactions where amount > 0? (income)
        const positiveTransactions = transactionsData.filter(t => t.amount > 0);
        
        // Second check: Are our transactions properly categorized?
        const categorizedTransactions = transactionsData.filter(t => t.category && t.category.trim() !== '');
        
        // Identify expense transactions (negative amounts) for total spending calculation
        const expenseTransactions = transactionsData.filter(t => t.amount < 0);
        
        // Calculate total spending from expense transactions only
        const calculatedTotalSpending = expenseTransactions.reduce((total, transaction) => 
          total + Math.abs(transaction.amount), 0);
        
        console.log('Positive Transactions:', positiveTransactions.length);
        console.log('Categorized Transactions:', categorizedTransactions.length);
        console.log('Expense Transactions:', expenseTransactions.length);
        console.log('Calculated Total Spending:', calculatedTotalSpending);
        
        // Create manual category breakdown if the API doesn't provide it but we have transactions
        let categoryBreakdown = {};
        
        // If we have transactions but no spending data from the API, create it manually
        if (hasTransactions && !hasSpendingData) {
          // Group transactions by category and sum their amounts
          transactionsData.forEach(transaction => {
            // Skip income transactions (positive amounts) to only show expenses
            if (transaction.amount >= 0) return;
            
            const amount = Math.abs(transaction.amount);
            const category = transaction.category || 'Uncategorized';
            
            // Include only expense transactions (negative amounts) with categories
            if (category && category.trim() !== '') {
              if (categoryBreakdown[category]) {
                categoryBreakdown[category] += amount;
              } else {
                categoryBreakdown[category] = amount;
              }
            }
          });
          
          console.log('Manually created category breakdown:', categoryBreakdown);
        }
        
        // Ensure analysis data has expected structure with defaults
        setAnalysis({
          // Use our calculated total spending from expense transactions only
          total_spending: calculatedTotalSpending || analysisData?.total_spending || 0,
          period: analysisData?.period || 'Monthly',
          category_breakdown: 
            // Use API data if available, otherwise use our manual calculation, or fallback to empty
            (analysisData?.category_breakdown && Object.keys(analysisData.category_breakdown).length > 0) 
              ? analysisData.category_breakdown 
              : (Object.keys(categoryBreakdown).length > 0 
                  ? categoryBreakdown 
                  : (transactionsData.length > 0 ? { 'No Categories': 0 } : {}))
        });

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [currentUser]);

  // Filter out income categories from the category breakdown
  useEffect(() => {
    if (!analysis) return;
    
    // Check if we need to filter income categories
    const filteredBreakdown = {...analysis.category_breakdown};
    
    // List of common income categories to filter out
    const incomeCategories = ['Income', 'Salary', 'Wages', 'Dividend', 'Interest', 'Gift', 'Refund'];
    
    let hasChanges = false;
    // Remove any income categories from the breakdown
    incomeCategories.forEach(category => {
      if (filteredBreakdown[category]) {
        delete filteredBreakdown[category];
        hasChanges = true;
      }
    });
    
    // Only update if we actually removed any categories to avoid unnecessary re-renders
    if (hasChanges) {
      setAnalysis(prev => ({
        ...prev,
        category_breakdown: filteredBreakdown
      }));
    }
  }, [analysis?.category_breakdown]);

  // Chart data preparation
  // Chart now shows expenses only, with income filtered out
  const chartData = {
    labels: analysis?.category_breakdown ? Object.keys(analysis.category_breakdown) : [],
    datasets: [
      {
        // Updated label to clarify we're showing expenses
        label: 'Expenses by Category',
        data: analysis?.category_breakdown ? Object.values(analysis.category_breakdown) : [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)',
          'rgba(199, 199, 199, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(199, 199, 199, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Amount ($)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Category'
        }
      }
    },
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      // Updated title to clarify we're showing expense categories
      title: {
        display: true,
        text: 'Expense Categories'
      },
    },
  };

  // Handle empty or loading states
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error">{error}</Typography>
        <Button 
          variant="contained" 
          sx={{ mt: 2 }}
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
        Welcome, {currentUser?.username}!
      </Typography>
      
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={4}>
          <Card 
            elevation={2}
            sx={{ 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              bgcolor: 'primary.light',
              color: 'white'
            }}
          >
            <CardContent sx={{ flexGrow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.dark', mr: 2 }}>
                  <AttachMoneyIcon />
                </Avatar>
                {/* Updated title to clarify we're showing total expenses */}
                <Typography variant="h6">
                  Total Expenses
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 2 }}>
                ${analysis?.total_spending.toFixed(2) || '0.00'}
              </Typography>
              <Typography variant="body2">
                Period: {analysis?.period || 'Monthly'}
              </Typography>
              <Button 
                variant="contained" 
                color="secondary" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/dashboard/analysis')}
              >
                View Analysis
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card 
            elevation={2}
            sx={{ 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              bgcolor: 'secondary.light',
              color: 'white'
            }}
          >
            <CardContent sx={{ flexGrow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'secondary.dark', mr: 2 }}>
                  <AccountBalanceIcon />
                </Avatar>
                <Typography variant="h6">
                  Budget Status
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 2 }}>
                {budgets.length} Active
              </Typography>
              <Typography variant="body2">
                Budget categories set up
              </Typography>
              <Button 
                variant="contained" 
                color="primary" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/dashboard/budget')}
              >
                Manage Budgets
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card 
            elevation={2}
            sx={{ 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              bgcolor: 'success.light',
              color: 'white'
            }}
          >
            <CardContent sx={{ flexGrow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'success.dark', mr: 2 }}>
                  <EmojiEventsIcon />
                </Avatar>
                <Typography variant="h6">
                  Financial Goals
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 2 }}>
                {goals?.length || 0} Goals
              </Typography>
              <Typography variant="body2">
                Track your financial journey
              </Typography>
              <Button 
                variant="contained" 
                color="primary" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/dashboard/goals')}
              >
                View Goals
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Spending Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400 }}>
            {/* Updated title to clarify we're showing expense breakdown */}
            <Typography variant="h6" gutterBottom>
              Expense Breakdown
            </Typography>
            <Box sx={{ height: 330 }}>
              {analysis?.category_breakdown && 
                Object.keys(analysis.category_breakdown).length > 0 && 
                Object.values(analysis.category_breakdown).some(value => value > 0) ? (
                <Bar data={chartData} options={chartOptions} />
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                  {/* Updated message to clarify we're showing expense data */}
                  <Typography color="text.secondary" gutterBottom>
                    No expense data available
                  </Typography>
                  {transactions.length > 0 ? (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, textAlign: 'center', maxWidth: '80%' }}>
                      Transaction categories are required to generate your spending breakdown.
                      Make sure your transactions have categories assigned.
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, textAlign: 'center', maxWidth: '80%' }}>
                      Add some transactions to see your spending analysis.
                    </Typography>
                  )}
                  <Button 
                    variant="contained" 
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => navigate('/dashboard/transactions')}
                    sx={{ mt: 2 }}
                  >
                    {transactions.length > 0 ? 'Manage Transactions' : 'Add Transactions'}
                  </Button>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
        
        {/* Recent Transactions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 400, overflow: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Recent Transactions
              </Typography>
              <Button 
                startIcon={<AddIcon />}
                size="small"
                onClick={() => navigate('/dashboard/transactions')}
              >
                Add
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            {transactions.length > 0 ? (
              <List>
                {transactions.slice(0, 5).map((transaction) => (
                  <ListItem key={transaction.id} sx={{ px: 1, py: 1 }}>
                    <ListItemText
                      primary={transaction.description}
                      secondary={`${transaction.date.substring(0, 10)}`}
                    />
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {transaction.amount < 0 ? (
                        <TrendingDownIcon color="error" sx={{ mr: 1 }} />
                      ) : (
                        <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                      )}
                      <Typography 
                        color={transaction.amount < 0 ? 'error' : 'success.main'} 
                        variant="body2" 
                        sx={{ fontWeight: 'bold' }}
                      >
                        ${Math.abs(transaction.amount).toFixed(2)}
                      </Typography>
                    </Box>
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
                <Box sx={{ textAlign: 'center' }}>
                  <ReceiptIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography color="text.secondary">
                    No transactions yet
                  </Typography>
                  <Button 
                    variant="contained" 
                    startIcon={<AddIcon />}
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/dashboard/transactions')}
                  >
                    Add Transaction
                  </Button>
                </Box>
              </Box>
            )}
            
            {transactions.length > 0 && (
              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Button 
                  variant="outlined" 
                  onClick={() => navigate('/dashboard/transactions')}
                >
                  View All Transactions
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 