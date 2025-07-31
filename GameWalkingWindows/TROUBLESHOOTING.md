# GameWalking Troubleshooting Guide

## 🔍 Your Current Issue: Windows App Shows "Listening" but Steps Received = 0

Based on your network configuration:
- **Your PC IP**: 192.168.86.35 (main network)
- **Your Phone IP**: 192.168.86.246 (same network ✅)
- **Alternative PC IP**: 172.17.144.1 (virtual adapter)

## 🎯 Quick Fix Steps

### 1. Update Android App IP Address
The Android app needs to send TO your PC's IP address:
- **Open GameWalking Android app**
- **Change IP address to: `192.168.86.35`**
- **Keep port as: `9000`**
- **Tap "Start Step Detection"**

### 2. Test Network Connectivity
Run this test on your PC:
```bash
cd GameWalkingWindows
python test_network.py
```

This will:
- Check if port 9000 is available
- Show all your PC's IP addresses
- Listen for UDP packets from your phone
- Verify firewall configuration

### 3. Verify Firewall Configuration
Run as Administrator:
```batch
firewall_setup.bat
```

Or manually check:
```cmd
netsh advfirewall firewall show rule name="GameWalking UDP"
```

## 🔧 Detailed Diagnosis Steps

### Step 1: Verify Network Connection
Both devices must be on the same WiFi network:

**On PC (Command Prompt):**
```cmd
ipconfig
```
Look for: `IPv4 Address. . . . . . . . . . . : 192.168.86.35`

**On Android:**
Settings → WiFi → Connected Network → Advanced
Should show: `IP address: 192.168.86.246`

✅ **Both start with 192.168.86.x** - Same network confirmed!

### Step 2: Test UDP Connectivity
**On PC:**
```bash
python test_network.py
```

**On Android:**
1. Enter IP: `192.168.86.35`
2. Enter Port: `9000`
3. Tap "Start Step Detection"
4. Walk around with phone

You should see packets appear in the PC test window.

### Step 3: Check Windows Firewall
**Automatic (Run as Admin):**
```batch
firewall_setup.bat
```

**Manual Check:**
1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Look for "GameWalking" or "Python"
4. Ensure both Private and Public are checked

### Step 4: Enable Debug Mode
**In Windows app:**
1. Stop the listener
2. Change settings or edit `gamewalking_config.ini`:
   ```ini
   [GENERAL]
   debug_mode = true
   ```
3. Restart the app
4. Check console output for detailed logs

## 🚨 Common Issues & Solutions

### Issue 1: "Port already in use"
**Symptoms:** Can't start UDP listener
**Solution:**
```cmd
netstat -an | findstr :9000
taskkill /f /im python.exe
```

### Issue 2: "No packets received"
**Symptoms:** Windows shows "Listening" but Steps = 0
**Causes & Solutions:**

1. **Wrong IP Address**
   - Android app sending to wrong IP
   - ✅ **Use: 192.168.86.35**

2. **Firewall Blocking**
   - Run `firewall_setup.bat` as Administrator
   - Or temporarily disable Windows Firewall for testing

3. **Different Networks**
   - PC on Ethernet, Phone on WiFi
   - ✅ **Both on same WiFi confirmed**

4. **Router Blocking**
   - Some routers block device-to-device communication
   - Try connecting both to mobile hotspot for testing

### Issue 3: "Android app can't connect"
**Check Android app logs:**
1. Enable Developer Options
2. USB Debugging
3. View logs: `adb logcat | grep GameWalking`

### Issue 4: "Intermittent connection"
**Symptoms:** Sometimes works, sometimes doesn't
**Solutions:**
- Move closer to WiFi router
- Restart WiFi on both devices
- Check for WiFi interference

## 🧪 Advanced Testing

### Test 1: Manual UDP Test
**On PC (PowerShell):**
```powershell
# Simple UDP listener
$endpoint = New-Object System.Net.IPEndPoint([System.Net.IPAddress]::Any, 9000)
$udpClient = New-Object System.Net.Sockets.UdpClient(9000)
while ($true) {
    $receivedBytes = $udpClient.Receive([ref]$endpoint)
    $receivedData = [System.Text.Encoding]::ASCII.GetString($receivedBytes)
    Write-Host "Received: $receivedData from $($endpoint.Address):$($endpoint.Port)"
}
```

### Test 2: Send Test Packet
**From another PC or phone:**
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"TEST", ("192.168.86.35", 9000))
```

### Test 3: Network Route Test
```cmd
ping 192.168.86.246
tracert 192.168.86.246
```

## 📱 Android App Debugging

### Enable Logging
Add to `StepDetectionService.kt`:
```kotlin
private fun onStepDetected() {
    Log.d("GameWalking", "Step detected, sending UDP packet")
    serviceScope.launch {
        udpSender.sendStep()
    }
}
```

### Check Permissions
Ensure these are granted:
- Internet
- Network State
- Activity Recognition (Android 10+)
- Post Notifications (Android 13+)

## 🎯 Your Specific Fix

Based on your configuration, the most likely issue is the IP address. Here's what to do:

1. **Update Android App:**
   - Change IP from `172.17.144.1` to `192.168.86.35`
   - Keep port as `9000`

2. **Test Connection:**
   ```bash
   cd GameWalkingWindows
   python test_network.py
   ```

3. **Start Both Apps:**
   - Windows: Click "Start Listener" → "Activate Key Sender"
   - Android: Enter `192.168.86.35:9000` → "Start Step Detection"

4. **Walk Test:**
   - Put phone in pocket
   - Walk around room
   - Check Windows app for "Steps Received" counter

## 📞 Still Not Working?

If you're still having issues:

1. **Run network test:** `python test_network.py`
2. **Enable debug mode** in both apps
3. **Check firewall:** Run `firewall_setup.bat` as Admin
4. **Try alternative IP:** Use `172.17.144.1` if main IP doesn't work
5. **Test with mobile hotspot:** Connect both devices to phone hotspot

The most common cause is incorrect IP address configuration. Make sure your Android app is sending to your PC's correct IP address on the same network!