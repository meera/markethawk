# DEPLOYMENT.md

Deployment guide for MarketHawk web application and infrastructure.

---

## Overview

MarketHawk deployment consists of:
1. **Web App** - Next.js on Vercel
2. **Database** - PostgreSQL (Neon, Supabase, or self-hosted)
3. **Storage** - Cloudflare R2 (videos, thumbnails, transcripts)
4. **Video Processing** - Sushi GPU machine (on-premise)

---

## Environment Variables

### Production Environment Variables

```bash
# Database
DATABASE_URL="postgresql://user:password@host:5432/markethawk?sslmode=require"

# Better Auth
AUTH_SECRET="<generate with: openssl rand -base64 32>"
AUTH_GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
AUTH_GOOGLE_CLIENT_SECRET="xxx"
NEXT_PUBLIC_GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"

# Stripe
STRIPE_SECRET_KEY="sk_live_..."
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
STRIPE_PRICE_ID_PRO="price_..."
STRIPE_PRICE_ID_TEAM="price_..."

# YouTube
YOUTUBE_API_KEY="..."
YOUTUBE_CLIENT_ID="..."
YOUTUBE_CLIENT_SECRET="..."
YOUTUBE_REFRESH_TOKEN="..."

# Cloudflare R2
R2_ACCOUNT_ID="..."
R2_ACCESS_KEY_ID="..."
R2_SECRET_ACCESS_KEY="..."
R2_BUCKET_NAME="markethawk"
R2_PUBLIC_URL="https://pub-{hash}.r2.dev"

# Email (Resend)
RESEND_API_KEY="re_..."

# Analytics (optional)
NEXT_PUBLIC_GA_ID="G-..."
NEXT_PUBLIC_POSTHOG_KEY="phc_..."

# App Config
NEXT_PUBLIC_APP_URL="https://markethawkeye.com"
```

---

## Vercel Deployment

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Link Project

```bash
cd ~/markethawk
vercel link
```

### 3. Set Environment Variables

```bash
# Set production environment variables
vercel env add DATABASE_URL
vercel env add AUTH_SECRET
vercel env add STRIPE_SECRET_KEY
# ... (add all env vars from above)
```

### 4. Deploy

```bash
# Deploy to production
vercel --prod
```

### 5. Configure Custom Domain

```bash
vercel domains add markethawkeye.com
```

**DNS Configuration:**
- Add CNAME record: `markethawkeye.com` → `cname.vercel-dns.com`
- Add A record for root domain (if needed)

---

## Database Setup (PostgreSQL)

### Option 1: Neon (Serverless Postgres)

**Pros:**
- Serverless (auto-scaling)
- Free tier (500 MB)
- Branch-based development

