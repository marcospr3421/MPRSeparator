from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QDateEdit,
    QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt, QDate, Signal
from datetime import datetime, timedelta

class FilterWindow(QDialog):
    # Signal to emit when data is filtered
    filtered_data_signal = Signal()
    
    def __init__(self, data_model):
        super().__init__()
        
        self.data_model = data_model
        
        # Setup the UI
        self.setWindowTitle("Filter Data")
        self.setMinimumSize(500, 400)
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        
        # Create filter groups
        self.setup_date_filters()
        self.setup_text_filters()
        self.setup_other_filters()
        
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
        
        date_group.setLayout(date_layout)
        self.main_layout.addWidget(date_group)
    
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
        
        text_group.setLayout(text_layout)
        self.main_layout.addWidget(text_group)
    
    def setup_other_filters(self):
        """Setup other miscellaneous filters"""
        other_group = QGroupBox("Other Filters")
        other_layout = QVBoxLayout()
        
        # Analysis checkbox
        self.analysis_checkbox = QCheckBox("Analysis Only")
        other_layout.addWidget(self.analysis_checkbox)
        
        other_group.setLayout(other_layout)
        self.main_layout.addWidget(other_group)
    
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
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(button_layout)
    
    def set_default_filters(self):
        """Set default filters (last 7 days)"""
        today = QDate.currentDate()
        week_ago = today.addDays(-7)
        
        self.from_date.setDate(week_ago)
        self.to_date.setDate(today)
        
        # Clear other filters
        self.order_number_edit.clear()
        self.separator_name_edit.clear()
        self.analysis_checkbox.setChecked(False)
        
        # Apply the default filters
        self.apply_filters()
    
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
        analysis_only = self.analysis_checkbox.isChecked()
        
        # Apply filters to the data model
        self.data_model.apply_filters(
            from_date=from_date,
            to_date=to_date,
            order_number=order_number,
            separator_name=separator_name,
            analysis_only=analysis_only
        )
        
        # Emit signal that data has been filtered
        self.filtered_data_signal.emit()
        
        # Close the dialog
        self.accept() 