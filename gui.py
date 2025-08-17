import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
from pathlib import Path
import config
from database import CredentialManager
from automation_engine import AutomationEngine

logger = logging.getLogger(__name__)

class AutomationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI-Powered Automation System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.credential_manager = CredentialManager()
        self.automation_engine = None
        self.current_automation = None
        
        self.setup_styles()
        self.create_widgets()
        self.setup_logging()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Error.TLabel', foreground='#e74c3c')
        style.configure('Info.TLabel', foreground='#3498db')
    
    def create_widgets(self):
        self.create_header()
        self.create_notebook()
        self.create_status_bar()
    
    def create_header(self):
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="AI-Powered Automation System", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(header_frame, text="Automate Login & Form Submission", 
                                 font=('Arial', 12), fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack()
    
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.create_credentials_tab()
        self.create_automation_tab()
        self.create_logs_tab()
        self.create_settings_tab()
    
    def create_credentials_tab(self):
        credentials_frame = ttk.Frame(self.notebook)
        self.notebook.add(credentials_frame, text="Credentials")
        
        left_frame = ttk.Frame(credentials_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(left_frame, text="Add New Credential", style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        form_frame = ttk.LabelFrame(left_frame, text="Credential Details", padding=10)
        form_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(form_frame, text="Website:").grid(row=0, column=0, sticky='w', pady=5)
        self.website_entry = ttk.Entry(form_frame, width=40)
        self.website_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(form_frame, text="Username:").grid(row=1, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(form_frame, width=40)
        self.username_entry.grid(row=1, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(form_frame, width=40, show='*')
        self.password_entry.grid(row=2, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky='w', pady=5)
        self.notes_entry = ttk.Entry(form_frame, width=40)
        self.notes_entry.grid(row=3, column=1, padx=(10, 0), pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add Credential", command=self.add_credential).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Clear Form", command=self.clear_credential_form).pack(side='left')
        
        right_frame = ttk.Frame(credentials_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right_frame, text="Stored Credentials", style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        self.website_var = tk.StringVar()
        website_combo = ttk.Combobox(right_frame, textvariable=self.website_var, state='readonly')
        website_combo.pack(fill='x', pady=(0, 10))
        website_combo.bind('<<ComboboxSelected>>', self.on_website_selected)
        
        self.credentials_tree = ttk.Treeview(right_frame, columns=('Username', 'Created', 'Last Used', 'Notes'), show='headings')
        self.credentials_tree.heading('Username', text='Username')
        self.credentials_tree.heading('Created', text='Created')
        self.credentials_tree.heading('Last Used', text='Last Used')
        self.credentials_tree.heading('Notes', text='Notes')
        self.credentials_tree.pack(fill='both', expand=True)
        
        button_frame2 = ttk.Frame(right_frame)
        button_frame2.pack(fill='x', pady=10)
        
        ttk.Button(button_frame2, text="Delete Selected", command=self.delete_credential).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame2, text="Refresh List", command=self.refresh_credentials).pack(side='left')
        
        self.refresh_websites()
    
    def create_automation_tab(self):
        automation_frame = ttk.Frame(self.notebook)
        self.notebook.add(automation_frame, text="Automation")
        
        left_frame = ttk.Frame(automation_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(left_frame, text="Start Automation", style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        config_frame = ttk.LabelFrame(left_frame, text="Automation Configuration", padding=10)
        config_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(config_frame, text="Website:").grid(row=0, column=0, sticky='w', pady=5)
        self.auto_website_var = tk.StringVar()
        self.auto_website_combo = ttk.Combobox(config_frame, textvariable=self.auto_website_var, state='readonly')
        self.auto_website_combo.grid(row=0, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        ttk.Label(config_frame, text="Username:").grid(row=1, column=0, sticky='w', pady=5)
        self.auto_username_var = tk.StringVar()
        self.auto_username_combo = ttk.Combobox(config_frame, textvariable=self.auto_username_var, state='readonly')
        self.auto_username_combo.grid(row=1, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        ttk.Label(config_frame, text="Action:").grid(row=2, column=0, sticky='w', pady=5)
        self.action_var = tk.StringVar(value="login")
        action_combo = ttk.Combobox(config_frame, textvariable=self.action_var, 
                                   values=["login", "form_submission"], state='readonly')
        action_combo.grid(row=2, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        ttk.Label(config_frame, text="Headless Mode:").grid(row=3, column=0, sticky='w', pady=5)
        self.headless_var = tk.BooleanVar()
        headless_check = ttk.Checkbutton(config_frame, variable=self.headless_var)
        headless_check.grid(row=3, column=1, padx=(10, 0), pady=5, sticky='w')
        
        config_frame.columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Automation", command=self.start_automation)
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Automation", command=self.stop_automation, state='disabled')
        self.stop_button.pack(side='left')
        
        right_frame = ttk.Frame(automation_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right_frame, text="Automation Status", style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        status_frame = ttk.LabelFrame(right_frame, text="Current Status", padding=10)
        status_frame.pack(fill='x', pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, text="No automation running", style='Info.TLabel')
        self.status_label.pack(anchor='w')
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=(10, 0))
        
        log_frame = ttk.LabelFrame(right_frame, text="Automation Log", padding=10)
        log_frame.pack(fill='both', expand=True)
        
        self.automation_log = tk.Text(log_frame, height=15, wrap='word')
        self.automation_log.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.automation_log.yview)
        scrollbar.pack(side='right', fill='y')
        self.automation_log.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_websites()
    
    def create_logs_tab(self):
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        ttk.Label(logs_frame, text="Automation Logs", style='Header.TLabel').pack(anchor='w', padx=20, pady=10)
        
        controls_frame = ttk.Frame(logs_frame)
        controls_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ttk.Label(controls_frame, text="Limit:").pack(side='left')
        self.log_limit_var = tk.StringVar(value="100")
        log_limit_combo = ttk.Combobox(controls_frame, textvariable=self.log_limit_var, 
                                      values=["50", "100", "200", "500"], width=10)
        log_limit_combo.pack(side='left', padx=(10, 20))
        
        ttk.Button(controls_frame, text="Refresh Logs", command=self.refresh_logs).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Clear Logs", command=self.clear_logs).pack(side='left')
        
        self.logs_tree = ttk.Treeview(logs_frame, columns=('Website', 'Action', 'Status', 'Timestamp', 'Details'), show='headings')
        self.logs_tree.heading('Website', text='Website')
        self.logs_tree.heading('Action', text='Action')
        self.logs_tree.heading('Status', text='Status')
        self.logs_tree.heading('Timestamp', text='Timestamp')
        self.logs_tree.heading('Details', text='Details')
        
        self.logs_tree.column('Website', width=150)
        self.logs_tree.column('Action', width=100)
        self.logs_tree.column('Status', width=80)
        self.logs_tree.column('Timestamp', width=150)
        self.logs_tree.column('Details', width=200)
        
        self.logs_tree.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.refresh_logs()
    
    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        ttk.Label(settings_frame, text="System Settings", style='Header.TLabel').pack(anchor='w', padx=20, pady=10)
        
        settings_container = ttk.Frame(settings_frame)
        settings_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        browser_frame = ttk.LabelFrame(settings_container, text="Browser Settings", padding=10)
        browser_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(browser_frame, text="Default Browser:").grid(row=0, column=0, sticky='w', pady=5)
        self.browser_var = tk.StringVar(value=config.BROWSER_TYPE)
        browser_combo = ttk.Combobox(browser_frame, textvariable=self.browser_var, 
                                    values=["chrome", "firefox", "edge"], state='readonly')
        browser_combo.grid(row=0, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        ttk.Label(browser_frame, text="Default Headless:").grid(row=1, column=0, sticky='w', pady=5)
        self.default_headless_var = tk.BooleanVar(value=config.HEADLESS)
        default_headless_check = ttk.Checkbutton(browser_frame, variable=self.default_headless_var)
        default_headless_check.grid(row=1, column=1, padx=(10, 0), pady=5, sticky='w')
        
        browser_frame.columnconfigure(1, weight=1)
        
        timing_frame = ttk.LabelFrame(settings_container, text="Timing Settings", padding=10)
        timing_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(timing_frame, text="Implicit Wait (seconds):").grid(row=0, column=0, sticky='w', pady=5)
        self.implicit_wait_var = tk.StringVar(value=str(config.IMPLICIT_WAIT))
        implicit_wait_entry = ttk.Entry(timing_frame, textvariable=self.implicit_wait_var, width=10)
        implicit_wait_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky='w')
        
        ttk.Label(timing_frame, text="Page Load Timeout (seconds):").grid(row=1, column=0, sticky='w', pady=5)
        self.page_load_timeout_var = tk.StringVar(value=str(config.PAGE_LOAD_TIMEOUT))
        page_load_timeout_entry = ttk.Entry(timing_frame, textvariable=self.page_load_timeout_var, width=10)
        page_load_timeout_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky='w')
        
        timing_frame.columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(settings_container)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_settings).pack(side='left')
    
    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready", relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
    
    def setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format=config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def add_credential(self):
        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        notes = self.notes_entry.get().strip()
        
        if not website or not username or not password:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if self.credential_manager.add_credential(website, username, password, notes):
            messagebox.showinfo("Success", "Credential added successfully")
            self.clear_credential_form()
            self.refresh_websites()
            self.refresh_credentials()
        else:
            messagebox.showerror("Error", "Failed to add credential")
    
    def clear_credential_form(self):
        self.website_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)
    
    def refresh_websites(self):
        websites = self.credential_manager.list_websites()
        self.website_var.set('')
        self.auto_website_var.set('')
        
        website_combo = self.notebook.children['!frame2'].children['!frame2'].children['!combobox']
        website_combo['values'] = websites
        
        self.auto_website_combo['values'] = websites
    
    def on_website_selected(self, event=None):
        website = self.website_var.get()
        if website:
            self.refresh_credentials()
    
    def refresh_credentials(self):
        website = self.website_var.get()
        if not website:
            return
        
        for item in self.credentials_tree.get_children():
            self.credentials_tree.delete(item)
        
        credentials = self.credential_manager.list_credentials(website)
        for cred in credentials:
            username, created, last_used, notes = cred
            self.credentials_tree.insert('', 'end', values=(username, created, last_used, notes))
    
    def delete_credential(self):
        selection = self.credentials_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a credential to delete")
            return
        
        item = self.credentials_tree.item(selection[0])
        username = item['values'][0]
        website = self.website_var.get()
        
        if messagebox.askyesno("Confirm", f"Delete credential for {username} on {website}?"):
            if self.credential_manager.delete_credential(website, username):
                messagebox.showinfo("Success", "Credential deleted successfully")
                self.refresh_credentials()
            else:
                messagebox.showerror("Error", "Failed to delete credential")
    
    def start_automation(self):
        website = self.auto_website_var.get()
        username = self.auto_username_var.get()
        action = self.action_var.get()
        headless = self.headless_var.get()
        
        if not website or not username:
            messagebox.showerror("Error", "Please select website and username")
            return
        
        self.automation_engine = AutomationEngine()
        
        def run_automation():
            try:
                if not self.automation_engine.start_automation(website, username, headless):
                    self.log_message("Failed to start automation")
                    return
                
                self.log_message(f"Started {action} automation for {website}")
                
                if action == "login":
                    login_config = self._get_default_login_config(website)
                    success = self.automation_engine.login_to_website(website, username, login_config)
                    if success:
                        self.log_message("Login successful")
                    else:
                        self.log_message("Login failed")
                
                self.log_message("Automation completed")
                
            except Exception as e:
                self.log_message(f"Automation error: {e}")
            finally:
                self.root.after(0, self._automation_finished)
        
        self.current_automation = threading.Thread(target=run_automation, daemon=True)
        self.current_automation.start()
        
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start()
        self.status_label.config(text="Automation running...", style='Success.TLabel')
    
    def stop_automation(self):
        if self.automation_engine:
            self.automation_engine.stop_automation()
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.status_label.config(text="Automation stopped", style='Info.TLabel')
    
    def _automation_finished(self):
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.status_label.config(text="Automation finished", style='Info.TLabel')
    
    def _get_default_login_config(self, website):
        return {
            'login_url': f'https://{website}/login',
            'username_field': {'selector': 'input[name="username"]', 'by': 'css'},
            'password_field': {'selector': 'input[name="password"]', 'by': 'css'},
            'submit_button': {'selector': 'input[type="submit"]', 'by': 'css'},
            'success_indicators': ['logout', 'profile', 'dashboard']
        }
    
    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.automation_log.insert(tk.END, log_entry)
        self.automation_log.see(tk.END)
        
        self.root.update_idletasks()
    
    def refresh_logs(self):
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        try:
            limit = int(self.log_limit_var.get())
            logs = self.credential_manager.get_automation_logs(limit)
            
            for log in logs:
                website, action, status, timestamp, details = log
                self.logs_tree.insert('', 'end', values=(website, action, status, timestamp, details))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load logs: {e}")
    
    def clear_logs(self):
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            try:
                import sqlite3
                with sqlite3.connect(config.DATABASE_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM automation_logs")
                    conn.commit()
                
                self.refresh_logs()
                messagebox.showinfo("Success", "Logs cleared successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {e}")
    
    def save_settings(self):
        try:
            config.BROWSER_TYPE = self.browser_var.get()
            config.HEADLESS = self.default_headless_var.get()
            config.IMPLICIT_WAIT = int(self.implicit_wait_var.get())
            config.PAGE_LOAD_TIMEOUT = int(self.page_load_timeout_var.get())
            
            messagebox.showinfo("Success", "Settings saved successfully")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings(self):
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            self.browser_var.set("chrome")
            self.default_headless_var.set(False)
            self.implicit_wait_var.set("10")
            self.page_load_timeout_var.set("30")
            
            messagebox.showinfo("Success", "Settings reset to defaults")
    
    def on_closing(self):
        if self.automation_engine:
            self.automation_engine.stop_automation()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    import time
    app = AutomationGUI()
    app.run()


