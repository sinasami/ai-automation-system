import time
from automation_engine import AutomationEngine
from database import CredentialManager
from captcha_solver import CaptchaSolver

def basic_login_example():
    print("=== Basic Login Example ===")
    
    automation_engine = AutomationEngine()
    
    try:
        if not automation_engine.start_automation("example.com", "testuser", headless=True):
            print("Failed to start automation")
            return
        
        login_config = {
            'login_url': 'https://example.com/login',
            'username_field': {'selector': 'input[name="username"]', 'by': 'css'},
            'password_field': {'selector': 'input[name="password"]', 'by': 'css'},
            'submit_button': {'selector': 'input[type="submit"]', 'by': 'css'},
            'success_indicators': ['logout', 'profile', 'dashboard']
        }
        
        success = automation_engine.login_to_website("example.com", "testuser", login_config)
        if success:
            print("Login successful!")
        else:
            print("Login failed!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        automation_engine.stop_automation()

def form_submission_example():
    print("=== Form Submission Example ===")
    
    automation_engine = AutomationEngine()
    
    try:
        if not automation_engine.start_automation("example.com", "testuser", headless=True):
            print("Failed to start automation")
            return
        
        form_config = {
            'form_url': 'https://example.com/apply',
            'fields': {
                'first_name': {'selector': 'input[name="first_name"]', 'by': 'css', 'type': 'text'},
                'last_name': {'selector': 'input[name="last_name"]', 'by': 'css', 'type': 'text'},
                'email': {'selector': 'input[name="email"]', 'by': 'css', 'type': 'text'},
                'experience': {'selector': 'select[name="experience"]', 'by': 'css', 'type': 'select'},
                'resume': {'selector': 'input[name="resume"]', 'by': 'css', 'type': 'file'}
            },
            'submit_button': {'selector': 'button[type="submit"]', 'by': 'css'},
            'success_indicators': ['thank you', 'submitted', 'success']
        }
        
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'experience': '5-10 years',
            'resume': '/path/to/resume.pdf'
        }
        
        success = automation_engine.submit_form("example.com", form_config, form_data)
        if success:
            print("Form submitted successfully!")
        else:
            print("Form submission failed!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        automation_engine.stop_automation()

def captcha_handling_example():
    print("=== CAPTCHA Handling Example ===")
    
    captcha_solver = CaptchaSolver()
    
    image_path = "captcha_image.png"
    
    captcha_text = captcha_solver.solve_captcha(image_path, "text")
    if captcha_text:
        print(f"CAPTCHA solved: {captcha_text}")
    else:
        print("Failed to solve CAPTCHA")
    
    math_result = captcha_solver.solve_captcha("2 + 3", "math")
    if math_result:
        print(f"Math CAPTCHA solved: {math_result}")
    else:
        print("Failed to solve math CAPTCHA")

def batch_processing_example():
    print("=== Batch Processing Example ===")
    
    automation_engine = AutomationEngine()
    
    websites = [
        {
            'website': 'linkedin.com',
            'username': 'user1',
            'login_config': {
                'login_url': 'https://linkedin.com/login',
                'username_field': {'selector': '#username', 'by': 'id'},
                'password_field': {'selector': '#password', 'by': 'id'},
                'submit_button': {'selector': 'button[type="submit"]', 'by': 'css'},
                'success_indicators': ['feed', 'network', 'profile']
            }
        },
        {
            'website': 'indeed.com',
            'username': 'user2',
            'login_config': {
                'login_url': 'https://secure.indeed.com/account/login',
                'username_field': {'selector': 'input[name="email"]', 'by': 'css'},
                'password_field': {'selector': 'input[name="password"]', 'by': 'css'},
                'submit_button': {'selector': 'button[type="submit"]', 'by': 'css'},
                'success_indicators': ['dashboard', 'jobs', 'profile']
            }
        }
    ]
    
    try:
        results = automation_engine.batch_process(websites, "login")
        
        print("Batch processing results:")
        for result in results:
            status = "✓ Success" if result['success'] else "✗ Failed"
            print(f"{result['website']} - {result['username']}: {status}")
            
    except Exception as e:
        print(f"Error during batch processing: {e}")

def custom_configuration_example():
    print("=== Custom Configuration Example ===")
    
    automation_engine = AutomationEngine()
    
    try:
        if not automation_engine.start_automation("custom.com", "user", headless=False):
            print("Failed to start automation")
            return
        
        custom_login_config = {
            'login_url': 'https://custom.com/auth',
            'username_field': {'selector': '.username-input', 'by': 'css'},
            'password_field': {'selector': '.password-input', 'by': 'css'},
            'submit_button': {'selector': '.login-btn', 'by': 'css'},
            'success_indicators': ['welcome', 'home', 'dashboard']
        }
        
        success = automation_engine.login_to_website("custom.com", "user", custom_login_config)
        if success:
            print("Custom login successful!")
            
            status = automation_engine.get_automation_status()
            print(f"Current URL: {status.get('current_url', 'Unknown')}")
            print(f"Page Title: {status.get('page_title', 'Unknown')}")
            
        else:
            print("Custom login failed!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        automation_engine.stop_automation()

def error_handling_example():
    print("=== Error Handling Example ===")
    
    automation_engine = AutomationEngine()
    
    try:
        if not automation_engine.start_automation("nonexistent.com", "user", headless=True):
            print("Failed to start automation")
            return
        
        login_config = {
            'login_url': 'https://nonexistent.com/login',
            'username_field': {'selector': 'input[name="username"]', 'by': 'css'},
            'password_field': {'selector': 'input[name="password"]', 'by': 'css'},
            'submit_button': {'selector': 'input[type="submit"]', 'by': 'css'},
            'success_indicators': ['logout', 'profile']
        }
        
        success = automation_engine.login_to_website("nonexistent.com", "user", login_config)
        if success:
            print("Login successful!")
        else:
            print("Login failed as expected")
            
    except Exception as e:
        print(f"Expected error occurred: {e}")
    finally:
        automation_engine.stop_automation()

def credential_management_example():
    print("=== Credential Management Example ===")
    
    credential_manager = CredentialManager()
    
    website = "example.com"
    username = "testuser"
    password = "testpass123"
    notes = "Test account for automation"
    
    if credential_manager.add_credential(website, username, password, notes):
        print("Credential added successfully")
        
        stored_credential = credential_manager.get_credential(website, username)
        if stored_credential:
            print(f"Retrieved credential for {username}")
            print(f"Notes: {stored_credential['notes']}")
        
        websites = credential_manager.list_websites()
        print(f"Stored websites: {websites}")
        
        if credential_manager.delete_credential(website, username):
            print("Credential deleted successfully")
    else:
        print("Failed to add credential")

def logging_and_monitoring_example():
    print("=== Logging and Monitoring Example ===")
    
    automation_engine = AutomationEngine()
    
    try:
        if not automation_engine.start_automation("example.com", "user", headless=True):
            print("Failed to start automation")
            return
        
        automation_engine.log_automation("example.com", "login", "started", "Automation initiated")
        
        time.sleep(2)
        
        status = automation_engine.get_automation_status()
        print(f"Automation status: {status}")
        
        logs = automation_engine.get_automation_logs(10)
        print(f"Recent logs: {len(logs)} entries")
        
        automation_engine.log_automation("example.com", "login", "completed", "Automation finished")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        automation_engine.stop_automation()

def main():
    print("AI-Powered Automation System - Example Usage")
    print("=" * 50)
    
    examples = [
        ("Basic Login", basic_login_example),
        ("Form Submission", form_submission_example),
        ("CAPTCHA Handling", captcha_handling_example),
        ("Batch Processing", batch_processing_example),
        ("Custom Configuration", custom_configuration_example),
        ("Error Handling", error_handling_example),
        ("Credential Management", credential_management_example),
        ("Logging and Monitoring", logging_and_monitoring_example)
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{i}. {name}")
    
    try:
        choice = int(input("\nSelect an example to run (1-8): "))
        if 1 <= choice <= len(examples):
            examples[choice-1][1]()
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")
    except KeyboardInterrupt:
        print("\nOperation cancelled")

if __name__ == "__main__":
    main()


