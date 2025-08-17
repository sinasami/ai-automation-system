import argparse
import logging
import sys
from pathlib import Path
import config
from database import CredentialManager
from automation_engine import AutomationEngine
from gui import AutomationGUI

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

def add_credentials():
    credential_manager = CredentialManager()
    
    print("Add Website Credentials")
    print("=" * 30)
    
    website = input("Website: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    notes = input("Notes (optional): ").strip()
    
    if not website or not username or not password:
        print("Error: Website, username, and password are required")
        return False
    
    if credential_manager.add_credential(website, username, password, notes):
        print("✓ Credential added successfully")
        return True
    else:
        print("✗ Failed to add credential")
        return False

def list_websites():
    credential_manager = CredentialManager()
    websites = credential_manager.list_websites()
    
    if not websites:
        print("No websites found")
        return
    
    print("Saved Websites:")
    print("=" * 20)
    for i, website in enumerate(websites, 1):
        print(f"{i}. {website}")

def show_logs(limit=50):
    credential_manager = CredentialManager()
    logs = credential_manager.get_automation_logs(limit)
    
    if not logs:
        print("No logs found")
        return
    
    print(f"Recent Automation Logs (Last {limit}):")
    print("=" * 50)
    print(f"{'Website':<20} {'Action':<15} {'Status':<10} {'Timestamp':<20}")
    print("-" * 70)
    
    for log in logs:
        website, action, status, timestamp, details = log
        print(f"{website:<20} {action:<15} {status:<10} {timestamp:<20}")
        if details:
            print(f"  Details: {details}")

def run_automation(website, username, headless=False):
    print(f"Starting automation for {website}")
    
    automation_engine = AutomationEngine()
    
    try:
        if not automation_engine.start_automation(website, username, headless):
            print("✗ Failed to start automation")
            return False
        
        print("✓ Browser started successfully")
        
        login_config = {
            'login_url': f'https://{website}/login',
            'username_field': {'selector': 'input[name="username"]', 'by': 'css'},
            'password_field': {'selector': 'input[name="password"]', 'by': 'css'},
            'submit_button': {'selector': 'input[type="submit"]', 'by': 'css'},
            'success_indicators': ['logout', 'profile', 'dashboard']
        }
        
        if automation_engine.login_to_website(website, username, login_config):
            print("✓ Login successful")
            return True
        else:
            print("✗ Login failed")
            return False
            
    except Exception as e:
        print(f"✗ Automation error: {e}")
        return False
    finally:
        automation_engine.stop_automation()

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Automation System")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    parser.add_argument("--automate", nargs=2, metavar=("WEBSITE", "USERNAME"), 
                       help="Run automation for specific website and username")
    parser.add_argument("--add-credentials", action="store_true", help="Add new credentials")
    parser.add_argument("--list-websites", action="store_true", help="List saved websites")
    parser.add_argument("--show-logs", action="store_true", help="Show automation logs")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--limit", type=int, default=50, help="Number of logs to show")
    
    args = parser.parse_args()
    
    setup_logging()
    
    if args.gui:
        print("Launching GUI...")
        app = AutomationGUI()
        app.run()
    elif args.automate:
        website, username = args.automate
        run_automation(website, username, args.headless)
    elif args.add_credentials:
        add_credentials()
    elif args.list_websites:
        list_websites()
    elif args.show_logs:
        show_logs(args.limit)
    else:
        parser.print_help()
        print("\nNo arguments provided. Use --gui to launch the interface.")

if __name__ == "__main__":
    main()


