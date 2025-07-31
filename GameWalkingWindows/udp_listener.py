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