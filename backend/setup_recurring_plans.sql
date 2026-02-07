USE [SMP_DB]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- 1. Create Recurring Plan Templates Table
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[RecurringPlanTemplates]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[RecurringPlanTemplates](
        [Id] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [PlanName] [nvarchar](100) NOT NULL,
        [DurationMonths] [int] NOT NULL, -- e.g., 1 for Monthly, 12 for Yearly
        [PriceMultiplier] [decimal](18, 2) NOT NULL DEFAULT ((1.00)), -- Multiplier of the base Sales Price
        [IsActive] [bit] DEFAULT ((1))
    );
    
    -- Insert Default Data
    INSERT INTO [dbo].[RecurringPlanTemplates] (PlanName, DurationMonths, PriceMultiplier)
    VALUES 
    ('Monthly', 1, 1.00),
    ('Quarterly', 3, 3.00),
    ('Yearly', 12, 12.00);

    PRINT 'RecurringPlanTemplates table created and populated.'
END
ELSE
BEGIN
    PRINT 'RecurringPlanTemplates table already exists.'
END
GO
