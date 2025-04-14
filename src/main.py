import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main() -> None:
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Set a consistent style
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 