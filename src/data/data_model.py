import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class DataModel:
    def __init__(self):
        self.original_df = None
        self.filtered_df = None
    
    def set_dataframe(self, df):
        """Set the data from a dataframe and standardize column names"""
        # Standardize column names (case-insensitive)
        std_columns = {
            'id': 'Id',
            'record_id': 'Id',
            'recordid': 'Id',
            'ordernumber': 'OrderNumber',
            'order': 'OrderNumber',
            'order number': 'OrderNumber',
            'order_number': 'OrderNumber',
            'separatorname': 'SeparatorName',
            'separator': 'SeparatorName',
            'separator name': 'SeparatorName',
            'separator_name': 'SeparatorName',
            'dateofseparation': 'DateOfSeparation',
            'date': 'DateOfSeparation',
            'date of separation': 'DateOfSeparation',
            'separation date': 'DateOfSeparation',
            'separation_date': 'DateOfSeparation',
            'analysis': 'Analysis',
            'analisys': 'Analysis'
        }
        
        # Rename columns (case insensitive)
        df.columns = [col.strip() for col in df.columns]
        for i, col in enumerate(df.columns):
            lower_col = col.lower()
            if lower_col in std_columns:
                df = df.rename(columns={col: std_columns[lower_col]})
        
        # Check for required columns and add if missing
        required_columns = ['OrderNumber', 'SeparatorName', 'DateOfSeparation', 'Analysis']
        for col in required_columns:
            if col not in df.columns:
                if col == 'Analysis':
                    df[col] = False  # Default: no analysis
                else:
                    df[col] = ''
        
        # Convert DateOfSeparation to datetime if it's not already
        if 'DateOfSeparation' in df.columns:
            df['DateOfSeparation'] = pd.to_datetime(df['DateOfSeparation'], errors='coerce')
        
        # Convert Analysis to boolean if it's not already
        if 'Analysis' in df.columns:
            # Determine the best way to convert to boolean
            if df['Analysis'].dtype == bool:
                pass  # Already boolean
            elif df['Analysis'].dtype in [int, float]:
                df['Analysis'] = df['Analysis'].astype(bool)
            else:
                # Convert various string representations to boolean
                df['Analysis'] = df['Analysis'].apply(self._str_to_bool)
        
        # Store the original dataframe
        self.original_df = df
        
        # Check if this is a small sample dataset (less than 100 records)
        # If it's small, show all records. Otherwise, apply default filters
        if len(df) < 100:
            # For small datasets, show all records
            self.filtered_df = df.copy()
        else:
            # For large datasets, apply the 7-day filter
            self.apply_default_filters()
            
        # Check if the filtered data is empty after applying date filters
        # This happens if all data is outside the default date range
        if self.filtered_df is None or self.filtered_df.empty:
            # If filtered data is empty, just show all data
            self.filtered_df = df.copy()
    
    def _str_to_bool(self, value):
        """Convert various string representations to boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            lower_value = value.lower().strip()
            if lower_value in ('yes', 'true', 't', 'y', '1'):
                return True
            elif lower_value in ('no', 'false', 'f', 'n', '0'):
                return False
        return False
    
    def get_dataframe(self):
        """Get the current filtered dataframe"""
        return self.filtered_df
    
    def apply_default_filters(self):
        """Apply default filters (last 7 days)"""
        if self.original_df is None:
            return
        
        # Calculate date range for last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Apply filter
        mask = (self.original_df['DateOfSeparation'] >= start_date) & (self.original_df['DateOfSeparation'] <= end_date)
        self.filtered_df = self.original_df[mask].copy()
    
    def apply_filters(self, from_date=None, to_date=None, order_number=None, separator_name=None, record_id=None, analysis_only=False):
        """Apply filters to the data"""
        if self.original_df is None:
            return
        
        # Start with the original data
        filtered_df = self.original_df.copy()
        
        # Apply date filter if specified
        if from_date is not None:
            filtered_df = filtered_df[filtered_df['DateOfSeparation'] >= pd.Timestamp(from_date)]
        
        if to_date is not None:
            # Add one day to include the end date fully
            to_date_inclusive = pd.Timestamp(to_date) + pd.Timedelta(days=1)
            filtered_df = filtered_df[filtered_df['DateOfSeparation'] < to_date_inclusive]
        
        # Apply record ID filter if specified
        if record_id and 'Id' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Id'].astype(str) == record_id]
        
        # Apply order number filter if specified
        if order_number:
            filtered_df = filtered_df[filtered_df['OrderNumber'].astype(str).str.contains(order_number, case=False)]
        
        # Apply separator name filter if specified
        if separator_name:
            filtered_df = filtered_df[filtered_df['SeparatorName'].astype(str).str.contains(separator_name, case=False)]
        
        # Apply analysis filter if specified
        if analysis_only:
            filtered_df = filtered_df[filtered_df['Analysis'] == True]
        
        # Update the filtered dataframe
        self.filtered_df = filtered_df 