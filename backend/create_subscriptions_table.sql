-- =============================================
-- Subscriptions Table Creation Script
-- =============================================
-- This script creates the Subscriptions table for managing customer subscriptions
-- Run this in SQL Server Management Studio

USE SMP_DB;
GO

-- Drop tables in correct order (child first, then parent)
IF OBJECT_ID('dbo.SubscriptionOrderLines', 'U') IS NOT NULL
    DROP TABLE dbo.SubscriptionOrderLines;
GO

IF OBJECT_ID('dbo.Subscriptions', 'U') IS NOT NULL
    DROP TABLE dbo.Subscriptions;
GO

-- Create Subscriptions table
CREATE TABLE Subscriptions (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    SubscriptionNumber NVARCHAR(50) NOT NULL UNIQUE,
    
    -- Customer Information
    CustomerId UNIQUEIDENTIFIER NOT NULL,
    
    -- Subscription Details
    QuotationTemplate NVARCHAR(255) NULL,
    ExpirationDate DATE NOT NULL,
    OrderDate DATE NOT NULL DEFAULT GETDATE(), -- Added OrderDate
    RecurringPlan NVARCHAR(50) NOT NULL, -- Monthly, Yearly, Quarterly, Weekly
    PaymentTerm NVARCHAR(100) NULL,
    NextInvoiceDate DATE NULL, -- Added NextInvoiceDate
    
    -- Pricing
    TotalPrice DECIMAL(18,2) NOT NULL DEFAULT 0,
    
    -- Other Info
    Salesperson NVARCHAR(255) NULL,
    StartDate DATE NOT NULL,
    PaymentMethod NVARCHAR(100) NULL,
    PaymentDone BIT NOT NULL DEFAULT 0,
    
    -- Status
    Status NVARCHAR(50) NOT NULL DEFAULT 'Quotation', -- Quotation, QuotationSent, Confirmed, InProgress, Churned
    
    -- Audit Fields
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedAt DATETIME NOT NULL DEFAULT GETDATE(),
    IsActive BIT NOT NULL DEFAULT 1,
    
    -- Foreign Keys
    CONSTRAINT FK_Subscription_Customer FOREIGN KEY (CustomerId) REFERENCES Users(user_id) ON DELETE CASCADE,
    
    -- Check constraints
    CONSTRAINT CK_Subscription_Status CHECK (Status IN ('Quotation', 'QuotationSent', 'Confirmed', 'InProgress', 'Churned')),
    CONSTRAINT CK_Subscription_TotalPrice CHECK (TotalPrice >= 0)
);
GO

-- Create SubscriptionOrderLines table
CREATE TABLE SubscriptionOrderLines (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    SubscriptionId INT NOT NULL,
    ProductId INT NULL,
    ProductName NVARCHAR(255) NOT NULL,
    Quantity INT NOT NULL DEFAULT 1,
    UnitPrice DECIMAL(18,2) NOT NULL DEFAULT 0,
    Discount DECIMAL(5,2) NOT NULL DEFAULT 0, -- Percentage
    Taxes DECIMAL(5,2) NOT NULL DEFAULT 0, -- Percentage
    Amount DECIMAL(18,2) NOT NULL DEFAULT 0,
    
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedAt DATETIME NOT NULL DEFAULT GETDATE(),
    
    -- Foreign Keys
    CONSTRAINT FK_OrderLine_Subscription FOREIGN KEY (SubscriptionId) REFERENCES Subscriptions(Id) ON DELETE CASCADE,
    CONSTRAINT FK_OrderLine_Product FOREIGN KEY (ProductId) REFERENCES Products(Id) ON DELETE SET NULL,
    
    -- Check constraints
    CONSTRAINT CK_OrderLine_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_OrderLine_UnitPrice CHECK (UnitPrice >= 0),
    CONSTRAINT CK_OrderLine_Discount CHECK (Discount >= 0 AND Discount <= 100),
    CONSTRAINT CK_OrderLine_Taxes CHECK (Taxes >= 0),
    CONSTRAINT CK_OrderLine_Amount CHECK (Amount >= 0)
);
GO

-- Create indexes for better query performance
CREATE INDEX IX_Subscriptions_CustomerId ON Subscriptions(CustomerId);
CREATE INDEX IX_Subscriptions_Status ON Subscriptions(Status);
CREATE INDEX IX_Subscriptions_ExpirationDate ON Subscriptions(ExpirationDate);
CREATE INDEX IX_Subscriptions_StartDate ON Subscriptions(StartDate);
CREATE INDEX IX_SubscriptionOrderLines_SubscriptionId ON SubscriptionOrderLines(SubscriptionId);
CREATE INDEX IX_SubscriptionOrderLines_ProductId ON SubscriptionOrderLines(ProductId);
GO

-- Verify table creation
PRINT 'Subscriptions table structure:';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Subscriptions'
ORDER BY ORDINAL_POSITION;
GO

PRINT '';
PRINT 'SubscriptionOrderLines table structure:';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'SubscriptionOrderLines'
ORDER BY ORDINAL_POSITION;
GO

PRINT 'Subscriptions tables created successfully!';
GO
