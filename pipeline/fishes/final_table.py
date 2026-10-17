# ------------------------ Modules ------------------------
# Libraries =>
import os
import datetime
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv
# Modules =>
from pipeline.fishes.fishes_type import FISHES_TYPE
from src.transform.log import log_decorator
from sql.query.dql.dql_query import DQLQuery
from src.transform.join import join_dataframe
from pipeline.fishes.bank import read_bank_table
from pipeline.fishes.dates import read_dates_table
from src.validation.safe_range import safe_range
from src.transform.filter import filter_dataframe
from pipeline.fishes.coding import read_coding_table
from pipeline.fishes.brnach import read_branch_table
from pipeline.fishes.read_control import read_control
from src.connection.sql_connection import SQLConnection
from pipeline.fishes.crucial_columns import CRUCIAL_COLUMNS
from src.extract.sql_extractor import extract, get_total_count
from pipeline.fishes.corespondent import read_corespondent_table
from pipeline.fishes.import_request import read_import_request_table
from src.validation.crucial_cols import filter_any_null, filter_all_not_null
from src.transform.maping import classify_source, classify_ministry, classify_device
from pipeline.fishes.import_request_organization import read_import_request_organization_table

# ------------------------ .env file ------------------------
load_dotenv()
# Source =>
SOURCE_FISHES_HOST = os.getenv("SOURCE_FISHES_HOST")
SOURCE_FISHES_PORT = int(os.getenv("SOURCE_FISHES_PORT"))
SOURCE_FISHES_USERNAME = os.getenv("SOURCE_FISHES_USERNAME")
SOURCE_FISHES_PASSWORD = os.getenv("SOURCE_FISHES_PASSWORD")
SOURCE_FISHES_DATABASE = os.getenv("SOURCE_FISHES_DATABASE")
SOURCE_FISHES_SCHEMA = os.getenv("SOURCE_FISHES_SCHEMA")
SOURCE_FISHES_TABLE = os.getenv("SOURCE_FISHES_TABLE")
SOURCE_FISHES_PRIMARY_KEY = os.getenv("SOURCE_FISHES_PRIMARY_KEY")

# Target =>
# FISHES
TARGET_FISHES_HOST = os.getenv("TARGET_FISHES_HOST")
TARGET_FISHES_PORT = int(os.getenv("TARGET_FISHES_PORT"))
TARGET_FISHES_USERNAME = os.getenv("TARGET_FISHES_USERNAME")
TARGET_FISHES_PASSWORD = os.getenv("TARGET_FISHES_PASSWORD")
TARGET_FISHES_DATABASE = os.getenv("TARGET_FISHES_DATABASE")
TARGET_FISHES_SCHEMA = os.getenv("TARGET_FISHES_SCHEMA")
TARGET_FISHES_TABLE = os.getenv("TARGET_FISHES_TABLE")
TARGET_FISHES_PRIMARY_KEY = os.getenv("TARGET_FISHES_PRIMARY_KEY")
# Log =>
LOG_HOST = os.getenv("LOG_HOST")
LOG_PORT = int(os.getenv("LOG_PORT"))
LOG_USERNAME = os.getenv("LOG_USERNAME")
LOG_PASSWORD = os.getenv("LOG_PASSWORD")
LOG_DATABASE = os.getenv("LOG_DATABASE")
LOG_SCHEMA = os.getenv("LOG_SCHEMA")
LOG_TABLE = os.getenv("LOG_TABLE")

# ------------------------ Connection ------------------------
source_sql_connection = SQLConnection(
    SOURCE_FISHES_HOST, SOURCE_FISHES_PORT,
    SOURCE_FISHES_USERNAME, SOURCE_FISHES_PASSWORD
)

target_sql_connection = SQLConnection(
    TARGET_FISHES_HOST, TARGET_FISHES_PORT,
    TARGET_FISHES_USERNAME, TARGET_FISHES_PASSWORD
)

log_sql_connection = SQLConnection(
    LOG_HOST, LOG_PORT,
    LOG_USERNAME, LOG_PASSWORD,
    LOG_DATABASE, True,
)

source_sql_connection.connect()
target_sql_connection.connect()
log_sql_connection.connect()


