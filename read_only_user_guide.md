# Creating a Read-Only User for Your Azure SQL Database

This guide will help you create a new user with read-only access to your Azure SQL Database.

## Step 1: Connect to Your Azure SQL Database

You'll need to connect to your Azure SQL Database using a user account that has administrative privileges. You can do this through:

- **Azure Data Studio**
- **SQL Server Management Studio (SSMS)**
- **Azure Portal's Query Editor**

## Step 2: Execute the SQL Script

1. Open the `create_readonly_user.sql` script in your SQL editor
2. Modify the username and password in the script (replace `readonlyuser` and `StrongPassword123!`)
3. Execute the script against your `mprDB02` database

The script will:
- Create a new user
- Grant the user membership in the `db_datareader` role
- Grant CONNECT permission to the database
- Verify the user creation and permissions

## Step 3: Test the Connection

After creating the user, you can test the connection using the Python script provided:

1. Ensure that you have the ODBC Driver 17 for SQL Server installed
2. Open the `test_readonly_connection.py` script
3. Update the credentials if you changed the username/password
4. Run the script:

```
python test_readonly_connection.py
```

The script will:
- Connect to the database using the read-only user
- Attempt to read data from the `SeparatorRecords` table
- Attempt an INSERT operation (which should fail, confirming read-only status)

## Step 4: Update Your Application

To use this read-only user in your application:

1. Create a new `.env.readonly` file with the read-only credentials
2. Update your connection code to use these credentials when read-only access is needed

Example `.env.readonly` content:
```
DB_SERVER=mprsqlserver.database.windows.net
DB_NAME=mprDB02
DB_USERNAME=readonlyuser
DB_PASSWORD=StrongPassword123!
DB_TABLE=SeparatorRecords
```

## Security Recommendations

1. Use a strong, unique password for the read-only user
2. Consider using Azure Key Vault to store the credentials
3. Limit the IP addresses that can connect using this user through Azure SQL firewall rules
4. Regularly rotate the password
5. Monitor for suspicious login attempts

## Troubleshooting

If you encounter issues:

1. Verify that the user was created successfully using the verification queries in the SQL script
2. Check if the user has the correct permissions
3. Ensure the server's firewall allows connections from your IP address
4. Verify that the connection string is correct 