from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QTableView, QHeaderView, QCheckBox, QDateEdit, QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QGroupBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QStandardItemModel, QStandardItem

import pandas as pd
import os
from datetime import datetime, timedelta

from src.data.data_model import DataModel
from src.services.sql_service import SQLService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.data_model = DataModel()
        self.sql_service = SQLService()
        
        # Setup the UI
        self.setWindowTitle("MPR Separator")
        self.setMinimumSize(1000, 700)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create the import section
        self.setup_import_section()
        
        # Create the filter section
        self.setup_filter_section()
        
        # Create the data table
        self.setup_data_table()
        
        # Create the action buttons
        self.setup_action_buttons()
        
        # Show status message
        self.statusBar().showMessage("Ready")
    
    def setup_import_section(self):
        """Create the file import section"""
        import_layout = QHBoxLayout()
        
        import_label = QLabel("Data Sources:")
        self.import_button = QPushButton("Import File...")
        self.import_button.clicked.connect(self.import_file)
        
        import_layout.addWidget(import_label)
        import_layout.addWidget(self.import_button)
        import_layout.addStretch()
        
        self.main_layout.addLayout(import_layout)
    
    def setup_filter_section(self):
        """Create centralized filter controls"""
        filter_group = QGroupBox("Search & Filter Database")
        filter_layout = QVBoxLayout(filter_group)
        
        # Date filters
        date_layout = QHBoxLayout()
        date_label = QLabel("Date Range:")
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-7))
        
        date_to_label = QLabel("to")
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        
        # Quick date buttons
        self.today_button = QPushButton("Today")
        self.today_button.clicked.connect(self.set_today_filter)
        
        self.week_button = QPushButton("Last 7 Days")
        self.week_button.clicked.connect(self.set_week_filter)
        
        self.month_button = QPushButton("Last 30 Days")
        self.month_button.clicked.connect(self.set_month_filter)
        
        self.all_button = QPushButton("All Dates")
        self.all_button.clicked.connect(self.clear_date_filter)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.from_date)
        date_layout.addWidget(date_to_label)
        date_layout.addWidget(self.to_date)
        date_layout.addWidget(self.today_button)
        date_layout.addWidget(self.week_button)
        date_layout.addWidget(self.month_button)
        date_layout.addWidget(self.all_button)
        date_layout.addStretch()
        
        # Text filters
        text_layout = QHBoxLayout()
        
        # Order number filter
        order_label = QLabel("Order:")
        self.order_edit = QLineEdit()
        self.order_edit.setPlaceholderText("Filter by order number")
        
        # Separator name filter
        name_label = QLabel("Separator:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Filter by separator name")
        
        # ID filter
        id_label = QLabel("ID:")
        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("Find by record ID")
        
        # Analysis filter
        self.analysis_checkbox = QCheckBox("Analysis Only")
        
        text_layout.addWidget(order_label)
        text_layout.addWidget(self.order_edit)
        text_layout.addWidget(name_label)
        text_layout.addWidget(self.name_edit)
        text_layout.addWidget(id_label)
        text_layout.addWidget(self.id_edit)
        text_layout.addWidget(self.analysis_checkbox)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Search button
        self.search_button = QPushButton("Search Database")
        self.search_button.clicked.connect(self.search_database)
        
        # All Records button
        self.all_records_button = QPushButton("All Records")
        self.all_records_button.clicked.connect(self.search_all_records)
        
        # Reset button 
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_filters_and_results)
        
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.all_records_button)
        button_layout.addWidget(self.reset_button)
        
        filter_layout.addLayout(date_layout)
        filter_layout.addLayout(text_layout)
        filter_layout.addLayout(button_layout)
        
        self.main_layout.addWidget(filter_group)
    
    def setup_data_table(self):
        """Create the data table view"""
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        
        # Set headers for the table
        self.table_model.setHorizontalHeaderLabels([
            "Select", "Order Number", "Separator Name", "Date of Separation", "Analysis"
        ])
        
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Make the select column narrower
        self.table_view.setColumnWidth(0, 50)
        
        self.main_layout.addWidget(self.table_view)
    
    def setup_action_buttons(self):
        """Create the action buttons"""
        button_layout = QHBoxLayout()
        
        # Selection controls
        selection_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.toggled.connect(self.toggle_select_all)
        
        # Selected items actions
        self.edit_selected_button = QPushButton("Edit Selected")
        self.edit_selected_button.clicked.connect(self.edit_selected_records)
        
        self.delete_selected_button = QPushButton("Delete Selected")
        self.delete_selected_button.clicked.connect(self.delete_selected_records)
        
        # Add widgets to layouts
        selection_layout.addWidget(self.select_all_checkbox)
        selection_layout.addStretch()
        
        button_layout.addLayout(selection_layout)
        button_layout.addWidget(self.edit_selected_button)
        button_layout.addWidget(self.delete_selected_button)
        
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
            
            # Show preview dialog
            if self.show_import_preview(df, os.path.basename(file_path)):
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
    
    def show_import_preview(self, df, filename):
        """Show a preview of the data to be imported and get user confirmation
        
        Args:
            df: DataFrame with data to preview
            filename: Name of the file being imported
            
        Returns:
            bool: True if user confirmed import, False otherwise
        """
        # Create preview dialog
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle(f"Preview Import: {filename}")
        preview_dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(preview_dialog)
        
        # Add info label
        info_text = (f"Preview of data from {filename}. "
                    f"Found {len(df)} records. "
                    "Please verify the data before importing.")
        info_label = QLabel(info_text)
        layout.addWidget(info_label)
        
        # Create preview table
        preview_table = QTableView()
        preview_model = QStandardItemModel()
        
        # Set up table headers
        headers = list(df.columns)
        preview_model.setHorizontalHeaderLabels(headers)
        
        # Add sample data (first 100 rows max)
        sample_rows = min(100, len(df))
        for i in range(sample_rows):
            row_items = []
            for col in headers:
                value = str(df.iloc[i].get(col, ''))
                item = QStandardItem(value)
                row_items.append(item)
            preview_model.appendRow(row_items)
            
        preview_table.setModel(preview_model)
        preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Add preview message
        if len(df) > sample_rows:
            preview_message = QLabel(f"Showing {sample_rows} of {len(df)} records")
            layout.addWidget(preview_message)
            
        layout.addWidget(preview_table)
        
        # Add data validation report
        validation_group = QGroupBox("Data Validation")
        validation_layout = QVBoxLayout(validation_group)
        
        # Check for missing required columns
        required_columns = ['OrderNumber', 'SeparatorName', 'DateOfSeparation']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            validation_message = QLabel(f"⚠️ Missing required columns: {', '.join(missing_columns)}")
            validation_message.setStyleSheet("color: red")
        else:
            validation_message = QLabel("✓ All required columns present")
            validation_message.setStyleSheet("color: green")
            
        validation_layout.addWidget(validation_message)
        
        # Check for empty values in key columns
        if 'OrderNumber' in df.columns:
            missing_orders = df['OrderNumber'].isna().sum()
            if missing_orders > 0:
                order_message = QLabel(f"⚠️ {missing_orders} records missing Order Number")
                order_message.setStyleSheet("color: red")
                validation_layout.addWidget(order_message)
                
        if 'SeparatorName' in df.columns:
            missing_names = df['SeparatorName'].isna().sum()
            if missing_names > 0:
                name_message = QLabel(f"⚠️ {missing_names} records missing Separator Name")
                name_message.setStyleSheet("color: red")
                validation_layout.addWidget(name_message)
                
        if 'DateOfSeparation' in df.columns:
            missing_dates = df['DateOfSeparation'].isna().sum()
            if missing_dates > 0:
                date_message = QLabel(f"⚠️ {missing_dates} records missing Date")
                date_message.setStyleSheet("color: red")
                validation_layout.addWidget(date_message)
        
        layout.addWidget(validation_group)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(preview_dialog.accept)
        button_box.rejected.connect(preview_dialog.reject)
        layout.addWidget(button_box)
        
        # Execute dialog
        return preview_dialog.exec() == QDialog.DialogCode.Accepted
    
    def display_data(self):
        """Display the current data in the table view"""
        # Clear the model
        self.table_model.setRowCount(0)
        
        # Get data from the model
        df = self.data_model.get_dataframe()
        
        if df is None or df.empty:
            self.statusBar().showMessage("No data to display")
            return
        
        # Fill the table with data
        for i, row in df.iterrows():
            # Add a checkbox for selection
            select_item = QStandardItem()
            select_item.setCheckable(True)
            select_item.setCheckState(Qt.CheckState.Unchecked)
            
            # Store ID as item data but don't display it
            id_value = str(row.get('Id', ''))
            
            order_item = QStandardItem(str(row.get('OrderNumber', '')))
            # Store the ID as user data in the order item for reference
            order_item.setData(id_value, Qt.ItemDataRole.UserRole)
            
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
            
            # Add the row to the table (without ID column)
            row_items = [select_item, order_item, name_item, date_item, analysis_item]
            self.table_model.appendRow(row_items)
        
        # Update status bar with record count
        record_count = len(df)
        self.statusBar().showMessage(f"Displaying {record_count} records")
    
    def set_today_filter(self):
        """Set date filter to today only"""
        today = QDate.currentDate()
        self.from_date.setDate(today)
        self.to_date.setDate(today)
    
    def set_week_filter(self):
        """Set date filter to last 7 days"""
        today = QDate.currentDate()
        week_ago = today.addDays(-7)
        self.from_date.setDate(week_ago)
        self.to_date.setDate(today)
    
    def set_month_filter(self):
        """Set date filter to last 30 days"""
        today = QDate.currentDate()
        month_ago = today.addDays(-30)
        self.from_date.setDate(month_ago)
        self.to_date.setDate(today)
    
    def clear_date_filter(self, and_search=False):
        """Clear date filter (set to all dates)"""
        self.from_date.setDate(QDate(2000, 1, 1))
        self.to_date.setDate(QDate.currentDate())
        
        if and_search:
            self.search_database()
    
    def reset_filters(self):
        """Reset all filters to default"""
        self.set_week_filter()
        self.order_edit.clear()
        self.name_edit.clear()
        self.id_edit.clear()
        self.analysis_checkbox.setChecked(False)
    
    def toggle_select_all(self, checked):
        """Toggle selection of all rows"""
        for row in range(self.table_model.rowCount()):
            select_item = self.table_model.item(row, 0)
            if select_item:
                select_item.setCheckState(
                    Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
                )
    
    def get_selected_rows(self):
        """Get a list of row indices that are currently selected"""
        selected_rows = []
        for row in range(self.table_model.rowCount()):
            select_item = self.table_model.item(row, 0)
            if select_item and select_item.checkState() == Qt.CheckState.Checked:
                selected_rows.append(row)
        return selected_rows
    
    def get_selected_ids(self):
        """Get a list of IDs from the selected rows"""
        selected_ids = []
        for row in self.get_selected_rows():
            # Get ID from the order item's user data
            order_item = self.table_model.item(row, 1)  # Order Number is now column 1
            if order_item:
                id_value = order_item.data(Qt.ItemDataRole.UserRole)
                if id_value:
                    selected_ids.append(id_value)
        return selected_ids
    
    def edit_selected_records(self):
        """Open a dialog to edit selected records"""
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select at least one record to edit."
            )
            return
        
        # Open the edit dialog for selected rows
        self.open_edit_dialog(selected_rows)
    
    def delete_selected_records(self):
        """Delete all selected records"""
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select at least one record to delete."
            )
            return
        
        # Confirm deletion with user
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_ids)} selected record(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            success_count = 0
            fail_count = 0
            
            for record_id in selected_ids:
                try:
                    if self.sql_service.delete_record(record_id):
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception:
                    fail_count += 1
            
            # Show results
            message = f"Successfully deleted {success_count} record(s)."
            if fail_count > 0:
                message += f"\n{fail_count} record(s) could not be deleted."
            
            QMessageBox.information(
                self,
                "Delete Results",
                message
            )
            
            # Refresh the view by searching again
            self.search_database()
    
    def open_edit_dialog(self, rows):
        """Open a dialog to edit records from the given rows
        
        Args:
            rows: List of row indices to edit
        """
        if not rows:
            return
            
        # Create a dialog for editing
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Edit Record(s)")
        edit_dialog.setMinimumWidth(400)
        
        layout = QFormLayout(edit_dialog)
        
        # Editable fields
        order_edit = QLineEdit()
        separator_edit = QLineEdit()
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        analysis_checkbox = QCheckBox()
        
        # If editing a single row, pre-fill the fields
        if len(rows) == 1:
            row = rows[0]
            order_number = self.table_model.item(row, 1).text()  # Order Number (column 1)
            separator_name = self.table_model.item(row, 2).text()  # Separator Name (column 2)
            
            # Date of separation
            date_str = self.table_model.item(row, 3).text()  # Date (column 3)
            try:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    date_edit.setDate(date)
            except Exception:
                pass
                
            # Analysis checkbox
            analysis_item = self.table_model.item(row, 4)  # Analysis (column 4)
            is_checked = analysis_item and analysis_item.checkState() == Qt.CheckState.Checked
            analysis_checkbox.setChecked(is_checked)
            
            # Set the text fields
            order_edit.setText(order_number)
            separator_edit.setText(separator_name)
            
        # Add fields to the form
        layout.addRow("Order Number:", order_edit)
        layout.addRow("Separator Name:", separator_edit)
        layout.addRow("Date of Separation:", date_edit)
        layout.addRow("Analysis:", analysis_checkbox)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(edit_dialog.accept)
        button_box.rejected.connect(edit_dialog.reject)
        layout.addRow(button_box)
        
        # Execute the dialog
        result = edit_dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Apply the changes to the selected rows
            updated_data = {
                'OrderNumber': order_edit.text(),
                'SeparatorName': separator_edit.text(),
                'DateOfSeparation': date_edit.date().toString("yyyy-MM-dd"),
                'Analysis': analysis_checkbox.isChecked()
            }
            
            self.update_records(rows, updated_data)
    
    def update_records(self, rows, data):
        """Update records with new data
        
        Args:
            rows: List of row indices to update
            data: Dictionary with the updated data
        """
        if not rows or not data:
            return
            
        # Get current DataFrame
        df = self.data_model.get_dataframe()
        
        # Check if DataFrame is valid
        if df is None or df.empty:
            return
            
        # Track which records were updated
        updated_ids = []
        db_updated_ids = []
        
        for row in rows:
            # Get the record ID from the order item's user data
            order_item = self.table_model.item(row, 1)  # Order Number (column 1)
            if not order_item:
                continue
                
            record_id = order_item.data(Qt.ItemDataRole.UserRole)
            if not record_id:
                continue
                
            # Find this record in the DataFrame by ID
            if 'Id' in df.columns:
                # Find the row in DataFrame by ID
                row_filter = df['Id'].astype(str) == record_id
                if not row_filter.any():
                    continue
                    
                # Update the DataFrame with new data
                for key, value in data.items():
                    if key in df.columns:
                        df.loc[row_filter, key] = value
                        
                updated_ids.append(record_id)
                
                # Try to update the database if record has an ID
                try:
                    if self.sql_service.update_record(record_id, data):
                        db_updated_ids.append(record_id)
                except Exception as e:
                    self.statusBar().showMessage(f"Error updating database: {str(e)}")
            
            # Update the table view
            for key, value in data.items():
                if key == 'OrderNumber':
                    self.table_model.item(row, 1).setText(value)
                elif key == 'SeparatorName':
                    self.table_model.item(row, 2).setText(value)
                elif key == 'DateOfSeparation':
                    self.table_model.item(row, 3).setText(value)
                elif key == 'Analysis':
                    analysis_item = self.table_model.item(row, 4)
                    if analysis_item:
                        analysis_item.setCheckState(
                            Qt.CheckState.Checked if value else Qt.CheckState.Unchecked
                        )
        
        # Update the DataModel with the modified DataFrame
        self.data_model.set_dataframe(df)
        
        # Show a success message
        if updated_ids:
            message = f"Updated {len(updated_ids)} record(s) in view."
            if db_updated_ids:
                message += f"\n{len(db_updated_ids)} record(s) updated in database."
            elif len(db_updated_ids) < len(updated_ids):
                message += "\nSome records were not updated in the database."
                
            QMessageBox.information(
                self,
                "Update Successful",
                message
            )
        else:
            QMessageBox.warning(
                self,
                "Update Failed",
                "No records were updated."
            )

    def reset_filters_and_results(self):
        """Reset filters and clear results"""
        # Reset filters
        self.reset_filters()
        
        # Clear the table
        self.table_model.setRowCount(0)
        
        # Clear the data model
        if self.data_model.original_df is not None:
            empty_df = pd.DataFrame(columns=self.data_model.original_df.columns)
            self.data_model.set_dataframe(empty_df)
        
        self.statusBar().showMessage("Filters and results cleared")
        
    def search_database(self):
        """Search the database using the current filter settings"""
        try:
            # Get filter values
            from_date = self.from_date.date().toString('yyyy-MM-dd')
            to_date = self.to_date.date().toString('yyyy-MM-dd')
            order_number = self.order_edit.text().strip()
            separator_name = self.name_edit.text().strip()
            record_id = self.id_edit.text().strip()
            analysis_only = self.analysis_checkbox.isChecked()
            
            # Fetch data directly from database with filters
            df = self.sql_service.fetch_data(
                from_date=from_date,
                to_date=to_date,
                order_number=order_number,
                separator_name=separator_name,
                analysis_only=analysis_only
            )
            
            # If record ID is specified, filter manually since SQL service doesn't have direct ID filtering
            if record_id and 'Id' in df.columns and not df.empty:
                df = df[df['Id'].astype(str) == record_id]
            
            if df is None or df.empty:
                QMessageBox.warning(
                    self, 
                    "No Results", 
                    "No records found matching your search criteria."
                )
                # Clear the table when no results found
                self.table_model.setRowCount(0)
                self.statusBar().showMessage("No records found matching search criteria")
                return
            
            # Update the data model with search results
            self.data_model.set_dataframe(df)
            
            # Display data in the table
            self.display_data()
            
            # Update status message
            self.statusBar().showMessage(f"Found {len(df)} records matching search criteria")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Search Error", 
                f"Failed to search database: {str(e)}"
            )

    def search_all_records(self):
        """Search for all records with no filters"""
        # Clear all filters first
        self.order_edit.clear()
        self.name_edit.clear()
        self.id_edit.clear()
        self.analysis_checkbox.setChecked(False)
        self.clear_date_filter()
        
        # Then search the database
        self.search_database() 