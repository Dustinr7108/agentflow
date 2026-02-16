# Deployment Guide

## Option 1: Railway (Recommended - $5-20/month)

1. Push to GitHub
2. Go to railway.app, connect your repo
3. Add PostgreSQL + Redis services
4. Set environment variables from .env.example
5. Deploy - Railway auto-detects Dockerfile

## Option 2: Vercel + Railway Split

- Frontend: Deploy /frontend to Vercel (free)
- Backend: Deploy root to Railway ($5/month)
- Database: Neon.tech (free tier)
- Redis: Upstash (free tier)

## Option 3: VPS (DigitalOcean/Hetzner - $6-12/month)

```bash
# On your VPS
git clone your-repo
cp .env.example .env
# Edit .env
docker-compose up -d
```

## Environment Variables (Required)

```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=random-string-here
OPENAI_API_KEY=sk-...  (or ANTHROPIC_API_KEY or OLLAMA_BASE_URL)
```

## Environment Variables (Optional - for billing)

```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STARTER=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ENTERPRISE=price_...
```
