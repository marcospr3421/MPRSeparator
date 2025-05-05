#!/usr/bin/env python
"""
Qt Translation Generator

This script creates a basic Qt binary translation file (.qm) for testing.
It uses a very simple approach by creating a text-based translation file (.ts)
and then compiling it using Python's QTranslator if available.

Usage:
    python create_qt_translation.py
"""

import os
import sys
from pathlib import Path

# Translations directory
translations_dir = Path("translations")
os.makedirs(translations_dir, exist_ok=True)

# Create a minimal TS file with one message
ts_content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="pt_BR" sourcelanguage="en">
<context>
    <name>MainWindow</name>
    <message>
        <source>MPR Separator</source>
        <translation>MPR Separator PT</translation>
    </message>
    <message>
        <source>Language</source>
        <translation>Idioma</translation>
    </message>
    <message>
        <source>Data Sources:</source>
        <translation>Fontes de Dados:</translation>
    </message>
    <message>
        <source>Ready</source>
        <translation>Pronto</translation>
    </message>
</context>
</TS>
"""

# Write the TS file
ts_file = translations_dir / "simple_pt_BR.ts"
with open(ts_file, 'w', encoding='utf-8') as f:
    f.write(ts_content)
    
print(f"Created TS file: {ts_file}")

# Try to compile using Qt
try:
    from PySide6.QtCore import QTranslator, QLocale
    from PySide6.QtWidgets import QApplication
    
    print("Using Qt tools for compilation")
    # Need to initialize app for Qt to work
    app = QApplication([])
    
    # Create translator
    translator = QTranslator()
    
    # Load the TS file
    if translator.load(str(ts_file)):
        print("TS file loaded successfully")
        
        # Copy our simple TS to the actual Portuguese file
        target_ts = translations_dir / "mpr_separator_pt_BR.ts"
        with open(target_ts, 'w', encoding='utf-8') as f:
            f.write(ts_content)
            
        print(f"Updated {target_ts}")
        
        # Try to make Qt generate the QM file
        qm_file = translations_dir / "mpr_separator_pt_BR.qm"
        
        # Directly create QM file
        # This approach might work if Qt's internals allow QM files to be read from memory
        print(f"Attempting to create QM file at {qm_file}")
        with open(qm_file, 'wb') as f:
            # Create minimal header
            f.write(b'\x3C\xB8\x64\x18\x01\x00\x00\x00')
            # Add 16 more bytes of zeros to make Qt happy
            f.write(b'\x00' * 16)
            
        print(f"Created basic QM file at {qm_file}")
        print("You may need to use actual Qt tools like lrelease for full functionality")
    else:
        print("Failed to load TS file")
        
except ImportError:
    print("PySide6 not available, can't compile QM file")
    print("Please use Qt's lrelease tool to compile the TS file to QM format")

print("Done.") 