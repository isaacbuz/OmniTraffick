# OmniTraffick: Enterprise AdOps Orchestration Platform
**Master Execution Prompt for OpenClaw / Autonomous Agents**

## Overview
You are an expert autonomous software engineer. Your objective is to build **OmniTraffick**, a next-generation Enterprise AdOps SaaS platform. OmniTraffick sits between media planners (human strategy input) and advertising platforms (Meta, TikTok, Google APIs). It enforces strict data taxonomy, automatically generates complex campaign payloads, executes pre-flight compliance QA, and orchestrates live API deployments.

You will build this system continuously. Do not ask for permission between logical phases if the tests pass. Use your available tools to scaffold the project, write the code, run the tests, and iterate.

## Tech Stack & AI Architecture
*   **Backend / Orchestration:** Python 3.11+, FastAPI, Celery, Redis, SQLAlchemy.
*   **Database:** PostgreSQL (for relational data), Pinecone/Weaviate (Vector DB for RAG).
*   **AI Engine (Agentic Core):** LangChain / LlamaIndex framework. Integration with Gemini 1.5 Pro / GPT-4o for complex reasoning.
*   **Model Context Protocol (MCP):** Implement MCP servers so the AI Agents can securely read real-time Postgres schemas, execute live Meta API calls, and query internal Confluence docs.
*   **Frontend:** Next.js 14+ (App Router), React, TailwindCSS, shadcn/ui.
*   **External Integrations:** Meta Marketing API, TikTok API, Google Ads API.

## Phase 1: Core Database & Governance Engine
**Goal:** Build the strict relational data model that prevents human error.
1. Initialize a Python FastAPI project with SQLAlchemy and Alembic for migrations.
2. Create the Database Schema:
    *   `markets` (id, code, country, region)
    *   `brands` (id, name, internal_code)
    *   `channels` (id, platform_name, api_identifier)
    *   `campaigns` (id, name, brand_id, market_id, budget, status)
    *   `tickets` / `requests` (id, campaign_id, channel_id, request_type, payload_config, status)
3. Build the CRUD REST APIs for these entities.
4. **The Taxonomy Engine:** Implement a Python service that automatically generates the perfect naming string when a ticket is created. 
    *   *Rule:* `[BrandCode]_[Geography]_[Channel]_[Year]_[CampaignName]` 
    *   *Example:* `DIS_US_META_2026_MoanaLaunch`
5. Write `pytest` unit tests asserting that invalid data (unregistered markets, missing brand codes) throws validation errors *before* saving to the DB.

## Phase 2: The EVE Executioner (Payload Builder)
**Goal:** Translate the standardized ticket data into platform-specific JSON payloads.
1. Create a `src/orchestration/translators/` directory.
2. Build an abstract base class `PlatformTranslator`.
3. Implement `MetaTranslator(PlatformTranslator)`:
    *   Write a method `build_campaign_payload(ticket: Ticket)` that outputs the exact JSON required by the Meta Graph API (e.g., `{"name": ticket.taxonomy, "objective": "OUTCOME_TRAFFIC", "status": "PAUSED", "special_ad_categories": []}`).
    *   Write `build_adset_payload()` handling geo-targeting arrays.
4. Implement `TikTokTranslator(PlatformTranslator)` with the distinct JSON schema required by TikTok's Marketing API.
5. Write unit tests ensuring the generated JSON schemas match the official Meta/TikTok documentation requirements based on mocked Ticket inputs.

## Phase 3: The Pre-Flight Safety Net (QA Engine)
**Goal:** Automatically block non-compliant payloads.
1. Create `src/qa/engine.py`.
2. Implement a rules engine that evaluates the generated payloads *before* they are sent to the API queue.
    *   *Rule 1 (Taxonomy Validity):* Does the `name` field strictly match our regex pattern?
    *   *Rule 2 (Brand Safety):* If the brand is marked "Family Friendly", verify that the payload does *not* contain targeting IDs for adult content or alcohol interests.
    *   *Rule 3 (Budget Limits):* Reject any request where daily budget > $100,000.
3. If QA fails, update the Ticket status in PostgreSQL to `"QA_FAILED"` and append the failure reason. If it passes, move to `"READY_FOR_API"`.

