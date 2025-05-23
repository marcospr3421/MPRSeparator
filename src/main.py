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
from PySide6.QtCore import QTranslator, QLocale
from src.ui.main_window import MainWindow
from src.services.translator import LanguageManager

def main() -> None:
    """Main entry point for the application."""
    # Initialize the application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Set a consistent style
    
    # Print debug information
    print(f"Application directory: {project_root}")
    print(f"Translation directory: {project_root / 'translations'}")
    
    # Create language manager with fixed Portuguese language
    language_manager = LanguageManager()
    
    # Install translator at the application level with Portuguese only
    app.installTranslator(language_manager.translator)
    
    # Create and show the main window, disabling language selection UI
    window = MainWindow(language_manager, show_language_selector=False)
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()