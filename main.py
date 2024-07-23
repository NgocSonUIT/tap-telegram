import os
import time
import subprocess
from datetime import datetime

ignore_files = 'main.py,memefi.py'

def run_python_files(directory):
    # List all files in the directory
    files = os.listdir(directory)
    
    # Filter out only Python files
    python_files = [f for f in files if f.endswith('.py') and f not in ignore_files.split(',')]

    print(python_files)
    
    # Run each Python file
    for file_name in python_files:
        file_path = os.path.join(directory, file_name)
        print(f"Running {file_name}...")

        os.system(f"python3 {file_name}")

        print(f"Waiting 10s to run next file")
        time.sleep(10)
       
    #     # print(f"Output of {file_name}:\n{result.stdout}")
    #     print("\n" + "="*40 + "\n")

def main():
    # Specify the directory containing the Python files
    directory = '/Users/son/Downloads/Memefi-proxy-dc'
    
    while True:
        print("Running Python files...\n")
        print(f"Time running {datetime.now()}")
        run_python_files(directory)
        print("Done. Waiting for 5 minutes...\n")
        print(f"Time end {datetime.now()}")
        time.sleep(5 * 60)

if __name__ == "__main__":
    main()
