# GameWalking Windows Desktop Development Guide

## Overview
This guide will help you create a Windows desktop application that receives UDP signals from the Android app and converts them into keyboard inputs for games like Death Stranding.

## Prerequisites
- Python 3.8 or higher
- Windows 10/11
- Administrator privileges (for firewall configuration)

## Project Setup

### 1. Create Project Directory
```
GameWalking-Desktop/
├── main.py
├── udp_listener.py
├── key_sender.py
├── config.py
├── gui.py
├── requirements.txt
├── build_exe.py
└── README.md
```

### 2. Install Required Packages

Create `requirements.txt`:
```
pyautogui==0.9.54
tkinter
socket
threading
configparser
pyinstaller==6.3.0
pystray==0.19.4
pillow==10.1.0
```

Install packages:
```bash
pip install -r requirements.txt
```

## Step 1: Create config.py

```python
import configparser
import os

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = 'gamewalking_config.ini'
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.config['NETWORK'] = {
            'port': '9000',
            'buffer_size': '1024'
        }
        
        self.config['CONTROLS'] = {
            'forward_key': 'w',
            'step_duration': '0.1',
            'key_hold_duration': '0.05'
        }
        
        self.config['GENERAL'] = {
            'minimize_to_tray': 'true',
            'auto_start': 'false',
            'debug_mode': 'false'
        }
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
    
    def get(self, section, key, fallback=None):
        """Get configuration value"""
        return self.config.get(section, key, fallback=fallback)
    
    def getint(self, section, key, fallback=None):
        """Get integer configuration value"""
        return self.config.getint(section, key, fallback=fallback)
    
    def getfloat(self, section, key, fallback=None):
        """Get float configuration value"""
        return self.config.getfloat(section, key, fallback=fallback)
    
    def getboolean(self, section, key, fallback=None):
        """Get boolean configuration value"""
        return self.config.getboolean(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()
```

## Step 2: Create key_sender.py

```python
import pyautogui
import time
import threading
from config import Config

class KeySender:
    def __init__(self):
        self.config = Config()
        self.is_active = False
        self.lock = threading.Lock()
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01  # Minimal pause between actions
        
        # Get configuration
        self.forward_key = self.config.get('CONTROLS', 'forward_key', 'w')
        self.step_duration = self.config.getfloat('CONTROLS', 'step_duration', 0.1)
        self.key_hold_duration = self.config.getfloat('CONTROLS', 'key_hold_duration', 0.05)
        
        self.debug_mode = self.config.getboolean('GENERAL', 'debug_mode', False)
        
    def send_step(self):
        """Send a step command (forward movement)"""
        if not self.is_active:
            return
            
        with self.lock:
            try:
                if self.debug_mode:
                    print(f"Sending key: {self.forward_key}")
                
                # Press and hold the key briefly
                pyautogui.keyDown(self.forward_key)
                time.sleep(self.key_hold_duration)
                pyautogui.keyUp(self.forward_key)
                
                # Small delay to prevent spam
                time.sleep(0.01)
                
            except pyautogui.FailSafeException:
                print("PyAutoGUI FailSafe triggered - mouse moved to corner")
                self.is_active = False
            except Exception as e:
                print(f"Error sending key: {e}")
    
    def send_continuous_forward(self, duration):
        """Send continuous forward movement for specified duration"""
        if not self.is_active:
            return
            
        try:
            if self.debug_mode:
                print(f"Continuous forward for {duration} seconds")
            
            pyautogui.keyDown(self.forward_key)
            time.sleep(duration)
            pyautogui.keyUp(self.forward_key)
            
        except pyautogui.FailSafeException:
            print("PyAutoGUI FailSafe triggered")
            self.is_active = False
            pyautogui.keyUp(self.forward_key)  # Ensure key is released
        except Exception as e:
            print(f"Error in continuous forward: {e}")
            pyautogui.keyUp(self.forward_key)  # Ensure key is released
    
    def activate(self):
        """Activate key sending"""
        self.is_active = True
        print("Key sender activated")
    
    def deactivate(self):
        """Deactivate key sending"""
        self.is_active = False
        # Release any held keys
        try:
            pyautogui.keyUp(self.forward_key)
        except:
            pass
        print("Key sender deactivated")
    
    def update_settings(self, forward_key=None, step_duration=None, key_hold_duration=None):
        """Update key sender settings"""
        if forward_key:
            self.forward_key = forward_key
            self.config.set('CONTROLS', 'forward_key', forward_key)
        
        if step_duration:
            self.step_duration = step_duration
            self.config.set('CONTROLS', 'step_duration', str(step_duration))
        
        if key_hold_duration:
            self.key_hold_duration = key_hold_duration
            self.config.set('CONTROLS', 'key_hold_duration', str(key_hold_duration))
    
    def test_key(self):
        """Test key sending functionality"""
        print(f"Testing key: {self.forward_key}")
        self.send_step()
```

