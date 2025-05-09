from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QTableView, QHeaderView, QCheckBox, QDateEdit, QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QGroupBox, QFrame, QMenu, QToolBar, QComboBox, QProgressDialog, QApplication
)
from PySide6.QtCore import Qt, QDate, QSortFilterProxyModel, QModelIndex, QTranslator, QCoreApplication, QTimer, QThread, Signal, QObject
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap, QBrush, QColor
from PySide6.QtWidgets import QProgressBar

import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path

from src.data.data_model import DataModel
from src.services.sql_service import SQLService
from src.services.translator import LanguageManager
from src.services.updater import Updater
APP_VERSION = "1.0.0"
GITHUB_REPO = "your-github-username/MPRSeparator"  # Replace with your actual GitHub username and repo

class UpdateDownloader(QObject):
    """Worker class for downloading updates in a separate thread"""
    progress = Signal(int)
    finished = Signal()
    
    def __init__(self, updater, release_info, version_str):
        super().__init__()
        self.updater = updater
        self.release_info = release_info
        self.version_str = version_str
        self.success = False
        self.file_path = None
        
    def run(self):
        """Run the download process"""
        try:
            self.file_path = self.updater.download_update(
                self.release_info, 
                progress_callback=self.progress.emit
            )
            self.success = True
        except Exception as e:
            print(f"Download error: {str(e)}")
            self.success = False
        finally:
            self.finished.emit()

