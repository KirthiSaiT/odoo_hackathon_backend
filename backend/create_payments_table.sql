-- =============================================
-- Payments Table Creation Script
-- =============================================
USE SMP_DB;
GO

IF OBJECT_ID('dbo.Payments', 'U') IS NOT NULL
    DROP TABLE dbo.Payments;
GO

CREATE TABLE Payments (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId NVARCHAR(255) NOT NULL, -- Changed to NVARCHAR to match Users.user_id/Orders.UserId
    OrderId INT NULL, -- Can be null initially if payment starts before order creation, or linked later
    StripePaymentIntentId NVARCHAR(255) NULL,
    Amount DECIMAL(18,2) NOT NULL,
    Currency NVARCHAR(10) NOT NULL DEFAULT 'INR',
    Status NVARCHAR(50) NOT NULL DEFAULT 'Pending', -- Pending, Processing, Succeeded, Failed
    PaymentMethod NVARCHAR(50) NULL,
    CreatedAt DATETIME DEFAULT GETDATE(),
    ModifiedAt DATETIME DEFAULT GETDATE(),
    
    -- Foreign Keys
    -- Note: Users.user_id is NVARCHAR, so UserId here must match
    -- CONSTRAINT FK_Payment_User FOREIGN KEY (UserId) REFERENCES Users(user_id), 
    -- CONSTRAINT FK_Payment_Order FOREIGN KEY (OrderId) REFERENCES Orders(Id)
);
GO

-- Create Indexes
CREATE INDEX IX_Payments_UserId ON Payments(UserId);
CREATE INDEX IX_Payments_OrderId ON Payments(OrderId);
CREATE INDEX IX_Payments_StripePaymentIntentId ON Payments(StripePaymentIntentId);
GO

PRINT 'Payments table created successfully.';
GO
