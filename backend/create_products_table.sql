USE [SMP_DB]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- 1. Create Products Table
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Products]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Products](
        [Id] [int] IDENTITY(1,1) NOT NULL,
        [Name] [nvarchar](255) NOT NULL,
        [ProductType] [nvarchar](50) NOT NULL, -- 'Storable Product', 'Consumable', 'Service'
        [SalesPrice] [decimal](18, 2) NULL DEFAULT ((0.00)),
        [CostPrice] [decimal](18, 2) NULL DEFAULT ((0.00)),
        [Tax] [nvarchar](50) NULL,
        [CreatedByEmployeeId] [int] NULL,
        [CreatedAt] [datetime2](7) NULL DEFAULT (sysdatetime()),
        [ModifiedAt] [datetime2](7) NULL,
        [IsActive] [bit] NULL DEFAULT ((1)),
    PRIMARY KEY CLUSTERED 
    (
        [Id] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
    ) ON [PRIMARY]

    -- Add Foreign Key to Link to Employees
    ALTER TABLE [dbo].[Products]  WITH CHECK ADD  CONSTRAINT [FK_Products_Employees] FOREIGN KEY([CreatedByEmployeeId])
    REFERENCES [dbo].[Employees] ([Id])

    ALTER TABLE [dbo].[Products] CHECK CONSTRAINT [FK_Products_Employees]

    PRINT 'Products table created successfully.'
END
ELSE
BEGIN
    PRINT 'Products table already exists.'
END
GO

-- =============================================
-- 2. Create Recurring Plans Table
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ProductRecurringPlans]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[ProductRecurringPlans](
        [Id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [ProductId] [int] NOT NULL,
        [PlanName] [nvarchar](100) NULL,
        [Price] [decimal](18, 2) NULL,
        [MinQty] [int] NULL DEFAULT ((1)),
        [StartDate] [date] NULL,
        [EndDate] [date] NULL
    );

    ALTER TABLE [dbo].[ProductRecurringPlans]  WITH CHECK ADD  CONSTRAINT [FK_ProductRecurringPlans_Products] FOREIGN KEY([ProductId])
    REFERENCES [dbo].[Products] ([Id])
    ON DELETE CASCADE

    PRINT 'ProductRecurringPlans table created successfully.'
END
GO

-- =============================================
-- 3. Create Variants Table
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ProductVariants]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[ProductVariants](
        [Id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [ProductId] [int] NOT NULL,
        [Attribute] [nvarchar](100) NULL,
        [Value] [nvarchar](100) NULL,
        [ExtraPrice] [decimal](18, 2) NULL DEFAULT ((0.00))
    );

    ALTER TABLE [dbo].[ProductVariants]  WITH CHECK ADD  CONSTRAINT [FK_ProductVariants_Products] FOREIGN KEY([ProductId])
    REFERENCES [dbo].[Products] ([Id])
    ON DELETE CASCADE

    PRINT 'ProductVariants table created successfully.'
END
GO

-- =============================================
-- 4. Create Stored Procedure to Insert Product
-- =============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SP_CreateProduct]') AND type in (N'P', N'PC'))
DROP PROCEDURE [dbo].[SP_CreateProduct]
GO

CREATE PROCEDURE [dbo].[SP_CreateProduct]
    @Name NVARCHAR(255),
    @ProductType NVARCHAR(50),
    @SalesPrice DECIMAL(18, 2),
    @CostPrice DECIMAL(18, 2),
    @Tax NVARCHAR(50),
    @UserId UNIQUEIDENTIFIER -- From the logged-in user credential
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @EmployeeId INT;

    -- Fetch the Employee ID associated with the User ID
    SELECT @EmployeeId = [Id]
    FROM [dbo].[Employees]
    WHERE [UserId] = @UserId;

    -- Insert Protocol
    INSERT INTO [dbo].[Products] (
        [Name], 
        [ProductType], 
        [SalesPrice], 
        [CostPrice], 
        [Tax], 
        [CreatedByEmployeeId], 
        [CreatedAt], 
        [IsActive]
    )
    VALUES (
        @Name, 
        @ProductType, 
        @SalesPrice, 
        @CostPrice, 
        @Tax, 
        @EmployeeId, -- This maps the user credential to the employee
        SYSDATETIME(), 
        1
    );

    -- Return the newly created Product ID
    SELECT SCOPE_IDENTITY() AS [ProductId];
END
GO
