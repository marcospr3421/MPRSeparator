from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QTableView, QHeaderView, QCheckBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem

import pandas as pd
import os
from datetime import datetime

from src.ui.filter_window import FilterWindow
from src.data.data_model import DataModel
from src.services.sql_service import SQLService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.data_model = DataModel()
        self.sql_service = SQLService()
        
        # Setup the UI
        self.setWindowTitle("MPR Separator")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create the import section
        self.setup_import_section()
        
        # Create the data table
        self.setup_data_table()
        
        # Create the action buttons
        self.setup_action_buttons()
        
        # Show status message
        self.statusBar().showMessage("Ready")
    
    def setup_import_section(self):
        """Create the file import section"""
        import_layout = QHBoxLayout()
        
        import_label = QLabel("Import Data:")
        self.import_button = QPushButton("Browse Files...")
        self.import_button.clicked.connect(self.import_file)
        
        import_layout.addWidget(import_label)
        import_layout.addWidget(self.import_button)
        import_layout.addStretch()
        
        self.main_layout.addLayout(import_layout)
    
    def setup_data_table(self):
        """Create the data table view"""
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        
        # Set headers for the table
        self.table_model.setHorizontalHeaderLabels([
            "Order Number", "Separator Name", "Date of Separation", "Analysis", "Actions"
        ])
        
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.main_layout.addWidget(self.table_view)
    
    def setup_action_buttons(self):
        """Create the action buttons"""
        button_layout = QHBoxLayout()
        
        self.filter_button = QPushButton("Filter Data")
        self.filter_button.clicked.connect(self.open_filter_window)
        
        self.save_button = QPushButton("Save to Database")
        self.save_button.clicked.connect(self.save_to_database)
        
        button_layout.addWidget(self.filter_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        
        self.main_layout.addLayout(button_layout)
    
    def import_file(self):
        """Import data from CSV or XLSX file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Data File", 
            "", 
            "Data Files (*.csv *.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Import data based on file extension
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            # Process and validate data
            self.data_model.set_dataframe(df)
            
            # Display data in the table
            self.display_data()
            
            self.statusBar().showMessage(f"Imported {len(df)} records from {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Import Error", 
                f"Failed to import data: {str(e)}"
            )
    
    def display_data(self):
        """Display the current data in the table view"""
        # Clear the model
        self.table_model.setRowCount(0)
        
        # Get data from the model
        df = self.data_model.get_dataframe()
        
        if df is None or df.empty:
            return
        
        # Fill the table with data
        for i, row in df.iterrows():
            order_item = QStandardItem(str(row.get('OrderNumber', '')))
            name_item = QStandardItem(str(row.get('SeparatorName', '')))
            
            # Format date if available
            date_str = str(row.get('DateOfSeparation', ''))
            if date_str and date_str != 'nan':
                try:
                    date_obj = pd.to_datetime(date_str)
                    date_str = date_obj.strftime('%Y-%m-%d')
                except:
                    pass
            date_item = QStandardItem(date_str)
            
            # Handle analysis boolean
            analysis_value = row.get('Analysis', False)
            analysis_item = QStandardItem()
            analysis_item.setCheckable(True)
            analysis_item.setCheckState(Qt.CheckState.Checked if analysis_value else Qt.CheckState.Unchecked)
            
            # Add an empty item for the Actions column (will be filled with buttons later)
            action_item = QStandardItem()
            
            self.table_model.appendRow([order_item, name_item, date_item, analysis_item, action_item])
    
    def open_filter_window(self):
        """Open the filter window"""
        self.filter_window = FilterWindow(self.data_model)
        self.filter_window.filtered_data_signal.connect(self.on_data_filtered)
        self.filter_window.show()
    
    def on_data_filtered(self):
        """Handle filtered data from the filter window"""
        self.display_data()
        
    def save_to_database(self):
        """Save the current data to the SQL database"""
        try:
            # Get the current data
            df = self.data_model.get_dataframe()
            
            if df is None or df.empty:
                QMessageBox.warning(
                    self, 
                    "No Data", 
                    "There is no data to save to the database."
                )
                return
            
            # Save to database
            records_saved = self.sql_service.save_data(df)
            
            QMessageBox.information(
                self, 
                "Save Successful", 
                f"Successfully saved {records_saved} records to the database."
            )
            
            self.statusBar().showMessage(f"Saved {records_saved} records to database")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Database Error", 
                f"Failed to save data to the database: {str(e)}"
            ) 