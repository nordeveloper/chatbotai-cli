import os
import subprocess

# Path to requirements.txt file
requirements_file = 'requirements.txt'

# Path to the virtual environment
venv_path = 'venv'

# Check if the virtual environment exists
if not os.path.exists(venv_path):
    print("Virtual environment doesn't exist. Creating...")
    # Create the virtual environment
    subprocess.run(['python', '-m', 'venv', venv_path], check=True)

# Install requirements
subprocess.run(['pip', 'install', '-r', requirements_file], check=True)

print("Requirements installed successfully.")