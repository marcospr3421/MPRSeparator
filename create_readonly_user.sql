-- SQL Script to create a read-only user in Azure SQL Database
-- Replace 'readonlyuser' and 'StrongPassword123!' with your desired username and password

-- 1. Create a new database user
CREATE USER lucascardoso WITH PASSWORD = 'Zaqmko21@';

-- 2. Grant the user read-only access to the database
-- This uses the built-in db_datareader role which allows SELECT permissions on all tables
EXEC sp_addrolemember 'db_datareader', 'lucascardoso';

-- 3. Grant CONNECT permission to the database
GRANT CONNECT TO lucascardoso;

-- Verify the user has been created and has appropriate permissions
-- Run this after creating the user
SELECT name, type_desc, create_date, modify_date
FROM sys.database_principals
WHERE name = 'lucascardoso';

-- Verify role membership
SELECT DP1.name AS DatabaseRoleName, DP2.name AS DatabaseUserName
FROM sys.database_role_members AS DRM
JOIN sys.database_principals AS DP1 ON DRM.role_principal_id = DP1.principal_id
JOIN sys.database_principals AS DP2 ON DRM.member_principal_id = DP2.principal_id
WHERE DP2.name = 'lucascardoso'; 