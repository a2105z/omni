# Omni

Omni is an AI search engine that combines web search, image search, and AI synthesis to deliver comprehensive answers with source citations.

## Features

- **Smart Search Query Optimization**: Cerebras (llama-3.1-8b) / OpenAI (gpt-4o-mini) — Automatically refines your search queries
- **Comprehensive Web Search**: Brave Search API, custom webscraping with HTML-to-Markdown conversion
- **Intelligent Image Search**: Cerebras for query optimization, Brave for images, Groq vision for descriptions
- **Detailed Content Summaries**: Cerebras (llama-3.3-70b/3.1-70b) / OpenAI for focused summaries
- **AI-Powered Synthesis**: OpenAI (gpt-4o-mini) for final answer generation with citations
- **Follow-up Questions**: Groq / OpenAI for relevant follow-up queries
- **Session Management**: Groq for session title generation
- **Real-time Updates**: Live search and processing progress
- **Source Attribution**: Clear links to and credits for original sources
- **Parallel Processing**: Efficient processing of multiple search results

## Deploy (Vercel)

Omni requires a server (API routes, Server Actions). Deploy to [Vercel](https://vercel.com) (free):

1. Push to GitHub
2. Import the repo at [vercel.com](https://vercel.com)
3. Add env vars (see [DEPLOYMENT.md](./DEPLOYMENT.md) or `frontend/.env.example`)
4. Deploy

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for step-by-step instructions.

---

## Project Structure (Monorepo)

```
omni/
├── frontend/     # Next.js UI (existing Omni)
├── backend/      # Python FastAPI (Phase 1 search pipeline)
└── packages/shared/  # Shared types
```

See [PHASE1_README.md](./PHASE1_README.md) for the Phase 1 pipeline (crawler, parser, indexer, vector store).

## Getting Started

### Prerequisites

- Node.js 22.x or higher
- Python 3.11+
- npm or pnpm

### Installation

1. Clone the repository
2. From root: `npm install --legacy-peer-deps` (installs frontend + shared)
3. Backend (optional): `cd backend && pip install -r requirements.txt`
4. Copy `frontend/.env.example` to `frontend/.env.local` and add your API keys

See `frontend/.env.example` for the full list of variables.

### Running locally

**Frontend** (Next.js):
```bash
npm run dev
```

**Backend** (FastAPI, optional for Phase 1 pipeline):
```bash
cd backend && uvicorn app.main:app --reload
```
API: http://localhost:8000

## Tech Stack

- **Next.js 15** — React framework
- **React 19** — UI library
- **shadcn/ui** — Radix UI + Tailwind CSS components
- **OpenAI, Groq, Cerebras** — AI providers
- **Brave Search API** — Web and image search
- **React Markdown, KaTeX** — Markdown and math rendering
- **Zod** — Schema validation
- **Axios** — HTTP client
