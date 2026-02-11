from __future__ import annotations

from io import BytesIO

import pandas as pd


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="result")
    output.seek(0)
    return output.getvalue()
