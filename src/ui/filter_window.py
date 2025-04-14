from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QDateEdit,
    QCheckBox, QGroupBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt, QDate, Signal
from datetime import datetime, timedelta

class FilterWindow(QDialog):
    # Signal to emit when data is filtered
    filtered_data_signal = Signal()
    
    def __init__(self, data_model, sql_service=None):
        super().__init__()
        
        self.data_model = data_model
        self.sql_service = sql_service
        
        # Setup the UI
        self.setWindowTitle("Search & Filter")
        self.setMinimumSize(600, 500)
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create filter tab
        self.filter_tab = QWidget()
        self.filter_layout = QVBoxLayout(self.filter_tab)
        
        # Create database tab
        self.database_tab = QWidget()
        self.database_layout = QVBoxLayout(self.database_tab)
        
        # Add tabs to widget
        self.tab_widget.addTab(self.filter_tab, "Filter Current Data")
        self.tab_widget.addTab(self.database_tab, "Load from Database")
        
        # Setup filter tab content
        self.setup_date_filters()
        self.setup_text_filters()
        self.setup_other_filters()
        
        # Setup database tab content
        self.setup_database_options()
        
        # Create action buttons
        self.setup_action_buttons()
        
        # Set default filters (last 7 days)
        self.set_default_filters()
        
    def setup_date_filters(self):
        """Setup date-related filters"""
        date_group = QGroupBox("Date Filters")
        date_layout = QFormLayout()
        
        # From date filter
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-7))
        date_layout.addRow("From Date:", self.from_date)
        
        # To date filter
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        date_layout.addRow("To Date:", self.to_date)
        
        # Date shortcuts
        date_shortcuts = QHBoxLayout()
        
        today_button = QPushButton("Today")
        today_button.clicked.connect(self.set_today_filter)
        
        last_week_button = QPushButton("Last 7 Days")
        last_week_button.clicked.connect(self.set_last_week_filter)
        
        last_month_button = QPushButton("Last 30 Days")
        last_month_button.clicked.connect(self.set_last_month_filter)
        
        date_shortcuts.addWidget(today_button)
        date_shortcuts.addWidget(last_week_button)
        date_shortcuts.addWidget(last_month_button)
        
        date_layout.addRow("Quick Date:", date_shortcuts)
        
        date_group.setLayout(date_layout)
        self.filter_layout.addWidget(date_group)
    
    def setup_text_filters(self):
        """Setup text-based filters"""
        text_group = QGroupBox("Text Filters")
        text_layout = QFormLayout()
        
        # Order number filter
        self.order_number_edit = QLineEdit()
        text_layout.addRow("Order Number:", self.order_number_edit)
        
        # Separator name filter
        self.separator_name_edit = QLineEdit()
        text_layout.addRow("Separator Name:", self.separator_name_edit)
        
        # ID filter
        self.id_edit = QLineEdit()
        text_layout.addRow("Record ID:", self.id_edit)
        
        text_group.setLayout(text_layout)
        self.filter_layout.addWidget(text_group)
    
    def setup_other_filters(self):
        """Setup other miscellaneous filters"""
        other_group = QGroupBox("Other Filters")
        other_layout = QVBoxLayout()
        
        # Analysis checkbox
        self.analysis_checkbox = QCheckBox("Analysis Only")
        other_layout.addWidget(self.analysis_checkbox)
        
        other_group.setLayout(other_layout)
        self.filter_layout.addWidget(other_group)
    
    def setup_database_options(self):
        """Setup database load options"""
        # Recent data options
        recent_group = QGroupBox("Recent Data")
        recent_layout = QVBoxLayout()
        
        self.load_recent_button = QPushButton("Load Last 7 Days")
        self.load_recent_button.clicked.connect(self.load_recent_data)
        recent_layout.addWidget(self.load_recent_button)
        
        self.load_last_month_button = QPushButton("Load Last 30 Days")
        self.load_last_month_button.clicked.connect(lambda: self.load_recent_data(30))
        recent_layout.addWidget(self.load_last_month_button)
        
        recent_group.setLayout(recent_layout)
        self.database_layout.addWidget(recent_group)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QVBoxLayout()
        
        self.load_all_button = QPushButton("Load All Records")
        self.load_all_button.clicked.connect(self.load_all_data)
        advanced_layout.addWidget(self.load_all_button)
        
        # Custom date range for database load
        date_range_layout = QFormLayout()
        
        self.db_from_date = QDateEdit()
        self.db_from_date.setCalendarPopup(True)
        self.db_from_date.setDate(QDate.currentDate().addDays(-30))
        date_range_layout.addRow("From:", self.db_from_date)
        
        self.db_to_date = QDateEdit()
        self.db_to_date.setCalendarPopup(True)
        self.db_to_date.setDate(QDate.currentDate())
        date_range_layout.addRow("To:", self.db_to_date)
        
        self.load_date_range_button = QPushButton("Load Custom Date Range")
        self.load_date_range_button.clicked.connect(self.load_custom_date_range)
        
        advanced_layout.addLayout(date_range_layout)
        advanced_layout.addWidget(self.load_date_range_button)
        
        advanced_group.setLayout(advanced_layout)
        self.database_layout.addWidget(advanced_group)
    
    def setup_action_buttons(self):
        """Setup action buttons"""
        button_layout = QHBoxLayout()
        
        # Apply filter button
        self.apply_button = QPushButton("Apply Filters")
        self.apply_button.clicked.connect(self.apply_filters)
        
        # Reset button
        self.reset_button = QPushButton("Reset Filters")
        self.reset_button.clicked.connect(self.reset_filters)
        
        # Cancel button
        self.cancel_button = QPushButton("Close")
        self.cancel_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(button_layout)
    
    def set_today_filter(self):
        """Set date filter to today only"""
        today = QDate.currentDate()
        self.from_date.setDate(today)
        self.to_date.setDate(today)
    
    def set_last_week_filter(self):
        """Set date filter to last 7 days"""
        today = QDate.currentDate()
        week_ago = today.addDays(-7)
        self.from_date.setDate(week_ago)
        self.to_date.setDate(today)
    
    def set_last_month_filter(self):
        """Set date filter to last 30 days"""
        today = QDate.currentDate()
        month_ago = today.addDays(-30)
        self.from_date.setDate(month_ago)
        self.to_date.setDate(today)
    
    def set_default_filters(self):
        """Set default filters (last 7 days)"""
        self.set_last_week_filter()
        
        # Clear other filters
        self.order_number_edit.clear()
        self.separator_name_edit.clear()
        self.id_edit.clear()
        self.analysis_checkbox.setChecked(False)
    
    def reset_filters(self):
        """Reset to default filters"""
        self.set_default_filters()
    
    def apply_filters(self):
        """Apply the current filters to the data"""
        # Get filter values
        from_date = self.from_date.date().toString('yyyy-MM-dd')
        to_date = self.to_date.date().toString('yyyy-MM-dd')
        order_number = self.order_number_edit.text().strip()
        separator_name = self.separator_name_edit.text().strip()
        record_id = self.id_edit.text().strip()
        analysis_only = self.analysis_checkbox.isChecked()
        
        # Apply filters to the data model
        self.data_model.apply_filters(
            from_date=from_date,
            to_date=to_date,
            order_number=order_number,
            separator_name=separator_name,
            record_id=record_id,
            analysis_only=analysis_only
        )
        
        # Emit signal that data has been filtered
        self.filtered_data_signal.emit()
        
        # Close the dialog
        self.accept()
    
    def load_recent_data(self, days=7):
        """Load recent data from database"""
        if not self.sql_service:
            return
            
        try:
            # Load data from database with date filter
            df = self.sql_service.load_data(days)
            
            if df is not None and not df.empty:
                # Process and validate data
                self.data_model.set_dataframe(df)
                
                # Emit signal to update UI
                self.filtered_data_signal.emit()
                
                # Close the dialog
                self.accept()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to load data from database: {str(e)}"
            )
    
    def load_all_data(self):
        """Load all data from database"""
        if not self.sql_service:
            return
            
        try:
            # Load all data from database
            df = self.sql_service.load_all_data()
            
            if df is not None and not df.empty:
                # Process and validate data
                self.data_model.set_dataframe(df)
                
                # Emit signal to update UI
                self.filtered_data_signal.emit()
                
                # Close the dialog
                self.accept()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to load data from database: {str(e)}"
            )
    
    def load_custom_date_range(self):
        """Load data from database with custom date range"""
        if not self.sql_service:
            return
            
        try:
            # Get date range
            from_date = self.db_from_date.date().toString('yyyy-MM-dd')
            to_date = self.db_to_date.date().toString('yyyy-MM-dd')
            
            # Load data from database with date filter
            df = self.sql_service.fetch_data(from_date=from_date, to_date=to_date)
            
            if df is not None and not df.empty:
                # Process and validate data
                self.data_model.set_dataframe(df)
                
                # Emit signal to update UI
                self.filtered_data_signal.emit()
                
                # Close the dialog
                self.accept()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to load data from database: {str(e)}"
            ) 
        self.accept() 