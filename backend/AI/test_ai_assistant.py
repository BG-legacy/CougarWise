#!/usr/bin/env python3
# Test script for WebsiteAIAssistant

import pytest
from AI.website_ai_assistant import WebsiteAIAssistant

def test_initialization():
    """Test that the AI assistant can be initialized."""
    assistant = WebsiteAIAssistant()
    assert assistant is not None
    assert hasattr(assistant, 'spending_analyzer')

def test_process_user_query():
    """Test the process_user_query method."""
    # Create an instance of the AI assistant
    assistant = WebsiteAIAssistant()
    
    # Test query processing
    query = "What are some good budgeting tips for college students?"
    user_context = {
        "year_in_school": "Sophomore",
        "major": "Computer Science",
        "monthly_income": 1200,
        "financial_aid": 5000
    }
    
    response = assistant.process_user_query(query, user_context)
    assert response is not None
    assert 'status' in response
    assert 'response' in response
    assert response['status'] == 'success'

def test_get_spending_advice():
    """Test the get_spending_advice method."""
    # Create an instance of the AI assistant
    assistant = WebsiteAIAssistant()
    
    # Test spending advice
    user_data = {
        "age": 20,
        "gender": "Male",
        "year_in_school": "Junior",
        "major": "Business",
        "monthly_income": 1500,
        "financial_aid": 3000,
        "tuition": 10000,
        "preferred_payment_method": "Credit Card"
    }
    
    advice = assistant.get_spending_advice(user_data)
    assert advice is not None
    assert 'status' in advice
    assert advice['status'] == 'success'
    assert 'predictions' in advice
    assert 'advice' in advice

def test_get_budget_template():
    """Test the get_budget_template method."""
    # Create an instance of the AI assistant
    assistant = WebsiteAIAssistant()
    
    # Test budget template
    user_context = {
        "year_in_school": "Sophomore",
        "major": "Computer Science",
        "monthly_income": 1200,
        "financial_aid": 5000
    }
    
    budget_template = assistant.get_budget_template(user_context)
    assert budget_template is not None
    assert 'status' in budget_template
    assert budget_template['status'] == 'success'
    assert 'template' in budget_template

if __name__ == "__main__":
    pytest.main() 