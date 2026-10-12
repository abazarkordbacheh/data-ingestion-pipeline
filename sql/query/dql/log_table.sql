CREATE TABLE etl_logs (
    id               BIGINT IDENTITY(1,1),
    table_name       NVARCHAR(100)  NOT NULL,
    start_time       DATETIME2      NOT NULL,
    end_time         DATETIME2,
    source_count     BIGINT,
    target_count     BIGINT,
    count_diff       BIGINT,
    duration_seconds FLOAT,
    status           NVARCHAR(20)   NOT NULL DEFAULT 'running',
    attempt_number   TINYINT        NOT NULL DEFAULT 1,
    error_message    NVARCHAR(MAX),
    source_host      NVARCHAR(200),
    target_host      NVARCHAR(200),
    pipeline_version NVARCHAR(50)
);