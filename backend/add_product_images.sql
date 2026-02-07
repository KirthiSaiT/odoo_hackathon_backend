USE [SMP_DB]
GO

-- 1. Add MainImage column to Products table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[Products]') AND name = 'MainImage')
BEGIN
    ALTER TABLE [dbo].[Products]
    ADD [MainImage] NVARCHAR(MAX) NULL;
    PRINT 'MainImage column added to Products table.';
END
ELSE
BEGIN
    PRINT 'MainImage column already exists in Products table.';
END
GO

-- 2. Create ProductSubImages table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ProductSubImages]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[ProductSubImages](
        [Id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [ProductId] [int] NOT NULL,
        [ImageURL] [nvarchar](MAX) NOT NULL
    );

    ALTER TABLE [dbo].[ProductSubImages]  WITH CHECK ADD  CONSTRAINT [FK_ProductSubImages_Products] FOREIGN KEY([ProductId])
    REFERENCES [dbo].[Products] ([Id])
    ON DELETE CASCADE;

    PRINT 'ProductSubImages table created successfully.';
END
ELSE
BEGIN
    PRINT 'ProductSubImages table already exists.';
END
GO
