import os
import sys
import json
import tempfile
import subprocess
import shutil
import platform
import requests
import time
from pathlib import Path
from packaging import version
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class Updater:
    """
    Handles application updates from GitHub releases.
    """
    
    def __init__(self, github_repo, current_version, app_name="MPRSeparator"):
        """
        Initialize the updater with GitHub repository info and current version.
        
        Args:
            github_repo (str): GitHub repository in format 'username/repo'
            current_version (str): Current application version (e.g., '1.0.0')
            app_name (str): Application name used for temp directories
        """
        self.github_repo = github_repo
        self.current_version = version.parse(current_version)
        self.app_name = app_name
        self.github_api_url = f"https://api.github.com/repos/{github_repo}/releases/latest"
        self.update_in_progress = False
        
        # Determine if running from PyInstaller bundle
        self.is_frozen = getattr(sys, 'frozen', False)
        if self.is_frozen:
            self.app_dir = Path(os.path.dirname(sys.executable))
        else:
            self.app_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
            
        # Store version info in a file
        self.version_file = self.app_dir / "version.json"
        if not os.path.exists(self.version_file):
            self._write_version_info()
    
    def check_for_updates(self):
        """
        Check if updates are available on GitHub.
        
        Returns:
            tuple: (bool for update available, version string, release notes)
        """
        try:
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            
            latest_release = response.json()
            latest_version_str = latest_release['tag_name'].lstrip('v')
            latest_version = version.parse(latest_version_str)
            
            update_available = latest_version > self.current_version
            release_notes = latest_release.get('body', 'No release notes available')
            
            return update_available, latest_version_str, release_notes, latest_release
        
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            print(f"Error checking for updates: {str(e)}")
            return False, self.current_version, "Error checking for updates", None
    
    def download_update(self, release_info, progress_callback=None):
        """
        Download the update package from GitHub.
        
        Args:
            release_info: Release information from GitHub API
            progress_callback: Function to call with download progress (0-100)
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Find the right asset to download based on platform
            system = platform.system().lower()
            if system == 'windows':
                asset_filter = '.exe'
            elif system == 'darwin':
                asset_filter = '.dmg'
            elif system == 'linux':
                asset_filter = '.AppImage'
            else:
                return None
                
            # Find matching asset
            asset = None
            for a in release_info.get('assets', []):
                if asset_filter in a.get('name', '').lower():
                    asset = a
                    break
            
            if not asset:
                print("No suitable download asset found")
                return None
            
            download_url = asset['browser_download_url']
            file_name = asset['name']
            
            # Create temp dir for download
            temp_dir = Path(tempfile.gettempdir()) / f"{self.app_name}_update"
            os.makedirs(temp_dir, exist_ok=True)
            
            download_path = temp_dir / file_name
            
            # Download with progress reporting
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 KB
            downloaded = 0
            
            with open(download_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    f.write(data)
                    downloaded += len(data)
                    progress = min(100, int(downloaded / total_size * 100)) if total_size > 0 else 0
                    
                    if progress_callback:
                        progress_callback(progress)
            
            return download_path
            
        except Exception as e:
            print(f"Error downloading update: {str(e)}")
            return None
    
    def install_update(self, update_file, version_str):
        """
        Install the downloaded update.
        
        Args:
            update_file (Path): Path to the downloaded update file
            version_str (str): Version string of the update
            
        Returns:
            bool: Success or failure of update installation
        """
        try:
            if not update_file or not update_file.exists():
                return False
                
            # Mark update as in progress
            self.update_in_progress = True
            self._write_version_info(version_str, True)
            
            # For Windows, start the installer and exit the current process
            if platform.system().lower() == 'windows':
                # Start a detached process that will:
                # 1. Wait for current process to exit
                # 2. Run the installer
                update_script = tempfile.NamedTemporaryFile(
                    suffix='.bat', 
                    delete=False
                )
                current_pid = os.getpid()
                
                with open(update_script.name, 'w') as f:
                    f.write(f'''@echo off
timeout /t 2 /nobreak > nul
taskkill /F /PID {current_pid} > nul 2>&1
timeout /t 1 /nobreak > nul
start "" "{update_file}"
del "%~f0"
''')
                
                # Execute the update script
                subprocess.Popen(
                    update_script.name,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS
                )
                
                # Exit the application to allow the update to proceed
                time.sleep(1)  # Give the script time to start
                return True
                
            # For other platforms, implement appropriate installation methods
            # (This is a basic implementation for Windows)
            return False
            
        except Exception as e:
            print(f"Error installing update: {str(e)}")
            self.update_in_progress = False
            self._write_version_info()
            return False
    
    def check_for_completed_update(self):
        """
        Check if we just completed an update.
        
        Returns:
            bool: True if update was just completed
        """
        if not self.version_file.exists():
            return False
            
        try:
            with open(self.version_file, 'r') as f:
                data = json.load(f)
                
            if data.get('update_in_progress', False):
                # Update just completed
                self._write_version_info()  # Reset the flag
                return True
                
        except (json.JSONDecodeError, KeyError):
            pass
            
        return False
    
    def _write_version_info(self, version_str=None, update_in_progress=False):
        """Write version info to file"""
        version_info = {
            'version': version_str or str(self.current_version),
            'update_in_progress': update_in_progress
        }
        
        with open(self.version_file, 'w') as f:
            json.dump(version_info, f)

# Azure Key Vault integration
# Replace with your Key Vault URL
key_vault_url = "https://mprkv2024az.vault.azure.net/"

# Create a SecretClient using DefaultAzureCredential
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)

# Retrieve secrets
try:
    # Try to get connection string directly from the environment variable first
    conn_str = os.environ.get("DB_CONN_STR")
    if not conn_str:
        # Try to get individual parameters from Key Vault with correct case-sensitive names
        # or fall back to environment variables
        sql_server = os.environ.get("DB_SERVER")
        sql_database = os.environ.get("DB_NAME")
        sql_username = os.environ.get("DB_USERNAME")
        sql_password = os.environ.get("DB_PASSWORD")
        
        # If we have all the necessary parameters, construct a connection string
        if sql_server and sql_database and sql_username and sql_password:
            conn_str = (f"Driver={{ODBC Driver 18 for SQL Server}};"
                        f"Server={sql_server};Database={sql_database};"
                        f"Uid={sql_username};Pwd={sql_password};"
                        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
except Exception as e:
    print(f"Error accessing database configuration: {str(e)}")
    conn_str = None