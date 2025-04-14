-- Check if there are any unique indexes on SeparatorName column
DECLARE @IndexName NVARCHAR(255)

-- Find all unique indexes on the SeparatorName column
SELECT 
    i.name AS IndexName
FROM 
    sys.indexes i
INNER JOIN 
    sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN 
    sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
INNER JOIN 
    sys.tables t ON i.object_id = t.object_id
WHERE 
    t.name = 'SeparatorRecords' 
    AND c.name = 'SeparatorName'
    AND i.is_unique = 1;

-- If a unique index exists, drop it (run this part manually after identifying the index)
-- DROP INDEX [IndexName] ON [dbo].[SeparatorRecords];

-- Check if there are any unique constraints on SeparatorName
SELECT 
    con.name AS ConstraintName
FROM 
    sys.key_constraints con
INNER JOIN 
    sys.tables t ON con.parent_object_id = t.object_id
INNER JOIN 
    sys.index_columns ic ON con.parent_object_id = ic.object_id AND con.unique_index_id = ic.index_id
INNER JOIN 
    sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE 
    t.name = 'SeparatorRecords'
    AND c.name = 'SeparatorName'
    AND con.type = 'UQ';

-- If a unique constraint exists, drop it (run this part manually after identifying the constraint)
-- ALTER TABLE [dbo].[SeparatorRecords] DROP CONSTRAINT [ConstraintName]; 