UPDATE SeparatorRecords
SET DateOfSeparation = '2025-04-23'
WHERE DateOfSeparation BETWEEN '2025-04-24' AND GETDATE();