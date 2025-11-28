# MarketHawk - Monorepo Structure

## Overview

MarketHawk uses a **monorepo** approach with separate directories for each concern:

```
markethawk/
├── web/               # User-facing website (Next.js)
├── api/               # API server (Express/Fastify)
├── dashboard/         # Admin interface (Next.js)
├── studio/            # Video production (Remotion)
├── insights/          # Analytics & data pipeline
├── shared/            # Shared packages/utilities
├── scripts/           # Deployment & maintenance scripts
└── docs/              # Documentation
```

**Project Names Explained:**
- **web** - Public website users visit (markethawkeye.com)
- **api** - Backend server for all data operations
- **dashboard** - Admin control panel (admin.markethawkeye.com)
- **studio** - Video rendering and production pipeline
- **insights** - Analytics, ETL jobs, recommendations

**Benefits:**
- ✅ Clear separation of concerns
- ✅ Independent deployment (frontend ≠ admin ≠ video generation)
- ✅ Different teams can own different parts
- ✅ Easier testing (test each part independently)
- ✅ Technology flexibility (different stack per directory)

---

## Directory Structure (Detailed)

### Root Level

```
markethawk/
├── web/                         # User-facing website
├── api/                         # API server
├── dashboard/                   # Admin dashboard
├── studio/                      # Video production (Remotion)
├── insights/                    # Data analytics
├── shared/                      # Shared code
│   ├── types/                   # TypeScript types
│   ├── utils/                   # Shared utilities
│   ├── config/                  # Shared configuration
│   └── database/                # Database client & schema
├── scripts/                     # Automation scripts
│   ├── deploy.sh
│   ├── seed-database.ts
│   └── batch-render.sh
├── docs/                        # Documentation
│   ├── PRD.md
│   ├── CLAUDE.md
│   ├── TESTING-INFRASTRUCTURE.md
│   └── DATA-ARCHITECTURE.md
├── .github/                     # GitHub Actions workflows
│   └── workflows/
│       ├── frontend.yml
│       ├── backend.yml
│       ├── admin.yml
│       └── video-generation.yml
├── package.json                 # Root package.json (workspace config)
├── turbo.json                   # Turborepo configuration
├── .env.example                 # Shared environment variables
└── README.md                    # Project overview
```

---

## 1. Frontend (`frontend/`)

**User-facing website** - Earnings videos, charts, subscriptions

### Structure

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── (public)/
│   │   │   ├── page.tsx         # Landing page
│   │   │   └── about/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── [company]/           # Dynamic company pages
│   │   │   └── [slug]/          # Video detail pages
│   │   └── api/                 # Frontend API routes (minimal)
│   ├── components/
│   │   ├── video/
│   │   │   ├── VideoPlayer.tsx
│   │   │   ├── Transcript.tsx
│   │   │   └── RelatedVideos.tsx
│   │   ├── charts/
│   │   │   ├── RevenueChart.tsx
│   │   │   ├── EPSChart.tsx
│   │   │   └── MarginChart.tsx
│   │   ├── ui/                  # shadcn/ui components
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── Footer.tsx
│   ├── lib/
│   │   ├── api-client.ts        # Calls backend API
│   │   └── utils.ts
│   └── hooks/
│       ├── useVideo.ts
│       └── useAuth.ts
├── public/
│   ├── logos/
│   └── images/
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── .env.local
```

### Technology

- **Framework:** Next.js 14+ (App Router)
- **Styling:** TailwindCSS
- **Charts:** Chart.js or Recharts
- **Auth:** Better Auth (configured here)
- **Deployment:** Vercel

### Key Files

```typescript
// frontend/src/lib/api-client.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';

export async function getVideo(slug: string) {
  const res = await fetch(`${API_URL}/api/videos/${slug}`);
  return res.json();
}

export async function getCompany(ticker: string) {
  const res = await fetch(`${API_URL}/api/companies/${ticker}`);
  return res.json();
}
```

---

## 2. Backend (`backend/`)

**API server** - All business logic, database queries, integrations

### Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── videos/
│   │   │   ├── routes.ts        # GET /api/videos/:slug
│   │   │   ├── controller.ts
│   │   │   └── service.ts
│   │   ├── companies/
│   │   │   ├── routes.ts
│   │   │   ├── controller.ts
│   │   │   └── service.ts
│   │   ├── analytics/
│   │   │   └── routes.ts
│   │   └── webhooks/
│   │       ├── stripe.ts
│   │       └── youtube.ts
│   ├── services/
│   │   ├── youtube.ts           # YouTube API integration
│   │   ├── r2.ts                # Cloudflare R2
│   │   ├── stripe.ts            # Stripe payments
│   │   └── email.ts             # Email service
│   ├── lib/
│   │   ├── db.ts                # Database client (Prisma/Drizzle)
│   │   ├── auth.ts              # Better Auth
│   │   └── logger.ts            # Logging
│   ├── middleware/
│   │   ├── auth.ts
│   │   ├── cors.ts
│   │   └── rate-limit.ts
│   └── index.ts                 # Server entry point
├── prisma/
│   └── schema.prisma            # Database schema
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── package.json
├── tsconfig.json
└── .env
```

