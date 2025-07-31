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