## Step 3: Create udp_listener.py

```python
import socket
import threading
import time
from config import Config

class UDPListener:
    def __init__(self, key_sender, gui_callback=None):
        self.config = Config()
        self.key_sender = key_sender
        self.gui_callback = gui_callback
        
        self.port = self.config.getint('NETWORK', 'port', 9000)
        self.buffer_size = self.config.getint('NETWORK', 'buffer_size', 1024)
        self.debug_mode = self.config.getboolean('GENERAL', 'debug_mode', False)
        
        self.socket = None
        self.is_listening = False
        self.listener_thread = None
        
        # Statistics
        self.steps_received = 0
        self.last_step_time = 0
        self.connection_status = "Disconnected"
        
    def start_listening(self):
        """Start UDP listener"""
        if self.is_listening:
            print("Listener already running")
            return False
        
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to all interfaces on specified port
            self.socket.bind(('', self.port))
            self.socket.settimeout(1.0)  # 1 second timeout for recv
            
            self.is_listening = True
            self.connection_status = "Listening"
            
            # Start listener thread
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()
            
            print(f"UDP Listener started on port {self.port}")
            self._update_gui_status()
            return True
            
        except socket.error as e:
            print(f"Failed to start UDP listener: {e}")
            self.connection_status = f"Error: {e}"
            self._update_gui_status()
            return False
    
    def stop_listening(self):
        """Stop UDP listener"""
        if not self.is_listening:
            print("Listener not running")
            return
        
        self.is_listening = False
        self.connection_status = "Stopping"
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=2.0)
        
        self.connection_status = "Disconnected"
        print("UDP Listener stopped")
        self._update_gui_status()
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                # Receive data
                data, addr = self.socket.recvfrom(self.buffer_size)
                message = data.decode('utf-8').strip()
                
                if self.debug_mode:
                    print(f"Received from {addr}: {message}")
                
                # Process message
                if message == "STEP":
                    self._handle_step(addr)
                else:
                    if self.debug_mode:
                        print(f"Unknown message: {message}")
                
            except socket.timeout:
                # Timeout is normal, just continue
                continue
            except socket.error as e:
                if self.is_listening:  # Only log if we're supposed to be listening
                    print(f"Socket error: {e}")
                break
            except Exception as e:
                print(f"Unexpected error in listener: {e}")
                break
        
        print("Listener loop ended")
    
    def _handle_step(self, addr):
        """Handle received step command"""
        self.steps_received += 1
        self.last_step_time = time.time()
        self.connection_status = f"Connected to {addr[0]}"
        
        # Send key command
        self.key_sender.send_step()
        
        # Update GUI
        self._update_gui_status()
        
        if self.debug_mode:
            print(f"Step #{self.steps_received} processed")
    
    def _update_gui_status(self):
        """Update GUI with current status"""
        if self.gui_callback:
            status_info = {
                'connection_status': self.connection_status,
                'steps_received': self.steps_received,
                'last_step_time': self.last_step_time,
                'is_listening': self.is_listening
            }
            self.gui_callback(status_info)
    
    def get_status(self):
        """Get current listener status"""
        return {
            'is_listening': self.is_listening,
            'connection_status': self.connection_status,
            'steps_received': self.steps_received,
            'last_step_time': self.last_step_time,
            'port': self.port
        }
    
    def update_port(self, new_port):
        """Update listening port"""
        if self.is_listening:
            print("Cannot change port while listening")
            return False
        
        self.port = new_port
        self.config.set('NETWORK', 'port', str(new_port))
        return True
```

## Step 4: Create gui.py

```python
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
```

## Step 5: Create main.py

