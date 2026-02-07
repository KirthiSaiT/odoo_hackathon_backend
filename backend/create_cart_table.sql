-- =============================================
-- Shopping Cart Table Creation Script
-- =============================================
-- This script creates the Cart table for the shopping cart feature
-- Run this in SQL Server Management Studio

USE SMP_DB;
GO

-- Drop table if exists (for clean re-runs)
IF OBJECT_ID('dbo.Cart', 'U') IS NOT NULL
    DROP TABLE dbo.Cart;
GO

-- Create Cart table
CREATE TABLE Cart (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId UNIQUEIDENTIFIER NOT NULL,
    ProductId INT NOT NULL,
    Quantity INT NOT NULL DEFAULT 1,
    SelectedVariantId INT NULL,
    SelectedPlanName NVARCHAR(100) NULL,
    AddedAt DATETIME NOT NULL DEFAULT GETDATE(),
    
    -- Foreign Keys
    CONSTRAINT FK_Cart_User FOREIGN KEY (UserId) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT FK_Cart_Product FOREIGN KEY (ProductId) REFERENCES Products(Id) ON DELETE CASCADE,
    
    -- Unique constraint to prevent duplicate cart items
    -- Same user can't have same product with same variant/plan twice
    CONSTRAINT UQ_Cart_Item UNIQUE (UserId, ProductId, SelectedVariantId, SelectedPlanName),
    
    -- Check constraints
    CONSTRAINT CK_Cart_Quantity CHECK (Quantity > 0)
);
GO

-- Create indexes for better query performance
CREATE INDEX IX_Cart_UserId ON Cart(UserId);
CREATE INDEX IX_Cart_ProductId ON Cart(ProductId);
GO

-- Verify table creation
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Cart'
ORDER BY ORDINAL_POSITION;
GO

PRINT 'Cart table created successfully!';
GO
