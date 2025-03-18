# Import required libraries for data processing, ML, and visualization
import pandas as pd  # For data manipulation and analysis
import numpy as np  # For numerical operations
from sklearn.model_selection import train_test_split  # For splitting data into training and testing sets
from sklearn.preprocessing import StandardScaler, LabelEncoder  # For data preprocessing
# Try to import keras, if not available use our mock
try:
    import keras  # Deep learning library
    from keras import layers, models  # Components for building neural networks
except ImportError:
    try:
        # Try to import from our mocks directory
        import sys
        import os
        # Add the mocks directory to the path
        mocks_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mocks')
        sys.path.insert(0, mocks_dir)
        import keras  # Import mock keras for testing
        from keras import layers, models
        print("Using mock keras module for testing")
    except ImportError:
        print("Error: Could not import keras or mock keras module")
        raise
import matplotlib.pyplot as plt  # For data visualization
from openai import OpenAI  # Import OpenAI client properly for v1.x
import os  # For file and environment operations
from dotenv import load_dotenv  # For loading environment variables
import json  # For parsing JSON responses
import re
import time
import datetime
import random

# Load environment variables from the root .env file
# Get the absolute path to the backend directory (one level up from current directory)
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path)  # Makes environment variables available via os.getenv()

class StudentSpendingAnalysis:
    """
    A class for analyzing and predicting student spending patterns using machine learning.
    This class loads student spending data, trains a neural network model, and provides
    predictions and personalized financial advice.
    """
    def __init__(self):
        """
        Initialize the spending analysis model.
        This method loads and preprocesses the data, builds the model,
        and sets up any necessary API clients.
        """
        # Load environment variables
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dotenv_path = os.path.join(backend_dir, '.env')
        load_dotenv(dotenv_path)
        
        # Get OpenAI API key from environment variables
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize OpenAI client if API key is available
        if self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                print("OpenAI client initialized successfully.")
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.client = None
        else:
            print("WARNING: OpenAI API key not found. AI features will be limited.")
            self.client = None
        
        # Set default values for model parameters
        self.model_epochs = int(os.getenv('MODEL_EPOCHS', '50'))
        self.batch_size = int(os.getenv('BATCH_SIZE', '32'))
        
        # Set the data path relative to the current directory
        self.data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'student_spending.csv')
        
        # Initialize preprocessing objects
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Other initialization code remains the same
        # Load and preprocess the data
        try:
            self.data = self.load_and_preprocess_data()
            print(f"Loaded {len(self.data)} preprocessed records for student spending analysis")
        except Exception as e:
            print(f"Warning: Could not load spending data: {e}")
            self.data = pd.DataFrame()  # Empty dataframe

        # Build the model architecture
        input_shape = (8,)  # Example shape for student demographic features
        self.model = self.build_model(input_shape)
        
        # Trained flag (will be set to True after training)
        self.trained = False

    def load_and_preprocess_data(self):
        """
        Load student spending data from CSV and preprocess it for machine learning.
        This includes encoding categorical variables, normalizing numerical features,
        and splitting the data into features and targets.
        
        Returns: 
            Tuple of (features, targets) where:
            - features: DataFrame of input variables (student characteristics)
            - targets: DataFrame of spending amounts by category
        """
        try:
            # Check if file exists
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Could not find student_spending.csv file at {self.data_path}")
                
            # Load CSV data into pandas DataFrame
            data = pd.read_csv(self.data_path)
            if data.empty:
                raise ValueError("The CSV file is empty")
            
            # Define column categories for processing
            categorical_columns = ['gender', 'year_in_school', 'major', 'preferred_payment_method']
            numerical_features = ['age', 'monthly_income', 'financial_aid', 'tuition']
            spending_columns = ['housing', 'food', 'transportation', 'books_supplies', 
                              'entertainment', 'personal_care', 'technology', 
                              'health_wellness', 'miscellaneous']
            
            # Convert categorical variables to numerical using label encoding
            # This transforms text categories into numbers that the model can process
            for column in categorical_columns:
                self.label_encoders[column] = LabelEncoder()
                data[column] = self.label_encoders[column].fit_transform(data[column])
            
            # Normalize numerical features using StandardScaler
            # This scales all numerical values to have mean=0 and std=1, improving model performance
            self.scaler = StandardScaler()
            data[numerical_features] = self.scaler.fit_transform(data[numerical_features])
            
            # Split data into features (inputs) and targets (spending categories)
            features = data[numerical_features + categorical_columns]
            targets = data[spending_columns]
            
            # Convert to numpy arrays before returning
            features_array = features.values
            targets_array = targets.values
            
            return features_array, targets_array
            
        except FileNotFoundError:
            raise FileNotFoundError("Could not find student_spending.csv file")
        except Exception as e:
            raise Exception(f"Error processing the data: {str(e)}")

    def build_model(self, input_shape):
        """
        Build the neural network model architecture for spending prediction.
        Creates a sequential model with multiple dense layers and dropout for regularization.
        
        Args:
            input_shape: Tuple defining the shape of input features
            
        Returns:
            Compiled Keras model ready for training
        """
        # Create sequential model with multiple layers
        model = models.Sequential([
            # Input layer with 64 neurons and ReLU activation
            # ReLU (Rectified Linear Unit) helps with non-linear relationships in the data
            layers.Dense(64, activation='relu', input_shape=input_shape),
            # Dropout layer to prevent overfitting (20% dropout rate)
            # Randomly sets 20% of inputs to 0 during training, improving generalization
            layers.Dropout(0.2),
            # Hidden layer with 32 neurons
            layers.Dense(32, activation='relu'),
            # Another dropout layer
            layers.Dropout(0.2),
            # Hidden layer with 16 neurons
            layers.Dense(16, activation='relu'),
            # Output layer with 9 neurons (one for each spending category)
            # Linear activation for regression (predicting continuous values)
            layers.Dense(9, activation='linear')
        ])
        
        # Configure model training parameters
        model.compile(
            optimizer='adam',  # Adam optimizer for efficient training
            loss='mean_squared_error',  # MSE loss for regression
            metrics=['mae']  # Track Mean Absolute Error during training
        )
        
        return model

    def train_model(self, epochs=None, batch_size=None):
        """
        Train the neural network on student spending data.
        Loads and preprocesses data, builds the model, and trains it.
        
        Args:
            epochs: Number of training iterations (default: from environment variable)
            batch_size: Number of samples per gradient update (default: from environment variable)
            
        Returns:
            Training history object containing loss and metrics over epochs
        """
        try:
            # Use provided values or fall back to instance variables
            epochs = epochs or self.model_epochs
            batch_size = batch_size or self.batch_size
            
            print(f"Starting model training with {epochs} epochs and batch size {batch_size}")
            print(f"Using data from: {self.data_path}")
            
            # Get preprocessed features and target values
            features, targets = self.load_and_preprocess_data()
            
            # Split data into training and testing sets (80/20 split)
            # This allows us to evaluate model performance on unseen data
            X_train, X_test, y_train, y_test = train_test_split(
                features, targets, test_size=0.2, random_state=42
            )
            
            # Create and compile the neural network
            self.model = self.build_model((features.shape[1],))
            
            # Train the model with validation split
            # validation_split=0.2 means 20% of training data is used for validation during training
            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.2,  # Use 20% of training data for validation
                verbose=1  # Show training progress
            )
            
            # Evaluate model performance on test set - handle both real and mock Keras
            try:
                test_loss, test_mae = self.model.evaluate(X_test, y_test, verbose=0)
                print(f"\nTest Mean Absolute Error: ${test_mae:.2f}")
            except AttributeError:
                # If using mock Keras, skip evaluation
                print("\nSkipping model evaluation (using mock Keras)")
            
            return history
            
        except FileNotFoundError as e:
            print(f"File not found error: {str(e)}")
            raise FileNotFoundError(f"Could not find student_spending.csv file at {self.data_path}")
        except Exception as e:
            print(f"Error training the model: {str(e)}")
            raise Exception(f"Error training the model: {str(e)}")

    def predict_spending(self, user_data):
        """
        Predict spending patterns for a new student based on their profile.
        
        Args:
            user_data: Dictionary containing student information (age, income, etc.)
            
        Returns:
            Dictionary mapping spending categories to predicted amounts
        """
        try:
            # Verify model is trained
            if self.model is None:
                raise ValueError("Model has not been trained yet")
            
            # Extract relevant features from user data
            input_data = {
                'age': user_data['age'],
                'monthly_income': user_data['monthly_income'],
                'financial_aid': user_data['financial_aid'],
                'tuition': user_data['tuition'],
                'gender': user_data['gender'],
                'year_in_school': user_data['year_in_school'],
                'major': user_data['major'],
                'preferred_payment_method': user_data['preferred_payment_method']
            }
            
            # Convert input data to DataFrame for processing
            input_df = pd.DataFrame([input_data])
            
            # Encode categorical variables using stored encoders
            # This ensures consistency with how the training data was encoded
            for column, encoder in self.label_encoders.items():
                if column in input_df.columns:
                    input_df[column] = encoder.transform(input_df[column])
            
            # Scale numerical features using stored scaler
            # This ensures consistency with how the training data was scaled
            numerical_features = ['age', 'monthly_income', 'financial_aid', 'tuition']
            input_df[numerical_features] = self.scaler.transform(input_df[numerical_features])
            
            # Generate predictions using trained model
            predictions = self.model.predict(input_df)
            
            # Map predictions to spending categories
            spending_categories = ['Housing', 'Food', 'Transportation', 'Books & Supplies',
                                 'Entertainment', 'Personal Care', 'Technology',
                                 'Health & Wellness', 'Miscellaneous']
            
            # Return dictionary of category-prediction pairs
            return dict(zip(spending_categories, predictions[0]))
            
        except Exception as e:
            raise Exception(f"Error making prediction: {str(e)}")

    def visualize_training_history(self, history):
        """
        Visualize the training history with loss and MAE plots.
        Creates a figure with two subplots showing how the model improved during training.
        
        Args:
            history: History object returned by model.fit()
        """
        # Create figure with two subplots
        plt.figure(figsize=(12, 4))
        
        # Plot training and validation loss
        # This shows how well the model is learning and if it's overfitting
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Plot training and validation MAE
        # This shows the average error in dollars
        plt.subplot(1, 2, 2)
        plt.plot(history.history['mae'], label='Training MAE')
        plt.plot(history.history['val_mae'], label='Validation MAE')
        plt.title('Model Mean Absolute Error')
        plt.xlabel('Epoch')
        plt.ylabel('MAE')
        plt.legend()
        
        # Adjust layout and display plots
        plt.tight_layout()
        plt.show()

    def generate_spending_advice(self, predictions, user_data):
        """
        Generate personalized spending advice based on predictions and user data.
        Uses OpenAI's GPT model to generate natural language advice.
        
        Args:
            predictions: Dictionary containing spending predictions
            user_data: Dictionary with user demographic and financial information
            
        Returns:
            Dictionary containing advice, savings tips, and budget recommendations
        """
        # Check if OpenAI client is available
        if not self.client:
            # Return mock advice if OpenAI client isn't available
            return self._generate_mock_spending_advice()
        
        try:
            # Create a prompt that includes both the predictions and user profile
            prompt = f"""
            As a financial advisor for college students, analyze the following:
            
            Student Profile:
            - Age: {user_data.get('age', 'Unknown')}
            - Gender: {user_data.get('gender', 'Unknown')}
            - Year in School: {user_data.get('year_in_school', 'Unknown')}
            - Major: {user_data.get('major', 'Unknown')}
            - Monthly Income: ${user_data.get('monthly_income', 0)}
            - Financial Aid: ${user_data.get('financial_aid', 0)}
            
            Predicted Monthly Spending:
            """
            
            # Add each spending category and amount to the prompt
            if 'categories' in predictions:
                for category, amount in predictions['categories'].items():
                    prompt += f"- {category.title()}: ${amount}\n"
            else:
                for category, amount in predictions.items():
                    if category != 'total':
                        prompt += f"- {category.title()}: ${amount}\n"
            
            # Add the total spending if available
            if 'total' in predictions:
                prompt += f"- Total: ${predictions['total']}\n"
            
            # Request specific advice formatted as JSON
            prompt += """
            Provide personalized financial advice for this student based on their profile and spending.
            
            Format your response as a JSON object with these fields:
            {
                "advice": "One paragraph of overall spending advice",
                "savings_tips": ["Tip 1", "Tip 2", "Tip 3"],
                "budget_allocation": {
                    "food": "25%",
                    "housing": "40%",
                    "entertainment": "10%",
                    "transportation": "15%",
                    "other": "10%"
                }
            }
            """
            
            # Call OpenAI API to generate the advice
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial advisor for college students. Provide advice in JSON format only."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract and parse the response
            if not hasattr(response, 'choices') or not response.choices:
                return self._generate_mock_spending_advice()
            
            advice_text = response.choices[0].message.content
            
            # Parse the JSON response
            advice_json = self._parse_ai_generated_json(advice_text)
            if not advice_json:
                # If JSON parsing fails, return mock advice
                return self._generate_mock_spending_advice()
            
            return advice_json
            
        except Exception as e:
            print(f"Error generating spending advice: {e}")
            # Return mock advice if any error occurs
            return self._generate_mock_spending_advice()

    def _generate_mock_spending_advice(self):
        """
        Generate mock spending advice when OpenAI is unavailable.
        
        Returns:
            Dictionary with mock advice, savings tips, and budget allocation
        """
        # Create a mock JSON response that matches the expected structure
        return {
            "advice": "You should focus on reducing your food expenses.",
            "savings_tips": ["Cook at home", "Use meal prep", "Avoid eating out"],
            "budget_allocation": {
                "food": "25%",
                "housing": "40%",
                "entertainment": "10%",
                "transportation": "15%",
                "other": "10%"
            }
        }

    def analyze_spending_patterns(self, user_data):
        """
        Complete analysis including predictions and advice for a student.
        
        Args:
            user_data: Dictionary containing student information
            
        Returns:
            Dictionary containing status, predictions and advice
        """
        try:
            # Get spending predictions using the trained model
            predictions = self.predict_spending(user_data)
            
            # Generate personalized spending advice
            advice = self.generate_spending_advice(predictions, user_data)
            
            # Return analysis results
            return {
                'status': 'success',
                'predictions': predictions,
                'advice': advice
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _parse_ai_generated_json(self, response_text):
        """
        Parse AI-generated JSON from a text response.
        
        Args:
            response_text: The raw text response from the AI model
            
        Returns:
            Parsed JSON dictionary
        """
        # Check for code blocks in markdown
        if "```json" in response_text:
            # Extract JSON between markdown code blocks
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            # Extract JSON between generic code blocks
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            # Use the full response if no code blocks
            json_str = response_text.strip()
        
        # Parse the JSON string
        import json
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response as JSON: {e}")
            print(f"Response text: {response_text[:100]}...")
            return {}  # Return empty dict if parsing fails

    def parse_ai_spending_advice(self, response_text):
        """
        Parse spending advice from AI response.
        
        Args:
            response_text: Raw text response from OpenAI
            
        Returns:
            Dictionary with advice and predictions
        """
        try:
            result = self._parse_ai_generated_json(response_text)
            # Ensure the result has expected fields
            if not result.get("advice"):
                result["advice"] = []
            if not result.get("predictions"):
                result["predictions"] = []
            return result
        except Exception as e:
            print(f"Error parsing AI spending advice: {e}")
            return {"advice": [], "predictions": []}

    def parse_ai_budget_template(self, response_text):
        """
        Parse budget template from AI response.
        
        Args:
            response_text: Raw text response from OpenAI
            
        Returns:
            Dictionary with categories and total
        """
        try:
            result = self._parse_ai_generated_json(response_text)
            # Ensure the result has expected fields
            if not result.get("categories"):
                result["categories"] = {}
            if not result.get("total"):
                # Calculate total from categories if not provided
                result["total"] = sum(result.get("categories", {}).values())
            return result
        except Exception as e:
            print(f"Error parsing AI budget template: {e}")
            return {"categories": {}, "total": 0}

    def parse_ai_goals_analysis(self, response_text):
        """
        Parse goals analysis from AI response.
        
        Args:
            response_text: Raw text response from OpenAI
            
        Returns:
            Dictionary with analysis and recommendations
        """
        try:
            result = self._parse_ai_generated_json(response_text)
            # Ensure the result has expected fields
            if not result.get("analysis"):
                result["analysis"] = []
            if not result.get("recommendations"):
                result["recommendations"] = []
            return result
        except Exception as e:
            print(f"Error parsing AI goals analysis: {e}")
            return {"analysis": [], "recommendations": []}

    def generate_ai_spending_json(self, user_profile):
        """
        Generate AI-powered spending insights in JSON format.
        
        Args:
            user_profile: Dictionary with user demographic information
            
        Returns:
            Dictionary with spending breakdown by category
        """
        # Return mock data if no API key or client
        if not self.openai_api_key or not self.client:
            return self._generate_mock_spending_json()
        
        try:
            # Create prompt with user information
            prompt = f"""
            Generate realistic spending allocation JSON for a {user_profile['year_in_school']} college student 
            majoring in {user_profile['major']} with a monthly income of ${user_profile['monthly_income']}.
            
            Additional profile information:
            """
            
            # Add any additional profile information to the prompt
            for key, value in user_profile.items():
                if key not in ['year_in_school', 'major', 'monthly_income']:
                    prompt += f"- {key}: {value}\n"
                
            prompt += """
            Return a JSON object with these categories:
            - Housing
            - Food
            - Transportation
            - Education
            - Entertainment
            - Healthcare
            - Clothing
            - Savings
            - Miscellaneous
            
            Format:
            {
                "Housing": 500,
                "Food": 300,
                ...
            }
            
            Make the values realistic for a college student and ensure they add up to the monthly income.
            Only return valid JSON with no additional text.
            """
            
            # Make API call to OpenAI's GPT model using the client
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst that generates realistic spending allocations in JSON format."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response text to extract JSON
            response_text = response.choices[0].message.content
            
            # Parse the JSON using our helper method
            spending_json = self._parse_ai_generated_json(response_text)
            
            return spending_json
            
        except Exception as e:
            print(f"Error generating AI spending JSON: {e}")
            # Return mock data if something goes wrong
            return self._generate_mock_spending_json()

    def _generate_mock_spending_json(self):
        """Generate mock spending data for testing."""
        return {
            "Housing": 600,
            "Food": 300,
            "Transportation": 150,
            "Education": 200,
            "Entertainment": 100,
            "Healthcare": 50,
            "Clothing": 75,
            "Savings": 100,
            "Miscellaneous": 50
        }

    def analyze_spending_patterns_with_ai(self, user_profile, spending_data):
        """
        Use AI to analyze spending patterns and generate insights.
        
        Args:
            user_profile: Dictionary with user demographic information
            spending_data: Dictionary with spending by category
            
        Returns:
            Dictionary with insights and recommendations
        """
        # Return mock data if no API key or client
        if not self.openai_api_key or not self.client:
            return {
                "insights": ["Based on your spending, you're allocating appropriately for a student"],
                "budget_allocation": {"food": "25%", "housing": "40%", "other": "35%"}
            }
        
        try:
            # Create a prompt for the AI model
            prompt = f"""
            Analyze the spending patterns for a {user_profile.get('year_in_school')} college student 
            majoring in {user_profile.get('major')} with monthly income of ${user_profile.get('monthly_income')}.
            
            Current spending by category:
            """
            
            # Add spending categories to the prompt
            for category, amount in spending_data.items():
                prompt += f"- {category}: ${amount}\n"
                
            prompt += """
            Please provide:
            1. Three specific insights about this spending pattern
            2. Budget allocation recommendations as percentages
            
            Format your response as JSON:
            {
                "insights": ["insight 1", "insight 2", "insight 3"],
                "budget_allocation": {
                    "food": "percentage",
                    "housing": "percentage",
                    "other": "percentage"
                }
            }
            """

            # Make API call to OpenAI's GPT model using the client
            response = self.client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for high-quality financial advice
                messages=[
                    {"role": "system", "content": "You are a helpful financial advisor specializing in student finances. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse the JSON response and return as a dictionary
            response_text = response.choices[0].message.content
            return self._parse_ai_generated_json(response_text)
            
        except Exception as e:
            print(f"Error analyzing spending patterns with AI: {e}")
            # Return mock data if something goes wrong
            return {
                "insights": ["Based on your spending, you're allocating appropriately for a student"],
                "budget_allocation": {"food": "25%", "housing": "40%", "other": "35%"}
            }

# Main execution block for testing
if __name__ == "__main__":
    # This code runs when the script is executed directly (not imported)
    
    # Create an instance of the analyzer
    analyzer = StudentSpendingAnalysis()
    
    # Train the model with specified epochs
    print("Training model...")
    history = analyzer.train_model(epochs=analyzer.model_epochs)
    
    # Generate visualization of training results
    print("\nGenerating training visualization...")
    analyzer.visualize_training_history(history)
    
    # Create sample student data for testing
    print("\nMaking sample prediction and generating advice...")
    sample_student = {
        'age': 20,
        'gender': 'Female',
        'year_in_school': 'Sophomore',
        'major': 'Computer Science',
        'monthly_income': 1000,
        'financial_aid': 500,
        'tuition': 5000,
        'preferred_payment_method': 'Credit Card'
    }
    
    # Generate and display analysis results
    analysis = analyzer.analyze_spending_patterns(sample_student)
    
    # Print predicted spending amounts
    print("\nPredicted monthly spending:")
    for category, amount in analysis['predictions'].items():
        print(f"{category}: ${amount:.2f}")
    
    # Print personalized financial advice
    print("\nPersonalized Financial Advice:")
    print(analysis['advice'])
        