### Technology

- **Framework:** Express.js or Fastify (or tRPC for type-safety)
- **Database:** Neon PostgreSQL (via Prisma or Drizzle)
- **Validation:** Zod
- **Deployment:** Railway, Render, or AWS ECS

### Key Files

```typescript
// backend/src/api/videos/routes.ts

import {Router} from 'express';
import {getVideo, getVideos, createVideo} from './controller';
import {authMiddleware} from '../../middleware/auth';

const router = Router();

router.get('/', getVideos);
router.get('/:slug', getVideo);
router.post('/', authMiddleware, createVideo);

export default router;
```

```typescript
// backend/src/api/videos/service.ts

import {db} from '../../lib/db';

export async function findVideoBySlug(slug: string) {
  return db.videos.findUnique({
    where: {slug},
    include: {
      company: true,
      earnings_data: true,
      transcripts: true,
    },
  });
}

export async function findRelatedVideos(videoId: string) {
  // Get same company, competitors, industry videos
  // ... complex query logic
}
```

### API Endpoints

```
GET    /api/videos              # List all videos
GET    /api/videos/:slug        # Get video by slug
POST   /api/videos              # Create video (admin only)
PUT    /api/videos/:id          # Update video (admin only)

GET    /api/companies           # List companies
GET    /api/companies/:ticker   # Get company by ticker

GET    /api/analytics/video/:id # Video analytics
GET    /api/analytics/dashboard # Admin dashboard stats

POST   /api/webhooks/stripe     # Stripe webhooks
POST   /api/webhooks/youtube    # YouTube webhooks
```

---

## 3. Admin (`admin/`)

**Admin dashboard** - Separate Next.js app for content management

### Structure

```
admin/
├── src/
│   ├── app/
│   │   ├── page.tsx             # Dashboard home
│   │   ├── videos/
│   │   │   ├── page.tsx         # Video list
│   │   │   └── [id]/
│   │   │       └── page.tsx     # Edit video
│   │   ├── companies/
│   │   │   └── page.tsx         # Manage companies
│   │   ├── analytics/
│   │   │   └── page.tsx         # Deep analytics
│   │   └── settings/
│   │       └── page.tsx         # Admin settings
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── StatsCard.tsx
│   │   │   ├── VideoTable.tsx
│   │   │   └── RealtimeChart.tsx
│   │   └── forms/
│   │       ├── VideoForm.tsx
│   │       └── CompanyForm.tsx
│   └── lib/
│       └── api-client.ts        # Calls backend API
├── package.json
├── next.config.js
└── .env.local
```

### Technology

- **Framework:** Next.js 14+
- **Styling:** TailwindCSS
- **Tables:** TanStack Table
- **Forms:** React Hook Form + Zod
- **Charts:** Recharts or Chart.js
- **Deployment:** Vercel (separate deployment from frontend)

### Key Features

```tsx
// admin/src/app/page.tsx

export default async function AdminDashboard() {
  const stats = await fetch(`${API_URL}/api/analytics/dashboard`).then(r => r.json());

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatsCard
        title="Total Views (24h)"
        value={stats.totalViews}
        change={stats.viewsChange}
      />
      <StatsCard
        title="Click-throughs"
        value={stats.clickThroughs}
        change={stats.clickThroughsChange}
      />
      <StatsCard
        title="Revenue (30d)"
        value={`$${stats.revenue}`}
        change={stats.revenueChange}
      />
      <StatsCard
        title="Active Subscribers"
        value={stats.subscribers}
        change={stats.subscribersChange}
      />

      <div className="col-span-full">
        <h2>Top Videos (24h)</h2>
        <VideoTable videos={stats.topVideos} />
      </div>
    </div>
  );
}
```

---

## 4. Video Generation (`video-generation/`)

**Remotion rendering pipeline** - Separate from web apps