## Phase 4: Async Queueing & Live Connectivity (Celery)
**Goal:** Safely orchestrate the API calls using retries and state management.
1. Integrate Celery and Redis into the FastAPI app.
2. Create a Celery task: `deploy_payload_to_platform(ticket_id)`.
3. This task should:
    *   Fetch the ticket and check if status is `"READY_FOR_API"`.
    *   Instantiate the correct translator (Meta/TikTok).
    *   Fire the `POST` request to the platform Sandbox API (use `requests` or `httpx`, pulling API tokens from `.env`).
    *   **Crucial Write-Back:** Capture the `campaign_id` returned by the Meta/TikTok API. Write this external ID back to the OmniTraffick PostgreSQL database to close the loop.
    *   Update ticket status to `"TRAFFICKED_SUCCESS"`.
4. Implement exponential backoff for rate limits (`429 Too Many Requests`).

## Phase 5: The Planner Dashboard & Admin Hub (Frontend UI/UX)
**Goal:** A blazing-fast Next.js UI with distinctly separate experiences for Data Admins (Governance) and Media Planners (Users). The application MUST look premium, avoiding generic generic component libraries. Use `shadcn/ui` combined with Tailwind, incorporating vibrant colors, a modern dark mode, subtle glassmorphism, and micro-animations for high engagement.

### 5.1 Admin UI (The Data Governance Hub)
**UX Philosophy:** Strict, tabular, and authoritative. The Admin dictates what the users can select.
1. Build a specialized `/admin` route protected by Role-Based Access Control (RBAC).
2. **Metadata Management:** Create dedicated data-grid screens (using `TanStack Table`) for `Markets`, `Brands`, and `Channels`.
    *   *UX Detail:* Admins must be able to inline-edit a Market code (e.g., changing `US_EN` to `US_ENG`). If they do, the UI must show a warning modal explaining the downstream impact on future taxonomy.
3. **QA Rules Engine UI:** A visual builder where admins define the "Shield".
    *   *UX Detail:* A logic builder UI (e.g., "IF [Brand] = 'Disney+' THEN [Exclude_Mature] = TRUE"). Needs clear drag-and-drop or visual node elements.

### 5.2 User UI (The Media Planner Dashboard)
**UX Philosophy:** Lightning fast, error-proof, and highly visual. This replaces Excel.
1. **The Campaign Command Center:** A dense, highly scannable data table showing all Active and Draft Campaigns.
    *   *UX Detail:* Implement real-time WebSockets. When a campaign is successfully pushed to the Meta API via Celery, the row should pulse green and the status badge should smoothly transition from `"Pending API"` to `"Live"`.
2. **The Ticket Builder (Error-Proof Creation):**
    *   *UX Detail:* A massive, multi-step slide-out panel (Sheet). Users cannot free-type anywhere. Every input is a searchable dropdown (Combobox) fetching directly from the Admin's PostgreSQL metadata.
    *   *UX Detail:* **Live Taxonomy Preview.** As the user selects "Disney+", "US", and "TikTok", a distinct visual box at the top of the form live-updates to show them the exact programmatic string EVE is building (`DIS_US_TikTok_2026`).
3. **The Kanban Trafficking Board:**
    *   *UX Detail:* A Trello-style board mapping the Orchestrator's state. Columns: `Draft` -> `QA Testing` -> `Trafficking (API)` -> `Live`. Users can drag a `Draft` card into `QA Testing` to instantly trigger the Python validation pipeline.

## Phase 6: The AI Agentic Brain (RAG & MCP)
**Goal:** OmniTraffick is not just a dumb pipe; it is a highly intelligent, proactive AI application. The system shouldn't just run ads—it should *think* about them.
1. **The RAG "Copilot" (Retrieval-Augmented Generation):**
    *   Ingest Disney's massive PDF brand guidelines and historical campaign performance into a Vector Database.
    *   *Feature:* When a user creates a ticket for "Hulu Horror Movie", the AI automatically scans the Vector DB and flashes an alert: *"Warning: Historical data shows Hulu Horror campaigns perform 12% better when TikTok is excluded. Shall I remove TikTok from this draft payload?"*
2. **Model Context Protocol (MCP) Servers:**
    *   Expose the OmniTraffick PostgreSQL database and the Meta API strictly via MCP. 
    *   This prevents the LLM from hallucinating queries. The OmniTraffick AI Agent uses the *exact* MCP tools to dynamically fetch real-time budget pacing ("Agent, why is the Loki campaign under-spending?").
