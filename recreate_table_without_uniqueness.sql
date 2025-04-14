-- Script to recreate SeparatorRecords table without uniqueness constraints on SeparatorName

-- First, back up existing data to a temporary table
SELECT * INTO #TempSeparatorRecords FROM SeparatorRecords;

-- Drop the existing table
DROP TABLE SeparatorRecords;

-- Create a new table without uniqueness constraints
CREATE TABLE SeparatorRecords (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    OrderNumber NVARCHAR(100) NOT NULL,
    SeparatorName NVARCHAR(255) NOT NULL,  -- No unique constraint here
    DateOfSeparation DATE,
    Analysis BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE()
);

-- Re-insert the data from the temporary table
-- Note: This will only maintain the OrderNumber, SeparatorName, DateOfSeparation, and Analysis columns
INSERT INTO SeparatorRecords (OrderNumber, SeparatorName, DateOfSeparation, Analysis)
SELECT OrderNumber, SeparatorName, DateOfSeparation, Analysis 
FROM #TempSeparatorRecords;

-- Drop the temporary table
DROP TABLE #TempSeparatorRecords;

-- Print results
PRINT 'SeparatorRecords table has been recreated without uniqueness constraints on SeparatorName.';
SELECT COUNT(*) AS RecordCount FROM SeparatorRecords; 