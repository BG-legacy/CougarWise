"""
Database package for CougarWise backend.
"""

from .database import get_db, get_collection, Collections, close_db_connection
from .models import User, Transaction, FinancialGoal

__all__ = [
    'get_db',
    'get_collection',
    'Collections',
    'close_db_connection',
    'User',
    'Transaction',
    'FinancialGoal'
] 