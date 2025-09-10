"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

#!/usr/bin/env python
"""
Generate a secure secret key for Django settings.
"""
import secrets
import string

# Generate a secure secret key with 50 characters
alphabet = string.ascii_letters + string.digits + string.punctuation
secret_key = ''.join(secrets.choice(alphabet) for _ in range(50))

print("\nGenerated Django Secret Key:")
print("-" * 60)
print(secret_key)
print("-" * 60)
print("\nUse this key in your .env file or settings configuration")
print("Remember to keep this key secure and do not share it!")
