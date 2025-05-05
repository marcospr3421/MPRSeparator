from PySide6.QtCore import QTranslator, QCoreApplication, QLocale, QObject, Signal
import os
from pathlib import Path

class LanguageManager(QObject):
    """Manages application language and translations"""
    
    language_changed = Signal(str)  # Signal emitted when language changes
    
    def __init__(self):
        super().__init__()
        self.translator = QTranslator()
        self.current_language = "en"  # Default language
        
        # Available languages
        self.languages = {
            "en": "English",
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
    
    def change_language(self, language_code):
        """Change the application language
        
        Args:
            language_code (str): Language code (e.g. 'en', 'pt_BR')
        
        Returns:
            bool: True if language was changed successfully
        """
        if language_code not in self.languages:
            print(f"Language code {language_code} not in available languages: {self.languages.keys()}")
            return False
            
        print(f"LanguageManager: Attempting to change language to {language_code}")
            
        # Remove previous translator if it exists
        QCoreApplication.removeTranslator(self.translator)
        print(f"LanguageManager: Removed previous translator")
        
        # Load the new translator
        if language_code != "en":  # English is the default, no translation needed
            translation_file = self.translations_dir / f"mpr_separator_{language_code}.qm"
            print(f"LanguageManager: Translation file path: {translation_file}")
            print(f"LanguageManager: File exists: {translation_file.exists()}")
            
            if translation_file.exists():
                print(f"LanguageManager: Loading translation file")
                success = self.translator.load(str(translation_file))
                print(f"LanguageManager: Translation file loaded: {success}")
                
                if not success:
                    print(f"LanguageManager: Failed to load translation file, using test translations")
                    # Even if loading fails, we'll proceed and use test translations
                else:
                    print(f"LanguageManager: Installing translator")
                    QCoreApplication.installTranslator(self.translator)
                    print(f"LanguageManager: Translator installed")
            else:
                print(f"LanguageManager: Translation file does not exist, using test translations")
        else:
            print(f"LanguageManager: English is default, no translation file needed")
        
        # Update current language
        self.current_language = language_code
        print(f"LanguageManager: Updated current language to {language_code}")
        
        # Emit signal that language has changed
        self.language_changed.emit(language_code)
        print(f"LanguageManager: Emitted language_changed signal")
        
        return True
    
    def get_available_languages(self):
        """Get list of available languages
        
        Returns:
            dict: Dictionary with language code as key and language name as value
        """
        return self.languages
    
    def get_current_language(self):
        """Get current language code
        
        Returns:
            str: Current language code
        """
        return self.current_language
        
    def translate(self, text):
        """Get translation for a string using our test translations if needed
        
        Returns: 
            str: Translated text
        """
        if self.current_language == "en":
            return text
            
        if self.current_language in self.test_translations and text in self.test_translations[self.current_language]:
            return self.test_translations[self.current_language][text]
            
        return text 