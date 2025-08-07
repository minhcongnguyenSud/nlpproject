"""
Simple Test Script for Students
This checks if everything is working befordef test_configuration():
    """Check if configuration is okay"""
    print("\n🔧 Testing configuration...")
    
    try:
        from src.core import config
        
        # Check if .env file exists in parent directory
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        if not os.path.exists(env_file):
            print("⚠️ No .env file found")
            print("   Copy .env.example to .env and add your API key")
            return Falsee main program
"""

import os
import sys

# Add parent directory to path so we can import from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_basic_setup():
    """Check if basic files exist"""
    print("🔍 Checking basic setup...")
    
    # Change to parent directory for file checks
    parent_dir = os.path.join(os.path.dirname(__file__), '..')
    os.chdir(parent_dir)
    
    important_files = [
        'main.py',
        'requirements.txt', 
        '.env.example',
        'src/core/config.py',
        'src/utils/utils.py'
    ]
    
    missing_files = []
    for file in important_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(" Missing important files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print(" All important files are there!")
    return True


def test_imports():
    """Check if we can import our modules"""
    print("\n Testing imports...")
    
    try:
        print("   Trying to import config...")
        from src.core import config
        print("    Config imported!")
        
        print("   Trying to import utils...")
        from src.utils.utils import print_step
        print("    Utils imported!")
        
        print("   Trying to import scraper...")
        from src.newsletter_generator import scraper
        print("    Scraper imported!")
        
        print("   Trying to import categorized summarizer...")
        from src.newsletter_generator import simple_categorized_summarizer
        print("    Categorized summarizer imported!")
        
        print("   Trying to import smart analyzer...")
        from src.newsletter_generator import smart_analyzer  
        print("    Smart analyzer imported!")
        
        print(" All imports work!")
        return True
        
    except ImportError as e:
        print(f" Import problem: {e}")
        print("   You might need to install packages:")
        print("   pip install -r requirements.txt")
        return False


def test_configuration():
    """Check if configuration is okay"""
    print("\n🔧 Testing configuration...")
    
    try:
        from src.core import config
        
        # Check if .env file exists in parent directory
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        if not os.path.exists(env_file):
            print("⚠️ No .env file found")
            print("   Copy .env.example to .env and add your API key")
            return False
            
        # Check basic config values
        if not hasattr(config, 'WEBSITES'):
            print(" WEBSITES not configured")
            return False
            
        if not hasattr(config, 'OUTPUT_FOLDER'):
            print(" OUTPUT_FOLDER not configured")  
            return False
            
        print(f" Configuration looks good!")
        print(f"   - {len(config.WEBSITES)} websites configured")
        print(f"   - Output folder: {config.OUTPUT_FOLDER}")
        return True
        
    except Exception as e:
        print(f" Configuration problem: {e}")
        return False


def test_main_script():
    """Check if main script can be imported"""
    print("\n Testing main script...")
    
    try:
        import main
        
        # Check if main functions exist
        if hasattr(main, 'make_newsletter'):
            print(" make_newsletter function found!")
        else:
            print(" make_newsletter function missing")
            return False
            
        if hasattr(main, 'show_help'):
            print(" show_help function found!")
        else:
            print(" show_help function missing") 
            return False
            
        print(" Main script is ready!")
        return True
        
    except Exception as e:
        print(f" Main script problem: {e}")
        return False


def main():
    """Run all tests and show results"""
    print("🧪 SIMPLE TESTS FOR STUDENTS")
    print("=" * 40)
    print("Let's check if everything is ready to use!")
    
    tests = [
        test_basic_setup,
        test_imports,
        test_configuration,
        test_main_script
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 40)
    print(" TEST RESULTS")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(" ALL TESTS PASSED!")
        print(" Everything looks ready to use!")
        print("\nYou can now run: python main.py")
    else:
        print(f" {passed}/{total} tests passed")
        print("\nSome things need to be fixed:")
        print("- Check the error messages above")
        print("- Make sure all packages are installed")
        print("- Ask for help if you're stuck!")


if __name__ == "__main__":
    main()
