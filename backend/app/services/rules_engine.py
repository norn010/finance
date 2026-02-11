from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from pandas.api.types import is_numeric_dtype

from app.models.schema import TransformOptions, TransformStats


@dataclass
class RuleEngineResult:
    dataframe: pd.DataFrame
    stats: TransformStats
    issues: list[str]


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none"}:
        return ""
    return " ".join(text.split())


def _build_group_id(tank_no: object) -> str:
    return f"TANK::{_normalize_text(tank_no)}"


def _first_non_empty(series: pd.Series):
    for value in series.tolist():
        if _normalize_text(value):
            return value
    return ""


def _ensure_column(df: pd.DataFrame, name: str):
    if name not in df.columns:
        df[name] = None


def _validate_required_columns(df: pd.DataFrame, options: TransformOptions) -> list[str]:
    mapping = options.mapping
    required = [
        mapping.tank_no,
        mapping.item,
        mapping.sale_price,
        mapping.total_value,
        mapping.product_value,
        mapping.tax,
        mapping.com_fn,
        mapping.com,
    ]
    issues: list[str] = []
    missing = [col for col in required if col not in df.columns]
    if missing:
        issues.append(f"Missing required columns: {', '.join(missing)}")
    return issues


def apply_business_rules(df: pd.DataFrame, options: TransformOptions) -> RuleEngineResult:
    working_df = df.copy()
    mapping = options.mapping
    issues = _validate_required_columns(working_df, options)
    if issues:
        empty_stats = TransformStats(
            rows_in=len(working_df),
            rows_out=0,
            finance_sent_count=0,
            finance_broker_count=0,
            duplicate_tank_groups=0,
            duplicate_rows=0,
        )
        return RuleEngineResult(dataframe=working_df, stats=empty_stats, issues=issues)

    _ensure_column(working_df, "rule_applied")
    _ensure_column(working_df, "is_duplicate_tank")
    _ensure_column(working_df, "group_id")

    tank_col = mapping.tank_no
    item_col = mapping.item

    tank_norm = working_df[tank_col].apply(_normalize_text)
    item_norm = working_df[item_col].apply(_normalize_text)

    duplicate_mask = tank_norm.duplicated(keep=False) & tank_norm.ne("")
    duplicate_groups = tank_norm[duplicate_mask].nunique()

    working_df["is_duplicate_tank"] = duplicate_mask
    working_df["group_id"] = working_df[tank_col].apply(_build_group_id)
    working_df["rule_applied"] = ""

    finance_sent_mask = item_norm.eq(options.finance_sent_item_label)
    finance_broker_mask = item_norm.eq(options.finance_broker_item_label)

    working_df.loc[finance_sent_mask, mapping.total_value] = working_df.loc[
        finance_sent_mask, mapping.sale_price
    ]
    working_df.loc[finance_sent_mask, "rule_applied"] = "finance_sent"

    working_df.loc[finance_broker_mask, mapping.product_value] = working_df.loc[
        finance_broker_mask, mapping.com_fn
    ]
    working_df.loc[finance_broker_mask, mapping.tax] = working_df.loc[finance_broker_mask, mapping.com]
    working_df.loc[finance_broker_mask, "rule_applied"] = "finance_broker"

    # Build tank-level lookup values from source rows:
    # ราคาขาย  = มูลค่ารวม ของรายการส่งไฟแนนซ์
    # COM F/N = มูลค่าสินค้า ของรายการนายหน้าไฟแนนซ์
    sent_price_by_tank = (
        working_df.loc[finance_sent_mask]
        .groupby(tank_norm[finance_sent_mask])[mapping.total_value]
        .agg(_first_non_empty)
    )
    broker_comfn_by_tank = (
        working_df.loc[finance_broker_mask]
        .groupby(tank_norm[finance_broker_mask])[mapping.product_value]
        .agg(_first_non_empty)
    )

    output_df = working_df
    if options.duplicate_mode == "group":
        grouped = []
        for column in working_df.columns:
            if column in {"is_duplicate_tank"}:
                grouped.append((column, "max"))
            elif column in {"rule_applied"}:
                grouped.append((column, _first_non_empty))
            elif is_numeric_dtype(working_df[column]):
                grouped.append((column, "sum"))
            else:
                grouped.append((column, _first_non_empty))

        agg_map = {name: op for name, op in grouped}
        output_df = (
            working_df.groupby(working_df[tank_col].apply(_normalize_text), as_index=False)
            .agg(agg_map)
            .rename(columns={"index": tank_col})
        )
        if tank_col not in output_df.columns:
            output_df[tank_col] = working_df[tank_col]
        output_df["group_id"] = output_df[tank_col].apply(_build_group_id)
        output_df["is_duplicate_tank"] = output_df[tank_col].apply(_normalize_text).isin(
            tank_norm[duplicate_mask].unique()
        )

    output_tank_norm = output_df[tank_col].apply(_normalize_text)
    output_df["ราคาขาย"] = output_tank_norm.map(sent_price_by_tank)
    output_df["COM F/N"] = output_tank_norm.map(broker_comfn_by_tank)
    if "COM" in output_df.columns:
        output_df = output_df.drop(columns=["COM"])

    tail_columns = ["ราคาขาย", "COM F/N", "rule_applied", "is_duplicate_tank", "group_id"]
    front_columns = [col for col in output_df.columns if col not in tail_columns]
    ordered_tail = [col for col in tail_columns if col in output_df.columns]
    output_df = output_df[front_columns + ordered_tail]

    stats = TransformStats(
        rows_in=len(working_df),
        rows_out=len(output_df),
        finance_sent_count=int(finance_sent_mask.sum()),
        finance_broker_count=int(finance_broker_mask.sum()),
        duplicate_tank_groups=int(duplicate_groups),
        duplicate_rows=int(duplicate_mask.sum()),
    )
    return RuleEngineResult(dataframe=output_df, stats=stats, issues=issues)
