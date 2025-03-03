# Import required libraries for data processing, ML, and visualization
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import keras
from keras import layers, models
import matplotlib.pyplot as plt
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class StudentSpendingAnalysis:
    def __init__(self):
        # Initialize model and preprocessing components
        self.model = None  # Neural network model
        self.scaler = StandardScaler()  # For normalizing numerical features
        self.label_encoders = {}  # Dictionary to store encoders for categorical variables
        # Set up API key and configuration from environment variables
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.data_path = os.getenv('STUDENT_DATA_PATH')
        self.model_epochs = int(os.getenv('MODEL_EPOCHS', 50))
        self.batch_size = int(os.getenv('BATCH_SIZE', 32))
        
    def load_and_preprocess_data(self):
        """
        Load and preprocess the data
        Returns: Preprocessed features and target variables
        """
        try:
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
            for column in categorical_columns:
                self.label_encoders[column] = LabelEncoder()
                data[column] = self.label_encoders[column].fit_transform(data[column])
            
            # Normalize numerical features using StandardScaler
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
        Build the neural network model architecture for spending prediction
        Args:
            input_shape: Tuple defining the shape of input features
        Returns:
            Compiled Keras model
        """
        # Create sequential model with multiple layers
        model = models.Sequential([
            # Input layer with 64 neurons and ReLU activation
            layers.Dense(64, activation='relu', input_shape=input_shape),
            # Dropout layer to prevent overfitting (20% dropout rate)
            layers.Dropout(0.2),
            # Hidden layer with 32 neurons
            layers.Dense(32, activation='relu'),
            # Another dropout layer
            layers.Dropout(0.2),
            # Hidden layer with 16 neurons
            layers.Dense(16, activation='relu'),
            # Output layer with 9 neurons (one for each spending category)
            layers.Dense(9, activation='linear')
        ])
        
        # Configure model training parameters
        model.compile(
            optimizer='adam',  # Use Adam optimizer for efficient training
            loss='mean_squared_error',  # MSE loss for regression
            metrics=['mae']  # Track Mean Absolute Error during training
        )
        
        return model

    def train_model(self, epochs=50, batch_size=32):
        """
        Train the neural network on student spending data
        Args:
            epochs: Number of training iterations
            batch_size: Number of samples per gradient update
        Returns:
            Training history object
        """
        try:
            # Get preprocessed features and target values
            features, targets = self.load_and_preprocess_data()
            
            # Split data into training and testing sets (80/20 split)
            X_train, X_test, y_train, y_test = train_test_split(
                features, targets, test_size=0.2, random_state=42
            )
            
            # Create and compile the neural network
            self.model = self.build_model((features.shape[1],))
            
            # Train the model with validation split
            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.2,  # Use 20% of training data for validation
                verbose=1  # Show training progress
            )
            
            # Evaluate model performance on test set
            test_loss, test_mae = self.model.evaluate(X_test, y_test, verbose=0)
            print(f"\nTest Mean Absolute Error: ${test_mae:.2f}")
            
            return history
            
        except Exception as e:
            raise Exception(f"Error training the model: {str(e)}")

    def predict_spending(self, user_data):
        """
        Predict spending patterns for a new student
        user_data: Dictionary containing student information
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
            for column, encoder in self.label_encoders.items():
                if column in input_df.columns:
                    input_df[column] = encoder.transform(input_df[column])
            
            # Scale numerical features using stored scaler
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
        Visualize the training history with loss and MAE plots
        """
        # Create figure with two subplots
        plt.figure(figsize=(12, 4))
        
        # Plot training and validation loss
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Plot training and validation MAE
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
        Generate personalized spending advice using OpenAI
        """
        try:
            # Verify OpenAI API key is set
            if not openai.api_key:
                raise ValueError("OpenAI API key not set")

            # Format the predictions and user data into a detailed prompt
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
                model="gpt-4",
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
        Complete analysis including predictions
        """
        # Get spending predictions using the trained model
        predictions = self.predict_spending(user_data)
        
        # Return analysis results
        return {
            'predictions': predictions
        }

# Main execution block for testing
if __name__ == "__main__":
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
        