**Setup:**
1. Create account at [neon.tech](https://neon.tech)
2. Create new project: `markethawk`
3. Copy connection string
4. Run migrations:

```bash
DATABASE_URL="postgresql://..." npx drizzle-kit push:pg
```

### Option 2: Supabase

**Pros:**
- Free tier (500 MB)
- Built-in auth (can replace Better Auth)
- Realtime subscriptions

**Setup:**
1. Create project at [supabase.com](https://supabase.com)
2. Copy connection string (in project settings → Database)
3. Run migrations

### Option 3: Self-Hosted

**Setup:**
```bash
# On production server
docker run -d \
  --name postgres \
  -e POSTGRES_DB=markethawk \
  -e POSTGRES_USER=markethawk \
  -e POSTGRES_PASSWORD=<secure-password> \
  -p 5432:5432 \
  postgres:15
```

---

## Cloudflare R2 Setup

### 1. Create R2 Bucket

1. Go to Cloudflare dashboard → R2
2. Create bucket: `markethawk`
3. Enable public access (for videos/thumbnails)

### 2. Generate Access Keys

1. R2 → Manage R2 API Tokens
2. Create API token with `Read` and `Write` permissions
3. Copy Access Key ID and Secret Access Key

### 3. Configure rclone (for uploads)

```bash
rclone config

# Choose: n (new remote)
# Name: r2-markethawk
# Type: s3
# Provider: Cloudflare
# Access Key ID: <from step 2>
# Secret Access Key: <from step 2>
# Endpoint: https://<account_id>.r2.cloudflarestorage.com
```

---

## Stripe Setup

### 1. Create Stripe Account

1. Sign up at [stripe.com](https://stripe.com)
2. Activate account (provide business details)

### 2. Create Products

**Pro Plan:**
- Name: MarketHawk Pro
- Price: $29/month
- Copy Price ID → `STRIPE_PRICE_ID_PRO`

**Team Plan:**
- Name: MarketHawk Team
- Price: $99/month
- Copy Price ID → `STRIPE_PRICE_ID_TEAM`

### 3. Configure Webhook

1. Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://markethawkeye.com/api/webhooks/stripe`
3. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy webhook signing secret → `STRIPE_WEBHOOK_SECRET`

---

## YouTube API Setup

### 1. Create Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project: `markethawk`
3. Enable APIs:
   - YouTube Data API v3
   - YouTube Analytics API

### 2. Create OAuth Credentials

1. APIs & Services → Credentials
2. Create OAuth 2.0 Client ID
3. Application type: Web application
4. Authorized redirect URIs: `http://localhost:3000/oauth/callback`
5. Copy Client ID and Client Secret

### 3. Get Refresh Token

```bash
# Use YouTube OAuth helper script
cd ~/markethawk
source .venv/bin/activate
python lens/scripts/youtube_oauth.py
```

---

## SSL/TLS Certificate

**Vercel handles SSL automatically** for custom domains.

If self-hosting:

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d markethawkeye.com
```

---

## Monitoring & Alerts

### Vercel Analytics

Enable in Vercel dashboard → Project → Analytics

### Error Tracking (Sentry)

```bash
npm install @sentry/nextjs
npx @sentry/wizard -i nextjs
```

### Uptime Monitoring (UptimeRobot)

1. Create account at [uptimerobot.com](https://uptimerobot.com)
2. Add monitor: `https://markethawkeye.com`
3. Set alert email

---

## Backup Strategy

### Database Backups

**Automated (Neon/Supabase):**
- Daily automatic backups (retained for 7 days)

**Manual Backup:**
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### R2 Backups

```bash
# Backup entire bucket
rclone copy r2-markethawk:markethawk ~/backups/r2/

# Scheduled backup (cron)
0 2 * * * rclone sync r2-markethawk:markethawk ~/backups/r2/
```

---

## CI/CD Pipeline

### GitHub Actions (Example)

```yaml
# .github/workflows/deploy.yml

name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install
      - run: npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

---

## Security Checklist

**Before Production:**

- [ ] Enable HTTPS (handled by Vercel)
- [ ] Set `AUTH_SECRET` to secure random value
- [ ] Enable Stripe webhook signature verification
- [ ] Set CORS headers on R2 bucket (if needed)
- [ ] Enable rate limiting on API routes
- [ ] Set up CSP headers in `next.config.js`
- [ ] Validate all user inputs with Zod
- [ ] Enable 2FA for admin accounts
- [ ] Configure allowed redirect URIs for OAuth

---

## Performance Optimization

### Next.js Configuration

```javascript
// next.config.js

module.exports = {
  images: {
    domains: ['pub-xxx.r2.dev', 'i.ytimg.com'],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizeCss: true,
  },
  compress: true,
};
```

### Enable CDN Caching

```typescript
// app/[company]/[slug]/page.tsx

// ISR: Revalidate every hour
export const revalidate = 3600;
```

---

## Troubleshooting

### Deployment Fails

**Check:**
- All environment variables set in Vercel
- Build logs in Vercel dashboard
- TypeScript errors: `npm run type-check`

### Database Connection Issues

**Check:**
- Connection string format
- SSL mode (`?sslmode=require` for production)
- Firewall rules (allow Vercel IP ranges)

### YouTube Upload Fails

**Check:**
- API quota (10,000 units/day)
- OAuth refresh token valid
- Video file size (<128 GB)

---

## Related Documentation

- **WEB-APP-GUIDE.md** - Application setup
- **DATABASE-SCHEMA.md** - Database migrations
- **ADMIN-DASHBOARD.md** - Monitoring setup

---

**Last Updated:** 2025-11-10
