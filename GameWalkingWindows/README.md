# GameWalking Windows Desktop Application

A Windows desktop application that receives UDP signals from the GameWalking Android app and converts them into keyboard inputs for games like Death Stranding.

## Features

- **Real-time UDP Communication**: Receives "STEP" messages from Android app
- **Keyboard Input Simulation**: Converts steps to keyboard presses (default: 'W' key)
- **GUI Interface**: Easy-to-use graphical interface with real-time status
- **System Tray Support**: Minimize to system tray for background operation
- **Configurable Settings**: Customize port, key bindings, and timing
- **Console Mode**: Optional command-line operation without GUI
- **Activity Logging**: Real-time log of received steps and system events

## Quick Start

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Windows Firewall
**Option A: Run as Administrator**
```batch
firewall_setup.bat
```

**Option B: Manual Configuration**
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Click "Change Settings" → "Allow another app..."
4. Browse and select GameWalking.exe (or python.exe if running from source)
5. Check both "Private" and "Public" networks
6. Click OK

### 3. Run the Application
```bash
# GUI Mode (default)
python main.py

# Console Mode
python main.py --no-gui

# Debug Mode
python main.py --debug

# Custom Port
python main.py --port 8000
```

### 4. Connect Android App
1. Find your PC's IP address: `ipconfig` in Command Prompt
2. Look for "IPv4 Address" under your WiFi adapter
3. Enter this IP in your GameWalking Android app
4. Use port 9000 (or your custom port)

## Usage Instructions

### GUI Mode
1. **Start the Application**: Run `python main.py`
2. **Start UDP Listener**: Click "Start Listener" button
3. **Activate Key Sender**: Click "Activate Key Sender" button
4. **Configure Settings**: Adjust port, forward key, and timing as needed
5. **Connect Android App**: Use your PC's IP address and port 9000
6. **Start Gaming**: Open your game and start walking with your phone!

### Settings Configuration
- **Port**: UDP port to listen on (default: 9000)
- **Forward Key**: Key to press for forward movement (default: 'w')
- **Key Hold Duration**: How long to hold the key per step (default: 0.05 seconds)

### System Tray
- Check "Minimize to system tray" to run in background
- Right-click tray icon to show/hide window or quit

## Building Executable

### Create Standalone EXE
```bash
python build_exe.py
```

The executable will be created in `dist/GameWalking.exe`

### Distribution Package
After building, create a distribution folder with:
- `GameWalking.exe`
- `firewall_setup.bat`
- `README.txt` (simplified instructions)
- `INSTALL.txt` (installation guide)

## Game Compatibility

### Tested Games
- **Death Stranding**: Works perfectly with default 'W' key
- **Any WASD Game**: Configure forward key as needed

### Game Setup Tips
1. **Focus Window**: Make sure game window is active/focused
2. **Key Bindings**: Verify game uses your configured key for forward movement
3. **Timing**: Adjust key hold duration for different games
4. **Performance**: Close unnecessary applications for best performance

## Troubleshooting

### Common Issues

**1. "Failed to start UDP listener"**
- Check if port is already in use: `netstat -an | findstr :9000`
- Try a different port in settings
- Run as Administrator if needed

**2. "Android app can't connect"**
- Verify both devices are on same WiFi network
- Check Windows Firewall allows the application
- Confirm IP address is correct: `ipconfig`
- Try disabling Windows Firewall temporarily for testing

**3. "Game not responding to key presses"**
- Ensure game window is active and focused
- Check if game uses your configured key for movement
- Try running as Administrator
- Verify key hold duration isn't too short

**4. "PyAutoGUI FailSafe triggered"**
- Don't move mouse to screen corners while app is active
- This is a safety feature to prevent runaway scripts

### Debug Mode
Enable debug mode to see detailed logs:
```bash
python main.py --debug
```

### Network Testing
Test UDP connectivity:
```bash
# Check if port is listening
netstat -an | findstr :9000

# Test with netcat (if available)
nc -u localhost 9000
```

## Performance Optimization

### For Best Performance
1. **Stable Network**: Use wired connection if WiFi is unstable
2. **Close Apps**: Close unnecessary applications
3. **Game Settings**: Lower game graphics if experiencing lag
4. **Timing**: Adjust key hold duration for your system

### System Requirements
- **OS**: Windows 10/11
- **Python**: 3.8 or higher
- **RAM**: 100MB minimum
- **Network**: WiFi or Ethernet connection
- **Permissions**: Administrator rights for firewall configuration

## Advanced Configuration

### Config File
Settings are automatically saved to `gamewalking_config.ini`:
```ini
[NETWORK]
port = 9000
buffer_size = 1024

[CONTROLS]
forward_key = w
step_duration = 0.1
key_hold_duration = 0.05

[GENERAL]
minimize_to_tray = true
auto_start = false
debug_mode = false
```

### Command Line Options
```bash
python main.py --help
```

## Security Notes

- The application only listens for UDP packets on the configured port
- No data is sent from your PC to external servers
- All communication is local network only
- Firewall rules are only for incoming connections on the specified port

## Support

### Getting Help
1. Check this README for common solutions
2. Enable debug mode to see detailed logs
3. Verify network connectivity between devices
4. Test with simple games first (like Notepad with 'W' key)

### Reporting Issues
When reporting issues, please include:
- Windows version
- Python version
- Error messages from debug mode
- Network configuration (WiFi/Ethernet)
- Game being used

## License

This project is for educational and personal use. Please respect game terms of service when using automation tools.