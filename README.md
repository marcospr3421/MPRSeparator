# MPR Separator

A desktop application for managing separator data, importing from CSV/XLSX files, and storing in a Microsoft SQL Server database with Azure Key Vault authentication.

## Features

- Import data from CSV or XLSX files
- Filter data by various criteria (date range, order number, separator name, analysis status)
- Default filter to show only last 7 days of data for faster loading
- Save data to Microsoft SQL Server
- Secure database authentication using Azure Key Vault

## Requirements

- Python 3.8+
- Microsoft ODBC Driver 17 for SQL Server
- Azure account with Key Vault configured
- SQL Server database

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file from the sample:
   ```
   copy .env.sample .env
   ```
6. Edit the `.env` file with your Azure Key Vault and database settings

## Setting up Azure Key Vault

1. Create an Azure Key Vault in your Azure subscription
2. Create two secrets:
   - `mpr-separator-db-username`: Your database username
   - `mpr-separator-db-password`: Your database password
3. Ensure your application has access to the Key Vault (using Azure AD authentication)
4. Update the `.env` file with your Key Vault URL

## Database Schema

Create the following table in your SQL Server database:

```sql
CREATE TABLE SeparatorRecords (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    OrderNumber NVARCHAR(100) NOT NULL,
    SeparatorName NVARCHAR(255) NOT NULL,
    DateOfSeparation DATE,
    Analysis BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE()
);
```

## Usage

1. Start the application:
   ```
   python src/main.py
   ```
2. Click "Browse Files..." to import a CSV or XLSX file
3. Use the "Filter Data" button to open the filter window
4. After reviewing the data, click "Save to Database" to store the records

## Data Format

Your CSV or XLSX file should contain the following columns (case insensitive):
- OrderNumber (required): The order number
- SeparatorName (required): The name of the separator
- DateOfSeparation: The date of separation (any recognizable date format)
- Analysis: Boolean value (1/0, Yes/No, True/False) indicating if analysis was done 