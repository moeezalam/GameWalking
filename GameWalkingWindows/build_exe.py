"""
Build script to create executable using PyInstaller
"""

import PyInstaller.__main__
import os
import sys

def build_executable():
    """Build executable using PyInstaller"""
    
    # PyInstaller arguments
    args = [
        'main.py',
        '--name=GameWalking',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',  # Optional: add if you have an icon
        '--add-data=gamewalking_config.ini;.',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--collect-submodules=pystray',
        '--noconsole',
    ]
    
    # Remove icon argument if file doesn't exist
    if not os.path.exists('icon.ico'):
        args = [arg for arg in args if not arg.startswith('--icon')]
    
    print("Building executable...")
    print("Arguments:", args)
    
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete!")
    print("Executable location: dist/GameWalking.exe")
    print("\nNote: Make sure to configure Windows Firewall to allow this application")

if __name__ == "__main__":
    build_executable()