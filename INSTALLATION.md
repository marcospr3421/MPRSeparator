# MPRSeparator - Installation Guide

## System Requirements
- Windows 10 or later
- Minimum 4GB RAM (8GB recommended)
- 500MB free disk space

## Installation Instructions

1. Extract the ZIP file to any location on your computer.
2. Make sure all files remain in the same folder structure as extracted.
3. Double-click on "Run MPRSeparator.bat" to start the application.

## Database Connection

The application requires a SQL Server database connection. Make sure to:

1. Have a SQL Server instance available (local or remote)
2. Edit the `.env` file to configure your database connection settings:

```
DB_SERVER=your_server_name
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

## Troubleshooting

If you encounter any issues:

1. Ensure your database server is running and accessible
2. Verify your connection settings in the `.env` file
3. Make sure no antivirus software is blocking the application

For further assistance, please contact support.

## First-time Usage

When you run the application for the first time:

1. Click "Import File..." to import your CSV or Excel data
2. Use the search and filter options to find records
3. Double-click on any record to edit it

The application will automatically save imported data to the database. 