-- Script to remove any unique constraint on the SeparatorName column in SeparatorRecords table

-- First, identify any unique constraints or indexes on SeparatorName
DECLARE @ConstraintName NVARCHAR(255)
DECLARE @IndexName NVARCHAR(255)
DECLARE @SQL NVARCHAR(MAX)

-- Find constraints
SELECT @ConstraintName = con.name
FROM sys.key_constraints con
INNER JOIN sys.tables t ON con.parent_object_id = t.object_id
INNER JOIN sys.index_columns ic ON con.parent_object_id = ic.object_id AND con.unique_index_id = ic.index_id
INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE t.name = 'SeparatorRecords'
    AND c.name = 'SeparatorName'
    AND con.type = 'UQ';

-- Find unique indexes
SELECT @IndexName = i.name
FROM sys.indexes i
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
INNER JOIN sys.tables t ON i.object_id = t.object_id
WHERE t.name = 'SeparatorRecords' 
    AND c.name = 'SeparatorName'
    AND i.is_unique = 1
    AND i.is_primary_key = 0; -- exclude primary key

-- Drop constraint if found
IF @ConstraintName IS NOT NULL
BEGIN
    SET @SQL = 'ALTER TABLE SeparatorRecords DROP CONSTRAINT ' + QUOTENAME(@ConstraintName)
    PRINT 'Dropping constraint: ' + @ConstraintName
    EXEC sp_executesql @SQL
    PRINT 'Constraint dropped successfully.'
END
ELSE
    PRINT 'No unique constraint found on SeparatorName column.'

-- Drop index if found
IF @IndexName IS NOT NULL
BEGIN
    SET @SQL = 'DROP INDEX ' + QUOTENAME(@IndexName) + ' ON SeparatorRecords'
    PRINT 'Dropping index: ' + @IndexName
    EXEC sp_executesql @SQL
    PRINT 'Index dropped successfully.'
END
ELSE
    PRINT 'No unique index found on SeparatorName column.' 