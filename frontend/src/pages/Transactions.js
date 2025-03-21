import React, { useState, useEffect, useContext, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  CircularProgress,
  IconButton,
  Alert,
  Chip
} from '@mui/material';
import { 
  Add as AddIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AuthContext from '../context/AuthContext';
import { getUserTransactions, createTransaction } from '../services/transactionService';

// Create a custom event for budget updates
export const BUDGET_UPDATE_EVENT = 'budgetUpdate';

// Transaction categories
const CATEGORIES = [
  'Housing',
  'Food',
  'Transportation',
  'Utilities',
  'Education',
  'Entertainment',
  'Health',
  'Shopping',
  'Personal',
  'Income',
  'Other'
];

const Transactions = () => {
  const { currentUser } = useContext(AuthContext);
  
  // State for transactions data
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for table pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // State for filters
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  
  // State for transaction dialog
  const [openDialog, setOpenDialog] = useState(false);
  const [newTransaction, setNewTransaction] = useState({
    amount: '',
    category: '',
    description: '',
    date: new Date()
  });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  // Memoize the fetch function to fix dependency warning
  const fetchTransactions = useCallback(async () => {
    if (!currentUser) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await getUserTransactions(currentUser.id);
      // The API returns the array directly, not inside a data property
      setTransactions(response || []);
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setError('Failed to load transactions. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [currentUser]);

  // Fetch transactions on component mount
  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  // Handle transaction form field changes
  const handleTransactionChange = (e) => {
    const { name, value } = e.target;
    setNewTransaction(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle date change for new transaction
  const handleDateChange = (date) => {
    setNewTransaction(prev => ({
      ...prev,
      date
    }));
  };

  // Handle dialog open/close
  const handleOpenDialog = () => {
    setOpenDialog(true);
    setFormError('');
    setNewTransaction({
      amount: '',
      category: '',
      description: '',
      date: new Date()
    });
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  // Handle submit new transaction
  const handleSubmitTransaction = async () => {
    // Validate form
    if (!newTransaction.amount || !newTransaction.category || !newTransaction.description) {
      setFormError('Please fill in all required fields');
      return;
    }
    
    setSubmitting(true);
    setFormError('');
    
    try {
      const transactionData = {
        user_id: currentUser.id,
        amount: parseFloat(newTransaction.amount),
        category: newTransaction.category,
        description: newTransaction.description,
        date: newTransaction.date.toISOString()
      };
      
      const response = await createTransaction(transactionData);
      
      // Add new transaction to state
      if (response && response.id) {
        // Ensure response has all the expected fields in the correct format
        setTransactions(prev => [{
          id: response.id,
          user_id: response.user_id || currentUser.id,
          amount: response.amount,
          category: response.category,
          description: response.description,
          date: response.date
        }, ...prev]);
        
        // Dispatch custom event to notify other components that budgets need to be refreshed
        window.dispatchEvent(new CustomEvent(BUDGET_UPDATE_EVENT));
      }
      
      // Close dialog
      handleCloseDialog();
    } catch (error) {
      console.error('Error creating transaction:', error);
      setFormError('Failed to create transaction. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle pagination changes
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle filter clear
  const handleClearFilters = () => {
    setSearchTerm('');
    setCategoryFilter('');
    setStartDate(null);
    setEndDate(null);
  };

  // Filter transactions based on search and filters
  const filteredTransactions = transactions.filter(transaction => {
    // Search term filter
    const matchesSearch = searchTerm === '' || 
      transaction.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Category filter
    const matchesCategory = categoryFilter === '' || 
      transaction.category === categoryFilter;
    
    // Date range filter
    let matchesDateRange = true;
    if (startDate) {
      matchesDateRange = matchesDateRange && new Date(transaction.date) >= startDate;
    }
    if (endDate) {
      matchesDateRange = matchesDateRange && new Date(transaction.date) <= endDate;
    }
    
    return matchesSearch && matchesCategory && matchesDateRange;
  });

  // Paginate transactions
  const paginatedTransactions = filteredTransactions.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  // Loading state
  if (loading && transactions.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Transactions
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenDialog}
        >
          Add Transaction
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
          <TextField
            label="Search"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ flexGrow: 1, minWidth: '200px' }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: searchTerm && (
                <InputAdornment position="end">
                  <IconButton size="small" onClick={() => setSearchTerm('')}>
                    <ClearIcon />
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
          
          <FormControl size="small" sx={{ minWidth: '150px' }}>
            <InputLabel id="category-filter-label">Category</InputLabel>
            <Select
              labelId="category-filter-label"
              id="category-filter"
              value={categoryFilter}
              label="Category"
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <MenuItem value="">All Categories</MenuItem>
              {CATEGORIES.map(category => (
                <MenuItem key={category} value={category}>{category}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="From"
              value={startDate}
              onChange={setStartDate}
              slotProps={{ textField: { size: 'small' } }}
            />
            
            <DatePicker
              label="To"
              value={endDate}
              onChange={setEndDate}
              slotProps={{ textField: { size: 'small' } }}
            />
          </LocalizationProvider>
          
          <Button
            variant="outlined"
            startIcon={<ClearIcon />}
            onClick={handleClearFilters}
            disabled={!searchTerm && !categoryFilter && !startDate && !endDate}
          >
            Clear Filters
          </Button>
        </Box>
      </Paper>

      {/* Transactions Table */}
      <Paper>
        <TableContainer>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Category</TableCell>
                <TableCell align="right">Amount</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedTransactions.length > 0 ? (
                paginatedTransactions.map((transaction) => (
                  <TableRow key={transaction.id} hover>
                    <TableCell>{new Date(transaction.date).toLocaleDateString()}</TableCell>
                    <TableCell>{transaction.description}</TableCell>
                    <TableCell>
                      <Chip
                        label={transaction.category}
                        size="small"
                        color={transaction.amount < 0 ? 'default' : 'success'}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                        {transaction.amount < 0 ? (
                          <TrendingDownIcon color="error" sx={{ mr: 1 }} fontSize="small" />
                        ) : (
                          <TrendingUpIcon color="success" sx={{ mr: 1 }} fontSize="small" />
                        )}
                        <Typography
                          variant="body2"
                          color={transaction.amount < 0 ? 'error' : 'success.main'}
                          sx={{ fontWeight: 'medium' }}
                        >
                          {formatCurrency(Math.abs(transaction.amount))}
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    {filteredTransactions.length === 0 && transactions.length > 0 ? (
                      'No transactions match your search criteria'
                    ) : (
                      'No transactions found. Add your first transaction!'
                    )}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredTransactions.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      {/* Add Transaction Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Transaction</DialogTitle>
        <DialogContent>
          {formError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {formError}
            </Alert>
          )}
          
          <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              required
              label="Amount"
              name="amount"
              value={newTransaction.amount}
              onChange={handleTransactionChange}
              type="number"
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
              fullWidth
              margin="dense"
              disabled={submitting}
            />
            
            <FormControl fullWidth required margin="dense">
              <InputLabel>Category</InputLabel>
              <Select
                name="category"
                value={newTransaction.category}
                onChange={handleTransactionChange}
                label="Category"
                disabled={submitting}
              >
                {CATEGORIES.map(category => (
                  <MenuItem key={category} value={category}>{category}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              required
              label="Description"
              name="description"
              value={newTransaction.description}
              onChange={handleTransactionChange}
              fullWidth
              margin="dense"
              disabled={submitting}
            />
            
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Date"
                value={newTransaction.date}
                onChange={handleDateChange}
                disabled={submitting}
                slotProps={{ textField: { fullWidth: true, margin: 'dense' } }}
              />
            </LocalizationProvider>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={submitting}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmitTransaction} 
            variant="contained" 
            disabled={submitting}
          >
            {submitting ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Transactions; 