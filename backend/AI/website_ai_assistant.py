# Import required libraries for API interaction, typing, and environment variables
import openai
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from student_spending_analysis import StudentSpendingAnalysis

# Load environment variables from .env file
load_dotenv()

class WebsiteAIAssistant:
    def __init__(self):
        # Initialize API key from environment variables
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        # Create instance of spending analysis model
        self.spending_analyzer = StudentSpendingAnalysis()
        # Set OpenAI API key for all future requests
        openai.api_key = self.openai_api_key
        
        # Try to train the spending model, with error handling
        try:
            self.spending_analyzer.train_model()
        except Exception as e:
            print(f"Warning: Could not train spending model: {e}")
            self.spending_analyzer = None

    def process_user_query(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user queries and generate appropriate responses using GPT-4
        Args:
            query: The user's question or request
            user_context: Optional dictionary containing user information
        Returns:
            Dictionary containing the AI response and status
        """
        try:
            # Define the AI assistant's role and capabilities through system context
            system_context = """
            You are a helpful AI assistant for a student financial website. You can:
            1. Provide financial advice
            2. Answer questions about student spending
            3. Explain financial concepts
            4. Give budgeting tips
            Please be concise, specific, and student-friendly in your responses.
            """

            # Build context string from user information if available
            context_str = ""
            if user_context:
                context_str = f"\nUser Context:\n"
                # Format each piece of user context as a bullet point
                for key, value in user_context.items():
                    context_str += f"- {key}: {value}\n"

            # Make API call to OpenAI's GPT model
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Use GPT-4 for high-quality responses
                messages=[
                    {"role": "system", "content": system_context},  # Set AI behavior
                    {"role": "user", "content": f"{context_str}\nUser Query: {query}"}  # Combine context and query
                ]
            )

            # Return successful response with generated content
            return {
                "response": response.choices[0].message.content,
                "status": "success"
            }

        except Exception as e:
            # Return error response if any exception occurs
            return {
                "response": "I apologize, but I encountered an error processing your request.",
                "status": "error",
                "error": str(e)
            }

    def get_spending_advice(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized spending advice using the spending model and GPT
        """
        try:
            # Check if spending analyzer is initialized
            if not self.spending_analyzer:
                raise ValueError("Spending analyzer not initialized")

            # Get predictions from the spending analyzer
            analysis_result = self.spending_analyzer.analyze_spending_patterns(user_data)
            predictions = analysis_result['predictions']

            # Construct prompt for GPT with user profile and predictions
            prompt = f"""
            Based on the analysis of this student's profile:
            - Year: {user_data['year_in_school']}
            - Major: {user_data['major']}
            - Monthly Income: ${user_data['monthly_income']}
            - Financial Aid: ${user_data['financial_aid']}

            Predicted monthly spending:
            {', '.join([f'{k}: ${v:.2f}' for k, v in predictions.items()])}

            Please provide:
            1. A brief analysis of their spending patterns
            2. 3-4 specific recommendations for improvement
            3. One key area of concern (if any)
            
            Keep the response concise and student-friendly.
            """

            # Generate personalized advice using GPT-4
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial advisor for students."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Return successful response with predictions and advice
            return {
                "predictions": predictions,
                "advice": response.choices[0].message.content,
                "status": "success"
            }

        except Exception as e:
            # Return error response if any exception occurs
            return {
                "status": "error",
                "error": str(e)
            }

    def get_budget_template(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized budget template based on user profile
        """
        try:
            # Construct detailed prompt for budget template generation
            prompt = f"""
            Create a monthly budget template for a student with the following profile:
            - Year: {user_profile.get('year_in_school', 'N/A')}
            - Major: {user_profile.get('major', 'N/A')}
            - Monthly Income: ${user_profile.get('monthly_income', 0)}
            - Financial Aid: ${user_profile.get('financial_aid', 0)}

            Provide:
            1. Recommended spending percentages for each category
            2. Specific dollar amounts based on their income
            3. Key considerations for their specific situation
            """

            # Generate personalized budget template using GPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a budget planning expert for students."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Return successful response with template
            return {
                "template": response.choices[0].message.content,
                "status": "success"
            }

        except Exception as e:
            # Return error response if any exception occurs
            return {
                "status": "error",
                "error": str(e)
            }

    def analyze_financial_goals(self, goals: List[str], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and provide feedback on user's financial goals
        """
        try:
            # Format goals list into bullet points
            goals_str = "\n".join([f"- {goal}" for goal in goals])
            
            # Construct detailed prompt for goal analysis
            prompt = f"""
            Analyze these financial goals for a student:
            {goals_str}

            Student Context:
            - Year: {user_context.get('year_in_school', 'N/A')}
            - Major: {user_context.get('major', 'N/A')}
            - Monthly Income: ${user_context.get('monthly_income', 0)}

            Please provide:
            1. Analysis of each goal's feasibility
            2. Suggested timeline for each goal
            3. Specific steps to achieve these goals
            4. Any potential obstacles to consider
            """

            # Generate goal analysis using GPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial goals advisor for students."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Return successful response with analysis
            return {
                "analysis": response.choices[0].message.content,
                "status": "success"
            }

        except Exception as e:
            # Return error response if any exception occurs
            return {
                "status": "error",
                "error": str(e)
            }