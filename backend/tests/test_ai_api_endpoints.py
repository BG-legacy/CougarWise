#!/usr/bin/env python3
"""
Test suite for CougarWise AI API endpoints.
These tests verify that the AI API endpoints correctly interact with the AI components
and handle various scenarios including success cases and error handling.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

# Add parent directory to path to allow importing from the backend package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the API module for testing
from api.API import app

# Create test client
client = TestClient(app)

@pytest.fixture
def mock_ai_assistant():
    """Create a mock AI assistant for testing."""
    with patch('api.API.ai_assistant') as mock_assistant:
        # Configure success responses for each method
        mock_assistant.process_user_query.return_value = {
            'status': 'success',
            'response': 'Here are some budgeting tips for college students...'
        }
        
        mock_assistant.get_spending_advice.return_value = {
            'status': 'success',
            'predictions': {
                'total': 1500,
                'categories': {'food': 400, 'housing': 700, 'other': 400}
            },
            'advice': {
                'advice': 'You should try to reduce your food expenses.',
                'savings_tips': ['Cook at home', 'Use student discounts'],
                'budget_allocation': {'food': '25%', 'housing': '45%', 'other': '30%'}
            }
        }
        
        mock_assistant.generate_budget_template.return_value = {
            'status': 'success',
            'template': {
                'income': {
                    'monthly_income': 1800,
                    'financial_aid': 625  # Monthly equivalent of $7500/year
                },
                'expenses': {
                    'housing': 700,
                    'food': 350,
                    'transportation': 150,
                    'entertainment': 100,
                    'education': 200,
                    'savings': 300
                }
            }
        }
        
        mock_assistant.analyze_financial_goals.return_value = {
            'status': 'success',
            'analysis': [
                {
                    'goal': 'Save $5000 for a new laptop',
                    'feasibility': 'Achievable in 17 months',
                    'recommendations': ['Save $300 per month', 'Consider part-time work']
                },
                {
                    'goal': 'Pay off $2000 in credit card debt',
                    'feasibility': 'Achievable in 7 months',
                    'recommendations': ['Pay $300 per month', 'Reduce interest by transferring balance']
                }
            ]
        }
        
        yield mock_assistant

@pytest.fixture
def mock_ai_assistant_error():
    """Create a mock AI assistant that raises exceptions for testing error handling."""
    with patch('api.API.ai_assistant') as mock_assistant:
        # Configure all methods to raise exceptions
        mock_assistant.process_user_query.side_effect = Exception("Error processing query")
        mock_assistant.get_spending_advice.side_effect = Exception("Error generating spending advice")
        mock_assistant.generate_budget_template.side_effect = Exception("Error generating budget template")
        mock_assistant.analyze_financial_goals.side_effect = Exception("Error analyzing financial goals")
        
        yield mock_assistant

@pytest.fixture
def sample_user_profile():
    """Sample user profile data for testing."""
    return {
        "year_in_school": "Junior",
        "major": "Engineering",
        "monthly_income": 1800,
        "financial_aid": 7500,
        "age": 21,
        "gender": "Female",
        "preferred_payment_method": "Debit Card"
    }

class TestAIQueryEndpoint:
    """Test suite for the /ai/query endpoint."""
    
    def test_process_query_success(self, mock_ai_assistant):
        """Test successful query processing."""
        # Test data
        query_data = {
            "query": "What are some good budgeting tips for college students?",
            "user_context": {
                "year_in_school": "Sophomore",
                "major": "Computer Science"
            }
        }
        
        # Send request to the endpoint
        response = client.post("/ai/query", json=query_data)
        
        # Assertions
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        assert 'response' in response.json()
        assert "budgeting tips" in response.json()['response'].lower()
        
        # Verify the mock was called with the right arguments
        mock_ai_assistant.process_user_query.assert_called_once_with(
            query_data['query'], 
            query_data['user_context']
        )
    
    def test_process_query_with_no_context(self, mock_ai_assistant):
        """Test query processing with no user context."""
        # Test data
        query_data = {
            "query": "How do I create a budget?"
        }
        
        # Send request to the endpoint
        response = client.post("/ai/query", json=query_data)
        
        # Assertions
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        
        # Verify the mock was called with the right arguments
        mock_ai_assistant.process_user_query.assert_called_once_with(
            query_data['query'], 
            None
        )
    
    def test_process_query_error(self, mock_ai_assistant_error):
        """Test error handling in query processing."""
        # Test data
        query_data = {
            "query": "What's the best way to save money?"
        }
        
        # Send request to the endpoint
        response = client.post("/ai/query", json=query_data)
        
        # Assertions
        assert response.status_code == 500
        assert "Error processing query" in response.json()['detail']

class TestAISpendingAdviceEndpoint:
    """Test suite for the /ai/spending-advice endpoint."""
    
    def test_spending_advice_success(self, mock_ai_assistant, sample_user_profile):
        """Test successful spending advice generation."""
        # Send request to the endpoint
        response = client.post("/ai/spending-advice", json=sample_user_profile)
        
        # Assertions
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        assert 'predictions' in response.json()
        assert 'advice' in response.json()
        
        # Verify the mock was called with the right arguments
        mock_ai_assistant.get_spending_advice.assert_called_once()
    
    def test_spending_advice_error(self, mock_ai_assistant_error, sample_user_profile):
        """Test error handling in spending advice generation."""
        # Send request to the endpoint
        response = client.post("/ai/spending-advice", json=sample_user_profile)
        
        # Assertions
        assert response.status_code == 500
        assert "Error getting spending advice" in response.json()['detail']

class TestAIBudgetTemplateEndpoint:
    """Test suite for the /ai/budget-template endpoint."""
    
    def test_budget_template_success(self, mock_ai_assistant, sample_user_profile):
        """Test successful budget template generation."""
        # Send request to the endpoint
        response = client.post("/ai/budget-template", json=sample_user_profile)
        
        # Assertions
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        assert 'template' in response.json()
        
        # Verify the mock was called with the right arguments
        mock_ai_assistant.generate_budget_template.assert_called_once()
    
    def test_budget_template_error(self, mock_ai_assistant_error, sample_user_profile):
        """Test error handling in budget template generation."""
        # Send request to the endpoint
        response = client.post("/ai/budget-template", json=sample_user_profile)
        
        # Assertions
        assert response.status_code == 500
        assert "Error generating budget template" in response.json()['detail']

class TestAIFinancialGoalsEndpoint:
    """Test suite for the /ai/analyze-goals endpoint."""
    
    def test_analyze_goals_success(self, mock_ai_assistant):
        """Test successful financial goals analysis."""
        # Test data
        goals_data = {
            "goals": [
                "Save $5000 for a new laptop",
                "Pay off $2000 in credit card debt"
            ],
            "user_context": {
                "monthly_income": 1800,
                "monthly_expenses": 1200
            }
        }
        
        # Send request to the endpoint
        response = client.post("/ai/analyze-goals", json=goals_data)
        
        # Assertions
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        assert 'analysis' in response.json()
        assert len(response.json()['analysis']) == 2
        
        # Verify the mock was called with the right arguments
        mock_ai_assistant.analyze_financial_goals.assert_called_once_with(
            goals_data['goals'],
            goals_data['user_context']
        )
    
    def test_analyze_goals_error(self, mock_ai_assistant_error):
        """Test error handling in financial goals analysis."""
        # Test data
        goals_data = {
            "goals": ["Build an emergency fund"],
            "user_context": {"monthly_income": 1500}
        }
        
        # Send request to the endpoint
        response = client.post("/ai/analyze-goals", json=goals_data)
        
        # Assertions
        assert response.status_code == 500
        assert "Error analyzing financial goals" in response.json()['detail']

@pytest.mark.parametrize("endpoint", [
    "/ai/query",
    "/ai/spending-advice",
    "/ai/budget-template",
    "/ai/analyze-goals"
])
@patch('api.API.AI_AVAILABLE', False)
def test_ai_endpoints_when_ai_unavailable(endpoint):
    """Test that AI endpoints return appropriate error when AI is not available."""
    # Sample data for each endpoint
    sample_data = {
        "/ai/query": {"query": "How do I save money?"},
        "/ai/spending-advice": {"year_in_school": "Junior", "major": "Engineering", "monthly_income": 1800, "financial_aid": 7500},
        "/ai/budget-template": {"year_in_school": "Junior", "major": "Engineering", "monthly_income": 1800, "financial_aid": 7500},
        "/ai/analyze-goals": {"goals": ["Save money"], "user_context": {"monthly_income": 1500}}
    }
    
    # Send request to the endpoint
    response = client.post(endpoint, json=sample_data[endpoint])
    
    # Assertions
    assert response.status_code == 503
    assert response.json()['detail'] == "AI features are not available"

class TestOpenAIConfigBehavior:
    """Test class for verifying endpoint behavior based on OpenAI configuration."""
    
    @patch('api.API.AI_AVAILABLE', True)
    def test_ai_query_endpoint_with_ai_available(self, mock_ai_assistant):
        """Test that AI query endpoint works when AI is available."""
        # Arrange
        query = "How do I create a budget?"
        user_context = {"year_in_school": "Freshman", "monthly_income": 1000}
        
        # Act
        response = client.post(
            "/ai/query",
            json={"query": query, "user_context": user_context}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "response" in data
        
    @patch('api.API.AI_AVAILABLE', False)
    def test_ai_query_endpoint_with_ai_unavailable(self):
        """Test that AI query endpoint returns appropriate message when AI is disabled."""
        # Arrange
        query = "How do I create a budget?"
        
        # Act
        response = client.post(
            "/ai/query",
            json={"query": query}
        )
        
        # Assert
        assert response.status_code == 503  # Service Unavailable
        # Check the structure of the error response, which appears to be using FastAPI's default format
        data = response.json()
        assert "detail" in data
        assert "AI features are not available" in data["detail"]
    
    @patch('api.API.AI_AVAILABLE', True)
    @patch('api.API.ai_assistant.openai_api_key', None)  # Simulate missing API key
    def test_ai_query_endpoint_with_missing_api_key(self):
        """Test that AI query endpoint handles missing API key correctly."""
        # Arrange - mock the process_user_query to return an error response
        with patch('api.API.ai_assistant.process_user_query') as mock_process_query:
            mock_process_query.return_value = {
                "status": "error",
                "error": "OpenAI API key not set",
                "response": "Sorry, I'm not able to process your request at the moment."
            }
            
            # Act
            query = "How do I create a budget?"
            response = client.post(
                "/ai/query",
                json={"query": query}
            )
            
            # Assert - the server should not return 500 but instead pass through the error from the AI component
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert "OpenAI API key not set" in data["error"]
    
    @patch('api.API.AI_AVAILABLE', True)
    @patch('openai.OpenAI')
    def test_ai_endpoint_with_rate_limit_error(self, mock_openai_client, mock_ai_assistant):
        """Test AI endpoint behavior when OpenAI rate limit is exceeded."""
        # Arrange
        mock_client = MagicMock()
        mock_openai_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        
        # Override the mock_ai_assistant to use our custom mock - but return a properly formatted error
        mock_ai_assistant.process_user_query.return_value = {
            "status": "error",
            "error": "Rate limit exceeded",
            "response": "I apologize, but I encountered an error processing your request."
        }
        
        # Act
        response = client.post(
            "/ai/query",
            json={"query": "How do I budget?"}
        )
        
        # Assert
        # The API should return 200 but with error status since it handled the rate limit gracefully
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Rate limit exceeded" in data["error"]

# Run the tests if the script is executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 