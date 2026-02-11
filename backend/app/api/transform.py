from __future__ import annotations

import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.models.schema import PreviewResponse, TransformOptions
from app.services.excel_reader import ExcelReadError, read_excel_bytes
from app.services.excel_writer import dataframe_to_excel_bytes
from app.services.rules_engine import apply_business_rules

router = APIRouter(prefix="/api", tags=["transform"])


def _parse_options(config_raw: str | None) -> TransformOptions:
    if not config_raw:
        return TransformOptions()
    try:
        payload = json.loads(config_raw)
        return TransformOptions.model_validate(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid config payload: {exc}") from exc


def _validate_file(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required.")
    if not file.filename.lower().endswith((".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only .xls or .xlsx files are allowed.")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/preview", response_model=PreviewResponse)
async def preview(
    file: UploadFile = File(...),
    config: str | None = Form(default=None),
):
    _validate_file(file)
    options = _parse_options(config)
    content = await file.read()
    try:
        df = read_excel_bytes(content, file.filename)
    except ExcelReadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = apply_business_rules(df, options)
    preview_df = result.dataframe.head(200)
    return PreviewResponse(
        columns=[str(col) for col in preview_df.columns.tolist()],
        rows=preview_df.where(preview_df.notna(), None).to_dict(orient="records"),
        stats=result.stats,
        issues=result.issues,
    )


@router.post("/transform")
async def transform(
    file: UploadFile = File(...),
    config: str | None = Form(default=None),
):
    _validate_file(file)
    options = _parse_options(config)
    content = await file.read()
    try:
        df = read_excel_bytes(content, file.filename)
    except ExcelReadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = apply_business_rules(df, options)
    if result.issues:
        return JSONResponse(status_code=422, content={"issues": result.issues})

    data = dataframe_to_excel_bytes(result.dataframe)
    output_name = "finance-screening-output.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{output_name}"'}
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
