"""
Utility Functions for Newsletter Generator

This module contains essential helper functions used across the application.
"""

import os


def print_step(step_number, description):
    """
    Print a numbered step to show progress to the user.
    
    This helps users understand what the program is doing at each stage.
    
    Args:
        step_number (int): The step number (1, 2, 3, etc.)
        description (str): What this step does
    """
    print(f"\n=== STEP {step_number}: {description} ===")


def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            print(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        print(f"Error creating directory {directory_path}: {e}")
        return False


def clean_text(text):
    """
    Clean and normalize text content.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace and clean up
    cleaned = ' '.join(text.split())
    return cleaned.strip()
