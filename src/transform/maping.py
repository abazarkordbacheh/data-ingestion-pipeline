import pandas as pd


def classify_source(row) -> str:
    """
    Classify for the <محل تامین ارز> column
    :param row: dataframe row
    :return: string classify
    """
    date = row["تاریخ ایجاد"]
    source = row["محل تامین ارز"]
    rate = row["نرخ ارز"]
    circular = str(row["کد بخشنامه"]) if pd.notna(row["کد بخشنامه"]) else ""
    threshold = "1401/12/14"

    if (date >= threshold and source == "بانک مرکزی" and "14011214" in circular) or \
            (rate == "آزاد" and date < threshold):
        return "بانک مرکزی-نرخ آزاد"
    elif source == "بانک مرکزی" and rate == "آزاد" and date <= threshold and "14011214" not in circular:
        return "بانک مرکزی-نرخ 28500"
    elif source == "بانک مرکزی" and rate == "ترجیحی":
        return "بانک مرکزی-نرخ 4200"
    elif (source == "بانک مرکزی") and (rate == "توافقی" or row["نرخ ارز (ساختار قدیمی)"] == "توافقی"):
        return "بانک مرکزی-نرخ توافقی"
    else:
        return source


def classify_ministry(row) -> str:
    """
    Classify for the <وزارتخانه> column
    :param row: dataframe row
    :return: string classify
    """
    licensing_organization = row["سازمان مجوز دهنده"]

    if licensing_organization == "وزارت بهداشت،درمان و آموزش پزشکی" or licensing_organization == "اداره کل تجهیزات پزشکی-تخصیص ارز":
        return "وزارت بهداشت، درمان و آموزش پزشکی"
    elif licensing_organization == "وزارت جهاد- تخصیص ارز":
        return "وزارت جهاد کشاورزی"
    elif licensing_organization == "سازمان مجازی":
        return "سازمان مجازی (ثبت خدمت)"
    elif licensing_organization == "دبیرخانه شورای عالی مناطق ازاد و ویژه اقتصادی-تخصیص ارز":
        return "دبیرخانه شورای عالی مناطق آزاد و ویژه اقتصادی"
    else:
        return "وزارت صنعت، معدن و تجارت"


def classify_device(row) -> str:
    """
    Classify for the <وضعیت نظر دستگاه> column
    :param row: dataframe row
    :return: string classify
    """
    device_comment_status = row["وضعیت نظر دستگاه"]
    if device_comment_status > 0:
        return "دارد"
    else:
        return "ندارد"


def classify_allocation(row) -> str:
    """
    Classify for the <تاریخ تخصیص> column
    :param row: dataframe row
    :return: string classify
    """
    date_of_allocation = row["تاریخ تخصیص"]
    status = row["وضعیت"]
    if status == "آماده برای تخصیص":
        return None
    else:
        return date_of_allocation
