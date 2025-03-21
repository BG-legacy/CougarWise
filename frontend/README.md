# CougarWise Frontend

A React-based frontend for the CougarWise application, a financial management system for CSU students.

## Features

- User authentication (login/registration)
- Dashboard with financial overview
- Transaction tracking and management
- Budget planning and monitoring
- Financial goal setting and tracking
- Financial analysis and insights
- AI-powered financial assistant

## Tech Stack

- React - Frontend library
- React Router - Navigation and routing
- Material UI - UI component library
- Chart.js - Data visualization
- Axios - API communication

## Prerequisites

- Node.js (v14+)
- npm or yarn
- CougarWise backend server running

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CougarWise/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
Create a `.env` file in the frontend directory with the following content:
```
REACT_APP_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm start
```

The application will be available at http://localhost:3000.

## Project Structure

```
frontend/
├── public/             # Static files
├── src/                # Source code
│   ├── components/     # Reusable UI components
│   ├── context/        # React context providers
│   ├── hooks/          # Custom React hooks
│   ├── pages/          # Page components
│   ├── services/       # API service functions
│   └── utils/          # Utility functions
├── package.json        # Dependencies and scripts
└── README.md           # Documentation
```

## Available Scripts

- `npm start` - Start development server
- `npm test` - Run tests
- `npm run build` - Build for production
- `npm run eject` - Eject from Create React App

## Connecting to the Backend

The frontend is configured to connect to the backend at `http://localhost:8000`. If your backend is running on a different URL, update the `REACT_APP_API_URL` in the `.env` file.

## Pages

- **Login/Register** - User authentication
- **Dashboard** - Overview of financial data
- **Transactions** - Transaction management
- **Budget** - Budget planning and tracking
- **Goals** - Financial goal setting and tracking
- **Analysis** - Financial data analysis
- **AI Assistant** - AI-powered financial advice

## License

This project is part of the CougarWise application suite for the CSU Senior Software Engineering Project.
