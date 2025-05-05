#!/usr/bin/env python
"""
Simple script to create a functioning QM file for testing translations
"""

import os
import struct
from pathlib import Path
import xml.etree.ElementTree as ET

# Path to your .ts file
ts_file = Path("translations/mpr_separator_pt_BR.ts")
# Path to the QM file that will be created
qm_file = Path("translations/mpr_separator_pt_BR.qm")

print(f"Reading from: {ts_file.absolute()}")
print(f"Writing to: {qm_file.absolute()}")

# Parse the TS file to extract some translations
try:
    tree = ET.parse(ts_file)
    root = tree.getroot()
    print(f"Successfully parsed TS file")
    
    # Find the first translation to use as a test
    first_source = None
    first_translation = None
    
    for message in root.findall(".//message"):
        source = message.find("source")
        translation = message.find("translation")
        
        if source is not None and translation is not None and source.text and translation.text:
            first_source = source.text
            first_translation = translation.text
            print(f"Found test translation: '{first_source}' -> '{first_translation}'")
            break
    
    if not first_source or not first_translation:
        print("Warning: No valid translation found in the TS file")
        first_source = "Test"
        first_translation = "Teste"
        
except Exception as e:
    print(f"Error parsing TS file: {e}")
    print("Using default test translation")
    first_source = "Test"
    first_translation = "Teste"

# Create a minimal valid QM file for testing
with open(qm_file, 'wb') as f:
    # QM file signature and format version (1)
    f.write(b'\x3C\xB8\x64\x18\x01\x00\x00\x00')
    
    # Write a single hardcoded translation for testing (simplistic)
    # In a real QM file, there would be much more structure,
    # but this minimal approach can help test if the infrastructure works
    
    # String length for source (4 bytes)
    f.write(struct.pack('!I', len(first_source)))
    # Source string
    f.write(first_source.encode('utf-8'))
    
    # String length for translation (4 bytes)
    f.write(struct.pack('!I', len(first_translation)))
    # Translation string
    f.write(first_translation.encode('utf-8'))
    
    # Write footer/end marker
    f.write(b'\x00\x00\x00\x00')

print(f"Created a basic QM file at {qm_file.absolute()}")
print(f"Test translation: '{first_source}' -> '{first_translation}'")
print("This is a minimal QM file for testing. For production use Qt tools.")
print("Done.") 