import pandas as pd
import pyodbc
import os
from datetime import datetime
import logging

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class SQLService:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def get_credentials_from_keyvault(self):
        """Get database credentials from Azure Key Vault"""
        try:
            # Get Key Vault URL from environment variables
            key_vault_url = os.environ.get("KEY_VAULT_URL")
            db_username_secret = os.environ.get("DB_USERNAME_SECRET", "mpr-separator-db-username")
            db_password_secret = os.environ.get("DB_PASSWORD_SECRET", "mpr-separator-db-password")
            
            if not key_vault_url:
                raise ValueError("KEY_VAULT_URL environment variable is not set")
            
            # Create a SecretClient using default Azure credentials
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=key_vault_url, credential=credential)
            
            # Get the secrets
            username = client.get_secret(db_username_secret).value
            password = client.get_secret(db_password_secret).value
            
            return username, password
            
        except Exception as e:
            self.logger.error(f"Error getting credentials from Key Vault: {str(e)}")
            raise
    
    def connect(self):
        """Connect to the SQL Server database using Azure Key Vault credentials"""
        try:
            # Get database connection details from environment variables
            server = os.environ.get("DB_SERVER")
            database = os.environ.get("DB_NAME")
            
            if not server or not database:
                raise ValueError("Database connection environment variables not set properly")
            
            # Get credentials from Azure Key Vault
            username, password = self.get_credentials_from_keyvault()
            
            # Create connection string
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            )
            
            # Connect to the database
            self.connection = pyodbc.connect(conn_str)
            self.cursor = self.connection.cursor()
            
            self.logger.info("Connected to SQL Server database successfully")
            
        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise
    
    def disconnect(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        
        if self.connection:
            self.connection.close()
            self.logger.info("Disconnected from SQL Server database")
            
        self.cursor = None
        self.connection = None
    
    def save_data(self, df):
        """Save data to the database"""
        if df is None or df.empty:
            return 0
        
        records_saved = 0
        
        try:
            # Connect to the database
            if not self.connection:
                self.connect()
            
            # Get the table name from environment variables, with a default
            table_name = os.environ.get("DB_TABLE", "SeparatorRecords")
            
            # Prepare data for insertion
            for _, row in df.iterrows():
                # Extract data from the row
                order_number = str(row.get('OrderNumber', ''))
                separator_name = str(row.get('SeparatorName', ''))
                
                # Format date properly
                date_value = row.get('DateOfSeparation')
                if pd.isna(date_value):
                    date_str = None
                else:
                    date_str = pd.to_datetime(date_value).strftime('%Y-%m-%d')
                
                # Convert analysis to 1 or 0
                analysis = 1 if row.get('Analysis', False) else 0
                
                # SQL query for insertion (using parameters to prevent SQL injection)
                insert_query = f"""
                INSERT INTO {table_name} (OrderNumber, SeparatorName, DateOfSeparation, Analysis)
                VALUES (?, ?, ?, ?)
                """
                
                # Execute the query
                self.cursor.execute(insert_query, (order_number, separator_name, date_str, analysis))
                records_saved += 1
            
            # Commit the transaction
            self.connection.commit()
            self.logger.info(f"Successfully saved {records_saved} records to database")
            
        except Exception as e:
            self.logger.error(f"Error saving data to database: {str(e)}")
            
            # Rollback in case of error
            if self.connection:
                self.connection.rollback()
                
            raise
            
        finally:
            # Disconnect from the database
            self.disconnect()
        
        return records_saved
    
    def fetch_data(self, from_date=None, to_date=None, order_number=None, separator_name=None, analysis_only=False):
        """Fetch data from the database with optional filters"""
        try:
            # Connect to the database
            if not self.connection:
                self.connect()
            
            # Get the table name from environment variables, with a default
            table_name = os.environ.get("DB_TABLE", "SeparatorRecords")
            
            # Build the SQL query with filters
            query = f"SELECT OrderNumber, SeparatorName, DateOfSeparation, Analysis FROM {table_name} WHERE 1=1"
            params = []
            
            # Add date filters if specified
            if from_date:
                query += " AND DateOfSeparation >= ?"
                params.append(from_date)
            
            if to_date:
                query += " AND DateOfSeparation <= ?"
                params.append(to_date)
            
            # Add order number filter if specified
            if order_number:
                query += " AND OrderNumber LIKE ?"
                params.append(f"%{order_number}%")
            
            # Add separator name filter if specified
            if separator_name:
                query += " AND SeparatorName LIKE ?"
                params.append(f"%{separator_name}%")
            
            # Add analysis filter if specified
            if analysis_only:
                query += " AND Analysis = 1"
            
            # Order by date descending
            query += " ORDER BY DateOfSeparation DESC"
            
            # Execute the query
            self.cursor.execute(query, params)
            
            # Fetch all results
            rows = self.cursor.fetchall()
            
            # Convert to DataFrame
            columns = [column[0] for column in self.cursor.description]
            df = pd.DataFrame.from_records(rows, columns=columns)
            
            # Convert Analysis from 0/1 to boolean
            if 'Analysis' in df.columns:
                df['Analysis'] = df['Analysis'].astype(bool)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data from database: {str(e)}")
            raise
            
        finally:
            # Disconnect from the database
            self.disconnect() 