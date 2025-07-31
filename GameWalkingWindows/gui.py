import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import pystray
from PIL import Image, ImageDraw
import os
import sys

class GameWalkingGUI:
    def __init__(self, udp_listener, key_sender):
        self.udp_listener = udp_listener
        self.key_sender = key_sender
        self.root = tk.Tk()
        self.is_minimized_to_tray = False
        
        # Set up the main window
        self.setup_window()
        self.create_widgets()
        self.setup_tray()
        
        # Status update timer
        self.update_status_timer()
        
    def setup_window(self):
        """Set up main window properties"""
        self.root.title("GameWalking Desktop")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass  # Icon file not found, continue without it
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="GameWalking Desktop", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Connection Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.status_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.port_label = ttk.Label(status_frame, text="9000")
        self.port_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Steps Received:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.steps_label = ttk.Label(status_frame, text="0")
        self.steps_label.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Last Step:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.last_step_label = ttk.Label(status_frame, text="Never")
        self.last_step_label.grid(row=3, column=1, sticky=tk.W)
        
        # Control Buttons Frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        
        self.start_button = ttk.Button(control_frame, text="Start Listener", 
                                      command=self.start_listener)
        self.start_button.grid(row=0, column=0, padx=(0, 5), pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Listener", 
                                     command=self.stop_listener, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(5, 0), pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.activate_button = ttk.Button(control_frame, text="Activate Key Sender", 
                                         command=self.toggle_key_sender)
        self.activate_button.grid(row=1, column=0, padx=(0, 5), pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.test_button = ttk.Button(control_frame, text="Test Key", 
                                     command=self.test_key)
        self.test_button.grid(row=1, column=1, padx=(5, 0), pady=(0, 5), sticky=(tk.W, tk.E))
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(settings_frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.port_entry = ttk.Entry(settings_frame, width=10)
        self.port_entry.insert(0, "9000")
        self.port_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(settings_frame, text="Forward Key:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.key_entry = ttk.Entry(settings_frame, width=10)
        self.key_entry.insert(0, "w")
        self.key_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(settings_frame, text="Key Hold Duration (s):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.duration_entry = ttk.Entry(settings_frame, width=10)
        self.duration_entry.insert(0, "0.05")
        self.duration_entry.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        self.save_settings_button = ttk.Button(settings_frame, text="Save Settings", 
                                              command=self.save_settings)
        self.save_settings_button.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Create text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
        # Minimize to tray checkbox
        self.minimize_to_tray_var = tk.BooleanVar()
        minimize_check = ttk.Checkbutton(main_frame, text="Minimize to system tray", 
                                        variable=self.minimize_to_tray_var)
        minimize_check.grid(row=5, column=0, columnspan=2, pady=(10, 0))
    
    def setup_tray(self):
        """Set up system tray icon"""
        # Create tray icon image
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        draw.text((24, 24), 'GW', fill='blue')
        
        # Create tray icon
        menu = (
            pystray.MenuItem("Show", self.show_from_tray),
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("GameWalking", image, "GameWalking Desktop", menu)
    
    def start_listener(self):
        """Start UDP listener"""
        if self.udp_listener.start_listening():
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.log_message("UDP Listener started")
        else:
            messagebox.showerror("Error", "Failed to start UDP listener")
    
    def stop_listener(self):
        """Stop UDP listener"""
        self.udp_listener.stop_listening()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log_message("UDP Listener stopped")
    
    def toggle_key_sender(self):
        """Toggle key sender activation"""
        if self.key_sender.is_active:
            self.key_sender.deactivate()
            self.activate_button.config(text="Activate Key Sender")
            self.log_message("Key sender deactivated")
        else:
            self.key_sender.activate()
            self.activate_button.config(text="Deactivate Key Sender")
            self.log_message("Key sender activated")
    
    def test_key(self):
        """Test key sending"""
        self.key_sender.test_key()
        self.log_message(f"Test key sent: {self.key_sender.forward_key}")
    
    def save_settings(self):
        """Save current settings"""
        try:
            port = int(self.port_entry.get())
            key = self.key_entry.get().strip()
            duration = float(self.duration_entry.get())
            
            if port < 1024 or port > 65535:
                raise ValueError("Port must be between 1024 and 65535")
            
            if not key:
                raise ValueError("Forward key cannot be empty")
            
            if duration < 0.01 or duration > 1.0:
                raise ValueError("Duration must be between 0.01 and 1.0 seconds")
            
            # Update settings
            if self.udp_listener.update_port(port):
                self.port_label.config(text=str(port))
            
            self.key_sender.update_settings(key, None, duration)
            
            messagebox.showinfo("Success", "Settings saved successfully")
            self.log_message("Settings updated")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid settings: {e}")
    
    def update_status(self, status_info):
        """Update status display with info from UDP listener"""
        if status_info['is_listening']:
            self.status_label.config(text=status_info['connection_status'], foreground="green")
        else:
            self.status_label.config(text="Disconnected", foreground="red")
        
        self.steps_label.config(text=str(status_info['steps_received']))
        
        if status_info['last_step_time'] > 0:
            last_step = datetime.fromtimestamp(status_info['last_step_time'])
            self.last_step_label.config(text=last_step.strftime("%H:%M:%S"))
        else:
            self.last_step_label.config(text="Never")
    
    def update_status_timer(self):
        """Timer to update status regularly"""
        status = self.udp_listener.get_status()
        self.update_status(status)
        
        # Schedule next update
        self.root.after(1000, self.update_status_timer)
    
    def log_message(self, message):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Limit log size (keep last 1000 lines)
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete("1.0", f"{len(lines)-1000}.0")
    
    def clear_log(self):
        """Clear activity log"""
        self.log_text.delete("1.0", tk.END)
    
    def on_closing(self):
        """Handle window close event"""
        if self.minimize_to_tray_var.get():
            self.hide_to_tray()
        else:
            self.quit_app()
    
    def hide_to_tray(self):
        """Hide window to system tray"""
        self.root.withdraw()
        self.is_minimized_to_tray = True
        
        # Start tray icon in separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def show_from_tray(self, icon=None, item=None):
        """Show window from system tray"""
        if self.is_minimized_to_tray:
            self.tray_icon.stop()
            self.is_minimized_to_tray = False
        
        self.root.deiconify()
        self.root.lift()
    
    def quit_app(self, icon=None, item=None):
        """Quit application"""
        # Stop listener
        if self.udp_listener.is_listening:
            self.udp_listener.stop_listening()
        
        # Stop key sender
        self.key_sender.deactivate()
        
        # Stop tray icon
        if self.is_minimized_to_tray:
            self.tray_icon.stop()
        
        # Quit
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the GUI"""
        self.log_message("GameWalking Desktop started")
        self.root.mainloop()