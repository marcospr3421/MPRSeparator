import pandas as pd
import pyodbc
import os
from datetime import datetime
import logging

class ReadOnlySQLService:
    """A read-only version of the SQL service for retrieving data without modification capabilities"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """Connect to the SQL Server database using read-only credentials"""
        try:
            # Get database connection details from environment variables
            server = os.environ.get("DB_SERVER", "")
            database = os.environ.get("DB_NAME", "")
            username = os.environ.get("DB_USERNAME", "readonlyuser")  # Default to readonly user
            password = os.environ.get("DB_PASSWORD", "")
            
            if not server or not database or not password:
                raise ValueError("Database connection environment variables not set properly")
            
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
            
            self.logger.info(f"Connected to SQL Server database successfully as {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            self.connection = None
            self.cursor = None
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
    
    def fetch_data(self, from_date=None, to_date=None, order_number=None, separator_name=None, analysis_only=False):
        """Fetch data from the database with optional filters"""
        try:
            # Connect to the database
            if not self.connection or not self.cursor:
                if not self.connect():
                    raise ValueError("Failed to establish database connection")
            
            # Get the table name from environment variables, with a default
            table_name = os.environ.get("DB_TABLE", "SeparatorRecords")
            
            # Build the SQL query with filters
            query = f"SELECT Id, OrderNumber, SeparatorName, DateOfSeparation, Analysis FROM {table_name} WHERE 1=1"
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
            
            # Check if cursor is available before executing
            if not self.cursor:
                raise ValueError("Database cursor is not available")
                
            # Execute the query
            self.cursor.execute(query, params)
            
            # Fetch all results
            rows = self.cursor.fetchall()
            
            # Make sure cursor.description is available
            if not self.cursor.description:
                self.logger.error("No description available for cursor")
                return pd.DataFrame()
                
            # Convert to pandas DataFrame
            columns = [column[0] for column in self.cursor.description]
            df = pd.DataFrame.from_records(rows, columns=columns)
            
            # Convert 'DateOfSeparation' to datetime
            if 'DateOfSeparation' in df.columns:
                df['DateOfSeparation'] = pd.to_datetime(df['DateOfSeparation'])
            
            # Convert 'Analysis' to boolean
            if 'Analysis' in df.columns:
                df['Analysis'] = df['Analysis'].astype(bool)
            
            self.logger.info(f"Successfully fetched {len(df)} records from database")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data from database: {str(e)}")
            raise
            
        finally:
            # Disconnect from the database
            self.disconnect()
    
    def load_data(self, days=7):
        """Load data from the last N days"""
        from_date = (datetime.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
        return self.fetch_data(from_date=from_date)
    
    def load_all_data(self):
        """Load all data from the database"""
        return self.fetch_data()
        
    # Note: This service doesn't include save_data, update_record, or delete_record methods
    # since it's intended for read-only access 