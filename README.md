# Finance Screening Web

Web app for screening and transforming finance-related rows from Excel files using `เลขถัง` and `รายการ`.

## Implemented rules

- `รายการ = ส่งไฟแนนซ์` -> set `มูลค่ารวม = ราคาขาย`
- `รายการ = นายหน้าไฟแนนซ์` -> set `มูลค่าสินค้า = COM F/N` and `ภาษี = COM`
- Duplicate tank support:
  - `keep`: keep all rows and append duplicate markers
  - `group`: merge duplicated tanks into one row per tank

Rule defaults and field mapping are documented in `docs/column-rules.md`.

## Project structure

- `backend`: FastAPI + pandas business rules + Excel read/write
- `frontend`: React + TypeScript + Ant Design upload/preview/export flow
- `docker-compose.yml`: local intranet deployment

## Run backend locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run frontend locally

```bash
cd frontend
npm install
npm run dev
```

## Run with Docker

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
