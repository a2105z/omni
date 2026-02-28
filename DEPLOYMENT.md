# Deploying Omni to Vercel

## Quick Deploy

1. **Push to GitHub** (or GitLab, Bitbucket)

2. **Import on Vercel**
   - Go to [vercel.com](https://vercel.com) → **Add New** → **Project**
   - Import your repository
   - **Important:** Set **Root Directory** to `frontend` (click Edit next to it and enter `frontend`)
   - Vercel will auto-detect Next.js

3. **Add environment variables** (Vercel → Project → Settings → Environment Variables):

   | Variable | Required | Description |
   |----------|----------|-------------|
   | `OPENAI_API_KEY` | ✓ | OpenAI API key for synthesis, fallbacks |
   | `BRAVE_API_KEY` | ✓ | Brave Search API for web & image search |
   | `CEREBRAS_API_KEY` | ✓ (or 2/3) | Cerebras for query optimization |
   | `GROQ_API_KEY` | ✓ (or 2/3) | Groq for follow-ups, session titles |
   | `CEREBRAS_API_KEY2`, `CEREBRAS_API_KEY3` | Optional | Fallbacks for Cerebras |
   | `GROQ_API_KEY2`, `GROQ_API_KEY3` | Optional | Fallbacks for Groq |
   | `BACKEND_URL` | Optional | Phase 3 backend URL (for indexed search pipeline) |
   | `FIRECRAWL_API_KEY` | Optional | Firecrawl for advanced scraping |

   See `frontend/.env.example` for the full list.

4. **Deploy** – Vercel will build and deploy. Your app will be live at `https://[project-name].vercel.app`.

---

## Build Configuration

The project uses `vercel.json` at the repo root. **Set Root Directory to `frontend`** in Vercel project settings (the Next.js app lives there).

- **Install**: `npm install --legacy-peer-deps`
- **Build**: `npm run build`

---

## Verify Build Locally

```bash
npm install --legacy-peer-deps
npm run build
npm run start
```

---

## Optional: Phase 3 Backend

Omni works with the legacy pipeline (Brave + scrape) out of the box. To use the **Phase 3 backend** (indexed search + synthesis):

1. Deploy the backend separately (Railway, Render, Fly.io, etc.)
2. Add `BACKEND_URL=https://your-backend-url.com` in Vercel
3. Redeploy the frontend

---

## Optional: GitHub Pages Redirect

To host a redirect page on GitHub Pages that points to your Vercel deployment:

1. Enable GitHub Pages: **Settings** → **Pages** → Source: **Deploy from a branch**
2. Branch: `main`, Folder: `/ (root)` or `/docs`
3. Add `docs/index.html` with a meta refresh or JavaScript redirect to your Vercel URL
