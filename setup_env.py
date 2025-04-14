#!/usr/bin/env python
"""
Setup environment script for MPR Separator

This script helps to configure the .env file for the MPR Separator application.
It will prompt for Azure Key Vault and SQL Server settings and test the connection.
"""

import os
import sys
import getpass
from pathlib import Path
from dotenv import load_dotenv, set_key

try:
    from AzureKeyVault import get_secret, SecretRetrievalError
except ImportError:
    print("Error: AzureKeyVault.py must be in the current directory or Python path.")
    sys.exit(1)

def create_env_file():
    """Create or update the .env file with user input"""
    env_file = Path('.env')
    
    # If .env file exists, load it
    if env_file.exists():
        load_dotenv(env_file)
        print("Existing .env file found. Update values or press Enter to keep current values.")
    else:
        print("Creating new .env file...")
    
    # Azure Key Vault Configuration
    print("\n=== Azure Key Vault Configuration ===")
    
    key_vault_url = input(f"Key Vault URL [current: {os.getenv('KEY_VAULT_URL', '')}]: ")
    if key_vault_url:
        set_key(env_file, 'KEY_VAULT_URL', key_vault_url)
    elif not os.getenv('KEY_VAULT_URL'):
        key_vault_url = input("Key Vault URL is required. Please enter a value: ")
        set_key(env_file, 'KEY_VAULT_URL', key_vault_url)
    else:
        key_vault_url = os.getenv('KEY_VAULT_URL')
    
    username_secret = input(f"Username Secret Name [current: {os.getenv('DB_USERNAME_SECRET', 'mpr-separator-db-username')}]: ")
    if username_secret:
        set_key(env_file, 'DB_USERNAME_SECRET', username_secret)
    else:
        username_secret = os.getenv('DB_USERNAME_SECRET', 'mpr-separator-db-username')
        set_key(env_file, 'DB_USERNAME_SECRET', username_secret)
    
    password_secret = input(f"Password Secret Name [current: {os.getenv('DB_PASSWORD_SECRET', 'mpr-separator-db-password')}]: ")
    if password_secret:
        set_key(env_file, 'DB_PASSWORD_SECRET', password_secret)
    else:
        password_secret = os.getenv('DB_PASSWORD_SECRET', 'mpr-separator-db-password')
        set_key(env_file, 'DB_PASSWORD_SECRET', password_secret)
    
    # Database Configuration
    print("\n=== Database Configuration ===")
    
    db_server = input(f"SQL Server [current: {os.getenv('DB_SERVER', '')}]: ")
    if db_server:
        set_key(env_file, 'DB_SERVER', db_server)
    elif not os.getenv('DB_SERVER'):
        db_server = input("SQL Server is required. Please enter a value: ")
        set_key(env_file, 'DB_SERVER', db_server)
    else:
        db_server = os.getenv('DB_SERVER')
    
    db_name = input(f"Database Name [current: {os.getenv('DB_NAME', '')}]: ")
    if db_name:
        set_key(env_file, 'DB_NAME', db_name)
    elif not os.getenv('DB_NAME'):
        db_name = input("Database Name is required. Please enter a value: ")
        set_key(env_file, 'DB_NAME', db_name)
    else:
        db_name = os.getenv('DB_NAME')
    
    db_table = input(f"Table Name [current: {os.getenv('DB_TABLE', 'SeparatorRecords')}]: ")
    if db_table:
        set_key(env_file, 'DB_TABLE', db_table)
    else:
        db_table = os.getenv('DB_TABLE', 'SeparatorRecords')
        set_key(env_file, 'DB_TABLE', db_table)
    
    # Application Settings
    print("\n=== Application Settings ===")
    
    debug_mode = input(f"Debug Mode (True/False) [current: {os.getenv('DEBUG', 'False')}]: ")
    if debug_mode:
        set_key(env_file, 'DEBUG', debug_mode)
    else:
        debug_mode = os.getenv('DEBUG', 'False')
        set_key(env_file, 'DEBUG', debug_mode)
    
    return {
        'key_vault_url': key_vault_url,
        'username_secret': username_secret,
        'password_secret': password_secret,
        'db_server': db_server,
        'db_name': db_name,
        'db_table': db_table
    }

def test_azure_keyvault(config):
    """Test the Azure Key Vault connection"""
    print("\nTesting Azure Key Vault connection...")
    
    try:
        print(f"Retrieving username secret '{config['username_secret']}'...")
        username = get_secret(config['username_secret'], config['key_vault_url'])
        print("✓ Username secret retrieved successfully")
        
        print(f"Retrieving password secret '{config['password_secret']}'...")
        password = get_secret(config['password_secret'], config['key_vault_url'])
        print("✓ Password secret retrieved successfully")
        
        return True
    
    except SecretRetrievalError as e:
        print(f"✗ Error retrieving secrets: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_database_connection(config):
    """Test the database connection using the retrieved credentials"""
    print("\nTesting database connection...")
    
    try:
        import pyodbc
        
        # Get credentials from Key Vault
        username = get_secret(config['username_secret'], config['key_vault_url'])
        password = get_secret(config['password_secret'], config['key_vault_url'])
        
        # Create connection string
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['db_server']};"
            f"DATABASE={config['db_name']};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        
        # Try to connect
        print("Connecting to database...")
        connection = pyodbc.connect(conn_str)
        cursor = connection.cursor()
        
        # Test the table
        print(f"Testing access to {config['db_table']} table...")
        cursor.execute(f"SELECT TOP 1 * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='{config['db_table']}'")
        
        if cursor.fetchone():
            print(f"✓ Table '{config['db_table']}' exists")
        else:
            print(f"✗ Table '{config['db_table']}' does not exist")
            print(f"You may need to create the table as described in the README.md file")
        
        cursor.close()
        connection.close()
        
        print("✓ Database connection successful")
        return True
    
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        return False

def main():
    """Main function"""
    print("=============================================")
    print("MPR Separator - Environment Setup Utility")
    print("=============================================")
    
    # Create/update .env file
    config = create_env_file()
    
    # Test Azure Key Vault connection
    if test_azure_keyvault(config):
        # Test database connection
        test_database_connection(config)
    
    print("\nSetup completed. You can now run the application with: python src/main.py")

if __name__ == "__main__":
    main() 