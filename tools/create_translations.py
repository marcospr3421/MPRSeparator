#!/usr/bin/env python
"""
Translation File Creator for MPR Separator

This script helps create and update translation files for the MPR Separator application.
It works by extracting translatable strings from the source code and updating the .ts files,
which can then be compiled to .qm files for use at runtime.

Usage:
    python create_translations.py

Requirements:
    - PyQt6 or PySide6 with lupdate and lrelease tools
    - Python 3.6+
"""

import os
import sys
import subprocess
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
translations_dir = project_root / "translations"

# Make sure directories exist
os.makedirs(translations_dir, exist_ok=True)

def find_executable(name):
    """Find executable in system PATH"""
    # Determine executable extension based on OS
    ext = '.exe' if sys.platform == 'win32' else ''
    
    # Try different prefixes (pyside, pyqt)
    prefixes = ['', 'pyside6-', 'pyside2-', 'pyqt6-', 'pyqt5-']
    
    for prefix in prefixes:
        # Check if executable exists in PATH
        for path in os.environ["PATH"].split(os.pathsep):
            exe_path = os.path.join(path, f"{prefix}{name}{ext}")
            if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                return exe_path
    
    return None

def update_translations():
    """Update translation files from source code"""
    lupdate = find_executable('lupdate')
    lrelease = find_executable('lrelease')
    
    if not lupdate or not lrelease:
        print("Error: Could not find lupdate and lrelease executables.")
        print("Please install PyQt6 or PySide6 tools.")
        sys.exit(1)
    
    # Define supported languages
    languages = {
        'pt_BR': 'Portuguese (Brazil)',
    }
    
    # Process each language
    for lang_code, lang_name in languages.items():
        ts_file = translations_dir / f"mpr_separator_{lang_code}.ts"
        qm_file = translations_dir / f"mpr_separator_{lang_code}.qm"
        
        # Check if .ts file exists, create it if not
        if not ts_file.exists():
            print(f"Creating new .ts file for {lang_name}...")
            with open(ts_file, 'w', encoding='utf-8') as f:
                f.write(f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="{lang_code}" sourcelanguage="en">
</TS>''')
        
        # Update .ts file from source code
        print(f"Updating translations for {lang_name}...")
        cmd = [lupdate, "-recursive", str(src_dir), "-ts", str(ts_file)]
        subprocess.run(cmd, check=True)
        
        # Compile .ts file to .qm file
        print(f"Compiling translations for {lang_name}...")
        cmd = [lrelease, str(ts_file), "-qm", str(qm_file)]
        subprocess.run(cmd, check=True)
    
    print("\nTranslation files updated successfully.")
    print(f"Translation files are located in: {translations_dir}")

if __name__ == "__main__":
    try:
        update_translations()
    except Exception as e:
        print(f"Error updating translations: {e}")
        sys.exit(1) 