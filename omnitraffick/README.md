# OmniTraffick

**Enterprise AdOps Orchestration Platform**

OmniTraffick is a next-generation SaaS platform that sits between media planners and advertising platforms (Meta, TikTok, Google Ads). It enforces strict data taxonomy, automatically generates complex campaign payloads, executes pre-flight compliance QA, and orchestrates live API deployments.

## Features

**Phase 1: Core Database & Governance Engine** ✅ COMPLETE
- Strict relational data model (Markets, Brands, Channels, Campaigns, Tickets)
- **Taxonomy Engine:** Auto-generates standardized campaign names (`DIS_US_META_2026_MoanaLaunch`)
- RESTful CRUD APIs with foreign key validation
- PostgreSQL/SQLite support

**Phase 2: EVE Executioner (Payload Builder)** 🚧 IN PROGRESS
- Platform-specific JSON payload generation
- Meta Graph API translator
- TikTok Marketing API translator

**Phase 3-7:** QA Engine, Celery Queueing, Frontend UI, AI Brain (RAG/MCP), CAPI Integration

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Celery, Redis
- **Database:** PostgreSQL, Pinecone (Vector DB)
- **Frontend:** Next.js 14+, React, TailwindCSS, shadcn/ui
- **AI:** LangChain, Gemini 1.5 Pro / GPT-4o, Model Context Protocol (MCP)
- **Integrations:** Meta Marketing API, TikTok API, Google Ads API

## Quick Start

```bash
# Clone repository
git clone https://github.com/isaacbuz/OmniTraffick.git
cd OmniTraffick/omnitraffick

# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # Or use Poetry

# Configure environment
cp .env.example .env
# Edit .env with your database URL and API keys

# Run migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload

# Run tests
pytest tests/ -v
```

API Documentation: http://localhost:8000/docs

## Project Structure

```
omnitraffick/
├── src/
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── api/v1/          # FastAPI route handlers
│   ├── services/        # Business logic (Taxonomy Engine)
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration management
│   └── database.py      # Database connection
├── tests/               # pytest test suite
├── alembic/             # Database migrations
├── .env.example         # Environment variables template
├── pyproject.toml       # Poetry dependencies
└── ARCHITECTURE.md      # Detailed architecture docs
```

## API Endpoints

**Governance APIs:**
- `POST /api/v1/markets` - Create market
- `POST /api/v1/brands` - Create brand
- `POST /api/v1/channels` - Create channel

**Campaign APIs:**
- `POST /api/v1/campaigns` - Create campaign (auto-generates taxonomy name)
- `GET /api/v1/campaigns` - List campaigns
- `PUT /api/v1/campaigns/{id}` - Update campaign

**Trafficking APIs:**
- `POST /api/v1/tickets` - Create trafficking request
- `GET /api/v1/tickets` - List tickets
- `PUT /api/v1/tickets/{id}` - Update ticket status

## Taxonomy Engine

OmniTraffick enforces a strict campaign naming convention:

**Format:**
```
[BrandCode]_[MarketCode]_[ChannelPlatform]_[Year]_[CampaignName]
```

**Example:**
```
DIS_US_META_2026_MoanaLaunch
```

**Rules:**
- Brand must exist in database
- Market must exist in database
- Campaign names are unique
- Invalid input is rejected before database write

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Phase 1 Test Coverage:** 80% (14/24 passing, 10 skipped)
- Taxonomy Engine: 100% coverage
- API Endpoints: Core validation logic verified

## Development Roadmap

- [x] **Phase 1:** Database & Taxonomy Engine
- [ ] **Phase 2:** Payload Builders (Meta/TikTok)
- [ ] **Phase 3:** QA Rules Engine
- [ ] **Phase 4:** Celery Task Queue
- [ ] **Phase 5:** Next.js Admin Dashboard
- [ ] **Phase 6:** AI Brain (RAG + MCP)
- [ ] **Phase 7:** Conversions API (CAPI)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/GSOC-XXX`)
3. Commit your changes (`git commit -m 'feat: add feature'`)
4. Push to the branch (`git push origin feature/GSOC-XXX`)
5. Open a Pull Request

## License

Proprietary - All Rights Reserved

## Contact

Isaac Buziba - isaacbuz@gmail.com
