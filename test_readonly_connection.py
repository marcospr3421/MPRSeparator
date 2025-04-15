import pyodbc
import pandas as pd
from dotenv import load_dotenv
import os

def test_readonly_connection():
    """Test connection with read-only user credentials"""
    # Configuration - replace these with your read-only user credentials
    server = "mprsqlserver.database.windows.net"  # From .env
    database = "mprDB02"  # From .env
    username = "lucascardoso"  # The read-only user you created
    password = "Zaqmko21@"  # The password you specified

    # Create connection string
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    
    try:
        # Connect to the database
        print(f"Connecting to {database} on {server} as {username}...")
        connection = pyodbc.connect(conn_str)
        cursor = connection.cursor()
        
        print("Connection successful!")
        
        # Test if we can read data
        table_name = os.environ.get("DB_TABLE", "SeparatorRecords")
        query = f"SELECT TOP 5 * FROM {table_name}"
        
        # Try to execute a SELECT query
        print(f"Testing SELECT access on {table_name}...")
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Display the results
        if rows:
            print(f"Successfully retrieved {len(rows)} rows:")
            columns = [column[0] for column in cursor.description]
            df = pd.DataFrame.from_records(rows, columns=columns)
            print(df)
        else:
            print("No data returned.")
            
        # Try to execute an INSERT query (should fail with read-only user)
        print("\nTesting INSERT access (should fail with read-only user)...")
        try:
            insert_query = f"INSERT INTO {table_name} (OrderNumber, SeparatorName, DateOfSeparation, Analysis) VALUES ('TEST', 'TEST', '2023-01-01', 0)"
            cursor.execute(insert_query)
            print("WARNING: Insert operation succeeded. This user has more than read-only permissions!")
        except pyodbc.Error as e:
            print(f"Expected error on INSERT (confirming read-only status): {e}")
            
        # Close cursor and connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Connection error: {str(e)}")

if __name__ == "__main__":
    # Load environment variables if needed
    load_dotenv()
    test_readonly_connection() 