from __future__ import annotations

from io import BytesIO

import pandas as pd


class ExcelReadError(Exception):
    pass


def read_excel_bytes(file_bytes: bytes, filename: str | None = None) -> pd.DataFrame:
    if not file_bytes:
        raise ExcelReadError("Empty file content.")

    ext = ""
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()

    if ext and ext not in {"xls", "xlsx"}:
        raise ExcelReadError("Unsupported file type. Use .xls or .xlsx.")

    try:
        stream = BytesIO(file_bytes)
        return pd.read_excel(stream)
    except Exception as exc:
        raise ExcelReadError(f"Unable to read Excel file: {exc}") from exc