# ------------------------ final_table ------------------------
@log_decorator(
    source_table_name=SOURCE_FISHES_TABLE,
    target_table_name=TARGET_FISHES_TABLE,
    source_schema_name=SOURCE_FISHES_SCHEMA,
    target_schema_name=TARGET_FISHES_SCHEMA,
    source_engine=source_sql_connection.engine,
    target_engine=target_sql_connection.engine,
    log_engine=log_sql_connection.engine
)
def final_table():
    # ------------------------ Get Max ID ------------------------
    # fishes_max_id = "0"
    fishes_max_id = read_control()

    # ------------------------ Generate query ------------------------
    # FISHES =>
    fishes_dql_query = DQLQuery(SOURCE_FISHES_DATABASE, SOURCE_FISHES_SCHEMA, SOURCE_FISHES_TABLE)
    fishes_dql_query.select(None)
    fishes_dql_query.order_by(TARGET_FISHES_PRIMARY_KEY)
    condition_1 = fishes_dql_query.greater_than(SOURCE_FISHES_PRIMARY_KEY, fishes_max_id)
    condition_2 = fishes_dql_query.equal("is_master", "1")
    conditions = fishes_dql_query.conditions([condition_1, condition_2])
    fishes_dql_query.where(conditions)
    fishes_query = fishes_dql_query.query
    # Count of total =>
    fishes_total_dql_query = DQLQuery(SOURCE_FISHES_DATABASE, SOURCE_FISHES_SCHEMA, SOURCE_FISHES_TABLE)
    fishes_total_dql_query.select(["COUNT(*)"])
    condition_1 = fishes_total_dql_query.greater_than(SOURCE_FISHES_PRIMARY_KEY, fishes_max_id)
    condition_2 = fishes_total_dql_query.equal("is_master", "1")
    conditions = fishes_total_dql_query.conditions([condition_1, condition_2])
    fishes_total_dql_query.where(conditions)
    total_query = fishes_total_dql_query.query
    total_record = get_total_count(source_sql_connection, total_query)

    CHUNK_SIZE = 500
    total_chunks = total_record / CHUNK_SIZE

    # ======================== ETL ========================
    coding_df = read_coding_table()
    # ------------------------ Read fishes from source ------------------------
    for chunk in tqdm(extract(source_sql_connection, fishes_query, CHUNK_SIZE),
                      total=int(total_chunks),
                      desc="ETL ► Fishes → final_table",
                      colour="white",
                      unit="chunk",
                      unit_scale=False,
                      ncols=100,
                      bar_format=(
                              "{desc}: {percentage:3.0f}%|{bar}| "
                              "{n_fmt}/{total_fmt} chunks "
                              "[{elapsed}<{remaining}, {rate_fmt}]"
                      ),
                      smoothing=0.3):
        # print("\n")
        # print(chunk.to_string())
        # ------------------------ Extract Min & Max for columns ------------------------
        min_dates_1, max_dates_1 = safe_range(chunk["CREATION_CODING_DATE_ID"])
        min_dates_2, max_dates_2 = safe_range(chunk["ALLOCATION_CODING_DATE_ID"])
        min_corespondent, corespondent = safe_range(chunk["CORESPONDENT_BANK_ID"])
        min_import_request, max_import_request = safe_range(chunk["IMPORT_REQUEST_ID"])
        (min_import_request_organization,
         max_import_request_organization) = safe_range(chunk["IMPORT_REQUEST_ORGANIZATION_ID"])
        min_bank, max_bank = safe_range(chunk["BANK_ID"])
        min_branch, max_branch = safe_range(chunk["BRANCH_ID"])

        # ------------------------ Strip String ------------------------
        chunk = chunk.map(lambda x: x.strip() if isinstance(x, str) else x)

        # ------------------------ Insert Time ------------------------
        chunk["insert_time2"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # ------------------------ Read more tables ------------------------
        dates1_df = read_dates_table(min_dates_1, max_dates_1)
        dates2_df = read_dates_table(min_dates_2, max_dates_2)
        corespondent_df = read_corespondent_table(min_corespondent, corespondent)
        import_request_df = read_import_request_table(min_import_request, max_import_request)
        import_request_organization_df = read_import_request_organization_table(min_import_request_organization,
                                                                                max_import_request_organization)
        bank_df = read_bank_table(min_bank, max_branch)
        branch_df = read_branch_table(min_branch, max_branch)

        # ------------------------ If any crucial columns is null ------------------------
        chunk_null = filter_any_null(chunk, CRUCIAL_COLUMNS)
        # TODO: Write to quarantine table
        # print("*" * 100)
        # print(chunk_null)
        del chunk_null
        chunk = filter_all_not_null(chunk, CRUCIAL_COLUMNS)

        # ------------------------ Join between tables ------------------------
        chunk = join_dataframe(
            chunk,
            dates1_df,
            ["CREATION_CODING_DATE_ID", "coding_date_id"],
            "left",
            ("", "_date1")
        )

        chunk = join_dataframe(
            chunk,
            dates2_df,
            ["ALLOCATION_CODING_DATE_ID", "coding_date_id"],
            "left",
            ("", "_date2")
        )
        print(0)

        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CREATION_CODING_DATE_ID", "CODING_DATE_ID"],
            "left"
        )
        print(1)
        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["ALLOCATION_CODING_DATE_ID", "CODING_DATE_ID"],
            "left"
        )
        print(2)
        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            corespondent_df,
            ["CORESPONDENT_BANK_ID", "CORESPONDENT_BANK_ID"],
            "left"
        )
        print(3)
        chunk.drop_duplicates(inplace=True)
        print(chunk.columns, "\n", bank_df.columns)
        chunk = join_dataframe(
            chunk,
            bank_df,
            ["BANK_ID", "bank_id"],
            "left"
        )
        print(4)
        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            branch_df,
            ["BRANCH_ID", "BRANCH_ID"],
            "left"
        )
        print(4)
        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            coding_df[coding_df["CODING_ID"] == "NEW"],
            ["CODING_ID", "NEW_FISHE_TYPE_CODING"],
            "left"
        )
        print(5)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "CIRCULAR_CODING_ID"],
            "left"
        )
        print(6)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "EXCHANGE_RATE_TYPE_CODING_ID"],
            "left"
        )
        print(7)
        chunk['fishes_type'] = chunk['fishes_type'].map(FISHES_TYPE)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "FISH_CURRENCY_CODING_ID"],
            "left"
        )
        print(8)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_TRADING_TYPE_CODING_ID"],
            "left"
        )
        print(9)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_GUARANTOR_TYPE_CODING_ID"],
            "left"
        )
        print(10)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_TERM_TYPE_CODING_ID"],
            "left"
        )
        print(11)
        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_LOAN_LOCATION_CODING_ID"],
            "left"
        )
        print(12)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_FOREIGN_EXCHANGE_LOCATION_CODING_ID"],
            "left"
        )
        print(13)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_EXCHANGE_RATE_TYPE_CODING_ID"],
            "left"
        )
        print(14)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "PRIORITY_TYPE_CODING_ID"],
            "left"
        )
        print(15)
        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            import_request_df,
            ["IMPORT_REQUEST_ID", "IMPORT_REQUEST_ID"],
            "left"
        )
        print(16)
        del import_request_df
        chunk = join_dataframe(
            chunk,
            import_request_organization_df,
            ["IMPORT_REQUEST_ID", "IMPORT_REQUEST_ID"],
            "left"
        )
        print(17)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["ORGANIZATION_CODING_ID", "CODING_ID"],
            "left"
        )
        print(18)
        del import_request_organization_df
        del coding_df
        chunk.drop_duplicates(inplace=True)
        chunk["کد مشتری"] = chunk["کد مشتری"].fillna(chunk["NATIONAL_CODE"]).fillna(chunk["NATIONAL_ID"])
        chunk["تاریخ تخصیص"] = chunk["تاریخ تخصیص"].fillna(chunk["تاریخ ایجاد"])

        chunk["تاریخ تخصیص"] = chunk["تاریخ تخصیص"].apply(
            lambda x: chunk["تاریخ تخصیص"] if pd.notna(x) else chunk["تاریخ ایجاد"])
        chunk = filter_dataframe(chunk, "مبلغ معادل دلاری", [0], "gt")
        chunk["محل تامین ارز"] = chunk.apply(classify_source, axis=1)
        # break


if __name__ == "__main__":
    final_table()
