#!/usr/bin/env python3
"""
Test Runner for AI Newsletter Generator
Run all tests from the tests directory
"""

import os
import sys
import subprocess
import importlib.util

# Add parent directory to path so we can import from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n{'='*50}")
    print(f"Running: {test_file}")
    print('='*50)
    
    try:
        # Change to project root directory
        project_root = os.path.join(os.path.dirname(__file__), '..')
        os.chdir(project_root)
        
        # Run the test file
        result = subprocess.run([sys.executable, os.path.join('tests', test_file)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
                
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False


def discover_and_run_tests():
    """Discover and run all test files"""
    tests_dir = os.path.dirname(__file__)
    test_files = []
    
    # Find all test files
    for file in os.listdir(tests_dir):
        if file.startswith('test_') and file.endswith('.py'):
            test_files.append(file)
    
    if not test_files:
        print("No test files found!")
        return
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file}")
    
    results = []
    for test_file in test_files:
        success = run_test_file(test_file)
        results.append((test_file, success))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_file, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} {test_file}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    print("🧪 AI Newsletter Generator Test Runner")
    discover_and_run_tests()
