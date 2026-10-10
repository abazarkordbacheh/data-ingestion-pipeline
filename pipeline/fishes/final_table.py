# ------------------------ modules ------------------------
# Libraries =>
import os
import datetime
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv
# Modules =>
from fishes_type import FISHES_TYPE
from sql.query.dql.dql_query import DQLQuery
from src.transform.join import join_dataframe
from pipeline.fishes.bank import read_bank_table
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


# ------------------------ final_table ------------------------

def final_table():
    # ------------------------ .env file ------------------------
    global coding_df
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

    # ------------------------ Get Max ID ------------------------
    fishes_max_id = "0"
    # fishes_max_id = read_control()
    # ------------------------ connection ------------------------
    source_sql_connection = SQLConnection(
        SOURCE_FISHES_HOST, SOURCE_FISHES_PORT,
        SOURCE_FISHES_USERNAME, SOURCE_FISHES_PASSWORD
    )

    target_sql_connection = SQLConnection(
        TARGET_FISHES_HOST, TARGET_FISHES_PORT,
        TARGET_FISHES_USERNAME, TARGET_FISHES_PASSWORD
    )

    source_sql_connection.connect()
    target_sql_connection.connect()

    # ------------------------ Generate query ------------------------
    # FISHES =>
    fishes_dql_query = DQLQuery(SOURCE_FISHES_DATABASE, SOURCE_FISHES_SCHEMA, SOURCE_FISHES_TABLE)
    fishes_dql_query.select(None)
    condition_1 = fishes_dql_query.greater_than(SOURCE_FISHES_PRIMARY_KEY, fishes_max_id)
    condition_2 = fishes_dql_query.equal("IS_MASTER", "1")
    conditions = fishes_dql_query.conditions([condition_1, condition_2])
    fishes_dql_query.where(conditions)
    fishes_query = fishes_dql_query.query
    # Count of total =>
    fishes_total_dql_query = DQLQuery(SOURCE_FISHES_DATABASE, SOURCE_FISHES_SCHEMA, SOURCE_FISHES_TABLE)
    fishes_total_dql_query.select(["COUNT(*)"])
    condition_1 = fishes_total_dql_query.greater_than(SOURCE_FISHES_PRIMARY_KEY, fishes_max_id)
    condition_2 = fishes_total_dql_query.equal("IS_MASTER", "1")
    conditions = fishes_total_dql_query.conditions([condition_1, condition_2])
    fishes_total_dql_query.where(conditions)
    total_query = fishes_total_dql_query.query
    total_record = get_total_count(source_sql_connection, total_query)

    CHUNK_SIZE = 200
    total_chunks = total_record / CHUNK_SIZE

    # ------------------------ ETL ------------------------
    coding_df = read_coding_table()

    # Read fishes from source
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
        global coding_df
        chunk["insert_time2"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        chunk.map(lambda x: x.strip() if isinstance(x, str) else x, inplace=True)

        corespondent_df = read_corespondent_table(
            min(chunk["CORESPONDENT_BANK_ID"]),
            max(chunk["CORESPONDENT_BANK_ID"])
        )
        import_request_df = read_import_request_table(
            min(chunk["IMPORT_REQUEST_ID"]),
            max(chunk["IMPORT_REQUEST_ID"])
        )
        import_request_organization_df = read_import_request_organization_table(
            min(chunk["IMPORT_REQUEST_ID"]),
            max(chunk["IMPORT_REQUEST_ID"])
        )
        bank_df = read_bank_table(min(chunk["BANK_ID"]), max(chunk["BANK_ID"]))
        branch_df = read_branch_table(min(chunk["BRANCH_ID"]), max(chunk["BRANCH_ID"]))
        # If any crucial columns is null =>
        chunk_null = filter_any_null(chunk, CRUCIAL_COLUMNS)
        # TODO: Write to quarantine table
        del chunk_null

        # If all crucial columns is not null =>
        chunk = filter_all_not_null(chunk, CRUCIAL_COLUMNS)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CREATION_CODING_DATE_ID", "CODING_DATE_ID"],
            "left"
        )

        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["ALLOCATION_CODING_DATE_ID", "CODING_DATE_ID"],
            "left"
        )

        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            corespondent_df,
            ["CORESPONDENT_BANK_ID", "CORESPONDENT_BANK_ID"],
            "left"
        )

        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            bank_df,
            ["BANK_ID", "BANK_ID"],
            "left"
        )

        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            branch_df,
            ["BRANCH_ID", "BRANCH_ID"],
            "left"
        )

        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            coding_df[coding_df["CODING_ID"] == "NEW"],
            ["CODING_ID", "NEW_FISHE_TYPE_CODING"],
            "left"
        )

        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "CIRCULAR_CODING_ID"],
            "left"
        )

        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "EXCHANGE_RATE_TYPE_CODING_ID"],
            "left"
        )

        chunk['fishes_type'] = chunk['fishes_type'].map(FISHES_TYPE)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "FISH_CURRENCY_CODING_ID"],
            "left"
        )

        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_TRADING_TYPE_CODING_ID"],
            "left"
        )
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_GUARANTOR_TYPE_CODING_ID"],
            "left"
        )

        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_TERM_TYPE_CODING_ID"],
            "left"
        )

        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_LOAN_LOCATION_CODING_ID"],
            "left"
        )
        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_FOREIGN_EXCHANGE_LOCATION_CODING_ID"],
            "left"
        )

        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "NEW_EXCHANGE_RATE_TYPE_CODING_ID"],
            "left"
        )

        chunk = join_dataframe(
            chunk,
            coding_df,
            ["CODING_ID", "PRIORITY_TYPE_CODING_ID"],
            "left"
        )

        chunk.drop_duplicates(inplace=True)
        chunk = join_dataframe(
            chunk,
            import_request_df,
            ["IMPORT_REQUEST_ID", "IMPORT_REQUEST_ID"],
            "left"
        )

        chunk = join_dataframe(
            chunk,
            import_request_organization_df,
            ["IMPORT_REQUEST_ID", "IMPORT_REQUEST_ID"],
            "left"
        )

        chunk = join_dataframe(
            chunk,
            coding_df,
            ["ORGANIZATION_CODING_ID", "CODING_ID"],
            "left"
        )
        del coding_df
        chunk.drop_duplicates(inplace=True)
        chunk["کد مشتری"] = chunk["کد مشتری"].apply(
            lambda x: chunk["NATIONAL_CODE"] if pd.notna(x) else chunk["NATIONAL_ID"])
        chunk["تاریخ تخصیص"] = chunk["تاریخ تخصیص"].apply(
            lambda x: chunk["تاریخ تخصیص"] if pd.notna(x) else chunk["تاریخ ایجاد"])
        chunk = filter_dataframe(chunk, "مبلغ معادل دلاری", [0], "gt")
        chunk["محل تامین ارز"] = chunk.apply(classify_source, axis=1)


final_table()
