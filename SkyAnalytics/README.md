# SkyAnalytics

A project for analytics with FastAPI backend and Streamlit dashboard.

## Structure

- `backend/`: FastAPI application
- `dashboard/`: Streamlit dashboard
- `docker-compose.yml`: Docker orchestration
- `.env`: Environment variables

## Setup

1. Update `.env` with your database credentials.
2. Run `docker-compose up --build` to start the services.

## Services

- Backend: http://localhost:8000
- Dashboard: http://localhost:8501
- Database: PostgreSQL on port 5432