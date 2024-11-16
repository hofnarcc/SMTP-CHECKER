import subprocess
import sys
import platform
import tkinter as tk
import os
import threading

def check_python_version():
    """
    Check and prompt for Python 3.11.8 installation.
    """
    required_version = "3.11.8"
    current_version = platform.python_version()
    if current_version != required_version:
        print(f"=============================================================================|")
        print(f"Python version {required_version} is required. You have {current_version} installed.")
        print("Please download Python from:")
        print("https://www.python.org/downloads/release/python-3118/")
        sys.exit(1)

def install_or_upgrade_package(package_name):
    """
    Attempt to install or upgrade a package using pip.
    """
    try:
        subprocess.check_call(["pip", "install", package_name])
        print(f"Package {package_name} installed successfully.")
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call(["pip", "install", "--upgrade", package_name])
            print(f"Package {package_name} upgraded successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install/upgrade package {package_name}.")

def check_package_installed_upgraded(package_name):
    """
    Check if a package is installed and up-to-date, and install/upgrade if needed.
    """
    try:
        subprocess.check_call(["pip", "show", package_name])
        print(f"Package {package_name} is already installed and up-to-date.")
    except subprocess.CalledProcessError:
        install_or_upgrade_package(package_name)

def create_and_run_button(root, text, script_path):
    """
    Create a button, pack it into the root window, and define its command action.
    """
    button = tk.Button(root, text=text, command=lambda: execute_script(script_path))
    button.pack(pady=10)

def execute_script(script_path):
    """
    Execute the Python script in a new thread.
    """
    thread = threading.Thread(target=os.system, args=(f"python {script_path}",))
    thread.start()

# Check and install required Python version
check_python_version()

# List of required packages
required_packages = ["tk"]

# Check and install/upgrade required packages
for package in required_packages:
    check_package_installed_upgraded(package)

# Create the main window
root = tk.Tk()
root.title("                 Gmail - Office365 - Mailgun - SendGrid - SMTP Checker Config [GUI]")
root.geometry("600x100")  # Adjust geometry for better visibility

# Dictionary mapping button text to script paths
button_scripts = {
    "1. =>   COMBO 2 SMTP [TRANSFORMER]": "01_transform_combo_2_smtp.py",
    "2. =>   EMAIL SENDER [CHECKER]": "02_email_sender.py",
}

# Create buttons and associate them with their scripts
for text, script_path in button_scripts.items():
    create_and_run_button(root, text, script_path)

# Start the GUI event loop
root.mainloop()
