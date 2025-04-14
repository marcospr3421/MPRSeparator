-- Script to check for multi-column unique constraints that include SeparatorName

-- Find multi-column unique constraints
SELECT 
    con.name AS ConstraintName,
    STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS ConstraintColumns
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
    AND con.type = 'UQ'
GROUP BY
    con.name
HAVING
    MAX(CASE WHEN c.name = 'SeparatorName' THEN 1 ELSE 0 END) = 1;

-- Find multi-column unique indexes
SELECT 
    i.name AS IndexName,
    STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS IndexColumns
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
    AND i.is_unique = 1
    AND i.is_primary_key = 0
GROUP BY
    i.name
HAVING
    MAX(CASE WHEN c.name = 'SeparatorName' THEN 1 ELSE 0 END) = 1; 