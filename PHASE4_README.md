# Phase 4: Frontend & Polish (Steps 16–20)

Phase 4 completes the Omni frontend with search-first UX, streaming answers, source panel, session management, and production polish.

---

## Step 16 — Search-First UI

**Features:**
- **Search input** with prominent placement on empty state
- **Focus mode selector** (General, Academic, Code, Writing) in the top bar
- **Empty state** with suggested prompts (e.g. "What is quantum computing?")
- **Debounced** input behavior via controlled state

**Files:** `app/page.tsx`, `components/ui/focus-mode-selector.tsx`, `lib/constants.ts`

---

## Step 17 — Answer Streaming UI

**Features:**
- **SSE streaming** for answers (via backend `/api/answer` or legacy pipeline)
- **Progressive citations** – `[1](url)` rendered with hover preview
- **Source cards** – expandable in SourcePanel
- **Math (KaTeX)** and **code syntax highlighting** (Prism oneDark)

**Files:** `components/ui/chat/markdown-content.tsx`, `components/ui/chat/ai-response-view.tsx`

---

## Step 18 — Source Panel & Citations

**Features:**
- **Numbered citations** in text with `[1]` format
- **Sources sidebar** with metadata (title, domain, snippet)
- **Expandable summaries** – click to expand/collapse
- **"Read more"** link to original URL
- **Trust signals** – badges for .edu, .gov, .ac, and verified domains

**Files:** `components/ui/chat/source-panel.tsx`, `components/ui/chat/markdown-content.tsx`

---

## Step 19 — Session & Chat UX

**Features:**
- **Multi-turn chat** – full conversation history
- **Editable messages** – click to edit and re-run
- **Regenerate** – retry button on each answer
- **Session sidebar** – list of messages and previous sessions
- **Keyboard shortcuts** – `⌘K` / `Ctrl+K` for new chat
- **Export** – download session as Markdown

**Files:** `lib/chat/chat-context.tsx`, `app/page.tsx`

---

## Step 20 — Polish & Production

**Features:**
- **Error states** – inline error message with Retry button
- **Loading** – streaming progress, cancel (X) during generation
- **Dark mode** – theme toggle (Sun/Moon) with persistence
- **Mobile layout** – responsive sidebar, collapsible on small screens
- **Rate limiting** – backend middleware (60 req/min per IP)
- **Basic security** – CORS, rate limits

**Backend:** `app/core/rate_limit.py`, `app/main.py`  
**Frontend:** `components/ui/theme-provider.tsx`, `components/ui/skeleton.tsx`

---

## New Dependencies

- `react-syntax-highlighter` – code blocks
- `@types/react-syntax-highlighter` – Types

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_REQUESTS` | 60 | Max requests per window |
| `RATE_LIMIT_WINDOW` | 60 | Window in seconds |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift+Enter` | New line |
| `⌘K` / `Ctrl+K` | New chat |