### Structure

```
video-generation/
├── src/
│   ├── compositions/
│   │   ├── Root.tsx             # Remotion root
│   │   ├── index.ts             # Entry point
│   │   └── EarningsVideo/
│   │       ├── index.tsx        # Main composition
│   │       ├── TitleCard.tsx
│   │       ├── ChartSequence.tsx
│   │       ├── TranscriptOverlay.tsx
│   │       └── schema.ts        # Zod schema
│   ├── utils/
│   │   ├── data-fetcher.ts      # Fetch earnings data from backend
│   │   └── chart-generator.ts   # Generate chart images for video
│   └── render/
│       ├── local.ts             # Local rendering
│       └── lambda.ts            # Lambda rendering
├── scripts/
│   ├── batch-render.sh          # Batch rendering script
│   └── upload-to-youtube.ts     # Upload to YouTube
├── public/
│   ├── audio/
│   ├── fonts/
│   └── templates/
├── package.json
├── remotion.config.ts
└── tsconfig.json
```

### Technology

- **Framework:** Remotion 4.0+
- **Rendering:** GPU machine or Lambda
- **Output:** H.264 MP4, 1080p, 30fps

### Key Files

```typescript
// video-generation/src/render/local.ts

import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';

export async function renderVideo(props: EarningsVideoProps) {
  // 1. Bundle Remotion code
  const bundleLocation = await bundle({
    entryPoint: './src/compositions/index.ts',
  });

  // 2. Select composition
  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: 'EarningsVideo',
    inputProps: props,
  });

  // 3. Render video
  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    codec: 'h264',
    outputLocation: `out/${props.ticker}-${props.quarter}-${props.year}.mp4`,
  });

  console.log('✅ Video rendered successfully');
}
```

```bash
# video-generation/scripts/batch-render.sh

#!/bin/bash

# Fetch companies from backend API
COMPANIES=$(curl -s http://localhost:4000/api/companies?quarter=Q4&year=2024)

# Loop through and render each
for row in $(echo "${COMPANIES}" | jq -r '.[] | @base64'); do
  _jq() {
    echo ${row} | base64 --decode | jq -r ${1}
  }

  TICKER=$(_jq '.ticker')
  NAME=$(_jq '.name')

  echo "Rendering $NAME ($TICKER)..."

  npx tsx src/render/local.ts \
    --ticker=$TICKER \
    --company="$NAME" \
    --quarter=Q4 \
    --year=2024

  # Upload to R2
  rclone copy out/${TICKER}-Q4-2024.mp4 \
    markethawkeye:${TICKER}/videos/2024-Q4-full.mp4 -P

  # Upload to YouTube via backend API
  curl -X POST http://localhost:4000/api/videos/upload \
    -F "file=@out/${TICKER}-Q4-2024.mp4" \
    -F "ticker=$TICKER" \
    -F "quarter=Q4" \
    -F "year=2024"
done
```

---

## 5. Analytics (`analytics/`)

**Data pipeline** - ETL jobs, data processing, recommendations

### Structure

```
analytics/
├── src/
│   ├── jobs/
│   │   ├── sync-youtube-analytics.ts
│   │   ├── calculate-recommendations.ts
│   │   └── update-trending.ts
│   ├── etl/
│   │   ├── extract/
│   │   │   ├── youtube.ts
│   │   │   └── stripe.ts
│   │   ├── transform/
│   │   │   └── normalize-data.ts
│   │   └── load/
│   │       └── to-database.ts
│   └── ml/
│       └── recommendation-engine.ts
├── cron/
│   ├── hourly.ts                # Run every hour
│   └── daily.ts                 # Run daily
├── package.json
└── tsconfig.json
```

### Technology

- **Runtime:** Node.js + TypeScript
- **Scheduling:** Cron jobs or AWS EventBridge
- **Queue:** BullMQ (if needed)
- **Deployment:** Background workers on Railway/Render

### Key Jobs

```typescript
// analytics/src/jobs/sync-youtube-analytics.ts

import {db} from '@markethawk/shared/database';
import {getVideoAnalytics} from '../../../backend/src/services/youtube';

export async function syncYouTubeAnalytics() {
  const videos = await db.videos.findMany({
    where: {status: 'published'},
  });

  for (const video of videos) {
    const analytics = await getVideoAnalytics(video.youtube_id);

    await db.videos.update({
      where: {id: video.id},
      data: {
        views_count: analytics.views,
        likes_count: analytics.likes,
        comments_count: analytics.comments,
        watch_time_minutes: analytics.watchTime,
      },
    });
  }

  console.log(`✅ Synced analytics for ${videos.length} videos`);
}
```

