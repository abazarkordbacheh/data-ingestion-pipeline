import pytest
import pandas as pd
import numpy as np
from src.transform.maping import (
    classify_source,
    classify_ministry,
    classify_device,
    classify_allocation,
)


# region classify_source test

class TestClassifySource:
    def _row(self, date, source, rate, circular, old_rate=""):
        return {
            "تاریخ ایجاد": date,
            "محل تامین ارز": source,
            "نرخ ارز": rate,
            "کد بخشنامه": circular,
            "نرخ ارز (ساختار قدیمی)": old_rate,
        }

    def test_free_rate_after_threshold_with_circular(self):
        row = self._row("1401/12/15", "بانک مرکزی", "آزاد", "14011214001")
        assert classify_source(row) == "بانک مرکزی-نرخ آزاد"

    def test_free_rate_before_threshold(self):
        row = self._row("1401/01/01", "بانک تجاری", "آزاد", "")
        assert classify_source(row) == "بانک مرکزی-نرخ آزاد"

    def test_free_rate_on_threshold_no_circular(self):
        row = self._row("1401/12/14", "بانک مرکزی", "آزاد", "99999999")
        assert classify_source(row) == "بانک مرکزی-نرخ 28500"

    def test_preferential_rate(self):
        row = self._row("1402/01/01", "بانک مرکزی", "ترجیحی", "")
        assert classify_source(row) == "بانک مرکزی-نرخ 4200"

    def test_agreed_rate_via_rate_col(self):
        row = self._row("1402/01/01", "بانک مرکزی", "توافقی", "", "توافقی")
        assert classify_source(row) == "بانک مرکزی-نرخ توافقی"

    def test_fallback_returns_source(self):
        row = self._row("1402/01/01", "بانک ملی", "نقدی", "")
        assert classify_source(row) == "بانک ملی"

    def test_null_circular_treated_as_empty(self):
        # تاریخ باید <= threshold باشه تا شرط elif دوم فعال بشه
        row = self._row("1401/12/14", "بانک مرکزی", "آزاد", np.nan)
        assert classify_source(row) == "بانک مرکزی-نرخ 28500"


# endregion

# region classify_ministry test

class TestClassifyMinistry:
    def _row(self, org):
        return {"سازمان مجوز دهنده": org}

    def test_health_ministry_direct(self):
        assert classify_ministry(
            self._row("وزارت بهداشت،درمان و آموزش پزشکی")
        ) == "وزارت بهداشت، درمان و آموزش پزشکی"

    def test_health_ministry_medical_devices(self):
        assert classify_ministry(
            self._row("اداره کل تجهیزات پزشکی-تخصیص ارز")
        ) == "وزارت بهداشت، درمان و آموزش پزشکی"

    def test_jahad_ministry(self):
        assert classify_ministry(
            self._row("وزارت جهاد- تخصیص ارز")
        ) == "وزارت جهاد کشاورزی"

    def test_virtual_org(self):
        assert classify_ministry(
            self._row("سازمان مجازی")
        ) == "سازمان مجازی (ثبت خدمت)"

    def test_free_zone(self):
        assert classify_ministry(
            self._row("دبیرخانه شورای عالی مناطق ازاد و ویژه اقتصادی-تخصیص ارز")
        ) == "دبیرخانه شورای عالی مناطق آزاد و ویژه اقتصادی"

    def test_fallback_industry(self):
        assert classify_ministry(
            self._row("سازمان ناشناخته")
        ) == "وزارت صنعت، معدن و تجارت"


# endregion

# region classify_device test

class TestClassifyDevice:
    def test_has_comment(self):
        assert classify_device({"وضعیت نظر دستگاه": 1}) == "دارد"

    def test_no_comment_zero(self):
        assert classify_device({"وضعیت نظر دستگاه": 0}) == "ندارد"

    def test_no_comment_negative(self):
        assert classify_device({"وضعیت نظر دستگاه": -1}) == "ندارد"

    def test_large_positive(self):
        assert classify_device({"وضعیت نظر دستگاه": 100}) == "دارد"


# endregion

# region classify_allocation test

class TestClassifyAllocation:
    def test_ready_returns_none(self):
        row = {"تاریخ تخصیص": "1402/03/01", "وضعیت": "آماده برای تخصیص"}
        assert classify_allocation(row) is None

    def test_other_status_returns_date(self):
        row = {"تاریخ تخصیص": "1402/03/01", "وضعیت": "تخصیص یافته"}
        assert classify_allocation(row) == "1402/03/01"

    def test_null_date_non_ready(self):
        row = {"تاریخ تخصیص": None, "وضعیت": "در انتظار"}
        assert classify_allocation(row) is None
# endregion
