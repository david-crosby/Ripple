#!/usr/bin/env python3
"""
Quick verification script to test password validation logic.
Run this to verify the validation works as expected.
"""

from utils.validation import validate_password_strength, validate_username

print("=" * 60)
print("Password Validation Tests")
print("=" * 60)

test_passwords = [
    ("weak", "Should fail - too short"),
    ("lowercase123", "Should fail - no uppercase"),
    ("UPPERCASE123", "Should fail - no lowercase"),
    ("NoNumbers", "Should fail - no numbers"),
    ("Password123", "Should fail - common password"),
    ("SecurePass123", "Should pass - strong password"),
    ("MyP@ssw0rd!", "Should pass - strong password"),
]

for password, description in test_passwords:
    is_valid, error = validate_password_strength(password)
    status = "✓ PASS" if is_valid else "✗ FAIL"
    print(f"\n{status} | {description}")
    print(f"  Password: '{password}'")
    if not is_valid:
        print(f"  Error: {error}")

print("\n" + "=" * 60)
print("Username Validation Tests")
print("=" * 60)

test_usernames = [
    ("ab", "Should fail - too short"),
    ("a" * 51, "Should fail - too long"),
    ("123user", "Should fail - starts with number"),
    ("user@name", "Should fail - invalid character"),
    ("valid_user123", "Should pass - valid username"),
    ("JohnDoe", "Should pass - valid username"),
]

for username, description in test_usernames:
    is_valid, error = validate_username(username)
    status = "✓ PASS" if is_valid else "✗ FAIL"
    display_username = username if len(username) <= 20 else username[:20] + "..."
    print(f"\n{status} | {description}")
    print(f"  Username: '{display_username}'")
    if not is_valid:
        print(f"  Error: {error}")

print("\n" + "=" * 60)
