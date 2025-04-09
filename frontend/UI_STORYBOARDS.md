# CougarWise UI Storyboards

## Overview
CougarWise is a financial management application designed for college students. The application features a maroon (CSU) and gold color scheme with a clean, modern UI built using React and Material UI.

## User Flows

### 1. New User Onboarding
1. **Landing Page** → User visits CougarWise for the first time
   - Hero section with app introduction
   - Benefits of using CougarWise
   - Call-to-action buttons: "Sign Up" and "Learn More"
   
2. **Registration Page** → User clicks "Sign Up"
   - Form with fields: Name, Email, Password, Confirm Password
   - Terms of service agreement checkbox
   - "Create Account" button
   - Link to "Already have an account? Log in"

3. **Initial Setup** → After successful registration
   - Welcome screen with brief tutorial option
   - Basic financial profile setup (optional)
   - Connect bank accounts (optional)

### 2. Authentication Flow
1. **Login Page** → Returning user logs in
   - Email/Username field
   - Password field
   - "Remember me" checkbox
   - "Log In" button
   - "Forgot Password?" link
   - "Create an account" link

2. **Dashboard Redirect** → After successful login
   - Redirect to main dashboard

### 3. Main Dashboard Experience
1. **Dashboard Page** → Central hub for all activities
   - Financial overview cards (spending summaries, account balances)
   - Recent transactions list
   - Budget status indicators
   - Financial goals progress
   - Quick action buttons

2. **Navigation** → Sidebar/Header navigation
   - Dashboard
   - Transactions
   - Budget
   - Goals
   - Analysis
   - AI Assistant
   - Profile/Settings
   - Logout

### 4. Transaction Management
1. **Transactions Page** → User manages transactions
   - Filterable transaction list
   - Search functionality
   - Date range selection
   - Category filters
   - Transaction details on click
   - Add manual transaction option
   - Export transactions feature

2. **Transaction Detail View** → User clicks on a transaction
   - Date, amount, merchant details
   - Category assignment
   - Notes/tags
   - Receipt upload option
   - Edit or delete options

### 5. Budget Management
1. **Budget Page** → User creates and manages budgets
   - Monthly overview with category breakdown
   - Progress bars for each category
   - Budget vs. actual spending comparisons
   - Create new budget category option
   - Adjust budget amounts
   - Budget alerts/notifications settings

2. **Category Detail View** → User clicks on a budget category
   - Detailed spending within category
   - Historical trends
   - Related transactions
   - Adjust budget limit

### 6. Financial Goals
1. **Goals Page** → User sets and tracks financial goals
   - Active goals cards with progress indicators
   - Completed goals section
   - "Create New Goal" button
   - Goal timeline visualization

2. **Goal Creation/Edit** → User creates or edits a goal
   - Goal name/description
   - Target amount
   - Timeline/deadline
   - Contribution schedule
   - Linked accounts
   - Visual progress tracker

### 7. Financial Analysis
1. **Analysis Page** → User views financial insights
   - Spending trends charts
   - Income vs. expenses
   - Category breakdown pie charts
   - Monthly comparisons
   - Savings rate
   - Custom date range selector
   - Export reports option

### 8. AI Financial Assistant
1. **AI Assistant Page** → User interacts with financial assistant
   - Chat interface
   - Quick question templates
   - Financial advice based on spending patterns
   - Budget optimization suggestions
   - Goal progress feedback
   - Educational resources

### 9. User Profile Management
1. **Profile Page** → User manages account settings
   - Personal information
   - Connected accounts
   - Notification preferences
   - Security settings
   - Theme preferences
   - Privacy settings
   - Data export/import options

## UI Components

### Common Elements
- **Header Bar**: Logo, search, notifications, user avatar
- **Navigation Sidebar**: Main menu items with icons
- **Footer**: Links to help, about, terms of service, privacy policy
- **Modals**: For confirmations, quick edits, alerts
- **Cards**: For displaying financial summaries and actions
- **Charts**: For visualizing financial data
- **Tables**: For displaying transaction lists and data
- **Forms**: For data entry with validation

### Visual Design Elements
- **Color Scheme**: CSU Maroon (#800000) primary, Gold (#FFD700) secondary
- **Typography**: Roboto font family with varying weights
- **Spacing**: Consistent padding and margins for readability
- **Responsive Design**: Adapts to desktop, tablet, and mobile devices
- **Animation**: Subtle transitions for improved user experience
- **Iconography**: Consistent icon set for navigation and actions

## Responsive Considerations
- Desktop: Full feature set with multi-column layouts
- Tablet: Adapted layouts with some content reordering
- Mobile: Simplified views with bottom navigation, collapsible sections

## Accessibility Features
- High contrast text options
- Screen reader compatibility
- Keyboard navigation support
- Customizable text size
- Focus indicators for keyboard users 