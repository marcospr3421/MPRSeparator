import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Import the read-only SQL service
from readonly_sql_service import ReadOnlySQLService

def main():
    """Main function for the read-only data viewer application"""
    
    # Load environment variables from the readonly .env file
    load_dotenv(".env.readonly")
    
    print("MPR Separator Read-Only Data Viewer")
    print("===================================")
    
    # Create a read-only SQL service instance
    sql_service = ReadOnlySQLService()
    
    try:
        # Menu loop
        while True:
            print("\nOptions:")
            print("1. View recent data (last 7 days)")
            print("2. View all data")
            print("3. Search by date range")
            print("4. Search by order number")
            print("5. Search by separator name")
            print("6. Exit")
            
            choice = input("\nSelect an option (1-6): ")
            
            if choice == "1":
                # Load recent data
                df = sql_service.load_data(days=7)
                display_data(df)
            
            elif choice == "2":
                # Load all data
                df = sql_service.load_all_data()
                display_data(df)
            
            elif choice == "3":
                # Search by date range
                from_date = input("Enter start date (YYYY-MM-DD): ")
                to_date = input("Enter end date (YYYY-MM-DD): ")
                
                # Validate dates
                try:
                    pd.to_datetime(from_date)
                    pd.to_datetime(to_date)
                except:
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    continue
                
                df = sql_service.fetch_data(from_date=from_date, to_date=to_date)
                display_data(df)
            
            elif choice == "4":
                # Search by order number
                order_number = input("Enter order number: ")
                df = sql_service.fetch_data(order_number=order_number)
                display_data(df)
            
            elif choice == "5":
                # Search by separator name
                separator_name = input("Enter separator name: ")
                df = sql_service.fetch_data(separator_name=separator_name)
                display_data(df)
            
            elif choice == "6":
                print("Exiting application.")
                break
            
            else:
                print("Invalid option. Please try again.")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
def display_data(df):
    """Display data from a dataframe"""
    if df.empty:
        print("No data found.")
        return
    
    # Format dataframe for display
    df_display = df.copy()
    
    # Format dates for display
    if 'DateOfSeparation' in df_display.columns:
        df_display['DateOfSeparation'] = df_display['DateOfSeparation'].dt.strftime('%Y-%m-%d')
    
    # Display data
    print(f"\nFound {len(df_display)} records:")
    pd.set_option('display.max_rows', 20)  # Limit display to 20 rows
    pd.set_option('display.width', 120)    # Set width for better display
    print(df_display)
    
    # If there are more than 20 records, show a message
    if len(df_display) > 20:
        print(f"(Showing 20 of {len(df_display)} records)")
    
    # Export option
    export = input("\nExport to Excel? (y/n): ")
    if export.lower() == 'y':
        filename = f"separator_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Data exported to {filename}")

if __name__ == "__main__":
    main() 