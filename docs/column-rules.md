# Column Mapping And Rules

This document defines the default column mapping and business rules for the finance screening flow.

## Required business fields

The system expects these business fields, mapped from source columns:

- `tank_no`: เลขถัง
- `item`: รายการ
- `sale_price`: ราคาขาย
- `total_value`: มูลค่ารวม
- `product_value`: มูลค่าสินค้า
- `tax`: ภาษี
- `com_fn`: COM F/N
- `com`: COM

## Rule set

Rows are matched by `tank_no` first and filtered by `item`.

1. If `item == "ส่งไฟแนนซ์"`:
   - Set `total_value = sale_price`
2. If `item == "นายหน้าไฟแนนซ์"`:
   - Set `product_value = com_fn`
   - Set `tax = com`

For traceability, each output row appends:

- `rule_applied`: `finance_sent`, `finance_broker`, or empty
- `is_duplicate_tank`: whether `tank_no` appears more than once in input
- `group_id`: normalized tank-based group id

## Duplicate strategy

Two modes are supported:

- `keep` (default): keep all source rows, only annotate duplicates
- `group`: merge duplicated `tank_no` rows into one row per tank

When mode is `group`:

- numeric columns are summed
- text columns keep first non-empty value
- appended columns are recalculated for merged rows
