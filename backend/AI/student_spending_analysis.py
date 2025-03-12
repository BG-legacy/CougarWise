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
import openai  # For generating AI-powered financial advice
import os  # For file and environment operations
from dotenv import load_dotenv  # For loading environment variables

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
        Initialize the StudentSpendingAnalysis with necessary components.
        Sets up the model, preprocessing tools, and configuration from environment variables.
        """
        # Initialize model and preprocessing components
        self.model = None  # Neural network model (will be created during training)
        self.scaler = StandardScaler()  # For normalizing numerical features
        self.label_encoders = {}  # Dictionary to store encoders for categorical variables
        # Set up API key and configuration from environment variables
        openai.api_key = os.getenv('OPENAI_API_KEY')  # For generating financial advice
        
        # Get the path to the CSV file - first try from env, then use default path
        self.data_path = os.getenv('STUDENT_DATA_PATH')
        
        # If data_path is not set or file doesn't exist, use the default path relative to this file
        if not self.data_path or not os.path.exists(self.data_path):
            # Get the directory where this script is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(current_dir, 'student_spending.csv')
            print(f"Using default data path: {self.data_path}")
        
        # Get training parameters from environment variables or use defaults
        self.model_epochs = int(os.getenv('MODEL_EPOCHS', 50))  # Number of training iterations
        self.batch_size = int(os.getenv('BATCH_SIZE', 32))  # Number of samples per gradient update
        
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
            
            return features, targets
            
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
        Generate personalized spending advice using OpenAI's GPT model.
        
        Args:
            predictions: Dictionary of predicted spending by category
            user_data: Dictionary containing student information
            
        Returns:
            String containing personalized financial advice
        """
        try:
            # Verify OpenAI API key is set
            if not openai.api_key:
                raise ValueError("OpenAI API key not set")

            # Format the predictions and user data into a detailed prompt
            # This prompt guides the AI to provide relevant and personalized advice
            prompt = f"""
            As a financial advisor, provide personalized advice for a {user_data['year_in_school']} 
            student majoring in {user_data['major']} with the following monthly spending patterns:

            Monthly Income: ${user_data['monthly_income']}
            Financial Aid: ${user_data['financial_aid']}
            
            Predicted Monthly Spending:
            """
            
            # Add each spending category and amount to the prompt
            for category, amount in predictions.items():
                prompt += f"\n{category}: ${amount:.2f}"
            
            prompt += "\n\nPlease provide specific advice to help them manage their spending better."

            # Get response from OpenAI using the chat completions API
            response = openai.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for high-quality financial advice
                messages=[
                    {"role": "system", "content": "You are a helpful financial advisor specializing in student finances."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Return the generated advice
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error generating advice: {str(e)}")

    def analyze_spending_patterns(self, user_data):
        """
        Complete analysis including predictions and advice for a student.
        
        Args:
            user_data: Dictionary containing student information
            
        Returns:
            Dictionary containing predictions and advice
        """
        # Get spending predictions using the trained model
        predictions = self.predict_spending(user_data)
        
        # Return analysis results
        return {
            'predictions': predictions
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
        