from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QProgressBar, QDialogButtonBox
from PySide6.QtCore import QThread
from src.services.update_worker import UpdateDownloader

class UpdateDownloader(QObject):
    """Worker class to download updates in a separate thread"""
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
                self.progress.emit
            )
            self.success = (self.file_path is not None)
        except Exception as e:
            print(f"Error in download thread: {str(e)}")
            self.success = False
        
        self.finished.emit()

    def setup_update_checker(self):
        """Set up the update checker UI elements"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        self.button_box = QDialogButtonBox()
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Skip")
        
        # Connect signals
        self.finished.connect(self.on_finished)
        self.progress.connect(self.update_progress)
        
    def on_finished(self):
        """Actions to perform when the download is finished"""
        if self.success:
            self.progress_bar.setValue(100)
            self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setEnabled(True)
        else:
            self.progress_bar.setValue(0)
            self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setEnabled(True)
            
    def update_progress(self, value):
        """Update the progress bar with the current download progress"""
        self.progress_bar.setValue(value)