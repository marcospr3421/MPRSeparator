CREATE TABLE SeparatorRecords (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    OrderNumber NVARCHAR(100) NOT NULL,
    SeparatorName NVARCHAR(255) NOT NULL,
    DateOfSeparation DATE,
    Analysis BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE()
);