# 🚀 ProposalAI — AI-Powered Proposal Generator + Lead CRM

A production-grade SaaS application built with **Django 5.1** + **Svelte 5** that helps freelancers win more clients with AI-generated proposals and behavioral lead scoring.

---

## ✨ Features

- **AI Proposal Generator** — GPT-4o powered proposal generation with structured output validation, tone control, and custom variables
- **Lead CRM** — Full customer relationship management with status tracking, pipeline visualization, and activity timelines
- **Behavioral Lead Scoring** — 6-dimension scoring engine (engagement, recency, frequency, depth, demographic, intent) with 0–100 composite scores
- **Real-time Dashboard** — Pipeline value, conversion rates, score distribution, AI usage analytics
- **Smart Notifications** — Auto-alerts for score changes, overdue follow-ups, and proposal acceptances
- **Role-based Quotas** — Free/Pro/Enterprise tiers with monthly AI generation limits
- **Background Processing** — Celery + Redis for async AI generation with retry logic and caching

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.1, DRF 3.15, JWT Auth |
| Database | PostgreSQL 16, Redis |
| Queue | Celery 5, Redis broker |
| AI | OpenAI GPT-4o, structured JSON output |
| Frontend | Svelte 5 (Runes), SvelteKit 2 |
| Styling | Tailwind CSS 4.0 |
| DevOps | Docker, Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 22+
- PostgreSQL 16+
- Redis 7+

### Backend Setup

```bash
cd proposalai/

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env file and configure
cp .env.example .env
# Edit .env with your database, Redis, and OpenAI credentials

# Run migrations
python manage.py migrate

# Seed demo data
python manage.py shell < seed.py  # or use the Django shell

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend/

# Install dependencies
npm install --legacy-peer-deps

# Copy env
cp .env.example .env

# Start dev server
npm run dev
```

### With Docker Compose

```bash
# Copy env files
cp proposalai/.env.example proposalai/.env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Access the app
open http://localhost:3000
```

---

## 📡 API Reference

Full OpenAPI documentation available at `/api/v1/docs/` when the server is running.

### Key Endpoints

```
POST /api/v1/auth/register/          # Register
POST /api/v1/auth/login/             # Login → JWT tokens
GET  /api/v1/auth/me/                # Current user

GET  /api/v1/proposals/              # List proposals
POST /api/v1/proposals/              # Create proposal
POST /api/v1/proposals/{id}/generate/ # AI generation

GET  /api/v1/leads/                  # List leads
POST /api/v1/leads/                  # Create lead
GET  /api/v1/leads/{id}/score/       # Lead score breakdown
POST /api/v1/leads/{id}/score/recalc/ # Recalculate score

GET  /api/v1/dashboard/stats/        # Dashboard metrics
GET  /api/v1/dashboard/pipeline/     # Pipeline stages
```

---

## 🎯 Lead Scoring Algorithm

Scores are calculated across 6 weighted dimensions:

| Dimension | Weight | Signals |
|-----------|--------|---------|
| Engagement | 25% | Website visits, email opens, proposal views |
| Recency | 20% | Time since last interaction (decay function) |
| Frequency | 20% | Visits/week, consistency, trend |
| Depth | 15% | Time-on-site, pages/visit, meeting quality |
| Demographic | 10% | Company size, industry, profile completeness |
| Intent | 10% | High-value actions: pricing page, form submit |

**Score Tiers:** Cold (0–25) → Warm (26–50) → Hot (51–75) → Qualified (76–100)

---

## 🔐 Demo Credentials

```
Admin:  admin@proposalai.com / Admin1234!
Demo:   demo@proposalai.com  / Demo1234!
```

---

## 📁 Project Structure

```
proposalai/          # Django backend
├── config/          # Settings, URLs, Celery
├── users/           # Auth, User model
├── proposals/       # Proposals, Templates, AI tasks
├── leads/           # CRM, Scoring, Activities
├── dashboard/       # Analytics views
├── analytics/       # AI usage tracking
└── notifications/   # Notification system

frontend/            # SvelteKit frontend
├── src/
│   ├── lib/
│   │   ├── api/     # API client + types
│   │   ├── stores/  # Svelte 5 runes state
│   │   └── components/
│   └── routes/
│       ├── (auth)/  # Login, Register
│       └── (app)/   # Dashboard, Proposals, Leads
```

---

## 🧪 Running Tests

```bash
# Backend
cd proposalai
pytest --reuse-db -x

# Frontend type-check
cd frontend
npm run check
```

---

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Railway/Render/AWS deployment guides.

### Environment Variables Required in Production

```env
SECRET_KEY=<50+ char random string>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
REDIS_URL=redis://...
OPENAI_API_KEY=sk-...
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```