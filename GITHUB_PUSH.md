# Push to GitHub

Your code is committed locally. To push to GitHub:

## 1. Create a new repository on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Repository name: **omni** (or any name you prefer)
3. Choose **Public**
4. **Do not** add a README, .gitignore, or license (we already have these)
5. Click **Create repository**

## 2. Push your code

If your repo is `https://github.com/aaravmittal2024/omni`:

```bash
cd "C:\Users\aarav\Downloads\omniscient-ai-main (1)\Perplexity Prototype"
git push -u origin main
```

If you used a different repo name, update the remote first:

```bash
git remote set-url origin https://github.com/aaravmittal2024/YOUR-REPO-NAME.git
git push -u origin main
```

## 3. Deploy on Vercel

After the push succeeds:

1. Go to [vercel.com](https://vercel.com)
2. **Add New** → **Project**
3. Import your GitHub repository
4. Add environment variables (see `frontend/.env.example`)
5. Deploy
