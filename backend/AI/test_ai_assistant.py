#!/usr/bin/env python3
# Test script for WebsiteAIAssistant

from website_ai_assistant import WebsiteAIAssistant

def main():
    # Create an instance of the AI assistant
    print("Initializing AI Assistant...")
    assistant = WebsiteAIAssistant()
    
    # Test the process_user_query method
    print("\nTesting basic query processing:")
    query = "What are some good budgeting tips for college students?"
    user_context = {
        "year_in_school": "Sophomore",
        "major": "Computer Science",
        "monthly_income": 1200,
        "financial_aid": 5000
    }
    
    response = assistant.process_user_query(query, user_context)
    print(f"Status: {response['status']}")
    print(f"Response: {response['response']}")
    
    # Test the get_spending_advice method
    print("\nTesting spending advice:")
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
    
    try:
        advice = assistant.get_spending_advice(user_data)
        print(f"Status: {advice['status']}")
        if advice['status'] == 'success':
            print("Predictions:")
            for category, amount in advice['predictions'].items():
                print(f"  {category}: ${amount:.2f}")
            print(f"\nAdvice: {advice['advice']}")
        else:
            print(f"Error: {advice.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error testing spending advice: {e}")
    
    # Test the get_budget_template method
    print("\nTesting budget template:")
    budget_template = assistant.get_budget_template(user_context)
    print(f"Status: {budget_template['status']}")
    if budget_template['status'] == 'success':
        print(f"Template: {budget_template['template']}")
    else:
        print(f"Error: {budget_template.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 