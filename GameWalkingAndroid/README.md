# GameWalking Android App

A real-time motion-to-game control Android application that detects steps using your phone's sensors and sends UDP signals to a desktop application for game control.

## Features

- **Step Detection**: Uses built-in step detector/counter sensors with accelerometer fallback
- **Real-time UDP Communication**: Sends "STEP" messages to desktop application
- **Foreground Service**: Continues detecting steps even when app is in background
- **Permission Management**: Handles all required permissions automatically
- **Battery Optimized**: Uses wake locks efficiently for continuous operation

## Setup Instructions

### 1. Build and Install
1. Open the project in Android Studio
2. Connect your Google Pixel 7a via USB
3. Enable Developer Options and USB Debugging on your phone
4. Click "Run" in Android Studio or build APK: Build → Build Bundle(s) / APK(s) → Build APK(s)

### 2. Configure Network
1. Ensure your phone and PC are on the same WiFi network
2. Find your PC's IP address:
   - Windows: Open Command Prompt and run `ipconfig`
   - Look for "IPv4 Address" under your WiFi adapter
3. Update the default IP in the app or enter it manually

### 3. Permissions
The app will automatically request these permissions:
- **Activity Recognition**: For step detection (Android 10+)
- **Post Notifications**: For foreground service notification (Android 13+)
- **Internet & Network State**: For UDP communication
- **Wake Lock**: To keep CPU active for step detection

### 4. Usage
1. Launch the GameWalking app
2. Enter your PC's IP address (default: 192.168.1.100)
3. Enter port number (default: 9000)
4. Tap "Start Step Detection"
5. Put phone in your pocket and start walking
6. The app will send "STEP" messages to your desktop application

## Technical Details

### Sensor Priority
1. **Step Detector** (preferred): Real-time step detection
2. **Step Counter**: Backup method using step count changes
3. **Accelerometer**: Fallback for devices without step sensors

### Network Protocol
- **Protocol**: UDP
- **Message**: "STEP" (4 bytes)
- **Default Port**: 9000
- **Target**: Desktop application on same network

### Service Architecture
- **Foreground Service**: Ensures continuous operation
- **Wake Lock**: Prevents CPU sleep during detection
- **Notification**: Shows service status in notification bar

## Troubleshooting

### Common Issues

1. **No Steps Detected**
   - Check if device has step sensors in Settings → Apps → GameWalking → Permissions
   - Try walking more vigorously for accelerometer fallback
   - Ensure phone is held vertically in pocket

2. **Network Connection Issues**
   - Verify both devices are on same WiFi network
   - Check Windows Firewall allows UDP traffic on port 9000
   - Try different IP address or port

3. **App Stops Working**
   - Add app to battery optimization whitelist
   - Check notification permission is granted
   - Restart the service from the app

4. **Permissions Denied**
   - Go to Settings → Apps → GameWalking → Permissions
   - Manually enable all required permissions
   - Restart the app

### Debug Tips
- Check notification bar for "GameWalking Active" notification
- Monitor battery usage in Settings → Battery
- Use network monitoring tools to verify UDP packets

## Compatibility

- **Minimum Android Version**: Android 5.0 (API 21)
- **Target Android Version**: Android 14 (API 34)
- **Tested Device**: Google Pixel 7a
- **Required Sensors**: Accelerometer (minimum), Step Detector/Counter (preferred)

## Next Steps

After installing this Android app:
1. Set up the desktop receiver application (see desktop guide)
2. Configure your game to respond to keyboard inputs
3. Test the complete system by walking and observing game character movement

The app is now ready to detect your steps and send them to your desktop for game control!