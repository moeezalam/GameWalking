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