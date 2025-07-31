# GameWalking Troubleshooting Guide

## 🔍 Common Issue: Windows App Shows "Listening" but Steps Received = 0

### 🎯 Quick Fix Steps

#### 1. Update Android App IP Address
The Android app needs to send TO your PC's IP address:
- **Open GameWalking Android app**
- **Change IP address to: `[YOUR_PC_IP]`** (find using `ipconfig`)
- **Keep port as: `9000`**
- **Tap "Start Step Detection"**

#### 2. Test Network Connectivity
Run this test on your PC:
```bash
cd GameWalkingWindows
python test_network.py
```

#### 3. Verify Firewall Configuration
Run as Administrator:
```batch
firewall_setup.bat
```

## 🔧 Detailed Diagnosis Steps

### Step 1: Find Your Network Configuration
**On PC (Command Prompt):**
```cmd
ipconfig
```
Look for: `IPv4 Address. . . . . . . . . . . : [YOUR_PC_IP]`

**On Android:**
Settings → WiFi → Connected Network → Advanced
Should show: `IP address: [YOUR_PHONE_IP]`

✅ **Both should start with same network prefix** (e.g., 192.168.1.x)

### Step 2: Test UDP Connectivity
**On PC:**
```bash
python test_network.py
```

**On Android:**
1. Enter IP: `[YOUR_PC_IP]`
2. Enter Port: `9000`
3. Tap "Start Step Detection"
4. Walk around with phone

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

## 🚨 Common Issues & Solutions

### Issue 1: "Port already in use"
**Solution:**
```cmd
netstat -an | findstr :9000
taskkill /f /im python.exe
```

### Issue 2: "No packets received"
**Causes & Solutions:**

1. **Wrong IP Address**
   - Android app sending to wrong IP
   - ✅ **Use your PC's actual IP from `ipconfig`**

2. **Firewall Blocking**
   - Run `firewall_setup.bat` as Administrator
   - Or temporarily disable Windows Firewall for testing

3. **Different Networks**
   - PC on Ethernet, Phone on WiFi
   - Ensure both on same network

### Issue 3: "Android app can't connect"
**Check Android app logs:**
1. Enable Developer Options
2. USB Debugging
3. View logs: `adb logcat | grep GameWalking`

## 🧪 Advanced Testing

### Manual UDP Test
**On PC (PowerShell):**
```powershell
$endpoint = New-Object System.Net.IPEndPoint([System.Net.IPAddress]::Any, 9000)
$udpClient = New-Object System.Net.Sockets.UdpClient(9000)
while ($true) {
    $receivedBytes = $udpClient.Receive([ref]$endpoint)
    $receivedData = [System.Text.Encoding]::ASCII.GetString($receivedBytes)
    Write-Host "Received: $receivedData from $($endpoint.Address):$($endpoint.Port)"
}
```

### Network Route Test
```cmd
ping [YOUR_PHONE_IP]
tracert [YOUR_PHONE_IP]
```

## 🎯 General Fix Process

1. **Find your PC's IP address:** `ipconfig`
2. **Update Android app** with correct PC IP
3. **Test connection:** `python test_network.py`
4. **Configure firewall:** Run `firewall_setup.bat` as Admin
5. **Test both apps** together

The most common cause is incorrect IP address configuration!