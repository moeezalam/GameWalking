@echo off
echo Creating GameWalking Distribution Package...

REM Create distribution folder
mkdir "GameWalking-Portable" 2>nul

REM Copy executable
copy "dist\GameWalking.exe" "GameWalking-Portable\"

REM Copy firewall setup
copy "firewall_setup.bat" "GameWalking-Portable\"

REM Create simplified README
echo GameWalking - Portable Edition > "GameWalking-Portable\README.txt"
echo ================================ >> "GameWalking-Portable\README.txt"
echo. >> "GameWalking-Portable\README.txt"
echo QUICK START: >> "GameWalking-Portable\README.txt"
echo 1. Run firewall_setup.bat as Administrator >> "GameWalking-Portable\README.txt"
echo 2. Double-click GameWalking.exe >> "GameWalking-Portable\README.txt"
echo 3. Click "Start Listener" then "Activate Key Sender" >> "GameWalking-Portable\README.txt"
echo 4. Connect Android app with your PC's IP address >> "GameWalking-Portable\README.txt"
echo 5. Start walking with your phone! >> "GameWalking-Portable\README.txt"
echo. >> "GameWalking-Portable\README.txt"
echo NETWORK SETUP: >> "GameWalking-Portable\README.txt"
echo - Find your PC's IP: Open Command Prompt, type "ipconfig" >> "GameWalking-Portable\README.txt"
echo - Look for "IPv4 Address" under WiFi adapter >> "GameWalking-Portable\README.txt"
echo - Enter this IP in your Android app with port 9000 >> "GameWalking-Portable\README.txt"
echo. >> "GameWalking-Portable\README.txt"
echo TROUBLESHOOTING: >> "GameWalking-Portable\README.txt"
echo - Run firewall_setup.bat as Administrator if connection fails >> "GameWalking-Portable\README.txt"
echo - Make sure both PC and phone are on same WiFi network >> "GameWalking-Portable\README.txt"
echo - Try different IP address if multiple found in ipconfig >> "GameWalking-Portable\README.txt"

echo.
echo ✅ Distribution package created in "GameWalking-Portable" folder
echo 📁 Contents:
echo    - GameWalking.exe (standalone executable)
echo    - firewall_setup.bat (Windows Firewall configuration)
echo    - README.txt (quick setup instructions)
echo.
echo 🚀 Ready to copy to any Windows PC!
pause