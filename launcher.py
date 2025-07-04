#!/usr/bin/env python3
import os
import sys
import subprocess
from scripts.interface import main_menu

def verify_ubuntu_version():
    """Check if running on Ubuntu 22.x (major version match only)"""
    try:
        version = subprocess.check_output(["lsb_release", "-rs"], text=True).strip().split('.')[0]
        version_full = subprocess.check_output(["lsb_release", "-rs"], text=True).strip()
        if version != "22":
            print("Error: This program requires Ubuntu 22.x")
            print(f"Detected version: {version}.x")
            return False
        elif version_full < "22.04":
            print("Warning: Optimized for Ubuntu 22.04+, minor issues may occur")
        elif version_full == "22.04.3":
            print("Note: Using HWE kernel (Linux 6.2)")  # Add HWE note
        return True
    except Exception as e:
        print(f"Version check failed: {e}")
        return False

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This program must be run with sudo. Restarting...")
        subprocess.call(['sudo', sys.executable] + sys.argv)
        sys.exit(0)
    if verify_ubuntu_version():
        main_menu()
    else:
        print("Exiting due to version incompatibility.")
        exit(1)