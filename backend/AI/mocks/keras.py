"""
Mock keras module for testing purposes.
This module provides mock implementations of keras classes and functions.
"""

class Sequential:
    """Mock Sequential model class."""
    def __init__(self, layers=None):
        self.layers = layers or []
    
    def add(self, layer):
        """Add a layer to the model."""
        self.layers.append(layer)
    
    def compile(self, optimizer=None, loss=None, metrics=None):
        """Compile the model."""
        self.optimizer = optimizer
        self.loss = loss
        self.metrics = metrics
    
    def fit(self, x, y, epochs=1, batch_size=32, validation_split=0.0, verbose=0):
        """Train the model."""
        # Return a mock history object
        return MockHistory()
    
    def predict(self, x):
        """Make predictions with the model."""
        # Return mock predictions
        import numpy as np
        if isinstance(x, dict):
            # Return a dictionary of predictions
            return {
                'Food': 200.0,
                'Housing': 500.0,
                'Transportation': 150.0,
                'Entertainment': 100.0,
                'Education': 300.0,
                'Other': 50.0
            }
        else:
            # Return a numpy array of predictions
            return np.random.rand(len(x), 6) * 1000

class MockHistory:
    """Mock history object returned by model.fit()."""
    def __init__(self):
        import numpy as np
        self.history = {
            'loss': np.random.rand(10).tolist(),
            'val_loss': np.random.rand(10).tolist(),
            'mean_absolute_error': np.random.rand(10).tolist(),
            'val_mean_absolute_error': np.random.rand(10).tolist()
        }

# Mock layers module
class layers:
    """Mock layers module."""
    @staticmethod
    def Dense(units, activation=None, input_shape=None):
        """Mock Dense layer."""
        return {'type': 'Dense', 'units': units, 'activation': activation, 'input_shape': input_shape}
    
    @staticmethod
    def Dropout(rate):
        """Mock Dropout layer."""
        return {'type': 'Dropout', 'rate': rate}

# Mock models module
class models:
    """Mock models module."""
    @staticmethod
    def Sequential(layers=None):
        """Create a Sequential model."""
        return Sequential(layers)

# Mock optimizers
optimizers = type('obj', (object,), {
    'Adam': lambda learning_rate=0.001: f"Adam(learning_rate={learning_rate})",
    'SGD': lambda learning_rate=0.01: f"SGD(learning_rate={learning_rate})",
    'RMSprop': lambda learning_rate=0.001: f"RMSprop(learning_rate={learning_rate})"
})()

# Mock losses
losses = {
    'mean_squared_error': 'mean_squared_error',
    'mean_absolute_error': 'mean_absolute_error',
    'categorical_crossentropy': 'categorical_crossentropy'
}

# Mock metrics
metrics = [
    'mean_squared_error',
    'mean_absolute_error',
    'accuracy'
] 