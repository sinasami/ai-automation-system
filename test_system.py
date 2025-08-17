import sys
import subprocess
import importlib
import os
from pathlib import Path

def test_imports():
    print("Testing module imports...")
    
    modules = [
        'config',
        'database',
        'browser_automation',
        'captcha_solver',
        'automation_engine',
        'gui'
    ]
    
    all_imports_ok = True
    
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name} imported successfully")
        except ImportError as e:
            print(f"✗ {module_name} import failed: {e}")
            all_imports_ok = False
    
    return all_imports_ok

def test_config():
    print("\nTesting configuration...")
    
    try:
        import config
        
        required_attrs = [
            'BASE_DIR', 'DATA_DIR', 'LOGS_DIR', 'SCREENSHOTS_DIR', 'TEMPLATES_DIR',
            'BROWSER_TYPE', 'HEADLESS', 'IMPLICIT_WAIT', 'PAGE_LOAD_TIMEOUT',
            'ENCRYPTION_KEY_FILE', 'DATABASE_FILE', 'LOG_LEVEL', 'LOG_FORMAT', 'LOG_FILE'
        ]
        
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(config, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"✗ Missing configuration attributes: {missing_attrs}")
            return False
        else:
            print("✓ All required configuration attributes present")
            return True
            
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_database():
    print("\nTesting database functionality...")
    
    try:
        from database import CredentialManager
        
        credential_manager = CredentialManager()
        
        test_website = "test.com"
        test_username = "testuser"
        test_password = "testpass123"
        test_notes = "Test credential"
        
        if credential_manager.add_credential(test_website, test_username, test_password, test_notes):
            print("✓ Credential added successfully")
        else:
            print("✗ Failed to add credential")
            return False
        
        stored_credential = credential_manager.get_credential(test_website, test_username)
        if stored_credential and stored_credential['password'] == test_password:
            print("✓ Credential retrieved successfully")
        else:
            print("✗ Failed to retrieve credential")
            return False
        
        websites = credential_manager.list_websites()
        if test_website in websites:
            print("✓ Website listed successfully")
        else:
            print("✗ Website not found in list")
            return False
        
        if credential_manager.delete_credential(test_website, test_username):
            print("✓ Credential deleted successfully")
        else:
            print("✗ Failed to delete credential")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_cli():
    print("\nTesting CLI functionality...")
    
    try:
        result = subprocess.run([sys.executable, "main.py", "--help"],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and "usage: main.py" in result.stdout:
            print("✓ CLI help command works")
        else:
            print(f"✗ CLI help command failed - return code: {result.returncode}")
            print(f"Output: {result.stdout[:200]}...")
            return False
        
        result = subprocess.run([sys.executable, "main.py", "--list-websites"],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ CLI list-websites command works")
        else:
            print(f"✗ CLI list-websites command failed - return code: {result.returncode}")
            print(f"Error: {result.stderr[:200]}...")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("✗ CLI test timed out")
        return False
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False

def test_file_structure():
    print("\nTesting file structure...")
    
    required_files = [
        'main.py',
        'config.py',
        'database.py',
        'browser_automation.py',
        'captcha_solver.py',
        'automation_engine.py',
        'gui.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    for file_name in required_files:
        if not Path(file_name).exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files present")
        return True

def test_dependencies():
    print("\nTesting dependencies...")
    
    try:
        import selenium
        print("✓ Selenium imported successfully")
    except ImportError:
        print("✗ Selenium not available")
        return False
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError:
        print("✗ OpenCV not available")
        return False
    
    try:
        import pytesseract
        print("✓ Tesseract imported successfully")
    except ImportError:
        print("✗ Tesseract not available")
        return False
    
    try:
        from cryptography.fernet import Fernet
        print("✓ Cryptography imported successfully")
    except ImportError:
        print("✗ Cryptography not available")
        return False
    
    return True

def main():
    print("AI-Powered Automation System - System Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("CLI", test_cli)
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results[test_name] = False
            all_passed = False
    
    print(f"\n{'='*50}")
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    if all_passed:
        print(f"\n🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print(f"\n❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