3. **Autonomous "Self-Healing" Trafficking:**
    *   *Feature:* If Celery catches a `400 Bad Request` from the Meta API (e.g., "Invalid Audience ID"), do not just fail. 
    *   The Agent grabs the error log, uses its API Reference MCP to read the Meta Documentation, identifies that the Audience ID was deprecated, rewrites the JSON payload dynamically, and re-submits the Celery task without human intervention.

## Phase 7: Tracking & Conversions API (CAPI) Integration
**Goal:** Close the loop by tracking website events (page views, sign-ups) back to the ad platforms.
1. **Meta Pixel & Front-end Tracking:** Create robust React components in the Next.js frontend to automatically inject the Meta/TikTok Base Pixel code using advanced data layers based on the `campaign_id`.
2. **Conversions API (CAPI) Service Backend:** Build `src/tracking/capi.py`.
    * Implements true server-to-server tracking to bypass browser ad-blockers and iOS 14+ tracking restrictions (ITP).
    * When a conversion occurs on the frontend, it sends a secure payload to the OmniTraffick FastAPI backend, which then sends SHA-256 hashed user data (Email, IP, User Agent) directly to the Meta Conversions API payload.
3. **Event Deduplication:** Ensure all front-end pixel events and back-end CAPI events use identical `event_id` strings so Meta can deduplicate them effectively.

## Phase 7: Tracking & Conversions API (CAPI) Integration\n**Goal:** Close the loop by tracking website events (page views, sign-ups) back to the ad platforms.\n1. **Meta Pixel & Front-end Tracking:** Create robust React components in the Next.js frontend to automatically inject the Meta/TikTok Base Pixel code using advanced data layers based on the `campaign_id`.\n2. **Conversions API (CAPI) Service Backend:** Build `src/tracking/capi.py`.\n    * Implements true server-to-server tracking to bypass browser ad-blockers and iOS 14+ tracking restrictions (ITP).\n    * When a conversion occurs on the frontend, it sends a secure payload to the OmniTraffick FastAPI backend, which then sends SHA-256 hashed user data (Email, IP, User Agent) directly to the Meta Conversions API payload.\n3. **Event Deduplication:** Ensure all front-end pixel events and back-end CAPI events use identical `event_id` strings so Meta can deduplicate them effectively.\n\n## Execution Protocol
*   Begin with Phase 1.
*   Do not move to a subsequent phase until `pytest` shows 100% coverage for the current phase's core logic.
*   Log all major design decisions in an `ARCHITECTURE.md` file within the repo.
*   Use environment variables for all secrets; provide a `.env.example`.

