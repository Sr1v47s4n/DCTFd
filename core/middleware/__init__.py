"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

"""
Core middleware package
"""
from .activity_logger import ActivityLogMiddleware

__all__ = ['ActivityLogMiddleware']
