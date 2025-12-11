# BrandList - Fashion Store Aggregator

A monorepo containing both the frontend and backend for the BrandList fashion store finder application.

## Project Structure

```
Brandlist/
├── backend/          # FastAPI backend with parsers
│   ├── parsers/      # Web scrapers for various stores
│   ├── system/       # FastAPI application (API routes, database, services)
│   ├── utils/        # Utility functions
│   └── requirements.txt
│
└── frontend/         # Next.js frontend application
    ├── src/          # Source code
    ├── public/       # Static assets
    └── package.json
```

## Backend

The backend consists of:
- **FastAPI API** (`backend/system/main.py`) - REST API endpoints
- **Parsers** (`backend/parsers/`) - Web scrapers for different fashion stores:
  - Adidas
  - Copa
  - FG Group
  - Lamoda
  - Ozze
  - Superstep
- **Database** - PostgreSQL with SQLAlchemy ORM
- **Services** - Product query builder, filter updates, AI services

## Frontend

The frontend is a Next.js 15 application with:
- React 19
- TypeScript
- Tailwind CSS
- Features: Search, Filters, Wishlist, Product browsing

## Getting Started

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Configure .env file in backend/system/.env
cd system
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Next Steps

- [ ] Set up Docker configuration
- [ ] Configure environment variables
- [ ] Set up CI/CD pipeline
- [ ] Initialize Git repository
