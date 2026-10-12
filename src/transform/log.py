import functools
from datetime import datetime
import sqlalchemy


def log_decorator(source_table_name, target_table_name, source_schema_name, target_schema_name,
                  source_engine, target_engine, log_engine=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = {
                "table_name": source_table_name,
                "start_time": datetime.now(),
                "end_time": None,
                "source_count": None,
                "target_count": None,
                "count_diff": None,
                "duration_seconds": None,
                "status": "running",
                "error_message": None,
            }

            # Number of sources before ETL
            try:
                with source_engine.connect() as conn:
                    log["source_count"] = conn.execute(
                        sqlalchemy.text(f"SELECT COUNT(*) FROM [{source_schema_name}].[{source_table_name}]")
                    ).scalar()
            except Exception:
                log["source_count"] = None

            try:
                result = func(*args, **kwargs)
                log["status"] = "success"
                return result

            except Exception as e:
                log["status"] = "failed"
                log["error_message"] = str(e)
                raise

            finally:
                log["end_time"] = datetime.now()
                log["duration_seconds"] = (
                        log["end_time"] - log["start_time"]
                ).total_seconds()

                # Number of destinations after ETL
                try:
                    with target_engine.connect() as conn:
                        log["target_count"] = conn.execute(
                            sqlalchemy.text(f"SELECT COUNT(*) FROM [{target_schema_name}].[{target_table_name}]")
                        ).scalar()
                except Exception as e:
                    log["source_count"] = None

                if log["source_count"] and log["target_count"]:
                    log["count_diff"] = log["source_count"] - log["target_count"]

                # log console
                icon = "✓" if log["status"] == "success" else "✗"
                # Save to database
                if log_engine:
                    with log_engine.begin() as conn:
                        conn.execute(
                            sqlalchemy.text("""
                                            INSERT INTO etl_logs (table_name, start_time, end_time,
                                                                  source_count, target_count, count_diff,
                                                                  duration_seconds, status, error_message)
                                            VALUES (:table_name, :start_time, :end_time,
                                                    :source_count, :target_count, :count_diff,
                                                    :duration_seconds, :status, :error_message)
                                            """), log)

        return wrapper

    return decorator

