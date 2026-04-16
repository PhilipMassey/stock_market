import subprocess
import sys

def ensure_authenticated():
    # Check if we are already logged in
    check = subprocess.run(["nlm", "login", "--check"], capture_output=True, text=True)
    
    if "Logged in" in check.stdout:
        print("Authenticated successfully.")
    else:
        print("Authentication required. Opening browser...")
        # This will open the browser and wait for the user to finish
        subprocess.run(["nlm", "login"], check=True)

if __name__ == "__main__":
    ensure_authenticated()