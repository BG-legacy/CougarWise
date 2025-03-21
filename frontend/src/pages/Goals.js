import React, { useState, useEffect } from 'react';
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
  Chip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import goalService from '../services/goalService';

const categoryOptions = [
  'Emergency Fund', 'Retirement', 'House', 'Car', 
  'Vacation', 'Education', 'Wedding', 'Business', 'Other'
];

const Goals = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingGoalId, setEditingGoalId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    targetAmount: '',
    currentAmount: '0',
    targetDate: new Date(new Date().setFullYear(new Date().getFullYear() + 1))
  });

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    setLoading(true);
    try {
      const data = await goalService.getGoals();
      setGoals(data);
    } catch (error) {
      console.error('Error fetching goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (goal = null) => {
    if (goal) {
      setFormData({
        name: goal.name,
        category: goal.category,
        targetAmount: goal.targetAmount.toString(),
        currentAmount: goal.currentAmount.toString(),
        targetDate: new Date(goal.targetDate)
      });
      setEditingGoalId(goal.id || goal._id);
    } else {
      setFormData({
        name: '',
        category: '',
        targetAmount: '',
        currentAmount: '0',
        targetDate: new Date(new Date().setFullYear(new Date().getFullYear() + 1))
      });
      setEditingGoalId(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name === 'targetAmount' || name === 'currentAmount') {
      setFormData(prev => ({
        ...prev,
        [name]: value.replace(/[^0-9.]/g, '')
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleDateChange = (date) => {
    setFormData(prev => ({
      ...prev,
      targetDate: date
    }));
  };

  const handleSaveGoal = async () => {
    try {
      const payload = {
        ...formData,
        targetAmount: parseFloat(formData.targetAmount),
        currentAmount: parseFloat(formData.currentAmount || 0)
      };
      
      if (editingGoalId) {
        await goalService.updateGoal(editingGoalId, payload);
      } else {
        await goalService.createGoal(payload);
      }
      fetchGoals();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving goal:', error);
    }
  };

  const handleDeleteGoal = async (id) => {
    if (window.confirm('Are you sure you want to delete this goal?')) {
      try {
        await goalService.deleteGoal(id);
        fetchGoals();
      } catch (error) {
        console.error('Error deleting goal:', error);
      }
    }
  };

  // Calculate percentage of goal completed
  const calculateProgress = (goal) => {
    return Math.min(100, Math.round((goal.currentAmount / goal.targetAmount) * 100));
  };

  // Get ID from goal object (handle both _id and id formats)
  const getGoalId = (goal) => {
    return goal.id || goal._id;
  };

  // Calculate time remaining
  const calculateTimeRemaining = (targetDate) => {
    const now = new Date();
    const target = new Date(targetDate);
    const diffTime = target - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'Overdue';
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return '1 day left';
    if (diffDays < 30) return `${diffDays} days left`;
    
    const diffMonths = Math.floor(diffDays / 30);
    if (diffMonths === 1) return '1 month left';
    if (diffMonths < 12) return `${diffMonths} months left`;
    
    const diffYears = Math.floor(diffMonths / 12);
    if (diffYears === 1) return '1 year left';
    return `${diffYears} years left`;
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Financial Goals
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add Goal
          </Button>
        </Box>

        {loading ? (
          <LinearProgress />
        ) : goals.length === 0 ? (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6">No financial goals found</Typography>
            <Typography variant="body2" color="textSecondary">
              Create your first goal to start planning for your future
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {goals.map((goal) => (
              <Grid item xs={12} sm={6} md={4} key={getGoalId(goal)}>
                <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="h6">{goal.name}</Typography>
                    <Box>
                      <IconButton 
                        size="small" 
                        onClick={() => handleOpenDialog(goal)}
                        aria-label="edit"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton 
                        size="small" 
                        onClick={() => handleDeleteGoal(getGoalId(goal))}
                        aria-label="delete"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={goal.category} 
                      size="small" 
                      sx={{ backgroundColor: 'secondary.light' }} 
                    />
                  </Box>
                  
                  <Box sx={{ mt: 1, mb: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={calculateProgress(goal)} 
                      sx={{ 
                        height: 10, 
                        borderRadius: 5,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: 'primary.main'
                        }
                      }}
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                    <Typography variant="body2">
                      Saved: ${goal.currentAmount.toFixed(2)}
                    </Typography>
                    <Typography variant="body2">
                      Goal: ${goal.targetAmount.toFixed(2)}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      {calculateTimeRemaining(goal.targetDate)}
                    </Typography>
                    <Typography variant="body2">
                      {calculateProgress(goal)}% complete
                    </Typography>
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      {/* Add/Edit Goal Dialog */}
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingGoalId ? 'Edit Goal' : 'Add New Goal'}
          </DialogTitle>
          <DialogContent>
            <TextField
              margin="normal"
              label="Goal Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              fullWidth
              required
            />
            
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
              label="Target Amount"
              name="targetAmount"
              value={formData.targetAmount}
              onChange={handleInputChange}
              fullWidth
              required
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
            />
            
            <TextField
              margin="normal"
              label="Current Amount"
              name="currentAmount"
              value={formData.currentAmount}
              onChange={handleInputChange}
              fullWidth
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
            />
            
            <Box sx={{ mt: 2 }}>
              <DatePicker
                label="Target Date"
                value={formData.targetDate}
                onChange={handleDateChange}
                slotProps={{ textField: { fullWidth: true } }}
                minDate={new Date()}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={handleSaveGoal}
              variant="contained"
              disabled={!formData.name || !formData.category || !formData.targetAmount || !formData.targetDate}
            >
              Save
            </Button>
          </DialogActions>
        </Dialog>
      </LocalizationProvider>
    </Container>
  );
};

export default Goals; 