```typescript
// analytics/src/jobs/calculate-recommendations.ts

export async function calculateRecommendations() {
  const videos = await db.videos.findMany({include: {company: true}});

  for (const video of videos) {
    // 1. Same company videos
    const sameCompany = await db.videos.findMany({
      where: {
        company_id: video.company_id,
        id: {not: video.id},
      },
      take: 5,
      orderBy: {call_date: 'desc'},
    });

    // 2. Competitor videos
    const competitors = await getCompetitorVideos(video);

    // 3. Trending in industry
    const trending = await getTrendingInIndustry(video.company.industry);

    // 4. Save recommendations
    await db.video_recommendations.createMany({
      data: [
        ...sameCompany.map(v => ({
          video_id: video.id,
          recommended_video_id: v.id,
          recommendation_type: 'same_company',
          score: 100,
        })),
        ...competitors.map((v, i) => ({
          video_id: video.id,
          recommended_video_id: v.id,
          recommendation_type: 'competitor',
          score: 90 - i * 10,
        })),
        // ... etc
      ],
    });
  }
}
```

---

## 6. Shared (`shared/`)

**Shared code** - Types, utilities, database client

### Structure

```
shared/
├── types/
│   ├── video.ts
│   ├── company.ts
│   ├── user.ts
│   └── index.ts
├── utils/
│   ├── format-currency.ts
│   ├── calculate-growth.ts
│   └── index.ts
├── config/
│   ├── constants.ts
│   └── env.ts
├── database/
│   ├── client.ts            # Prisma/Drizzle client
│   └── schema.prisma        # Database schema
└── package.json
```

### Usage in Other Packages

```typescript
// frontend/src/app/page.tsx

import {formatCurrency} from '@markethawk/shared/utils';
import {Video} from '@markethawk/shared/types';

const revenue = formatCurrency(89500000000); // "$89.5B"
```

```json
// frontend/package.json

{
  "dependencies": {
    "@markethawk/shared": "*"
  }
}
```

---

## Workspace Configuration (Turborepo)

### Root `package.json`

```json
{
  "name": "markethawk",
  "private": true,
  "workspaces": [
    "frontend",
    "backend",
    "admin",
    "video-generation",
    "analytics",
    "shared/*"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "deploy": "turbo run deploy"
  },
  "devDependencies": {
    "turbo": "latest",
    "typescript": "^5.0.0"
  }
}
```

### `turbo.json`

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "dev": {
      "cache": false,
      "persistent": true
    },
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "deploy": {
      "dependsOn": ["build", "test"],
      "cache": false
    }
  }
}
```

---

## Deployment Strategy

### Separate Deployments

```
frontend/        → Vercel (markethawkeye.com)
admin/           → Vercel (admin.markethawkeye.com)
backend/         → Railway or AWS ECS (api.markethawkeye.com)
video-generation → GPU machine (local) or Lambda
analytics/       → Railway (background workers)
```

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/frontend.yml

name: Frontend

on:
  push:
    paths:
      - 'frontend/**'
      - 'shared/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm test --workspace=frontend

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: amondnet/vercel-action@v20
        with:
          working-directory: ./frontend
```

---

## Development Workflow

### Start All Services

```bash
# Root directory
npm run dev

# Starts:
# - frontend (localhost:3000)
# - backend (localhost:4000)
# - admin (localhost:3001)
```

### Work on Single Service

```bash
# Only frontend
npm run dev --filter=frontend

# Only backend
npm run dev --filter=backend
```

### Run Tests

```bash
# All tests
npm run test

# Single workspace
npm run test --filter=backend
```

---

## Summary

**Monorepo Structure Benefits:**

✅ **Separation of Concerns**
- Frontend, backend, admin are independent
- Video generation is isolated
- Analytics runs separately

✅ **Independent Deployment**
- Deploy frontend without touching backend
- Update admin without affecting users
- Video rendering doesn't block deployments

✅ **Shared Code Reuse**
- Types, utilities shared across all projects
- Database client used by backend + analytics
- No code duplication

✅ **Technology Flexibility**
- Different stack per directory if needed
- Frontend can use different Node version than backend

✅ **Easier Testing**
- Test each part independently
- Smaller test suites per workspace
- Faster CI/CD

This structure mirrors VideotoBe platform and scales to 100+ engineers.
