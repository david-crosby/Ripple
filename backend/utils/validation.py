"""
Validation utilities for user input.

Provides functions for validating passwords, emails, and other user data.
"""

import re
from typing import Tuple


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - Not a common password
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string
    """
    # Check minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase letter
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    # Check for common passwords
    # In production, use a library like 'zxcvbn' for comprehensive checking
    common_passwords = [
        'password', 'password123', '12345678', 'qwerty', 'abc123',
        'monkey', '1234567890', 'letmein', 'trustno1', 'dragon',
        'baseball', 'iloveyou', 'master', 'sunshine', 'ashley'
    ]
    
    if password.lower() in common_passwords:
        return False, "Password is too common. Please choose a stronger password"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username meets requirements.
    
    Requirements:
    - 3-50 characters
    - Alphanumeric and underscores only
    - Must start with a letter
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", username):
        return False, "Username must start with a letter and contain only letters, numbers, and underscores"
    
    return True, ""