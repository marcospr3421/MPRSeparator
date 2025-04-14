import os
import sys
import pyodbc
from dotenv import load_dotenv

# Add the project root to the path
from pathlib import Path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

def check_db_connection():
    """Check if we can connect to the database and validate table structure."""
    try:
        # Get database connection details from environment variables
        server = os.environ.get("DB_SERVER", "")
        database = os.environ.get("DB_NAME", "")
        username = os.environ.get("DB_USERNAME", "")
        password = os.environ.get("DB_PASSWORD", "")
        table_name = os.environ.get("DB_TABLE", "SeparatorRecords")
        
        # Print connection details (mask password)
        print(f"Server: {server}")
        print(f"Database: {database}")
        print(f"Username: {username}")
        print(f"Table: {table_name}")
        
        if not server or not database or not username or not password:
            return False, "Missing database connection details in .env file."
        
        # Create connection string
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        
        print("\nAttempting to connect to the database...")
        # Connect to the database
        connection = pyodbc.connect(conn_str)
        cursor = connection.cursor()
        
        print("Connection successful!")
        
        # Check if the table exists
        print(f"\nChecking if table '{table_name}' exists...")
        cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'")
        result = cursor.fetchone()
        table_exists = result is not None and result[0] > 0
        
        if not table_exists:
            cursor.close()
            connection.close()
            return False, f"Table '{table_name}' does not exist in the database."
        
        print(f"Table '{table_name}' exists!")
        
        # Check table structure
        print("\nChecking table structure...")
        cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
        columns = {row[0].lower(): row[1] for row in cursor.fetchall()}
        
        required_columns = {
            'ordernumber': 'Order Number',
            'separatorname': 'Separator Name',
            'dateofseparation': 'Date of Separation',
            'analysis': 'Analysis'
        }
        
        missing_columns = []
        for col_name, display_name in required_columns.items():
            if col_name not in columns:
                missing_columns.append(display_name)
        
        if missing_columns:
            cursor.close()
            connection.close()
            return False, f"Missing required columns in table: {', '.join(missing_columns)}"
        
        # Check if the table has data
        print("\nChecking if table contains data...")
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        result = cursor.fetchone()
        row_count = result[0] if result is not None else 0
        print(f"Table contains {row_count} records.")
        
        # All checks passed
        cursor.close()
        connection.close()
        return True, "Database connection and structure validated successfully."
        
    except Exception as e:
        return False, f"Database connection error: {str(e)}"

if __name__ == "__main__":
    print("Validating database connection...")
    is_valid, message = check_db_connection()
    print(f"\nValidation result: {'SUCCESS' if is_valid else 'FAILED'}")
    print(message)
    
    if not is_valid:
        print("\nIf the table doesn't exist, you can create it with this SQL script:")
        print("""
CREATE TABLE SeparatorRecords (
    id INT IDENTITY(1,1) PRIMARY KEY,
    OrderNumber NVARCHAR(100),
    SeparatorName NVARCHAR(100),
    DateOfSeparation DATE,
    Analysis BIT
);
""") 