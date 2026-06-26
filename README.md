# Brandlist

Fashion product aggregator with natural language search across Kazakh retailers.

Users type a free-text query — the app extracts filters via OpenAI API and returns matching products from a unified database scraped from 7 stores.

## Stack

Python · FastAPI · PostgreSQL · SQLAlchemy · Next.js · Tailwind CSS · Docker

## How it works

```
User query → OpenAI extracts filters (category, color, size, brand)
           → SQL query built dynamically
           → Products returned from PostgreSQL
```

Scrapers run separately and normalize 50,000+ products from Adidas, Superstep, Salomon, FG Group and others into a single schema.

## Run locally

```bash
git clone https://github.com/anuarippolit/brandlist
cp .env.example .env   # fill in your values
docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000

## Environment variables

```
# Backend
DATABASE_URL=postgresql://user:password@host:5432/dbname
OPENAI_API_KEY=your_key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
```

## Project structure

```
brandlist/
├── backend/
│   ├── parsers/   # scrapers per retailer
│   ├── system/    # FastAPI app, routes, services
│   └── utils/
└── frontend/      # Next.js 15, React 19, TypeScript
```