```python
#!/usr/bin/env python3
"""
GameWalking Desktop Application
Receives UDP signals from Android app and converts to keyboard input for games
"""

import sys
import os
import argparse
from config import Config
from key_sender import KeySender
from udp_listener import UDPListener
from gui import GameWalkingGUI

def setup_firewall_message():
    """Display firewall setup message"""
    print("=" * 60)
    print("FIREWALL CONFIGURATION REQUIRED")
    print("=" * 60)
    print("To allow the Android app to connect, you need to:")
    print("1. Open Windows Defender Firewall")
    print("2. Click 'Allow an app or feature through Windows Defender Firewall'")
    print("3. Click 'Change Settings' then 'Allow another app...'")
    print("4. Browse and select this GameWalking.exe")
    print("5. Make sure both 'Private' and 'Public' are checked")
    print("6. Click OK")
    print()
    print("Alternative: Run this command as Administrator:")
    print(f"netsh advfirewall firewall add rule name=\"GameWalking\" dir=in action=allow protocol=UDP localport=9000")
    print("=" * 60)
    print()

def main():
    parser = argparse.ArgumentParser(description='GameWalking Desktop Application')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI (console mode)')
    parser.add_argument('--port', type=int, default=9000, help='UDP port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Show firewall message
    setup_firewall_message()
    
    # Initialize components
    config = Config()
    if args.debug:
        config.set('GENERAL', 'debug_mode', 'true')
    
    key_sender = KeySender()
    
    if args.no_gui:
        # Console mode
        udp_listener = UDPListener(key_sender)
        if args.port != 9000:
            udp_listener.update_port(args.port)
        
        print(f"Starting GameWalking in console mode on port {udp_listener.port}")
        print("Press Ctrl+C to stop")
        
        try:
            key_sender.activate()
            udp_listener.start_listening()
            
            # Keep running
            while True:
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            udp_listener.stop_listening()
            key_sender.deactivate()
    else:
        # GUI mode
        def gui_status_callback(status_info):
            # This will be called by UDP listener to update GUI
            pass
        
        udp_listener = UDPListener(key_sender, gui_status_callback)
        if args.port != 9000:
            udp_listener.update_port(args.port)
        
        # Create and run GUI
        app = GameWalkingGUI(udp_listener, key_sender)
        # Update callback to point to GUI
        udp_listener.gui_callback = app.update_status
        
        try:
            app.run()
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Cleanup
            if udp_listener.is_listening:
                udp_listener.stop_listening()
            key_sender.deactivate()

if __name__ == "__main__":
    main()
```

## Step 6: Create build_exe.py

```python
"""
Build script to create executable using PyInstaller
"""

import PyInstaller.__main__
import os
import sys

def build_executable():
    """Build executable using PyInstaller"""
    
    # PyInstaller arguments
    args = [
        'main.py',
        '--name=GameWalking',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',  # Optional: add if you have an icon
        '--add-data=gamewalking_config.ini;.',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--collect-submodules=pystray',
        '--noconsole',
    ]
    
    # Remove icon argument if file doesn't exist
    if not os.path.exists('icon.ico'):
        args = [arg for arg in args if not arg.startswith('--icon')]
    
    print("Building executable...")
    print("Arguments:", args)
    
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete!")
    print("Executable location: dist/GameWalking.exe")
    print("\nNote: Make sure to configure Windows Firewall to allow this application")

if __name__ == "__main__":
    build_executable()
```

## Step 7: Windows Firewall Configuration

### Automatic Method (Run as Administrator):
```batch
@echo off
echo Adding GameWalking to Windows Firewall...
netsh advfirewall firewall add rule name="GameWalking UDP" dir=in action=allow protocol=UDP localport=9000
netsh advfirewall firewall add rule name="GameWalking TCP" dir=in action=allow protocol=TCP localport=9000
echo Firewall rules added successfully!
pause
```

### Manual Method:
1. Open Windows Defender Firewall with Advanced Security
2. Click "Inbound Rules" → "New Rule"
3. Select "Port" → "UDP" → "Specific local ports: 9000"
4. Allow the connection
5. Apply to all profiles (Domain, Private, Public)
6. Name it "GameWalking"

## Building and Distribution

### Development Testing:
```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py

# Run with debug
python main.py --debug

# Run console mode
python main.py --no-gui
```

### Build Executable:
```bash
# Build executable
python build_exe.py

# The executable will be in dist/GameWalking.exe
```

### Distribution Package Structure:
```
GameWalking-v1.0/
├── GameWalking.exe
├── README.txt
├── firewall_setup.bat
└── INSTALL.txt
```

## Testing

### Network Testing:
1. Find your PC's IP address: `ipconfig`
2. Test UDP connectivity: `netstat -an | findstr :9000`
3. Use network testing tools if needed

### Game Testing:
1. Start GameWalking.exe
2. Click "Start Listener"
3. Click "Activate Key Sender" 
4. Open Death Stranding (or any game)
5. Connect Android app with PC's IP
6. Walk with phone - character should move forward

## Troubleshooting

### Common Issues:
1. **Firewall blocking**: Configure Windows Firewall
2. **Port already in use**: Change port in settings
3. **Game not responding**: Check if game window is active
4. **PyAutoGUI FailSafe**: Move mouse away from screen corners

### Debug Mode:
- Enable debug in GUI or use `--debug` flag
- Check console output for detailed logs
- Verify UDP packets are being received

### Performance Tips:
- Close unnecessary applications
- Ensure stable WiFi connection
- Adjust key hold duration for different games
- Use wired network if wireless is unstable

This completes the Windows Desktop development guide. The application provides both GUI and console modes, proper firewall configuration, and robust error handling for reliable game control.