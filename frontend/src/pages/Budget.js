import React, { useState, useEffect, useCallback } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Grid, 
  Button, 
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  LinearProgress,
  MenuItem,
  InputAdornment,
  Alert,
  Snackbar
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import budgetService from '../services/budgetService';
import { useAuth } from '../context/AuthContext';
import { BUDGET_UPDATE_EVENT } from './Transactions';

const categoryOptions = [
  'Housing', 'Transportation', 'Food', 'Utilities', 
  'Insurance', 'Healthcare', 'Savings', 'Debt', 
  'Personal', 'Entertainment', 'Education', 'Other'
];

const Budget = () => {
  const { currentUser } = useAuth();
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingBudgetId, setEditingBudgetId] = useState(null);
  const [formData, setFormData] = useState({
    category: '',
    amount: '',
    period: 'monthly'
  });
  const [alert, setAlert] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  const handleCloseAlert = () => {
    setAlert(prev => ({ ...prev, open: false }));
  };

  const showAlert = useCallback((message, severity = 'info') => {
    setAlert({
      open: true,
      message,
      severity
    });
  }, []);

  const fetchBudgets = useCallback(async () => {
    setLoading(true);
    try {
      // Check if user is logged in
      if (!currentUser || !currentUser.id) {
        showAlert('Please log in to view your budgets', 'warning');
        setLoading(false);
        return;
      }
      
      // Fetch budgets data
      const budgetsData = await budgetService.getBudgets();
      
      // Use the 'spent' field from the budget if available, otherwise default to 0
      const budgetsWithSpending = budgetsData.map(budget => ({
        ...budget,
        spent: budget.spent || 0
      }));
      
      setBudgets(budgetsWithSpending);
    } catch (error) {
      console.error('Error fetching budgets:', error);
      showAlert('Error fetching budgets: ' + (error.message || error), 'error');
    } finally {
      setLoading(false);
    }
  }, [currentUser, showAlert]);

  useEffect(() => {
    fetchBudgets();
    
    // Listen for budget update events from transactions
    window.addEventListener(BUDGET_UPDATE_EVENT, fetchBudgets);
    
    // Clean up event listener on component unmount
    return () => {
      window.removeEventListener(BUDGET_UPDATE_EVENT, fetchBudgets);
    };
  }, [fetchBudgets]);

  const handleOpenDialog = (budget = null) => {
    if (budget) {
      setFormData({
        category: budget.category,
        amount: budget.amount,
        period: budget.period || 'monthly'
      });
      setEditingBudgetId(budget.id);
    } else {
      setFormData({
        category: '',
        amount: '',
        period: 'monthly'
      });
      setEditingBudgetId(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'amount' ? value.replace(/[^0-9.]/g, '') : value
    }));
  };

  const handleSaveBudget = async () => {
    try {
      if (editingBudgetId) {
        await budgetService.updateBudget(editingBudgetId, formData);
        showAlert('Budget updated successfully', 'success');
      } else {
        await budgetService.createBudget(formData);
        showAlert('Budget created successfully', 'success');
      }
      fetchBudgets();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving budget:', error);
      showAlert('Error saving budget: ' + (error.message || error), 'error');
    }
  };

  const handleDeleteBudget = async (id) => {
    if (window.confirm('Are you sure you want to delete this budget?')) {
      try {
        await budgetService.deleteBudget(id);
        showAlert('Budget deleted successfully', 'success');
        fetchBudgets();
      } catch (error) {
        console.error('Error deleting budget:', error);
        showAlert('Error deleting budget: ' + (error.message || error), 'error');
      }
    }
  };

  // Calculate percentage of budget used
  const calculateUsage = (budget) => {
    if (!budget.spent) return 0;
    return Math.min(100, Math.round((budget.spent / budget.amount) * 100));
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Budget Management
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            disabled={!currentUser}
          >
            Add Budget
          </Button>
        </Box>

        {!currentUser && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Please log in to manage your budgets
          </Alert>
        )}

        {loading ? (
          <LinearProgress />
        ) : budgets.length === 0 ? (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6">No budgets found</Typography>
            <Typography variant="body2" color="textSecondary">
              Create your first budget to start tracking your expenses
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {budgets.map((budget) => (
              <Grid item xs={12} sm={6} md={4} key={budget.id}>
                <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="h6">{budget.category}</Typography>
                    <Box>
                      <IconButton 
                        size="small" 
                        onClick={() => handleOpenDialog(budget)}
                        aria-label="edit"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton 
                        size="small" 
                        onClick={() => handleDeleteBudget(budget.id)}
                        aria-label="delete"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    {budget.period.charAt(0).toUpperCase() + budget.period.slice(1)} Budget
                  </Typography>
                  
                  <Box sx={{ mt: 1, mb: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={calculateUsage(budget)} 
                      sx={{ 
                        height: 10, 
                        borderRadius: 5,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: calculateUsage(budget) > 85 ? 'error.main' : 
                                          calculateUsage(budget) > 70 ? 'warning.main' : 'success.main'
                        }
                      }}
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                    <Typography variant="body2">
                      Spent: ${budget.spent?.toFixed(2) || '0.00'}
                    </Typography>
                    <Typography variant="body2">
                      Budget: ${budget.amount.toFixed(2)}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 1 }}>
                    {calculateUsage(budget)}% used
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      {/* Snackbar for alerts */}
      <Snackbar 
        open={alert.open}
        autoHideDuration={6000}
        onClose={handleCloseAlert}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseAlert} severity={alert.severity}>
          {alert.message}
        </Alert>
      </Snackbar>

      {/* Add/Edit Budget Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingBudgetId ? 'Edit Budget' : 'Add New Budget'}
        </DialogTitle>
        <DialogContent>
          <TextField
            select
            margin="normal"
            label="Category"
            name="category"
            value={formData.category}
            onChange={handleInputChange}
            fullWidth
            required
          >
            {categoryOptions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </TextField>
          
          <TextField
            margin="normal"
            label="Amount"
            name="amount"
            value={formData.amount}
            onChange={handleInputChange}
            fullWidth
            required
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
          />
          
          <TextField
            select
            margin="normal"
            label="Period"
            name="period"
            value={formData.period}
            onChange={handleInputChange}
            fullWidth
            required
          >
            <MenuItem value="weekly">Weekly</MenuItem>
            <MenuItem value="monthly">Monthly</MenuItem>
            <MenuItem value="yearly">Yearly</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSaveBudget}
            variant="contained"
            disabled={!formData.category || !formData.amount || !formData.period}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Budget; 