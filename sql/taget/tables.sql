-- Generated SQL Server DDL. Run in the intended database context.
SET NOCOUNT ON;
GO

CREATE TABLE dbo.bank (
    bank_id INT NOT NULL,
    bank_code NVARCHAR(10) NULL,
    bank_name NVARCHAR(200) NULL,
    swift_code NVARCHAR(20) NULL,
    is_active TINYINT NULL ,
    created_at DATETIME NULL ,
    insert_time2 DATETIME NULL
);
GO

CREATE TABLE dbo.bransh (
    BRANCH_ID INT NOT NULL,
    bransh_name NVARCHAR(300) NULL,
    city NVARCHAR(100) NULL,
    address NVARCHAR(500) NULL,
    is_active TINYINT NULL ,
    created_at DATETIME NULL ,
        insert_time2 DATETIME NULL

);
GO

CREATE TABLE dbo.coding (
    coding_id INT NOT NULL,
    coding_type NVARCHAR(50) NULL,
    code NVARCHAR(20) NULL,
    description NVARCHAR(300) NULL,
    parent_id INT NULL,
    is_active TINYINT NULL ,
    created_at DATETIME NULL ,
    CODING_DATE_ID INT NULL,
    NEW_FISHE_TYPE_CODING INT NULL,
    CIRCULAR_CODING_ID INT NULL,
    EXCHANGE_RATE_TYPE_CODING_ID INT NULL,
    FISH_CURRENCY_CODING_ID INT NULL,
    NEW_TRADING_TYPE_CODING_ID INT NULL,
    NEW_GUARANTOR_TYPE_CODING_ID INT NULL,
    NEW_TERM_TYPE_CODING_ID INT NULL,
    NEW_LOAN_LOCATION_CODING_ID INT NULL,
    NEW_FOREIGN_EXCHANGE_LOCATION_CODING_ID INT NULL,
    NEW_EXCHANGE_RATE_TYPE_CODING_ID INT NULL,
    PRIORITY_TYPE_CODING_ID INT NULL,
    insert_time2 DATETIME NULL

);
GO

CREATE TABLE dbo.corespondent_banks (
    correspondent_id INT NOT NULL,
    bank_id INT NULL,
    country_code NVARCHAR(10) NULL,
    swift_code NVARCHAR(20) NULL,
    bank_name NVARCHAR(300) NULL,
    currency_code NVARCHAR(10) NULL,
    account_number NVARCHAR(50) NULL,
    is_active TINYINT NULL ,
    created_at DATETIME NULL,
    CORESPONDENT_BANK_ID INT NULL,
    insert_time2 DATETIME NULL

);
GO

CREATE TABLE dbo.import_request (
    IMPORT_REQUEST_ID INT NOT NULL,
    import_request NVARCHAR(500) NULL,
    insert_time2 DATETIME NULL

);
GO

CREATE TABLE dbo.import_request_organization (
    import_request_organization_ID INT NOT NULL,
    import_request_organization NVARCHAR(500) NULL,
    IMPORT_REQUEST_ID INT NULL,
    insert_time2 DATETIME NULL

);
GO

CREATE TABLE dbo.fishes (
    fish_id                             INT             NOT NULL,
    fish_code                           NVARCHAR(20)    NULL,
    fish_name                           NVARCHAR(300)   NULL,
    unit_code                           NVARCHAR(10)    NULL,
    is_master                           TINYINT         NULL,
    fish_type                           NVARCHAR(50)    NULL,
    CORESPONDENT_BANK_ID                INT             NULL,
    IMPORT_REQUEST_ID                   INT             NULL,
    IMPORT_REQUEST_ORGANIZATION_ID      INT             NULL,
    BANK_ID                             INT             NULL,
    CREATION_CODING_DATE_ID             INT             NULL,
    ALLOCATION_CODING_DATE_ID           INT             NULL,
    BRANCH_ID                           INT             NULL,
    CODING_ID                           INT             NULL,
    ORGANIZATION_CODING_ID              INT             NULL,
    -- ستون‌های جدید
    [کد مشتری]                       NVARCHAR(20)    NULL,  -- کد مشتری
    [تاریخ تخصیص]                     DATE            NULL,  -- تاریخ تخصیص
    [محل تامین ارز]                     NVARCHAR(50)    NULL,  -- محل تامین ارز
    [مبلغ معادل دلاری]               DECIMAL(18, 2)  NULL,  -- مبلغ معادل دلاری
    created_at                          DATETIME        NULL,
    insert_time2 DATETIME NULL
);
GO

