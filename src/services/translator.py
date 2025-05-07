from PySide6.QtCore import QTranslator, QCoreApplication, QLocale, QObject, Signal
import os
from pathlib import Path

class LanguageManager(QObject):
    """Manages application language and translations"""
    
    language_changed = Signal(str)  # Signal kept for compatibility
    
    def __init__(self):
        super().__init__()
        self.translator = QTranslator()
        self.current_language = "pt_BR"  # Always use Portuguese (Brazil)
        
        # Only keep Portuguese
        self.languages = {
            "pt_BR": "Português (Brasil)"
        }
        
        # Test translations - for testing when QM files aren't working
        self.test_translations = {
            "pt_BR": {
                "MPR Separator": "MPR Separator PT",
                "Language": "Idioma",
                "Data Sources:": "Fontes de Dados:",
                "Import File...": "Importar Arquivo...",
                "Search & Filter Database": "Pesquisar & Filtrar Banco de Dados",
                "Date Range:": "Período:",
                "to": "até",
                "Today": "Hoje",
                "Last 7 Days": "Últimos 7 Dias",
                "Last 30 Days": "Últimos 30 Dias",
                "All Dates": "Todas as Datas",
                "Order:": "Pedido:",
                "Separator:": "Separador:",
                "ID:": "ID:",
                "Analysis Only": "Apenas Análise",
                "Search Database": "Pesquisar Banco de Dados", 
                "All Records": "Todos os Registros",
                "Reset": "Redefinir",
                "Ready": "Pronto"
            }
        }
        
        # Find the translations directory
        self.translations_dir = Path(__file__).parent.parent.parent / "translations"
        if not self.translations_dir.exists():
            os.makedirs(self.translations_dir, exist_ok=True)
            
        # Initialize with Portuguese
        self._load_portuguese()
        
    def _load_portuguese(self):
        """Load Portuguese language"""
        # Remove previous translator if it exists
        QCoreApplication.removeTranslator(self.translator)
        
        # Load the Portuguese translator
        translation_file = self.translations_dir / "mpr_separator_pt_BR.qm"
        
        if translation_file.exists():
            success = self.translator.load(str(translation_file))
            if success:
                QCoreApplication.installTranslator(self.translator)
            # If loading fails, we'll use test translations
        # If file doesn't exist, we'll use test translations
        
    # Methods below kept for compatibility, but simplified
    def change_language(self, language_code=None):
        """Always returns Portuguese"""
        return True
    
    def get_available_languages(self):
        """Get list of available languages"""
        return self.languages
    
    def get_current_language(self):
        """Get current language code"""
        return "pt_BR"
        
    def translate(self, text):
        """Get translation for a string using our test translations if needed"""
        if text in self.test_translations["pt_BR"]:
            return self.test_translations["pt_BR"][text]
            
        return text