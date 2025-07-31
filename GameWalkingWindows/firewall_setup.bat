@echo off
echo Adding GameWalking to Windows Firewall...
netsh advfirewall firewall add rule name="GameWalking UDP" dir=in action=allow protocol=UDP localport=9000
netsh advfirewall firewall add rule name="GameWalking TCP" dir=in action=allow protocol=TCP localport=9000
echo Firewall rules added successfully!
pause