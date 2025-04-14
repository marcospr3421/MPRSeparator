import pandas as pd
import os

def validate_file(file_path):
    """Validate a data file for the MPR Separator application."""
    if not os.path.exists(file_path):
        return False, f"File {file_path} does not exist."
    
    try:
        # Import data based on file extension
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return False, "Unsupported file format. Only .csv and .xlsx are supported."
        
        # Check if dataframe is empty
        if df.empty:
            return False, "File is empty."
        
        # Check for required columns (case-insensitive)
        required_columns = ['OrderNumber', 'SeparatorName', 'DateOfSeparation', 'Analysis']
        columns_lower = [col.lower() for col in df.columns]
        
        for col in required_columns:
            if col.lower() not in columns_lower:
                return False, f"Required column '{col}' not found in the file."
        
        # Validate date format in DateOfSeparation column
        date_col_idx = columns_lower.index('dateofseparation')
        actual_date_col = df.columns[date_col_idx]
        
        try:
            df[actual_date_col] = pd.to_datetime(df[actual_date_col])
        except Exception as e:
            return False, f"Invalid date format in '{actual_date_col}' column: {str(e)}"
        
        # Check for blank values in required columns
        for col in ['OrderNumber', 'SeparatorName']:
            col_idx = columns_lower.index(col.lower())
            actual_col = df.columns[col_idx]
            if df[actual_col].isna().any() or (df[actual_col] == '').any():
                return False, f"Blank values found in required column '{col}'."
        
        # Validation passed!
        return True, f"File is valid. Contains {len(df)} records."
        
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

# Validate both sample files
if __name__ == "__main__":
    csv_path = "sample_data.csv"
    xlsx_path = "sample_data.xlsx"
    
    print("Validating CSV file...")
    is_valid, message = validate_file(csv_path)
    print(f"CSV file valid: {is_valid}")
    print(message)
    
    print("\nValidating Excel file...")
    is_valid, message = validate_file(xlsx_path)
    print(f"Excel file valid: {is_valid}")
    print(message) 