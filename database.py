import sqlite3
import logging
from pathlib import Path
from cryptography.fernet import Fernet
import json
from datetime import datetime
import config

logger = logging.getLogger(__name__)

class CredentialManager:
    def __init__(self):
        self.db_path = config.DATABASE_FILE
        self.key_path = config.ENCRYPTION_KEY_FILE
        self.fernet = self._get_or_create_key()
        self._init_database()
    
    def _get_or_create_key(self):
        if self.key_path.exists():
            with open(self.key_path, 'rb') as key_file:
                return Fernet(key_file.read())
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
            return Fernet(key)
    
    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website TEXT NOT NULL,
                    username TEXT NOT NULL,
                    encrypted_password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website TEXT NOT NULL,
                    template_name TEXT NOT NULL,
                    form_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def add_credential(self, website, username, password, notes=""):
        try:
            encrypted_password = self.fernet.encrypt(password.encode())
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO credentials (website, username, encrypted_password, notes)
                    VALUES (?, ?, ?, ?)
                ''', (website, username, encrypted_password, notes))
                conn.commit()
                logger.info(f"Added credential for {website}")
                return True
        except Exception as e:
            logger.error(f"Error adding credential: {e}")
            return False
    
    def get_credential(self, website, username):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT encrypted_password, notes FROM credentials
                    WHERE website = ? AND username = ?
                ''', (website, username))
                result = cursor.fetchone()
                
                if result:
                    encrypted_password, notes = result
                    password = self.fernet.decrypt(encrypted_password).decode()
                    self._update_last_used(website, username)
                    return {"password": password, "notes": notes}
                return None
        except Exception as e:
            logger.error(f"Error getting credential: {e}")
            return None
    
    def _update_last_used(self, website, username):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE credentials SET last_used = CURRENT_TIMESTAMP
                    WHERE website = ? AND username = ?
                ''', (website, username))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating last_used: {e}")
    
    def list_websites(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT website FROM credentials')
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listing websites: {e}")
            return []
    
    def list_credentials(self, website):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username, created_at, last_used, notes
                    FROM credentials WHERE website = ?
                ''', (website,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error listing credentials: {e}")
            return []
    
    def delete_credential(self, website, username):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM credentials
                    WHERE website = ? AND username = ?
                ''', (website, username))
                conn.commit()
                logger.info(f"Deleted credential for {website}")
                return True
        except Exception as e:
            logger.error(f"Error deleting credential: {e}")
            return False
    
    def log_automation(self, website, action, status, details=""):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO automation_logs (website, action, status, details)
                    VALUES (?, ?, ?, ?)
                ''', (website, action, status, details))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging automation: {e}")
    
    def get_automation_logs(self, limit=100):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT website, action, status, timestamp, details
                    FROM automation_logs
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting automation logs: {e}")
            return []
    
    def save_form_template(self, website, template_name, form_data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO form_templates (website, template_name, form_data)
                    VALUES (?, ?, ?)
                ''', (website, template_name, json.dumps(form_data)))
                conn.commit()
                logger.info(f"Saved form template for {website}")
                return True
        except Exception as e:
            logger.error(f"Error saving form template: {e}")
            return False
    
    def get_form_template(self, website, template_name):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT form_data FROM form_templates
                    WHERE website = ? AND template_name = ?
                ''', (website, template_name))
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None
        except Exception as e:
            logger.error(f"Error getting form template: {e}")
            return None
    
    def list_form_templates(self, website):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT template_name, created_at
                    FROM form_templates WHERE website = ?
                ''', (website,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error listing form templates: {e}")
            return []


