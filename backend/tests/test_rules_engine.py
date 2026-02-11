from __future__ import annotations

import pandas as pd

from app.models.schema import TransformOptions
from app.services.rules_engine import apply_business_rules


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "เลขถัง": "ABC123",
                "รายการ": "ส่งไฟแนนซ์",
                "ราคาขาย": 100000,
                "มูลค่ารวม": 0,
                "มูลค่าสินค้า": 0,
                "COM F/N": 0,
                "COM": 0,
                "ภาษี": 0,
            },
            {
                "เลขถัง": "ABC123",
                "รายการ": "นายหน้าไฟแนนซ์",
                "ราคาขาย": 0,
                "มูลค่ารวม": 0,
                "มูลค่าสินค้า": 0,
                "COM F/N": 5000,
                "COM": 350,
                "ภาษี": 0,
            },
            {
                "เลขถัง": "XYZ999",
                "รายการ": "อื่นๆ",
                "ราคาขาย": 80000,
                "มูลค่ารวม": 0,
                "มูลค่าสินค้า": 0,
                "COM F/N": 0,
                "COM": 0,
                "ภาษี": 0,
            },
        ]
    )


def test_finance_sent_updates_total_value():
    result = apply_business_rules(_sample_df(), TransformOptions())
    sent_row = result.dataframe[result.dataframe["รายการ"] == "ส่งไฟแนนซ์"].iloc[0]
    assert sent_row["มูลค่ารวม"] == sent_row["ราคาขาย"]
    assert result.stats.finance_sent_count == 1


def test_finance_broker_updates_product_and_tax():
    result = apply_business_rules(_sample_df(), TransformOptions())
    broker_row = result.dataframe[result.dataframe["รายการ"] == "นายหน้าไฟแนนซ์"].iloc[0]
    assert broker_row["มูลค่าสินค้า"] == broker_row["COM F/N"]
    assert broker_row["ภาษี"] == broker_row["COM"]
    assert result.stats.finance_broker_count == 1


def test_group_mode_merges_duplicate_tank_rows():
    options = TransformOptions(duplicate_mode="group")
    result = apply_business_rules(_sample_df(), options)
    assert len(result.dataframe) == 2
    assert result.stats.duplicate_tank_groups == 1
