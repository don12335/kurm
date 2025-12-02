<img width="1874" height="974" alt="image" src="https://github.com/user-attachments/assets/71c9f2dc-d5d7-4688-b538-9d3cc730f6de" />
KURMControlToolkit is a multifunctional Python-based tool for automated control of Android devices via ADB and scrcpy.

This tool is designed for Windows only.

Key Features

Seamless Device Control

Full control of Android devices over USB and TCP/IP (Wireless).
Automatic Device Detection: Real-time monitoring of connection status with instant feedback.
Live Telemetry: Displays device health stats including Battery level, Android OS version, IP address, and RAM usage.
High-Performance Mirroring
Integrated scrcpy support for low-latency, high-resolution screen mirroring and recording directly from the dashboard.

GUI File System Manager

Built-in File Explorer to browse device directories (/sdcard/).
Supports intuitive Push (Upload) and Pull (Download) operations without typing complex commands.
Automation & Stress Testing (Chaos Module)
Macro Bot: Automated XY coordinate tapping for repetitive tasks.
Chaos Engine: Includes "App Glitcher", "Ghost Touch", and "Clipboard Spam" modules for UI stress testing and stability verification.
Security Simulation: Features a PIN Brute Force simulator for educational security testing.

Modular & Lightweight Architecture

Tabbed Interface: Organized into Dashboard, File Explorer, Macro Bot, and Chaos Ops for efficient workflow.
Intuitive Console: Integrated terminal-style logging window provides real-time execution feedback.
Stealth UI: Features a hacker-style "Dark Mode" aesthetic with red accents (#C0392B) and ASCII art integration.

Requirements (Windows only)

1. Install ADB (Android Debug Bridge)
Download Android Platform Tools:
https://developer.android.com/tools/releases/platform-tools
Extract the archive and add the folder path to your System PATH
(e.g., C:\platform-tools)

2. Install scrcpy (for screen mirroring)
Download the latest version of scrcpy:
https://github.com/Genymobile/scrcpy/releases
Extract the folder and add it to your System PATH
Make sure you can run adb and scrcpy from the terminal (CMD/PowerShell).
