#!/usr/bin/env python3
"""
Network connectivity test for GameWalking
"""

import socket
import sys

def test_udp_listener(port=9000):
    """Test if we can bind to the UDP port"""
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Try to bind to the port
        sock.bind(('', port))
        print(f"✅ Successfully bound to UDP port {port}")
        
        # Get local IP addresses
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"📍 Hostname: {hostname}")
        print(f"📍 Primary IP: {local_ip}")
        
        # Try to get all network interfaces
        try:
            import subprocess
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
            lines = result.stdout.split('\n')
            ipv4_lines = [line.strip() for line in lines if 'IPv4 Address' in line]
            print(f"📍 All IPv4 addresses found:")
            for line in ipv4_lines:
                print(f"   {line}")
        except:
            pass
        
        print(f"\n🔍 Listening for UDP packets on port {port}...")
        print("Send a test packet from your Android app now!")
        print("Press Ctrl+C to stop\n")
        
        sock.settimeout(5.0)  # 5 second timeout
        
        packet_count = 0
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                packet_count += 1
                message = data.decode('utf-8', errors='ignore')
                print(f"📦 Packet #{packet_count} from {addr[0]}:{addr[1]} - Message: '{message}'")
                
                if message == "STEP":
                    print("✅ Received valid STEP message!")
                else:
                    print("⚠️  Unknown message format")
                    
            except socket.timeout:
                print("⏰ Waiting for packets... (5s timeout)")
                continue
                
    except socket.error as e:
        print(f"❌ Socket error: {e}")
        if "Address already in use" in str(e):
            print("💡 Port 9000 is already in use. Close GameWalking app and try again.")
        elif "Permission denied" in str(e):
            print("💡 Permission denied. Try running as Administrator.")
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped. Received {packet_count} packets total.")
    finally:
        try:
            sock.close()
        except:
            pass

def test_firewall():
    """Check Windows Firewall status"""
    try:
        import subprocess
        print("🔥 Checking Windows Firewall rules for GameWalking...")
        
        # Check for existing firewall rules
        result = subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=GameWalking UDP'
        ], capture_output=True, text=True, shell=True)
        
        if "No rules match" in result.stdout:
            print("❌ No firewall rule found for 'GameWalking UDP'")
            print("💡 Run firewall_setup.bat as Administrator to add firewall rules")
        else:
            print("✅ Firewall rule 'GameWalking UDP' exists")
            
    except Exception as e:
        print(f"⚠️  Could not check firewall: {e}")

def main():
    print("🎮 GameWalking Network Connectivity Test")
    print("=" * 50)
    
    # Test firewall
    test_firewall()
    print()
    
    # Test UDP listener
    port = 9000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number, using default 9000")
    
    print(f"🌐 Your PC should be reachable at these addresses:")
    print(f"   📱 Enter in Android app: 192.168.86.35:9000")
    print(f"   📱 Alternative address: 172.17.144.1:9000")
    print()
    
    test_udp_listener(port)

if __name__ == "__main__":
    main()