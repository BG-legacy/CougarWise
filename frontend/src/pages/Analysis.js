import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  MenuItem,
  TextField,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import { 
  Chart as ChartJS, 
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  LineElement,
  PointElement
} from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';
import transactionService from '../services/transactionService';
import budgetService from '../services/budgetService';
import goalService from '../services/goalService';

// Register ChartJS components
ChartJS.register(
  ArcElement, 
  Tooltip, 
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  LineElement,
  PointElement
);

const Analysis = () => {
  // Memoize the chartColors to prevent it from being a dependency in useCallback
  const chartColors = useMemo(() => [
    '#800000', // CSU Maroon
    '#FFD700', // Gold
    '#4B0082', // Indigo
    '#006400', // Dark Green
    '#8B0000', // Dark Red
    '#483D8B', // Dark Slate Blue
    '#2F4F4F', // Dark Slate Gray
    '#8B4513', // Saddle Brown
    '#4682B4', // Steel Blue
    '#708090', // Slate Gray
    '#A0522D', // Sienna
    '#C71585', // Medium Violet Red
  ], []);

  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [goals, setGoals] = useState([]);
  const [tabValue, setTabValue] = useState(0);
  const [timeframe, setTimeframe] = useState('month'); // 'month', 'quarter', 'year'
  const [categoryExpenseData, setCategoryExpenseData] = useState(null);
  const [monthlyTotalsData, setMonthlyTotalsData] = useState(null);
  const [budgetComparisonData, setBudgetComparisonData] = useState(null);
  const [goalProgressData, setGoalProgressData] = useState(null);

  const fetchData = useCallback(async () => {
    

    setLoading(true);
    try {
      // Get user from localStorage
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        console.error('User not authenticated');
        setLoading(false);
        return;
      }
      
      const user = JSON.parse(userStr);
      if (!user || !user.id) {
        console.error('Invalid user data');
        setLoading(false);
        return;
      }
      
      // Initialize with Promise.all to fetch data in parallel
      const [transactionsData, budgetsData, goalsData] = await Promise.all([
        transactionService.getTransactions().catch(err => {
          console.error('Error fetching transactions:', err);
          return [];
        }),
        budgetService.getBudgets().catch(err => {
          console.error('Error fetching budgets:', err);
          return [];
        }),
        goalService.getGoals().catch(err => {
          console.error('Error fetching goals:', err);
          return [];
        })
      ]);
      


      
      // Ensure we always set the state, even with empty arrays
      setTransactions(transactionsData || []);
      console.log("Fetched transactions:", transactionsData); // log the transactions for bugtesting

      setBudgets(budgetsData || []);
      setGoals(goalsData || []);
    } catch (error) {
      console.error('Error fetching data for analysis:', error);
      // Set empty arrays to trigger default chart states
      setTransactions([]);
      setBudgets([]);
      setGoals([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleTimeframeChange = (event) => {
    setTimeframe(event.target.value);
  };

  // Memoize the filterTransactionsByTimeframe function
  const filterTransactionsByTimeframe = useCallback((transactions) => {
    const now = new Date();
    let startDate;

    switch (timeframe) {
      case 'month':
        startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
        break;
      case 'quarter':
        startDate = new Date(now.getFullYear(), now.getMonth() - 3, now.getDate());
        break;
      case 'year':
        startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
        break;
      default:
        startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
    }

    return transactions.filter(t => new Date(t.date) > startDate);
  }, [timeframe]);

  const prepareChartData = useCallback(() => {
    // If there are no transactions, set default empty charts
    if (transactions.length === 0) {
      setCategoryExpenseData({
        labels: ['No Data'],
        datasets: [{ 
          data: [1], 
          backgroundColor: ['#e0e0e0'],
          borderWidth: 1
        }]
      });

      setMonthlyTotalsData({
        labels: ['No Data'],
        datasets: [
          {
            label: 'No Transaction Data',
            data: [0],
            backgroundColor: 'rgba(200, 200, 200, 0.5)',
            borderColor: 'rgba(200, 200, 200, 1)',
            borderWidth: 1,
          }
        ]
      });
      return;
    }

    // Filter transactions based on timeframe
    const filteredTransactions = filterTransactionsByTimeframe(transactions);
    
    // Prepare data for all charts
    // Category expense data
    // Inititally had an error where income was included in the pie charts, now income is excluded
    const expensesByCategory = filteredTransactions
    .filter(t => {
      // Exclude 'income' category explicitly and only include actual expenses
      return (
        typeof t.category === 'string' &&
        t.category.trim().toLowerCase() !== 'income' &&
        (t.amount > 0 || t.amount < 0 || t.type === 'expense')
      );
    })
    .reduce((acc, transaction) => {
      const category = transaction.category?.trim().toLowerCase() || 'uncategorized';
      if (!acc[category]) acc[category] = 0;
      acc[category] += Math.abs(transaction.amount); // Use absolute value for clarity
      return acc;
    }, {});
    
    // If no expense data, set default empty chart
    if (Object.keys(expensesByCategory).length === 0) {
      setCategoryExpenseData({
        labels: ['No Expense Data'],
        datasets: [{ 
          data: [1], 
          backgroundColor: ['#e0e0e0'],
          borderWidth: 1
        }]
      });
    } else {
      const sortedCategories = Object.entries(expensesByCategory)
        .sort((a, b) => b[1] - a[1]);
      
      setCategoryExpenseData({
        labels: sortedCategories.map(([category]) => category),
        datasets: [
          {
            data: sortedCategories.map(([, amount]) => amount),
            backgroundColor: chartColors.slice(0, sortedCategories.length),
            borderWidth: 1,
          },
        ],
      });
    }

    // Monthly totals data
    const months = [];
    const now = new Date();
    for (let i = 11; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      months.push(d.toLocaleString('default', { month: 'short', year: '2-digit' }));
    }

    const monthlyData = months.reduce((acc, month, index) => {
      acc.income.push(0);
      acc.expenses.push(0);
      acc.savings.push(0);
      return acc;
    }, { income: [], expenses: [], savings: [] });

    transactions.forEach(transaction => {
      // Make sure transaction.date is a valid date
      const transactionDate = transaction.date ? new Date(transaction.date) : new Date();
      
      const monthIndex = months.findIndex(m => {
        const [monthStr, yearStr] = m.split(' ');
        const monthNum = new Date(Date.parse(`${monthStr} 1, 20${yearStr}`)).getMonth();
        const year = 2000 + parseInt(yearStr);
        return transactionDate.getMonth() === monthNum && transactionDate.getFullYear() === year;
      });

      if (monthIndex !== -1) {
        const isIncome = transaction.category?.trim().toLowerCase() === 'income';
      
        if (isIncome) {
          monthlyData.savings[monthIndex] += Math.abs(transaction.amount);
        } else {
          monthlyData.expenses[monthIndex] += Math.abs(transaction.amount);
        }
      


      }
    });

    setMonthlyTotalsData({
      labels: months,
      datasets: [
        {
          label: 'Expenses',
          data: monthlyData.expenses,
          backgroundColor: 'rgba(139, 0, 0, 0.5)',
          borderColor: 'rgba(139, 0, 0, 1)',
          borderWidth: 1,
        },
        {
          label: 'Savings',
          data: monthlyData.savings,
          backgroundColor: 'rgba(255, 215, 0, 0.5)',
          borderColor: 'rgba(255, 215, 0, 1)',
          borderWidth: 1,
        }
      ],
    });

    const filteredForSpending = filterTransactionsByTimeframe(transactions);

    const categorySpendings = filteredForSpending
      .filter(t => {
        return (
          typeof t.category === 'string' &&
          t.category.trim().toLowerCase() !== 'income' &&
          t.amount !== 0
        );
      })
      .reduce((acc, transaction) => {
        const category = transaction.category.trim().toLowerCase();
        if (!acc[category]) acc[category] = 0;
        acc[category] += Math.abs(transaction.amount);
        return acc;
      }, {});
  
  const budgetCategories = [];
  const budgetAmounts = [];
  const actualAmounts = [];
  
  // Displays budget vs actual spending [FIXED]
  // initially had error which only budget would show but now both budget and spending show
  budgets.forEach(budget => {
    const categoryLabel = budget.category.toLowerCase();
    budgetCategories.push(categoryLabel);
    budgetAmounts.push(budget.amount);
    const spending = categorySpendings[categoryLabel] || 0;
    actualAmounts.push(spending);
  });

    setBudgetComparisonData({
      labels: budgetCategories,
      datasets: [
        {
          label: 'Budget',
          data: budgetAmounts,
          backgroundColor: 'rgba(255, 215, 0, 0.5)',
          borderColor: 'rgba(255, 215, 0, 1)',
          borderWidth: 1,
        },
        {
          label: 'Actual',
          data: actualAmounts,
          backgroundColor: 'rgba(128, 0, 0, 0.5)',
          borderColor: 'rgba(128, 0, 0, 1)',
          borderWidth: 1,
        }
      ]
    });

    // Goal progress data
    if (goals.length > 0) {
      const goalNames = goals.map(goal => goal.name);
      const targetAmounts = goals.map(goal => goal.targetAmount);
      const currentAmounts = goals.map(goal => goal.currentAmount);

      setGoalProgressData({
        labels: goalNames,
        datasets: [
          {
            label: 'Current Amount',
            data: currentAmounts,
            backgroundColor: 'rgba(128, 0, 0, 0.5)',
            borderColor: 'rgba(128, 0, 0, 1)',
            borderWidth: 1,
          },
          {
            label: 'Target Amount',
            data: targetAmounts,
            backgroundColor: 'rgba(255, 215, 0, 0.5)',
            borderColor: 'rgba(255, 215, 0, 1)',
            borderWidth: 1,
          }
        ]
      });
    }
  }, [transactions, budgets, goals, filterTransactionsByTimeframe, chartColors]);

  useEffect(() => {
    if (!loading) {
      prepareChartData();
    }
  }, [transactions, budgets, goals, timeframe, prepareChartData, loading]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Financial Analysis
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="analysis tabs"
            sx={{ mb: 2 }}
          >
            <Tab label="Overview" />
            <Tab label="Income & Expenses" />
            <Tab label="Budget" />
            <Tab label="Goals" />
          </Tabs>
          
          <Box sx={{ minWidth: 120 }}>
            <TextField
              select
              label="Timeframe"
              value={timeframe}
              onChange={handleTimeframeChange}
              variant="outlined"
              size="small"
            >
              <MenuItem value="month">Last Month</MenuItem>
              <MenuItem value="quarter">Last Quarter</MenuItem>
              <MenuItem value="year">Last Year</MenuItem>
            </TextField>
          </Box>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Overview Tab */}
            {tabValue === 0 && (
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card sx={{ height: '100%', minHeight: 400 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Expenses by Category
                      </Typography>
                      <Box sx={{ height: 350 }}>
                        {categoryExpenseData ? (
                          <Pie data={categoryExpenseData} options={chartOptions} />
                        ) : (
                          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                            <Typography>No expense data available</Typography>
                          </Box>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card sx={{ height: '100%', minHeight: 400 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Monthly Income & Expenses
                      </Typography>
                      <Box sx={{ height: 350 }}>
                        {monthlyTotalsData ? (
                          <Bar 
                            data={monthlyTotalsData} 
                            options={{
                              ...chartOptions,
                              scales: {
                                x: {
                                  stacked: false,
                                },
                                y: {
                                  stacked: false,
                                  beginAtZero: true,
                                }
                              }
                            }} 
                          />
                        ) : (
                          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                            <Typography>No transaction data available</Typography>
                          </Box>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}

            {/* Income & Expenses Tab */}
            {tabValue === 1 && (
              <Card sx={{ minHeight: 500 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Monthly Trends
                  </Typography>
                  <Box sx={{ height: 450 }}>
                    {monthlyTotalsData ? (
                      <Line 
                        data={monthlyTotalsData}
                        options={{
                          ...chartOptions,
                          scales: {
                            y: {
                              beginAtZero: true,
                            }
                          }
                        }}
                      />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <Typography>No transaction data available</Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            )}

            {/* Budget Tab */}
            {tabValue === 2 && (
              <Card sx={{ minHeight: 500 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Budget vs. Actual Spending
                  </Typography>
                  <Box sx={{ height: 450 }}>
                    {budgetComparisonData ? (
                      <Bar 
                        data={budgetComparisonData}
                        options={{
                          ...chartOptions,
                          scales: {
                            y: {
                              beginAtZero: true,
                            }
                          }
                        }}
                      />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <Typography>No budget data available</Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            )}

            {/* Goals Tab */}
            {tabValue === 3 && (
              <Card sx={{ minHeight: 500 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Goal Progress
                  </Typography>
                  <Box sx={{ height: 450 }}>
                    {goalProgressData ? (
                      <Bar 
                        data={goalProgressData}
                        options={{
                          ...chartOptions,
                          scales: {
                            y: {
                              beginAtZero: true,
                            }
                          }
                        }}
                      />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <Typography>No goal data available</Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </Box>
    </Container>
  );
};

export default Analysis; 