class SortableTableModel(QStandardItemModel):
    """Custom model that handles sorting properly for different data types"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sort_order = {}  # Track sort order for each column
        
    def sort(self, column, order):
        # Skip the checkbox column (column 0)
        if column == 0:
            return
            
        # For date column, use the timestamp data for proper sorting
        if column == 3:  # Date column
            self.setSortRole(Qt.ItemDataRole.UserRole)
        # For analysis column, use the boolean value for sorting
        elif column == 4:  # Analysis column
            self.setSortRole(Qt.ItemDataRole.UserRole)
        else:
            # Use display text for other columns
            self.setSortRole(Qt.ItemDataRole.DisplayRole)
            
        # Call the parent sort method
        super().sort(column, order)

class MainWindow(QMainWindow):
    def __init__(self, language_manager, show_language_selector=False):
        super().__init__()
        self.language_manager = language_manager
        
        # Initialize UI
        self.setup_ui()
        
        # Setup the automatic update checker
        self.setup_update_checker()
    
    def update_progress(self, progress_dialog):
        """Create a callback function for updating progress
        
        Args:
            progress_dialog: The QProgressDialog to update
            
        Returns:
            Callback function that takes percentage value
        """
        def callback(percent):
            # Calculate percentage in the 80-100% range (since db save is 80-100%)
            value = 80 + int(percent * 0.2)
            progress_dialog.setValue(value)
            progress_dialog.setLabelText(f"{self.tr('Saving to database...')} {percent:.0f}%")
            
            # Process events to update UI
            QCoreApplication.processEvents()
            
            # Check if user canceled
            return not progress_dialog.wasCanceled()
        
        return callback
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.data_model = DataModel()
        self.sql_service = SQLService()
        
        # Initialize language manager
        if self.language_manager:
            self.language_manager = self.language_manager
        else:
            self.language_manager = LanguageManager()
            
        self.language_manager.language_changed.connect(self.retranslate_ui)
        
        # Setup the UI
        self.setWindowTitle(self.tr("MPR Separator"))
        self.setMinimumSize(1000, 700)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar with language selector
        self.setup_toolbar()
        
        # Create the import section
        self.setup_import_section()
        
        # Create the filter section
        self.setup_filter_section()
        
        # Create the data table
        self.setup_data_table()
        
        # Create the action buttons
        self.setup_action_buttons()
        
        # Show status message
        self.statusBar().showMessage(self.tr("Ready"))
    
    def setup_toolbar(self):
        """Create the toolbar with language selector"""
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)
        
        # Add language label
        language_label = QLabel(self.tr("Language") + ": ")
        language_label.setObjectName("language_label")
        toolbar.addWidget(language_label)
        
        # Add language selector
        self.language_selector = QComboBox()
        
        # Populate language selector
        available_languages = self.language_manager.get_available_languages()
        for code, name in available_languages.items():
            self.language_selector.addItem(name, code)
            
        # Set current language
        current_lang = self.language_manager.get_current_language()
        for i in range(self.language_selector.count()):
            if self.language_selector.itemData(i) == current_lang:
                self.language_selector.setCurrentIndex(i)
                break
        
        # Connect language change signal
        self.language_selector.currentIndexChanged.connect(self.on_language_changed)
        
        toolbar.addWidget(self.language_selector)
        toolbar.addSeparator()
    
    def on_language_changed(self, index):
        """Handle language change from dropdown"""
        if index < 0:
            return
            
        language_code = self.language_selector.itemData(index)
        current_language = self.language_manager.get_current_language()
        
        print(f"Language selected: {language_code}, Current language: {current_language}")
        
        if language_code != current_language:
            print(f"Changing language from {current_language} to {language_code}")
            success = self.language_manager.change_language(language_code)
            print(f"Language change result: {'Success' if success else 'Failed'}")
            
            # Debug translation file existence
            translation_file = Path(self.language_manager.translations_dir) / f"mpr_separator_{language_code}.qm"
            print(f"Translation file path: {translation_file}")
            print(f"Translation file exists: {translation_file.exists()}")
            print(f"Translation file size: {translation_file.stat().st_size if translation_file.exists() else 'N/A'}")
        else:
            print("No language change needed (same language)")
    
    def retranslate_ui(self, language_code=None):
        """Update all UI text with Portuguese translations"""
        print("Using Portuguese (Brazil) language")
        
        # Window title
        new_title = self.tr("MPR Separator")
        self.setWindowTitle(new_title)
        
        # Remove language selector UI components
        language_label = self.findChild(QLabel, "language_label")
        if language_label:
            language_label.hide()
            
        # If you have a language combo box, hide it too
        language_combo = self.findChild(QComboBox, "language_combo")
        if language_combo:
            language_combo.hide()
        
        # Update import section
        import_label = self.findChild(QLabel, "import_label")
        if import_label:
            import_label.setText(self.tr("Data Sources:"))
        self.import_button.setText(self.tr("Import File..."))
        
        # Update filter section
        filter_group = self.findChild(QGroupBox, "filter_group")
        if filter_group:
            filter_group.setTitle(self.tr("Search & Filter Database"))
            
        # Remove all translation settings for date controls and buttons
        # date_label = self.findChild(QLabel, "date_label")
        # if date_label:
        #     date_label.setText(self.tr("Date Range:"))
            
        # date_to_label = self.findChild(QLabel, "date_to_label")
        # if date_to_label:
        #     date_to_label.setText(self.tr("to"))
            
        # self.today_button.setText(self.tr("Today"))
        # self.week_button.setText(self.tr("Last 7 Days"))
        # self.month_button.setText(self.tr("Last 30 Days"))
        # self.all_button.setText(self.tr("All Dates"))
        
        # Keep the remaining translations
        order_label = self.findChild(QLabel, "order_label")
        if order_label:
            order_label.setText(self.tr("Order:"))
        self.order_edit.setPlaceholderText(self.tr("Filter by order number"))
        
        name_label = self.findChild(QLabel, "name_label")
        if name_label:
            name_label.setText(self.tr("Separator:"))
        self.name_edit.setPlaceholderText(self.tr("Filter by separator name"))
        
        # Remove ID label translation
        # id_label = self.findChild(QLabel, "id_label")
        # if id_label:
        #     id_label.setText(self.tr("ID:"))
        # self.id_edit.setPlaceholderText(self.tr("Find by record ID"))
        
        self.analysis_checkbox.setText(self.tr("Analysis Only"))
        
        self.search_button.setText(self.tr("Search Database"))
        # self.all_records_button.setText(self.tr("All Records"))  # Remove this line
        self.reset_button.setText(self.tr("Reset"))
        
        # Update table headers
        self.table_model.setHorizontalHeaderLabels([
            self.tr("Select"), 
            self.tr("Order Number"), 
            self.tr("Separator Name"), 
            self.tr("Date of Separation"), 
            self.tr("Analysis")
        ])
        
        # Update action buttons
        self.select_all_checkbox.setText(self.tr("Select All"))
        self.edit_selected_button.setText(self.tr("Edit Selected"))
        # The all_records_button was removed from the UI
        # The delete_selected_button is commented out in setup_action_buttons,
        # so we don't need to check for it here
        
        # Update status bar if it has message
        current_status = self.statusBar().currentMessage()
        if current_status:
            if "Ready" in current_status:
                self.statusBar().showMessage(self.tr("Ready"))
            # Other status messages could be added here if needed
    
    def setup_import_section(self):
        """Create the file import section"""
        import_layout = QHBoxLayout()
        
        import_label = QLabel(self.tr("Data Sources:"))
        import_label.setObjectName("import_label")
        self.import_button = QPushButton(self.tr("Import File..."))
        self.import_button.clicked.connect(self.import_file)
        
        import_layout.addWidget(import_label)
        import_layout.addWidget(self.import_button)
        import_layout.addStretch()
        
        self.main_layout.addLayout(import_layout)
    
    def setup_filter_section(self):
        """Create centralized filter controls"""
        filter_group = QGroupBox(self.tr("Search & Filter Database"))
        filter_group.setObjectName("filter_group")
        filter_layout = QVBoxLayout(filter_group)
        
        # Text filters
        text_layout = QHBoxLayout()
        
        # Order number filter
        order_label = QLabel(self.tr("Order:"))
        order_label.setObjectName("order_label")
        self.order_edit = QLineEdit()
        self.order_edit.setPlaceholderText(self.tr("Filter by order number"))
        self.order_edit.returnPressed.connect(self.search_database)
        
        # Separator name filter
        name_label = QLabel(self.tr("Separator:"))
        name_label.setObjectName("name_label")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(self.tr("Filter by separator name"))
        self.name_edit.returnPressed.connect(self.search_database)
        
        # Remove ID filter
        # id_label = QLabel(self.tr("ID:"))
        # id_label.setObjectName("id_label")
        # self.id_edit = QLineEdit()
        # self.id_edit.setPlaceholderText(self.tr("Find by record ID"))
        # self.id_edit.returnPressed.connect(self.search_database)
        
        # Analysis filter
        self.analysis_checkbox = QCheckBox(self.tr("Analysis Only"))
        
        text_layout.addWidget(order_label)
        text_layout.addWidget(self.order_edit)
        text_layout.addWidget(name_label)
        text_layout.addWidget(self.name_edit)
        # text_layout.addWidget(id_label)  # Remove ID label
        # text_layout.addWidget(self.id_edit)  # Remove ID edit field
        text_layout.addWidget(self.analysis_checkbox)
        
        # Button layout - keep just the reset button
        button_layout = QHBoxLayout()
        
        # Remove "All Records" button
        # self.all_records_button = QPushButton(self.tr("All Records"))
        # self.all_records_button.clicked.connect(self.search_all_records)
        # button_layout.addWidget(self.all_records_button)
        
        # Reset button 
        self.reset_button = QPushButton(self.tr("Reset"))
        self.reset_button.clicked.connect(self.reset_filters_and_results)
        
        button_layout.addWidget(self.reset_button)
        
        # Add layouts to the filter group
        filter_layout.addLayout(text_layout)
        filter_layout.addLayout(button_layout)
        
        self.main_layout.addWidget(filter_group)
        
        # Add these lines after creating all the input fields (after text_layout setup)
        # Connect Enter/Return key presses to trigger search
        self.order_edit.returnPressed.connect(self.search_database)
        self.name_edit.returnPressed.connect(self.search_database)
        # id_edit was removed from the UI
        
        # Date fields have been removed, so no need to install event filters for them
    
    def setup_data_table(self):
        """Create the data table view"""
        self.table_view = QTableView()
        
        # Use the custom sortable model
        self.table_model = SortableTableModel()
        
        # Create a proxy model for sorting
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        
        # Setup custom sorting
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        # Set headers for the table
        self.table_model.setHorizontalHeaderLabels([
            self.tr("Select"), 
            self.tr("Order Number"), 
            self.tr("Separator Name"), 
            self.tr("Date of Separation"), 
            self.tr("Analysis")
        ])
        
        # Set the proxy model to the view
        self.table_view.setModel(self.proxy_model)
        
        # Configure the header for sorting
        header = self.table_view.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)  # Default no sort
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Connect sorting signal
        header.sortIndicatorChanged.connect(self.on_sort_changed)
        
        # Enable sorting
        self.table_view.setSortingEnabled(True)
        
        # Make the select column narrower
        self.table_view.setColumnWidth(0, 50)
        
        # Disable direct editing of cells
        self.table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        
        # Enable row selection
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        
        # Connect double-click signal to open edit dialog
        self.table_view.doubleClicked.connect(self.handle_double_click)
        
        self.main_layout.addWidget(self.table_view)
    
    def setup_action_buttons(self):
        """Create the action buttons"""
        button_layout = QHBoxLayout()
        
        # Selection controls
        selection_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox(self.tr("Select All"))
        self.select_all_checkbox.toggled.connect(self.toggle_select_all)
        
        # Selected items actions
        self.edit_selected_button = QPushButton(self.tr("Edit Selected"))
        self.edit_selected_button.clicked.connect(self.edit_selected_records)
        
        # Add reset button here (moved from filter section)
        
        # Create search button
        self.search_button = QPushButton(self.tr("Search Database"))
        self.search_button.clicked.connect(self.search_database)
        
        # Add widgets to layouts
        selection_layout.addWidget(self.select_all_checkbox)
        selection_layout.addStretch()
        
        button_layout.addLayout(selection_layout)
        button_layout.addWidget(self.edit_selected_button)
        button_layout.addWidget(self.reset_button)  # Add the reset button here, next to Edit Selected
        button_layout.addWidget(self.search_button)
        
        self.main_layout.addLayout(button_layout)
    
    def import_file(self):
        """Import data from CSV or XLSX file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            self.tr("Select Data File"), 
            "", 
            self.tr("Data Files (*.csv *.xlsx);;All Files (*)")
        )
        
        if not file_path:
            return
        
        try:
            # Create progress dialog
            progress = QProgressDialog(self.tr("Reading file..."), self.tr("Cancel"), 0, 100, self)
            progress.setWindowTitle(self.tr("Importing Data"))
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setValue(0)
            progress.show()
            
            # Update progress - file reading (20%)
            progress.setValue(10)
            progress.setLabelText(self.tr("Reading file data..."))
            
            # Import data based on file extension
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            # Update progress - processing (40%)
            progress.setValue(40)
            progress.setLabelText(self.tr("Processing data..."))
            
            # Show preview dialog
            if progress.wasCanceled():
                return
                
            # Close progress during preview display
            progress.close()
            
            if self.show_import_preview(df, os.path.basename(file_path)):
                # Reopen progress dialog for saving
                progress = QProgressDialog(self.tr("Saving data..."), self.tr("Cancel"), 0, 100, self)
                progress.setWindowTitle(self.tr("Saving Data"))
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setValue(60)
                progress.show()
                
                # Process and validate data
                self.data_model.set_dataframe(df)
                
                # Update progress - saving (80%)
                progress.setValue(80)
                progress.setLabelText(self.tr("Saving to database..."))
                
                if progress.wasCanceled():
                    return
                    
                # Automatically save the imported data to the database
                try:
                    records_saved = self.sql_service.save_data(df, progress_callback=self.update_progress(progress))
                    
                    # Complete progress
                    progress.setValue(100)
                    progress.setLabelText(self.tr("Import complete"))
                    
                    self.statusBar().showMessage(f"{self.tr('Imported and saved')} {records_saved} {self.tr('records to database from')} {os.path.basename(file_path)}")
                    
                    # Refresh the view by performing a search to display what was saved
                    self.search_database()
                    
                    QMessageBox.information(
                        self, 
                        self.tr("Import Successful"), 
                        f"{self.tr('Successfully imported and saved')} {records_saved} {self.tr('records to the database.')}",
                    )
                    
                except Exception as e:
                    QMessageBox.warning(
                        self, 
                        self.tr("Save Warning"), 
                        f"{self.tr('Data was imported, but could not be saved to database:')} {str(e)}"
                    )
                    # Display data in the table without saving to DB
                    self.display_data()
                    self.statusBar().showMessage(f"{self.tr('Imported')} {len(df)} {self.tr('records from')} {os.path.basename(file_path)} {self.tr('(not saved to database)')}")
                
                finally:
                    progress.close()
    
        except Exception as e:
            QMessageBox.critical(
                self, 
                self.tr("Import Error"), 
                f"{self.tr('Failed to import data:')} {str(e)}"
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
                    # Store the original date for proper sorting
                    date_item = QStandardItem(date_str)
                    date_item.setData(date_obj.timestamp(), Qt.ItemDataRole.UserRole)
                except:
                    date_item = QStandardItem(date_str)
            else:
                date_item = QStandardItem(date_str)
            
            # Handle analysis boolean
            analysis_value = row.get('Analysis', False)
            analysis_item = QStandardItem()
            analysis_item.setCheckable(True)
            analysis_item.setCheckState(Qt.CheckState.Checked if analysis_value else Qt.CheckState.Unchecked)
            # Store a numeric value for sorting
            analysis_item.setData(1 if analysis_value else 0, Qt.ItemDataRole.UserRole)
            
            # Add the row to the table (without ID column)
            row_items = [select_item, order_item, name_item, date_item, analysis_item]
            self.table_model.appendRow(row_items)
        
        # Update status bar with record count
        record_count = len(df)
        self.statusBar().showMessage(f"Displaying {record_count} records")
        
        # Reset sort indicator
        self.table_view.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
    
    def set_today_filter(self):
        """Set date filter to today only - DEPRECATED"""
        # This method is kept for backwards compatibility
        # Date controls have been removed from the UI
        pass
    
    def set_week_filter(self):
        """Set date filter to last 7 days - DEPRECATED"""
        # This method is kept for backwards compatibility
        # Date controls have been removed from the UI
        pass
    
    def set_month_filter(self):
        """Set date filter to last 30 days - DEPRECATED"""
        # This method is kept for backwards compatibility
        # Date controls have been removed from the UI
        pass
    
    def clear_date_filter(self, and_search=False):
        """Clear date filter (set to all dates) - DEPRECATED"""
        # This method is kept for backwards compatibility
        # Date controls have been removed from the UI
        
        # Clear text filters too
        self.order_edit.clear()
        self.name_edit.clear()
        
        if and_search:
            self.search_database()
    def reset_filters(self):
        """Reset all filters to default"""
        # Reset text filters
        self.order_edit.clear()
        self.name_edit.clear()
        # id_edit was removed from the UI
        self.analysis_checkbox.setChecked(False)
    
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
            # If no rows are explicitly selected via checkboxes, 
            # check if there's a current row selected in the table
            selected_indexes = self.table_view.selectionModel().selectedRows()
            if selected_indexes:
                # Map proxy indexes to source model indexes
                source_rows = [self.proxy_model.mapToSource(idx).row() for idx in selected_indexes]
                self.open_edit_dialog(source_rows)
                return
        
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
        edit_dialog.setMinimumWidth(500)
        
        layout = QFormLayout(edit_dialog)
        
        # Add a note at the top of the dialog
        note_label = QLabel("Edit the fields below. Only changed fields will be updated.")
        note_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addRow(note_label)
        
        # Add a separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addRow(line)
        
        # Editable fields
        order_edit = QLineEdit()
        separator_edit = QLineEdit()
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        analysis_checkbox = QCheckBox()
        
        # Store original values to compare later
        original_values = {
            'OrderNumber': '',
            'SeparatorName': '',
            'DateOfSeparation': '',
            'Analysis': False
        }
        
        # If editing a single row, pre-fill the fields
        if len(rows) == 1:
            row = rows[0]
            order_number = self.table_model.item(row, 1).text()  # Order Number (column 1)
            separator_name = self.table_model.item(row, 2).text()  # Separator Name (column 2)
            
            # Date of separation
            date_str = self.table_model.item(row, 3).text()  # Date (column 3)
            try:
                # Try different date formats (both yyyy-MM-dd and dd-MM-yyyy)
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if not date.isValid():
                    date = QDate.fromString(date_str, "dd-MM-yyyy")
                
                if date.isValid():
                    date_edit.setDate(date)
                    original_values['DateOfSeparation'] = date_str
                else:
                    original_values['DateOfSeparation'] = ""
            except Exception:
                original_values['DateOfSeparation'] = ""
            
            # Analysis checkbox
            analysis_item = self.table_model.item(row, 4)  # Analysis (column 4)
            is_checked = analysis_item and analysis_item.checkState() == Qt.CheckState.Checked
            analysis_checkbox.setChecked(is_checked)
            
            # Set the text fields
            order_edit.setText(order_number)
            separator_edit.setText(separator_name)
            
            # Store original values
            original_values['OrderNumber'] = order_number
            original_values['SeparatorName'] = separator_name
            original_values['Analysis'] = is_checked
            
            # Show record ID if available (as read-only)
            order_item = self.table_model.item(row, 1)
            record_id = order_item.data(Qt.ItemDataRole.UserRole) if order_item else ""
            if record_id:
                id_display = QLineEdit(str(record_id))
                id_display.setReadOnly(True)
                id_display.setStyleSheet("background-color: #f0f0f0;")
                layout.addRow("Record ID:", id_display)
        else:
            # If editing multiple rows, show a message
            multi_edit_label = QLabel(f"Editing {len(rows)} records. Changes will apply to all selected records.")
            multi_edit_label.setStyleSheet("color: #007bff; font-weight: bold;")
            layout.addRow(multi_edit_label)
            
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
        
        # Set a nicer style for the dialog
        edit_dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit, QDateEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-height: 20px;
            }
            QPushButton {
                min-height: 25px;
                padding: 5px 15px;
            }
            QCheckBox {
                margin-left: 5px;
            }
        """)
        
        # Execute the dialog
        result = edit_dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Track only the fields that were changed
            updated_data = {}
            
            # Check what has changed and add only those fields
            new_order = order_edit.text()
            if new_order != original_values['OrderNumber']:
                updated_data['OrderNumber'] = new_order
                
            new_separator = separator_edit.text()
            if new_separator != original_values['SeparatorName']:
                updated_data['SeparatorName'] = new_separator
                
            new_date = date_edit.date().toString("yyyy-MM-dd")
            if new_date != original_values['DateOfSeparation']:
                updated_data['DateOfSeparation'] = new_date
                
            new_analysis = analysis_checkbox.isChecked()
            if new_analysis != original_values['Analysis']:
                updated_data['Analysis'] = new_analysis
            
            # Apply changes only if there are actual changes
            if updated_data:
                self.update_records(rows, updated_data)
            else:
                QMessageBox.information(
                    self,
                    "No Changes",
                    "No changes were made to the record(s)."
                )
    
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
                    
                # Update the DataFrame with new data (only changed fields)
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
            
            # Update the table view (only changed fields)
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
        """Search the database with filters"""
        try:
            # Get filter values
            order_number = self.order_edit.text().strip()
            separator_name = self.name_edit.text().strip()
            # record_id = self.id_edit.text().strip()  # Remove ID filter
            analysis_only = self.analysis_checkbox.isChecked()
            
            # Show loading indicator
            self.statusBar().showMessage(self.tr("Searching database..."))
            
            # Set default date range (last 7 days) if no filters are applied
            from_date = None
            to_date = None
            
            # Check if all filters are empty
            if not order_number and not separator_name and not analysis_only:
                # Use last 7 days as default
                to_date = datetime.now().strftime('%Y-%m-%d')
                from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                self.statusBar().showMessage(self.tr("Searching for records from the last 7 days..."))
            
            # Perform search without ID parameter
            result_df = self.sql_service.fetch_data(
                from_date=from_date,
                to_date=to_date,
                order_number=order_number,
                separator_name=separator_name,
                # record_id=record_id,  # Remove ID parameter
                analysis_only=analysis_only
            )
            
            # Update the data model and display the results
            self.data_model.set_dataframe(result_df)
            self.display_data()
            
            # Update status bar
            count = len(result_df) if result_df is not None else 0
            if from_date and to_date and not order_number and not separator_name and not analysis_only:
                self.statusBar().showMessage(self.tr(f"Found {count} records from the last 7 days"))
            else:
                self.statusBar().showMessage(self.tr(f"Found {count} records"))
            
        except Exception as e:
            self.statusBar().showMessage(self.tr("Error searching database"))
            QMessageBox.critical(
                self,
                self.tr("Search Error"),
                str(e)
            )

    def search_all_records(self):
        """Search for all records with no filters"""
        # Clear all filters first
        self.order_edit.clear()
        self.name_edit.clear()
        # self.id_edit was removed from the UI
        self.analysis_checkbox.setChecked(False)
        self.clear_date_filter()
        
        # Then search the database
        self.search_database()

    def on_sort_changed(self, column, order):
        """Handle changes in the sort indicator"""
        # Skip sorting for the checkbox column
        if column == 0:
            # Reset to no sorting
            self.table_view.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
            return
            
        # Apply the sort
        self.proxy_model.sort(column, order)
        
        # Update status message with the current sort
        column_names = [
            self.tr("Select"), 
            self.tr("Order Number"), 
            self.tr("Separator Name"), 
            self.tr("Date"), 
            self.tr("Analysis")
        ]
        order_text = self.tr("ascending") if order == Qt.SortOrder.AscendingOrder else self.tr("descending")
        if 0 <= column < len(column_names):
            self.statusBar().showMessage(f"{self.tr('Sorted by')} {column_names[column]} ({order_text})")

    def handle_double_click(self, index):
        """Handle double-click on a table cell by opening the edit dialog for that row"""
        # Get the source index from the proxy model
        source_idx = self.proxy_model.mapToSource(index)
        row = source_idx.row()
        
        # Check if the row is valid
        if row >= 0 and row < self.table_model.rowCount():
            # Open the edit dialog for this row
            self.open_edit_dialog([row])

    def tr(self, text):
        """Override the tr method to use our language manager's translation as fallback
        
        This ensures translations work even if the QM file isn't properly loaded
        """
        # Try Qt's translation system first
        qt_translation = super().tr(text)
        
        # If Qt didn't translate (returns the same text), use our fallback
        if qt_translation == text and hasattr(self, 'language_manager'):
            return self.language_manager.translate(text)
        
        return qt_translation

    def toggle_select_all(self, checked):
        """Toggle selection of all rows in the table"""
        for row in range(self.table_model.rowCount()):
            select_item = self.table_model.item(row, 0)
            if select_item:
                select_item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        
        # Update status message
        if checked:
            self.statusBar().showMessage(self.tr(f"Selected all {self.table_model.rowCount()} records"))
        else:
            self.statusBar().showMessage(self.tr("Cleared all selections"))
    
    def setup_update_checker(self):
        """Setup the automatic update checker"""
        self.updater = Updater(GITHUB_REPO, APP_VERSION)
        
        # Check if we just completed an update
        if self.updater.check_for_completed_update():
            QMessageBox.information(
                self,
                self.tr("Update Complete"),
                self.tr("MPR Separator has been successfully updated to version {0}").format(APP_VERSION)
            )
        
        # Schedule periodic update checks
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_for_updates)
        self.update_timer.start(3600000)  # Check every hour (3600000 ms)
        
        # Do an initial update check with a delay
        QTimer.singleShot(3000, self.check_for_updates)

    def check_for_updates(self):
        """Check for application updates"""
        try:
            update_available, latest_version, release_notes, release_info = self.updater.check_for_updates()
            
            if update_available:
                update_message = (
                    f"{self.tr('A new version of MPR Separator is available!')}\n\n"
                    f"{self.tr('Current version')}: {APP_VERSION}\n"
                    f"{self.tr('New version')}: {latest_version}\n\n"
                    f"{self.tr('Release notes')}:\n{release_notes}\n\n"
                    f"{self.tr('Would you like to download and install this update?')}"
                )
                
                reply = QMessageBox.question(
                    self,
                    self.tr("Update Available"),
                    update_message,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.download_and_install_update(release_info, latest_version)
        
        except Exception as e:
            # Silently handle errors to not disrupt the user experience
            print(f"Error in automatic update check: {str(e)}")

    def download_and_install_update(self, release_info, version_str):
        """Download and install the update"""
        # Create and configure the progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle(self.tr("Downloading Update"))
        progress_dialog.setMinimumWidth(400)
        progress_dialog.setModal(True)
        
        layout = QVBoxLayout(progress_dialog)
        
        # Add information about the update
        info_label = QLabel(f"{self.tr('Downloading MPR Separator')} {version_str}...")
        layout.addWidget(info_label)
        
        # Add progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        layout.addWidget(progress_bar)
        
        # Add cancel button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(progress_dialog.reject)
        layout.addWidget(button_box)
        
        # Show the dialog but don't block
        progress_dialog.show()
        
        # Update function for the progress callback
        def update_progress(progress):
            progress_bar.setValue(progress)
            if progress >= 100:
                progress_dialog.accept()
        
        # Start download in a separate thread
        download_thread = QThread()
        download_worker = UpdateDownloader(self.updater, release_info, version_str)
        download_worker.moveToThread(download_thread)
        
        # Connect signals
        download_thread.started.connect(download_worker.run)
        download_worker.progress.connect(update_progress)
        download_worker.finished.connect(download_thread.quit)
        download_worker.finished.connect(download_worker.deleteLater)
        download_thread.finished.connect(download_thread.deleteLater)
        download_thread.finished.connect(lambda: self.handle_download_complete(download_worker.success, 
                                                                           download_worker.file_path,
                                                                           version_str))
        
        # Start download
        download_thread.start()

    def handle_download_complete(self, success, file_path, version_str):
        """Handle the completion of the download"""
        if not success or not file_path:
            QMessageBox.warning(
                self,
                self.tr("Download Failed"),
                self.tr("Failed to download the update. Please try again later or download manually from the project website.")
            )
            return
        
        # Ask user to confirm installation
        reply = QMessageBox.question(
            self,
            self.tr("Install Update"),
            self.tr("The update has been downloaded. The application will close and the update will be installed. Continue?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Install the update
            self.updater.install_update(file_path, version_str)
            QApplication.quit()  # Close the application to allow the update to proceed

