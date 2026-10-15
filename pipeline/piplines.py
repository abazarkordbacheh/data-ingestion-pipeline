# ------------------------ Modules ------------------------
# Libraries =>
import sys
import time
import signal
import logging
import schedule
import threading
# Modules =>
from pipeline.bank.final_table import final_table as banks_final_table
from pipeline.coding.final_table import final_table as coding_final_table
# from pipeline.fishes.final_table import final_table as fishes_final_table
from pipeline.bransh.final_table import final_table as branches_final_table
from pipeline.import_request.final_table import final_table as import_request_final_table
from pipeline.corespondent_banks.final_table import final_table as corespondent_banks_final_table
from pipeline.import_request_organization import final_table as import_request_organization_final_table

# ------------------------ Logging ------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

running = True


def signal_handler(sig, frame):
    global running
    logger.info("Receiving shutdown signal...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ------------------------ Threading ------------------------
def run_threaded(job_func):
    thread = threading.Thread(target=job_func)
    thread.daemon = True
    thread.start()


def make_etl_job(name: str, func):
    def etl_job():
        logger.info(f"Start ETL: {name}")
        for attempt in range(1, 2):
            try:
                func()
                logger.info(f"ETL {name} finished successfully")
                return
            except Exception as e:
                logger.warning(f"ETL {name} attempt {attempt}/5 failed: {e}")
        logger.error(f"ETL {name} failed after 5 attempts")

    return etl_job

# ------------------------ Jobs ------------------------
etl_banks = make_etl_job("Banks", banks_final_table)
etl_coding = make_etl_job("Coding", coding_final_table)
# etl_fishes = make_etl_job("Fishes", fishes_final_table)
etl_branches = make_etl_job("Branches", branches_final_table)
etl_import_request = make_etl_job("Import", import_request_final_table)
etl_corespondent_banks = make_etl_job("Corespondent Banks", corespondent_banks_final_table)
etl_import_request_organization = make_etl_job("ImportRequestOrganization", import_request_organization_final_table)

# schedule.every().day.at("17:02").do(run_threaded, etl_banks).tag("etl")
# schedule.every().day.at("17:02").do(run_threaded, etl_coding).tag("etl")
# schedule.every().day.at("15:44").do(run_threaded, etl_fishes).tag("etl")
# schedule.every().day.at("17:02").do(run_threaded, etl_branches).tag("etl")
# schedule.every().day.at("17:02").do(run_threaded, etl_import_request).tag("etl")
# schedule.every().day.at("17:02").do(run_threaded, etl_corespondent_banks).tag("etl")
# schedule.every().day.at("17:02").do(run_threaded, etl_import_request_organization).tag("etl")


schedule.every().minutes.do(run_threaded, etl_banks).tag("etl")
schedule.every().minutes.do(run_threaded, etl_coding).tag("etl")
schedule.every().minutes.do(run_threaded, etl_branches).tag("etl")
schedule.every().minutes.do(run_threaded, etl_import_request).tag("etl")
schedule.every().minutes.do(run_threaded, etl_import_request_organization).tag("etl")
schedule.every().minutes.do(run_threaded, etl_import_request_organization).tag("etl")

logger.info("Scheduler started.")

while running:
    schedule.run_pending()
    time.sleep(1)

logger.info("Scheduler stopped.")
sys.exit(0)
