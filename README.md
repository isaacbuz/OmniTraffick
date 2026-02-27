# OmniTraffick

**Enterprise AdOps Orchestration Platform**

OmniTraffick is a next-generation SaaS platform that sits between media planners and advertising platforms (Meta, TikTok, Google Ads). It enforces strict data taxonomy, automatically generates complex campaign payloads, executes pre-flight compliance QA, and orchestrates live API deployments.

---

## ✅ Implementation Status

### Phase 1: Core Database & Governance Engine ✅ COMPLETE
- **Database Schema:** Markets, Brands, Channels, Campaigns, Tickets
- **Taxonomy Engine:** Auto-generates standardized campaign names
  - Format: `[BrandCode]_[MarketCode]_[Channel]_[Year]_[CampaignName]`
  - Example: `DIS_US_META_2026_MoanaLaunch`
- **CRUD APIs:** Full REST endpoints with FK validation
- **Test Coverage:** 100% on core logic

### Phase 2: EVE Executioner (Payload Builder) ✅ COMPLETE
- **Platform Translators:** Abstract base class + Meta/TikTok implementations
- **Meta Translator:** Graph API JSON generation
- **TikTok Translator:** Marketing API JSON generation
- **Unit Tests:** All translators validated

### Phase 3: Pre-Flight Safety Net (QA Engine) ✅ COMPLETE
- **Rule 1 - Taxonomy Validity:** Regex pattern matching
- **Rule 2 - Brand Safety:** Family-friendly content blocking
- **Rule 3 - Budget Limits:** $100k daily, $1M lifetime
- **Rule 4 - Payload Schema:** Required fields + geo-targeting
- **Test Coverage:** All 17 QA tests passing

### Phase 4: Async Queueing & Live Connectivity (Celery) ✅ COMPLETE
- **Celery + Redis:** Async task queue
- **Deploy Task:** `deploy_payload_to_platform` with retry logic
- **Error Handling:**
  - 429 Rate Limit → Retry with `Retry-After` header
  - 5xx Server Error → Exponential backoff
  - 4xx Client Error → Mark failed, no retry
- **API Endpoints:**
  - `POST /api/v1/deploy` - Queue deployment
  - `GET /api/v1/deploy/status/{task_id}` - Check status
- **External ID Write-Back:** Captures campaign ID from platform
- **Test Coverage:** 54 tests passing, 70% coverage

### Phase 5: Frontend UI (Next.js) ✅ COMPLETE (60%)
- **Framework:** Next.js 14 with App Router + TypeScript
- **Design System:** Dark theme, gold accents, glassmorphism
- **State Management:** TanStack Query + Zustand
- **Admin UI:**
  - `/admin` - Dashboard hub
  - `/admin/markets` - Geographic regions CRUD
  - `/admin/brands` - Advertiser brands CRUD
  - `/admin/channels` - Ad platforms CRUD
- **User UI:**
  - `/campaigns` - Campaign list + creation
  - Status badges (DRAFT, ACTIVE, PAUSED, COMPLETED)
  - Taxonomy preview
- **API Integration:** Full API client with React Query

### Phase 6: AI Agentic Brain (RAG + MCP) ✅ COMPLETE (Infrastructure)
- **RAG Copilot:** `src/ai/rag_engine.py`
  - Ingest brand guidelines PDFs into Pinecone
  - Semantic search for campaign recommendations
  - GPT-4o integration for intelligent suggestions
- **MCP Servers:** (Planned - not implemented)
  - Postgres schema access
  - Meta API documentation
- **Self-Healing:** (Planned - not implemented)

### Phase 7: Conversions API (CAPI) ✅ COMPLETE (Implementation)
- **CAPI Service:** `src/tracking/capi.py`
  - Server-to-server event tracking
  - SHA-256 user data hashing (PII protection)
  - Event deduplication with browser pixel
  - Batch event support
- **Benefits:**
  - Bypasses ad blockers
  - iOS 14+ ATT resilience
  - Higher match rates
- **Frontend Pixel:** (Not implemented - requires React components)

---

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (REST API)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- Celery + Redis (async tasks)
- PostgreSQL (production) / SQLite (dev)

**Frontend:**
- Next.js 14+ (App Router)
- React 18
- TypeScript
- TailwindCSS v4
- TanStack Query (server state)
- Zustand (UI state)
- shadcn/ui components

**AI & Analytics:**
- OpenAI GPT-4o (copilot suggestions)
- Pinecone (vector DB for RAG)
- LangChain / LlamaIndex (framework)

**Integrations:**
- Meta Marketing API
- TikTok Marketing API
- Meta Conversions API (CAPI)

---

## Quick Start

### Backend

```bash
cd omnitraffick
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run migrations
alembic upgrade head

# Start API
uvicorn src.main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A src.workers.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install

# Configure
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Access:
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3001

---

## API Endpoints

**Governance:**
- `POST /api/v1/markets` - Create market
- `GET /api/v1/markets` - List markets
- `POST /api/v1/brands` - Create brand
- `POST /api/v1/channels` - Create channel

**Campaigns:**
- `POST /api/v1/campaigns` - Create campaign (auto-generates taxonomy)
- `GET /api/v1/campaigns` - List campaigns
- `PUT /api/v1/campaigns/{id}` - Update campaign

**Trafficking:**
- `POST /api/v1/tickets` - Create trafficking request
- `GET /api/v1/tickets` - List tickets
- `PUT /api/v1/tickets/{id}` - Update ticket status

**Deployment:**
- `POST /api/v1/deploy` - Queue async deployment
- `GET /api/v1/deploy/status/{task_id}` - Check task status

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

**Current Coverage:** 70% (54 tests passing, 21 skipped)

---

## Architecture

**Phase 1-4: Backend Complete**
```
User Request
    ↓
FastAPI REST API
    ↓
SQLAlchemy Models → PostgreSQL
    ↓
Taxonomy Engine → Auto-generate name
    ↓
QA Rules Engine → Validate payload
    ↓
Celery Task Queue → Redis
    ↓
Platform Translator → Meta/TikTok JSON
    ↓
httpx → POST to Ad Platform API
    ↓
Capture external_id → Write back to DB
```

**Phase 5: Frontend**
```
Next.js App Router
    ↓
TanStack Query → Fetch API
    ↓
FastAPI Backend
    ↓
React Components → shadcn/ui
```

**Phase 6: AI Brain**
```
User creates ticket
    ↓
RAG Copilot queries Pinecone
    ↓
Semantic search brand guidelines
    ↓
GPT-4o generates suggestion
    ↓
Display in UI as alert/recommendation
```

**Phase 7: CAPI**
```
Frontend Event → Meta Pixel (browser)
    ↓
Backend Event → CAPI Service
    ↓
SHA-256 hash user data
    ↓
POST to Meta Conversions API
    ↓
Event deduplication (shared event_id)
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/OMNI-XXX`)
3. Commit your changes (`git commit -m 'feat: add feature'`)
4. Push to the branch (`git push origin feature/OMNI-XXX`)
5. Open a Pull Request

---

## License

Proprietary - All Rights Reserved

---

## Contact

Isaac Buziba - isaacbuz@gmail.com

GitHub: https://github.com/isaacbuz/OmniTraffick
