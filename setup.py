"""
Setup script for Simple AI Newsletter Generator

This script helps junior developers set up the project easily.
It checks requirements, creates folders, and guides through setup.
"""

import os
import sys
import subprocess

def print_header(text):
    """Print a nice header for each setup step."""
    print("\n" + "="*50)
    print(f" {text}")
    print("="*50)

def print_step(step_num, description):
    """Print a numbered step."""
    print(f"\n[{step_num}] {description}")

def check_python_version():
    """Check if Python version is compatible."""
    print_step(1, "Checking Python Version")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} is too old")
        print("Please install Python 3.8 or newer")
        return False

def create_folders():
    """Create necessary project folders."""
    print_step(2, "Creating Project Folders")
    
    folders = ['output', 'templates']
    
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"✓ Created folder: {folder}")
        except Exception as e:
            print(f"✗ Error creating folder {folder}: {e}")
            return False
    
    return True

def check_env_file():
    """Check if .env file exists and guide user to create it."""
    print_step(3, "Checking Environment Configuration")
    
    if os.path.exists('.env'):
        print("✓ .env file found")
        
        # Check if API key is set
        try:
            with open('.env', 'r') as f:
                content = f.read()
                if 'your_api_key_here' in content:
                    print("⚠ Warning: Please update your API key in .env file")
                    print("  1. Go to https://console.mistral.ai/")
                    print("  2. Create account and copy your API key")
                    print("  3. Replace 'your_api_key_here' in .env file")
                    return False
                else:
                    print("✓ API key appears to be configured")
                    return True
        except Exception as e:
            print(f"✗ Error reading .env file: {e}")
            return False
    else:
        print("✗ .env file not found")
        print("Please create .env file using the template provided")
        return False

def install_packages():
    """Install required Python packages."""
    print_step(4, "Installing Required Packages")
    
    if not os.path.exists('requirements.txt'):
        print("✗ requirements.txt not found")
        return False
    
    try:
        print("Installing packages... (this may take a few minutes)")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Packages installed successfully")
            return True
        else:
            print("✗ Error installing packages:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error running pip install: {e}")
        return False

def install_playwright():
    """Install Playwright browsers."""
    print_step(5, "Installing Browser for Web Scraping")
    
    try:
        print("Installing Chromium browser... (this may take a few minutes)")
        result = subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Browser installed successfully")
            return True
        else:
            print("✗ Error installing browser:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error installing browser: {e}")
        print("Try running: playwright install chromium")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    print_step(6, "Testing Package Imports")
    
    required_modules = [
        ('playwright', 'playwright.async_api'),
        ('mistralai', 'mistralai.client'),
        ('beautifulsoup4', 'bs4'),
        ('python-dotenv', 'dotenv')
    ]
    
    all_good = True
    
    for package_name, import_name in required_modules:
        try:
            __import__(import_name)
            print(f"✓ {package_name} import successful")
        except ImportError:
            print(f"✗ {package_name} import failed")
            all_good = False
    
    return all_good

def main():
    """Run the complete setup process."""
    print_header("Simple AI Newsletter Generator - Setup")
    print("This script will help you set up the project step by step.")
    
    # Run all setup steps
    steps_passed = 0
    total_steps = 6
    
    if check_python_version():
        steps_passed += 1
    
    if create_folders():
        steps_passed += 1
    
    if check_env_file():
        steps_passed += 1
    
    if install_packages():
        steps_passed += 1
    
    if install_playwright():
        steps_passed += 1
    
    if test_imports():
        steps_passed += 1
    
    # Print final results
    print_header("Setup Complete")
    print(f"Completed {steps_passed}/{total_steps} setup steps")
    
    if steps_passed == total_steps:
        print("\n🎉 SUCCESS! Your project is ready to run!")
        print("\nNext steps:")
        print("1. Make sure your API key is set in .env file")
        print("2. Run: python main.py")
        print("3. Check the output folder for your newsletter!")
    else:
        print("\n⚠ Setup incomplete. Please fix the issues above and run setup again.")
        print("\nCommon issues:")
        print("- Missing .env file with API key")
        print("- Network connection problems")
        print("- Permission issues")

if __name__ == "__main__":
    main()