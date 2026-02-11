from __future__ import annotations

import pandas as pd

from app.models.schema import ColumnMapping, TransformOptions
from app.services.rules_engine import apply_business_rules


def _sample_options(duplicate_mode: str = "keep") -> TransformOptions:
    return TransformOptions(
        duplicate_mode=duplicate_mode,
        mapping=ColumnMapping(
            tank_no="เลขถัง",
            item="รายการ",
            sale_price="ราคาขายเดิม",
            total_value="มูลค่ารวม",
            product_value="มูลค่าสินค้า",
            tax="ภาษี",
            com_fn="COM F/N",
            com="COM",
        ),
    )


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "เลขถัง": "ABC123",
                "รายการ": "ส่งไฟแนนซ์",
                "ราคาขายเดิม": 100000,
                "มูลค่ารวม": 0,
                "มูลค่าสินค้า": 933644.86,
                "COM F/N": 0,
                "COM": 0,
                "ภาษี": 0,
            },
            {
                "เลขถัง": "ABC123",
                "รายการ": "นายหน้าไฟแนนซ์",
                "ราคาขายเดิม": 0,
                "มูลค่ารวม": 0,
                "มูลค่าสินค้า": 0,
                "COM F/N": 5000,
                "COM": 350,
                "ภาษี": 0,
            },
            {
                "เลขถัง": "XYZ999",
                "รายการ": "อื่นๆ",
                "ราคาขายเดิม": 80000,
                "มูลค่ารวม": 0,
                "มูลค่าสินค้า": 0,
                "COM F/N": 0,
                "COM": 0,
                "ภาษี": 0,
            },
        ]
    )


def test_finance_sent_updates_total_value():
    result = apply_business_rules(_sample_df(), _sample_options())
    sent_row = result.dataframe[result.dataframe["รายการ"] == "ส่งไฟแนนซ์"].iloc[0]
    assert sent_row["มูลค่ารวม"] == sent_row["ราคาขายเดิม"]
    assert result.stats.finance_sent_count == 1


def test_finance_broker_updates_product_and_tax():
    result = apply_business_rules(_sample_df(), _sample_options())
    broker_row = result.dataframe[result.dataframe["รายการ"] == "นายหน้าไฟแนนซ์"].iloc[0]
    assert broker_row["มูลค่าสินค้า"] == broker_row["COM F/N"]
    assert broker_row["ภาษี"] == 350
    assert result.stats.finance_broker_count == 1


def test_group_mode_merges_duplicate_tank_rows():
    options = _sample_options(duplicate_mode="group")
    result = apply_business_rules(_sample_df(), options)
    assert len(result.dataframe) == 2
    assert result.stats.duplicate_tank_groups == 1


def test_same_tank_canonical_columns_follow_item_rules():
    result = apply_business_rules(_sample_df(), _sample_options())
    abc_rows = result.dataframe[result.dataframe["เลขถัง"] == "ABC123"]
    assert not abc_rows.empty
    assert set(abc_rows["ราคาขาย"].tolist()) == {100000}
    assert set(abc_rows["COM F/N"].tolist()) == {5000}
    assert "COM" not in result.dataframe.columns
