# CougarWise
![alt text](https://file%2B.vscode-resource.vscode-cdn.net/Users/bernardginnjr./Desktop/Screenshot%202025-03-20%20at%209.39.47%E2%80%AFPM.png?version%3D1742521226755)

CougarWise is a comprehensive financial management system designed specifically for CSU students to help them manage their finances, track spending, set budgets, and receive AI-powered financial advice.

## Project Overview

CougarWise consists of two main components:

1. **Frontend**: A React-based web application that provides an intuitive user interface for students to interact with their financial data
2. **Backend**: A FastAPI server that handles data processing, AI analysis, and database operations

## Tech Stack

### Frontend

- **React 19**: Modern JavaScript library for building user interfaces
- **React Router 7**: For navigation and routing between different app sections
- **Material UI 6**: Component library that implements Google's Material Design for consistent and attractive UI
- **Chart.js/React-Chartjs-2**: For visualizing financial data with interactive charts
- **Axios**: Promise-based HTTP client for making API requests
- **Framer Motion**: For adding smooth animations and transitions

**Why This Stack?**
- React provides a component-based architecture allowing for reusable UI elements and efficient rendering
- Material UI ensures a professional-looking interface with minimal custom CSS required
- Chart.js makes it easy to create interactive visualizations for financial data
- This combination delivers a modern, responsive application that works well across devices

### Backend

- **FastAPI**: High-performance web framework for building APIs with Python
- **MongoDB**: NoSQL database for flexible and scalable data storage
- **OpenAI**: Integration for AI-powered financial advice
- **TensorFlow/Scikit-learn**: Machine learning libraries for spending analysis and financial pattern recognition
- **Pandas/NumPy**: Data manipulation and analysis
- **pytest**: For comprehensive backend testing

**Why This Stack?**
- FastAPI provides excellent performance, automatic API documentation, and data validation
- MongoDB's flexible schema works well for evolving data requirements and different types of financial information
- Python's rich ecosystem of data science libraries enables sophisticated analysis of student spending patterns
- The AI components can provide personalized financial guidance based on student data

## Key Features

- User authentication and profile management
- Transaction tracking and categorization
- Budget planning and monitoring
- Financial goal setting and progress tracking
- AI-powered spending analysis and insights
- Personalized financial recommendations
- Visual reporting of financial data

## Project Structure

```
CougarWise/
├── frontend/              # React frontend application
│   ├── public/            # Static files
│   ├── src/               # Source code
│   │   ├── components/    # Reusable UI components
│   │   ├── context/       # React context providers
│   │   ├── pages/         # Page components
│   │   └── services/      # API service functions
│   └── package.json       # Dependencies and scripts
│
├── backend/               # Python backend server
│   ├── api/               # FastAPI application
│   ├── AI/                # AI and machine learning components
│   │   ├── student_spending_analysis.py  # Spending analysis model
│   │   └── website_ai_assistant.py       # AI assistant
│   ├── Database/          # Database models and connection
│   └── tests/             # Backend test suite
```

## Getting Started

### Backend Setup

1. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Then edit the .env file with your actual values, especially the OpenAI API key.

4. Start the backend server:
   ```
   python run.py
   ```

### Frontend Setup

1. Install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Configure environment:
   Create a `.env` file in the frontend directory:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

3. Start the development server:
   ```
   npm start
   ```

The frontend will be available at http://localhost:3000, and it will connect to the backend at http://localhost:8000.