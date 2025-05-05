# MPR Separator Translations

This directory contains translation files for the MPR Separator application.

## Structure

- `mpr_separator_*.ts` - Translation source files (XML format)
- `mpr_separator_*.qm` - Compiled translation files (binary format used at runtime)

## Supported Languages

- English (en) - Default language, no translation file needed
- Portuguese Brazil (pt_BR)

## How to Update Translations

1. Run the translation update tool:
   ```
   python tools/create_translations.py
   ```

2. This will update the .ts files with new translatable strings from the code.

3. Edit the .ts files with Qt Linguist or another translation editor to add or update translations.

4. Run the translation update tool again to compile the updated .ts files to .qm files.

## Adding a New Language

1. Create a new .ts file for your language using the following format:
   `mpr_separator_LANGUAGE_CODE.ts`

2. Add the new language to the `languages` dictionary in `tools/create_translations.py`.

3. Run the translation update tool to extract translatable strings.

4. Edit the new .ts file to add translations.

5. Run the translation update tool again to compile to .qm format.

6. Add the new language to the `languages` dictionary in `src/services/translator.py`.

## Manual Translation Process

If you can't use the automated tools:

1. Copy the existing .ts file as a template
2. Translate each `<translation>` element
3. Save with the correct language code
4. Compile manually with `lrelease`

## Notes for Translators

- Keep the original format specifiers (e.g., `{variable}`, `%s`, etc.)
- Don't translate technical terms unless there is a well-established translation
- Pay attention to context and screenshots if available 