// Import React and necessary hooks
import React, { useState, useContext } from 'react';
// Import routing components from react-router-dom
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
// Import Material-UI components for layout and UI elements
import {
  AppBar, // Top navigation bar
  Box, // Flexible container component
  CssBaseline, // Normalize CSS across browsers
  Divider, // Visual separator
  Drawer, // Side navigation panel
  IconButton, // Button with an icon
  List, // Container for list items
  ListItem, // Individual list item
  ListItemButton, // Makes list item clickable
  ListItemIcon, // Container for icon in list item
  ListItemText, // Text content of list item
  Toolbar, // Container for app bar content
  Typography, // Text component with controlled typography
  Menu, // Dropdown menu component
  MenuItem, // Individual item in menu
  Avatar, // User profile picture/icon
  useMediaQuery, // Hook to check screen size for responsiveness
  useTheme // Hook to access theme object
} from '@mui/material';
// Import Material-UI icons for navigation and actions
import {
  Menu as MenuIcon, // Hamburger menu icon
  Dashboard as DashboardIcon, // Icon for dashboard
  Receipt as ReceiptIcon, // Icon for transactions
  AccountBalance as AccountBalanceIcon, // Icon for budget
  EmojiEvents as EmojiEventsIcon, // Icon for goals
  ShowChart as ShowChartIcon, // Icon for analysis
  QuestionAnswer as QuestionAnswerIcon, // Icon for AI assistant
  Person as PersonIcon, // Icon for profile
  Logout as LogoutIcon // Icon for logout
} from '@mui/icons-material';
// Import authentication context for user state management
import AuthContext from '../context/AuthContext';

// Define drawer width for consistent sizing
const drawerWidth = 240;

// Main layout component that wraps dashboard pages
const Layout = () => {
  // Access user data and logout function from AuthContext
  const { currentUser, logout } = useContext(AuthContext);
  // Access theme for responsive design
  const theme = useTheme();
  // Hook for programmatic navigation
  const navigate = useNavigate();
  // Hook to access current location/URL
  const location = useLocation();
  // Check if device is mobile for responsive behavior
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // State to control drawer open/close on mobile
  const [mobileOpen, setMobileOpen] = useState(false);
  // State to control user menu (avatar menu) position
  const [anchorEl, setAnchorEl] = useState(null);

  // Toggle drawer visibility on mobile
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Open user menu with clicked element as anchor
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  // Close user menu
  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Handle user logout action
  const handleLogout = () => {
    handleMenuClose(); // Close menu first
    logout(); // Call logout function from AuthContext
    navigate('/login'); // Redirect to login page
  };

  // Handle navigation to different routes
  const handleNavigation = (path) => {
    navigate(path); // Navigate to selected path
    if (isMobile) {
      setMobileOpen(false); // Close drawer on mobile after navigation
    }
  };

  // Navigation items configuration with text, route path, and icon
  const navItems = [
    { text: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
    { text: 'Transactions', path: '/dashboard/transactions', icon: <ReceiptIcon /> },
    { text: 'Budget', path: '/dashboard/budget', icon: <AccountBalanceIcon /> },
    { text: 'Goals', path: '/dashboard/goals', icon: <EmojiEventsIcon /> },
    { text: 'Analysis', path: '/dashboard/analysis', icon: <ShowChartIcon /> },
    { text: 'AI Assistant', path: '/dashboard/assistant', icon: <QuestionAnswerIcon /> },
  ];

  // Drawer content definition reused in both temporary and permanent drawers
  const drawer = (
    <Box>
      <Toolbar>
        {/* App title in drawer header */}
        <Typography variant="h6" noWrap component="div">
          CougarWise
        </Typography>
      </Toolbar>
      <Divider /> {/* Visual separator between header and navigation */}
      <List>
        {/* Map navigation items to list items */}
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton 
              selected={location.pathname === item.path} // Highlight current route
              onClick={() => handleNavigation(item.path)} // Navigate on click
            >
              <ListItemIcon>
                {item.icon} {/* Display appropriate icon */}
              </ListItemIcon>
              <ListItemText primary={item.text} /> {/* Display navigation text */}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  // Return the complete layout structure
  return (
    <Box sx={{ display: 'flex' }}> {/* Root container with flex layout */}
      <CssBaseline /> {/* Normalize CSS */}
      <AppBar
        position="fixed" // Fixed position at top of viewport
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` }, // Adjust width for non-mobile
          ml: { sm: `${drawerWidth}px` }, // Push to the right on non-mobile to make room for drawer
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle} // Toggle drawer on click
            sx={{ mr: 2, display: { sm: 'none' } }} // Only show on mobile
          >
            <MenuIcon /> {/* Hamburger menu icon */}
          </IconButton>
          <Typography
            variant="h6"
            component="div"
            sx={{ flexGrow: 1 }} // Take available space to push avatar to right
          >
            {/* Dynamic title based on current route */}
            {navItems.find(item => 
              location.pathname === item.path || 
              (location.pathname === '/dashboard' && item.path === '/dashboard')
            )?.text || 'CougarWise'}
          </Typography>
          
          <IconButton
            onClick={handleMenuOpen} // Open user menu on click
            size="large"
            edge="end"
            color="inherit"
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
              {/* Display first letter of username or fallback to 'U' */}
              {currentUser?.username?.charAt(0)?.toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl} // Position relative to avatar button
            open={Boolean(anchorEl)} // Show when anchorEl is set
            onClose={handleMenuClose} // Close on outside click
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem onClick={() => {
              handleMenuClose(); // Close menu
              navigate('/dashboard/profile'); // Navigate to profile page
            }}>
              <ListItemIcon>
                <PersonIcon fontSize="small" />
              </ListItemIcon>
              Profile
            </MenuItem>
            <MenuItem onClick={handleLogout}> {/* Logout action */}
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }} // Fixed width on non-mobile
      >
        <Drawer
          variant="temporary" // Temporary drawer for mobile
          open={mobileOpen} // Controlled by mobileOpen state
          onClose={handleDrawerToggle} // Close on outside click
          ModalProps={{
            keepMounted: true, // Better mobile performance by keeping in DOM
          }}
          sx={{
            display: { xs: 'block', sm: 'none' }, // Only visible on mobile
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth }, // Set drawer width
          }}
        >
          {drawer} {/* Render drawer content */}
        </Drawer>
        <Drawer
          variant="permanent" // Always visible on non-mobile
          sx={{
            display: { xs: 'none', sm: 'block' }, // Only visible on non-mobile
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth }, // Set drawer width
          }}
          open
        >
          {drawer} {/* Render drawer content */}
        </Drawer>
      </Box>
      <Box
        component="main" // Main content area
        sx={{ 
          flexGrow: 1, // Take available space
          p: 3, // Padding
          width: { sm: `calc(100% - ${drawerWidth}px)` }, // Adjust width for non-mobile
          minHeight: '100vh', // Full viewport height
          backgroundColor: 'background.default' // Use theme background color
        }}
      >
        <Toolbar /> {/* Empty toolbar to push content below AppBar */}
        <Outlet /> {/* Render child routes here */}
      </Box>
    </Box>
  );
};

export default Layout; // Export component for use in app