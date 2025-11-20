# Backend - Attendance Management System

FastAPI backend with PostgreSQL database.

## 📁 Structure

```
backend/
├── app/
│   ├── api/              # API routes (by feature)
│   ├── core/             # Core config & database
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── utils/            # Utilities
├── tests/                # Tests
├── .env                  # Environment variables (gitignored)
├── .env.example          # Example env file
└── requirements.txt      # Python dependencies
```

## 🚀 Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example`:
```bash
cp .env.example .env
```

4. Update DATABASE_URL in `.env`

5. Run migrations (future):
```bash
alembic upgrade head
```

6. Start server:
```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

## 📖 API Documentation

Visit: http://localhost:8000/docs

## 🧪 Testing

```bash
pytest
```
