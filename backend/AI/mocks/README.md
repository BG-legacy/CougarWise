# Mock Modules for Testing

This directory contains mock implementations of external libraries that are used by the CougarWise AI modules. These mocks allow the tests to run without requiring the actual libraries to be installed.

## Available Mocks

### keras.py

A mock implementation of the Keras library, which is used by the `StudentSpendingAnalysis` class. This mock provides the minimum functionality needed for the tests to run, including:

- `Sequential` model class with methods like `add`, `compile`, `fit`, and `predict`
- `layers` module with `Dense` and `Dropout` layer types
- `models` module with `Sequential` model factory
- Mock optimizers, losses, and metrics

## Usage

The mocks are automatically used when the real libraries are not available. This is handled in the import statements of the AI modules, which try to import the real libraries first and fall back to the mocks if they're not available.

For example, in `student_spending_analysis.py`:

```python
try:
    import keras
    from keras import layers, models
except ImportError:
    try:
        # Try to import from our mocks directory
        import sys
        import os
        # Add the mocks directory to the path
        mocks_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mocks')
        sys.path.insert(0, mocks_dir)
        import keras
        from keras import layers, models
        print("Using mock keras module for testing")
    except ImportError:
        print("Error: Could not import keras or mock keras module")
        raise
```

## Adding New Mocks

If you need to add a new mock for another library, follow these steps:

1. Create a new Python file in this directory with the same name as the library you want to mock
2. Implement the minimum functionality needed for the tests to run
3. Update the import statements in the AI modules to use the mock when the real library is not available
4. Update this README to document the new mock 