import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="my_api_key",
)

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=20000,
    temperature=1,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "# OmniTraffick: Enterprise AdOps Orchestration Platform\n**Master Execution Prompt for OpenClaw / Autonomous Agents**\n\n## Overview\nYou are an expert autonomous software engineer. Your objective is to build **OmniTraffick**, a next-generation Enterprise AdOps SaaS platform. OmniTraffick sits between media planners (human strategy input) and advertising platforms (Meta, TikTok, Google APIs). It enforces strict data taxonomy, automatically generates complex campaign payloads, executes pre-flight compliance QA, and orchestrates live API deployments.\n\nYou will build this system continuously. Do not ask for permission between logical phases if the tests pass. Use your available tools to scaffold the project, write the code, run the tests, and iterate.\n\n## Tech Stack & AI Architecture\n*   **Backend / Orchestration:** Python 3.11+, FastAPI, Celery, Redis, SQLAlchemy.\n*   **Database:** PostgreSQL (for relational data), Pinecone/Weaviate (Vector DB for RAG).\n*   **AI Engine (Agentic Core):** LangChain / LlamaIndex framework. Integration with Gemini 1.5 Pro / GPT-4o for complex reasoning.\n*   **Model Context Protocol (MCP):** Implement MCP servers so the AI Agents can securely read real-time Postgres schemas, execute live Meta API calls, and query internal Confluence docs.\n*   **Frontend:** Next.js 14+ (App Router), React, TailwindCSS, shadcn/ui.\n*   **External Integrations:** Meta Marketing API, TikTok API, Google Ads API.\n\n## Phase 1: Core Database & Governance Engine\n**Goal:** Build the strict relational data model that prevents human error.\n1. Initialize a Python FastAPI project with SQLAlchemy and Alembic for migrations.\n2. Create the Database Schema:\n    *   `markets` (id, code, country, region)\n    *   `brands` (id, name, internal_code)\n    *   `channels` (id, platform_name, api_identifier)\n    *   `campaigns` (id, name, brand_id, market_id, budget, status)\n    *   `tickets` / `requests` (id, campaign_id, channel_id, request_type, payload_config, status)\n3. Build the CRUD REST APIs for these entities.\n4. **The Taxonomy Engine:** Implement a Python service that automatically generates the perfect naming string when a ticket is created. \n    *   *Rule:* `[BrandCode]_[Geography]_[Channel]_[Year]_[CampaignName]` \n    *   *Example:* `DIS_US_META_2026_MoanaLaunch`\n5. Write `pytest` unit tests asserting that invalid data (unregistered markets, missing brand codes) throws validation errors *before* saving to the DB.\n\n## Phase 2: The EVE Executioner (Payload Builder)\n**Goal:** Translate the standardized ticket data into platform-specific JSON payloads.\n1. Create a `src/orchestration/translators/` directory.\n2. Build an abstract base class `PlatformTranslator`.\n3. Implement `MetaTranslator(PlatformTranslator)`:\n    *   Write a method `build_campaign_payload(ticket: Ticket)` that outputs the exact JSON required by the Meta Graph API (e.g., `{\"name\": ticket.taxonomy, \"objective\": \"OUTCOME_TRAFFIC\", \"status\": \"PAUSED\", \"special_ad_categories\": []}`).\n    *   Write `build_adset_payload()` handling geo-targeting arrays.\n4. Implement `TikTokTranslator(PlatformTranslator)` with the distinct JSON schema required by TikTok's Marketing API.\n5. Write unit tests ensuring the generated JSON schemas match the official Meta/TikTok documentation requirements based on mocked Ticket inputs.\n\n## Phase 3: The Pre-Flight Safety Net (QA Engine)\n**Goal:** Automatically block non-compliant payloads.\n1. Create `src/qa/engine.py`.\n2. Implement a rules engine that evaluates the generated payloads *before* they are sent to the API queue.\n    *   *Rule 1 (Taxonomy Validity):* Does the `name` field strictly match our regex pattern?\n    *   *Rule 2 (Brand Safety):* If the brand is marked \"Family Friendly\", verify that the payload does *not* contain targeting IDs for adult content or alcohol interests.\n    *   *Rule 3 (Budget Limits):* Reject any request where daily budget > $100,000.\n3. If QA fails, update the Ticket status in PostgreSQL to `\"QA_FAILED\"` and append the failure reason. If it passes, move to `\"READY_FOR_API\"`.\n\n## Phase 4: Async Queueing & Live Connectivity (Celery)\n**Goal:** Safely orchestrate the API calls using retries and state management.\n1. Integrate Celery and Redis into the FastAPI app.\n2. Create a Celery task: `deploy_payload_to_platform(ticket_id)`.\n3. This task should:\n    *   Fetch the ticket and check if status is `\"READY_FOR_API\"`.\n    *   Instantiate the correct translator (Meta/TikTok).\n    *   Fire the `POST` request to the platform Sandbox API (use `requests` or `httpx`, pulling API tokens from `.env`).\n    *   **Crucial Write-Back:** Capture the `campaign_id` returned by the Meta/TikTok API. Write this external ID back to the OmniTraffick PostgreSQL database to close the loop.\n    *   Update ticket status to `\"TRAFFICKED_SUCCESS\"`.\n4. Implement exponential backoff for rate limits (`429 Too Many Requests`).\n\n## Phase 5: The Planner Dashboard & Admin Hub (Frontend UI/UX)\n**Goal:** A blazing-fast Next.js UI with distinctly separate experiences for Data Admins (Governance) and Media Planners (Users). The application MUST look premium, avoiding generic generic component libraries. Use `shadcn/ui` combined with Tailwind, incorporating vibrant colors, a modern dark mode, subtle glassmorphism, and micro-animations for high engagement.\n\n### 5.1 Admin UI (The Data Governance Hub)\n**UX Philosophy:** Strict, tabular, and authoritative. The Admin dictates what the users can select.\n1. Build a specialized `/admin` route protected by Role-Based Access Control (RBAC).\n2. **Metadata Management:** Create dedicated data-grid screens (using `TanStack Table`) for `Markets`, `Brands`, and `Channels`.\n    *   *UX Detail:* Admins must be able to inline-edit a Market code (e.g., changing `US_EN` to `US_ENG`). If they do, the UI must show a warning modal explaining the downstream impact on future taxonomy.\n3. **QA Rules Engine UI:** A visual builder where admins define the \"Shield\".\n    *   *UX Detail:* A logic builder UI (e.g., \"IF [Brand] = 'Disney+' THEN [Exclude_Mature] = TRUE\"). Needs clear drag-and-drop or visual node elements.\n\n### 5.2 User UI (The Media Planner Dashboard)\n**UX Philosophy:** Lightning fast, error-proof, and highly visual. This replaces Excel.\n1. **The Campaign Command Center:** A dense, highly scannable data table showing all Active and Draft Campaigns.\n    *   *UX Detail:* Implement real-time WebSockets. When a campaign is successfully pushed to the Meta API via Celery, the row should pulse green and the status badge should smoothly transition from `\"Pending API\"` to `\"Live\"`.\n2. **The Ticket Builder (Error-Proof Creation):**\n    *   *UX Detail:* A massive, multi-step slide-out panel (Sheet). Users cannot free-type anywhere. Every input is a searchable dropdown (Combobox) fetching directly from the Admin's PostgreSQL metadata.\n    *   *UX Detail:* **Live Taxonomy Preview.** As the user selects \"Disney+\", \"US\", and \"TikTok\", a distinct visual box at the top of the form live-updates to show them the exact programmatic string EVE is building (`DIS_US_TikTok_2026`).\n3. **The Kanban Trafficking Board:**\n    *   *UX Detail:* A Trello-style board mapping the Orchestrator's state. Columns: `Draft` -> `QA Testing` -> `Trafficking (API)` -> `Live`. Users can drag a `Draft` card into `QA Testing` to instantly trigger the Python validation pipeline.\n\n## Phase 6: The AI Agentic Brain (RAG & MCP)\n**Goal:** OmniTraffick is not just a dumb pipe; it is a highly intelligent, proactive AI application. The system shouldn't just run ads—it should *think* about them.\n1. **The RAG \"Copilot\" (Retrieval-Augmented Generation):**\n    *   Ingest Disney's massive PDF brand guidelines and historical campaign performance into a Vector Database.\n    *   *Feature:* When a user creates a ticket for \"Hulu Horror Movie\", the AI automatically scans the Vector DB and flashes an alert: *\"Warning: Historical data shows Hulu Horror campaigns perform 12% better when TikTok is excluded. Shall I remove TikTok from this draft payload?\"*\n2. **Model Context Protocol (MCP) Servers:**\n    *   Expose the OmniTraffick PostgreSQL database and the Meta API strictly via MCP. \n    *   This prevents the LLM from hallucinating queries. The OmniTraffick AI Agent uses the *exact* MCP tools to dynamically fetch real-time budget pacing (\"Agent, why is the Loki campaign under-spending?\").\n3. **Autonomous \"Self-Healing\" Trafficking:**\n    *   *Feature:* If Celery catches a `400 Bad Request` from the Meta API (e.g., \"Invalid Audience ID\"), do not just fail. \n    *   The Agent grabs the error log, uses its API Reference MCP to read the Meta Documentation, identifies that the Audience ID was deprecated, rewrites the JSON payload dynamically, and re-submits the Celery task without human intervention.\n\n## Phase 7: Tracking & Conversions API (CAPI) Integration\n**Goal:** Close the loop by tracking website events (page views, sign-ups) back to the ad platforms.\n1. **Meta Pixel & Front-end Tracking:** Create robust React components in the Next.js frontend to automatically inject the Meta/TikTok Base Pixel code using advanced data layers based on the `campaign_id`.\n2. **Conversions API (CAPI) Service Backend:** Build `src/tracking/capi.py`.\n    * Implements true server-to-server tracking to bypass browser ad-blockers and iOS 14+ tracking restrictions (ITP).\n    * When a conversion occurs on the frontend, it sends a secure payload to the OmniTraffick FastAPI backend, which then sends SHA-256 hashed user data (Email, IP, User Agent) directly to the Meta Conversions API payload.\n3. **Event Deduplication:** Ensure all front-end pixel events and back-end CAPI events use identical `event_id` strings so Meta can deduplicate them effectively.\n\n## Execution Protocol\n*   Begin with Phase 1.\n*   Do not move to a subsequent phase until `pytest` shows 100% coverage for the current phase's core logic.\n*   Log all major design decisions in an `ARCHITECTURE.md` file within the repo.\n*   Use environment variables for all secrets; provide a `.env.example`.\n"
                }
            ]
        }
    ]
)
print(message.content)