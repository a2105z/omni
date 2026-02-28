# Phase 3: Synthesis & AI (Steps 11–15)

Phase 3 adds the full Perplexity-style synthesis pipeline to the Omni backend.

## Summary

| Step | Module | Description |
|------|--------|-------------|
| 11 | `context/` | Context assembly – aggregate top N sources, token budget, section structure |
| 12 | `synthesis/` | Citation-aware synthesizer – streaming LLM with `[1](url)` format |
| 13 | `focus_modes/` | Focus modes – General, Academic, Code, Writing |
| 14 | `followup/` | Follow-up queries, session title generation |
| 15 | `image_search/` | Brave image search + optional vision descriptions |

---

## Step 11 — Context Assembly

**Path:** `backend/app/modules/context/`

- `TextSource` / `ImageSource` dataclasses
- `ContextAssemblyService.assemble()`:
  - Takes text sources and optional image sources
  - Truncates by token budget (`CONTEXT_MAX_TOKENS`, default 12k)
  - Structure: `Source 1 (url): title\ncontent`, `Image Source N (url): title\nsummary`

---

## Step 12 — Citation-Aware Synthesizer

**Path:** `backend/app/modules/synthesis/`

- Streaming answer via OpenAI with strict citation rules
- Format: `[number](url)` at end of supported claims
- Fallback when no sources: "I don't have any sources to answer..."
- Uses focus mode prompts

---

## Step 13 — Focus Modes

**Path:** `backend/app/modules/focus_modes/`

Modes: `general`, `academic`, `code`, `writing`

- Mode-specific system prompts (formal for Academic, code blocks for Code, etc.)
- Source quality: Academic mode boosts `.edu` / `.ac` domains

---

## Step 14 — Follow-up & Session

**Path:** `backend/app/modules/followup/`

- `generate_follow_ups()`: follow-up search queries from response + expanded queries
- `generate_session_title()`: short title from first query
- Requires `OPENAI_API_KEY`

---

## Step 15 — Image Search Pipeline

**Path:** `backend/app/modules/image_search/`

- Brave image search via `BRAVE_API_KEY`
- `ImageResult`: img_url, title, summary, page_url
- Optional `describe_with_vision()` for image descriptions (OpenAI gpt-4o-mini)

---

## API

### POST /api/answer

Full Phase 3 pipeline: search → context assembly → streaming synthesis.

**Request body:**
```json
{
  "query": "What is FastAPI?",
  "mode": "general",
  "limit": 10,
  "session_id": "optional",
  "history": [],
  "include_images": true
}
```

**Response:** Server-Sent Events (SSE)

- `event: meta` – sources, image_sources, processed_query
- `event: chunk` – streaming text fragments
- `event: done` – follow_ups
- `event: error` – error message

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CONTEXT_MAX_TOKENS` | 12000 | Max context size for assembly |
| `SYNTHESIS_MODEL` | gpt-4o-mini | LLM for synthesis |
| `FOLLOWUP_NUM_QUERIES` | 5 | Number of follow-up suggestions |
| `BRAVE_API_KEY` | - | For image search |
| `IMAGE_SEARCH_MAX_RESULTS` | 5 | Max image results |
| `ENABLE_IMAGE_SEARCH` | true | Toggle image search |
| `OPENAI_API_KEY` | - | Required for synthesis + follow-ups |

---

## Frontend Integration

Set `BACKEND_URL` (e.g. `http://localhost:8000`) to proxy through `/api/answer`:

```bash
# .env.local
BACKEND_URL=http://localhost:8000
```

The frontend `/api/answer` route proxies to the backend when `BACKEND_URL` is set.
