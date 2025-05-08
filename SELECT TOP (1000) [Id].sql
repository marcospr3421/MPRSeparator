SELECT TOP (1000) [Id]
      ,[OrderNumber]
      ,[SeparatorName]
      ,[DateOfSeparation]
      ,[Analysis]
      ,[CreatedAt]
  FROM [dbo].[SeparatorRecords] order by DateOfSeparation desc