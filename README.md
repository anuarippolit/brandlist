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
  - FG Group
  - Superstep
  - Salomon
  - And more...
- **Database** - PostgreSQL with SQLAlchemy ORM
- **Services** - Product query builder, filter updates

## Frontend

The frontend is a Next.js 15 application with:
- React 19
- TypeScript
- Tailwind CSS
- Features: Search, Filters, Wishlist, Product browsing
- Google Analytics 4 + Google Tag Manager integration

## Getting Started

### Local Development

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Configure .env file in backend/system/.env
cd system
uvicorn main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
# Create .env.local file with:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_GTM_ID=your_gtm_id
npm run dev
```

### Docker Deployment

#### Local Development

```bash
# Create .env file in root directory
docker-compose up -d --build

# Services will be available at:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Database: localhost:5432
```

#### Production Deployment

For production deployment, see [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

Quick start:
```bash
# Use production docker-compose file
docker compose -f docker-compose.prod.yml up -d --build
```

## Analytics

The project includes Google Analytics 4 (GA4) and Google Tag Manager (GTM) integration for tracking:
- Page views
- Product card clicks
- Product detail views
- "Go to shop" button clicks
- User sessions with UUID tracking

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
```

### Backend (backend/system/.env)
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Docker (.env in root)
```
POSTGRES_USER=brandlist
POSTGRES_PASSWORD=your_password
POSTGRES_DB=brandlist_db
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
```
