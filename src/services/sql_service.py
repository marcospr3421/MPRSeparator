import pandas as pd
import pyodbc
import os
from datetime import datetime
import logging

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
        
    def connect(self):
        """Connect to the SQL Server database"""
        try:
            # Get database connection details from environment variables
            server = os.environ.get("DB_SERVER", "")
            database = os.environ.get("DB_NAME", "")
            username = os.environ.get("DB_USERNAME", "")
            password = os.environ.get("DB_PASSWORD", "")
            
            if not server or not database:
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
            
            self.logger.info("Connected to SQL Server database successfully")
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
    
    def save_data(self, df):
        """Save data to the database"""
        if df is None or df.empty:
            return 0
        
        records_saved = 0
        failed_records = 0
        
        try:
            # Connect to the database
            if not self.connection or not self.cursor:
                if not self.connect():
                    raise ValueError("Failed to establish database connection")
            
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
                
                # Check if cursor is available before executing
                if self.cursor:
                    try:
                        # Execute the query
                        self.cursor.execute(insert_query, (order_number, separator_name, date_str, analysis))
                        records_saved += 1
                    except pyodbc.IntegrityError as e:
                        # Log but continue - allows us to skip duplicate records
                        error_msg = str(e)
                        if "UNIQUE KEY" in error_msg or "UNIQUE constraint" in error_msg:
                            self.logger.warning(f"Skipping duplicate record: {order_number}, {separator_name}")
                            failed_records += 1
                        else:
                            # Re-raise if it's another type of integrity error
                            raise
                else:
                    raise ValueError("Database cursor is not available")
            
            # Commit the transaction
            if self.connection:
                self.connection.commit()
                if failed_records > 0:
                    self.logger.info(f"Successfully saved {records_saved} records to database, {failed_records} records skipped due to duplicates")
                else:
                    self.logger.info(f"Successfully saved {records_saved} records to database")
            else:
                raise ValueError("Database connection is not available")
            
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
                return pd.DataFrame(columns=['Id', 'OrderNumber', 'SeparatorName', 'DateOfSeparation', 'Analysis'])
            
            # Convert to DataFrame
            columns = [column[0] for column in self.cursor.description]
            df = pd.DataFrame.from_records(rows, columns=columns)
            
            # Convert Analysis from 0/1 to boolean
            if 'Analysis' in df.columns and not df.empty:
                df['Analysis'] = df['Analysis'].astype(bool)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data from database: {str(e)}")
            raise
            
        finally:
            # Disconnect from the database
            self.disconnect() 

    def load_data(self, days=7):
        """Load data from the database with a default filter of the past 7 days
        
        Args:
            days (int): Number of days to look back. Default is 7.
        """
        try:
            # Calculate date range for last X days
            import datetime
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Fetch data with date filter
            return self.fetch_data(from_date=start_date, to_date=end_date)
        except Exception as e:
            self.logger.error(f"Error loading data from database: {str(e)}")
            raise
            
    def delete_record(self, record_id):
        """Delete a record from the database by ID
        
        Args:
            record_id (int): The ID of the record to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Connect to the database
            if not self.connection or not self.cursor:
                if not self.connect():
                    raise ValueError("Failed to establish database connection")
            
            # Get the table name from environment variables, with a default
            table_name = os.environ.get("DB_TABLE", "SeparatorRecords")
            
            # SQL query for deletion
            delete_query = f"DELETE FROM {table_name} WHERE Id = ?"
            
            # Execute the deletion
            if self.cursor:
                self.cursor.execute(delete_query, (record_id,))
                
                # Check if a row was affected
                rows_affected = self.cursor.rowcount
                
                # Commit the transaction
                if self.connection:
                    self.connection.commit()
                    
                    if rows_affected > 0:
                        self.logger.info(f"Successfully deleted record with ID {record_id}")
                        return True
                    else:
                        self.logger.warning(f"No record found with ID {record_id}")
                        return False
            
            return False
                
        except Exception as e:
            self.logger.error(f"Error deleting record from database: {str(e)}")
            if self.connection:
                self.connection.rollback()
            raise
            
        finally:
            # Disconnect from the database
            self.disconnect() 

    def load_all_data(self):
        """Load all data from the database without date filters"""
        try:
            # Fetch all data without any filters
            return self.fetch_data()
        except Exception as e:
            self.logger.error(f"Error loading all data from database: {str(e)}")
            raise 

    def update_record(self, record_id, data):
        """Update a record in the database
        
        Args:
            record_id (int): The ID of the record to update
            data (dict): Dictionary containing the fields to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Connect to the database
            if not self.connection or not self.cursor:
                if not self.connect():
                    raise ValueError("Failed to establish database connection")
            
            # Get the table name from environment variables, with a default
            table_name = os.environ.get("DB_TABLE", "SeparatorRecords")
            
            # Prepare SET clause and parameters
            set_clauses = []
            parameters = []
            
            # Extract fields to update
            if 'OrderNumber' in data:
                set_clauses.append("OrderNumber = ?")
                parameters.append(str(data['OrderNumber']))
                
            if 'SeparatorName' in data:
                set_clauses.append("SeparatorName = ?")
                parameters.append(str(data['SeparatorName']))
                
            if 'DateOfSeparation' in data:
                set_clauses.append("DateOfSeparation = ?")
                date_str = None
                if data['DateOfSeparation']:
                    date_str = pd.to_datetime(data['DateOfSeparation']).strftime('%Y-%m-%d')
                parameters.append(date_str)
                
            if 'Analysis' in data:
                set_clauses.append("Analysis = ?")
                analysis = 1 if data['Analysis'] else 0
                parameters.append(analysis)
            
            # If no fields to update, return early
            if not set_clauses:
                self.logger.warning("No fields to update")
                return False
            
            # Build the UPDATE query
            update_query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE Id = ?"
            
            # Add the ID parameter
            parameters.append(record_id)
            
            # Execute the update
            if self.cursor:
                self.cursor.execute(update_query, parameters)
                
                # Check if a row was affected
                rows_affected = self.cursor.rowcount
                
                # Commit the transaction
                if self.connection:
                    self.connection.commit()
                    
                    if rows_affected > 0:
                        self.logger.info(f"Successfully updated record with ID {record_id}")
                        return True
                    else:
                        self.logger.warning(f"No record found with ID {record_id}")
                        return False
            
            return False
                
        except Exception as e:
            self.logger.error(f"Error updating record in database: {str(e)}")
            if self.connection:
                self.connection.rollback()
            raise
            
        finally:
            # Disconnect from the database
            self.disconnect() 