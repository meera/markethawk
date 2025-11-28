# CLAUDE.md

Guidance for Claude Code when working with MarketHawk repository.

---

## Project: MarketHawk

**Website:** [markethawkeye.com](https://markethawkeye.com)

### Overview
MarketHawk transforms earnings call audio into visually-enhanced YouTube videos with an interactive SaaS web platform.

**Monetization Strategy:**
1. Sell SaaS subscriptions
2. YouTube monetization (ad revenue)
3. Enterprise orders from companies

**Core Value:**
- Fantastic visually appealing videos from boring earnings calls
- Automated pipeline at scale (1000+ companies, every quarter)
- Speed to market (full video within hours)

**We compete on presentation and automation, not on data.**

---

## ⚠️ GOVERNING PRINCIPLES (CRITICAL)

### Audio is Sacred
- Use ACTUAL earnings call audio (30-60 minutes, unaltered)
- NEVER synthesize, paraphrase, or alter what was said
- Three pillars of truth: **Original audio + SEC filings + Initial prompt**

### Trust & Integrity
- **NEVER make up data**
- **NEVER infer or guess numbers**
- Carefully vet all data sources
- If uncertain, don't show it

### Security & Privacy
- **NEVER hardcode credentials or API keys in code**
- **NEVER commit .env files to git**
- Never expose internal pipeline/job IDs on external UI
- Never output the source of earnings call media URLs

### Pipeline Consistency

**Render Output Filename:**
- ALL render methods MUST output to: `{job_dir}/renders/rendered.mp4`
- NEVER use method-specific names (`ffmpeg_render.mp4`, `remotion_render.mp4`)
- Ensures consistent R2 URLs: `r2://{bucket}/{company}/{year}/{quarter}/{job_id}/rendered.mp4`

**R2 Bucket Strategy:**
- Dev environment (`DEV_MODE=true`): Upload to `dev-markethawkeye`, store URLs as `r2://dev-markethawkeye/...`
- Prod environment (`DEV_MODE=false`): Upload to `markethawkeye`, store URLs as `r2://markethawkeye/...`
- URLs must be honest (match actual file location)

### Approved Data Sources

**Tier 1 (Always Trust):**
- Earnings call audio (company IR or YouTube official)
- SEC filings (10-K, 10-Q, 8-K)
- Company investor relations websites

**Tier 2 (Verify First):**
- Bloomberg, Reuters, WSJ
- Yahoo Finance, Google Finance
- Seeking Alpha transcripts (verify against audio)

**Never Use:**
- Unverified sources
- AI-generated summaries (unless from official source)
- Forums, message boards

---

## Environments & Setup

### Environment Overview

| Environment | Database | R2 Bucket | DEV_MODE | How to Run |
|-------------|----------|-----------|----------|------------|
| **Local Dev** | PostgreSQL @ 192.168.86.250:54322 | dev-markethawkeye | true | `npm run dev` |
| **Production** | Neon (see .env.production) | markethawkeye | false | `npx dotenv -e .env.production -- npm run dev` |

### Environment Variables

**Required for Web App:**

Create `.env.local` for development:
```bash
# Database
DATABASE_URL="postgresql://user:pass@192.168.86.250:54322/markethawk"

# Authentication (Better Auth)
BETTER_AUTH_SECRET="your-secret-key"
BETTER_AUTH_URL="http://localhost:3000"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# Storage (Cloudflare R2)
R2_ACCOUNT_ID="your-account-id"
R2_ACCESS_KEY_ID="your-access-key"
R2_SECRET_ACCESS_KEY="your-secret-key"
R2_BUCKET_NAME="dev-markethawkeye"
R2_PUBLIC_URL="https://dev-markethawkeye.your-domain.com"

# Payments (Stripe)
STRIPE_SECRET_KEY="sk_test_..."
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."

# Analytics
NEXT_PUBLIC_POSTHOG_KEY="your-posthog-key"
NEXT_PUBLIC_POSTHOG_HOST="https://app.posthog.com"

# App
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

**Production (.env.production):**
- Same variables as above, but with production values
- Store in `.env.production` (NOT committed to git)
- Use `npx dotenv -e .env.production -- npm run dev` to test production config locally

**Python Pipeline:**
```bash
# Set in shell or .env file
DEV_MODE=true   # Use dev R2 bucket
DEV_MODE=false  # Use production R2 bucket
```

### Database Setup

**Technology:** PostgreSQL with Drizzle ORM

**Development Database:**
- Host: 192.168.86.250:54322
- Database: markethawk
- Set `DATABASE_URL` in `.env.local`

**Production Database:**
- Neon serverless PostgreSQL
- Set `DATABASE_URL` in `.env.production`
- Never commit database URLs to git

**Database Commands:**
```bash
# Navigate to web directory
cd /Users/Meera/markethawk/web

# Generate migrations
npm run db:generate

# Apply migrations
npm run db:migrate

# Push schema changes directly
npm run db:push

# Open Drizzle Studio
npm run db:studio

# Delete a user (development)
npm run delete-user -- user@example.com

# Delete a user (production)
DEV_MODE=false npm run delete-user -- user@example.com

# Delete by user ID
npm run delete-user -- --id usr_abc123
```

### User Management

**Delete User Script:** Safely delete users and all related data.

```bash
cd /Users/Meera/markethawk/web

# Delete by email (development)
npm run delete-user -- simran.gupt.497@gmail.com

# Delete by email (production)
DEV_MODE=false npm run delete-user -- user@example.com

# Delete by user ID
npm run delete-user -- --id usr_abc123
```

**What gets deleted:**
- User account
- Sessions (cascade)
- OAuth accounts (cascade)
- Organization memberships (cascade)
- Invitations sent by user (cascade)
- Video views
- Video engagement records
- Click through tracking

**Environment Selection:**
- `DEV_MODE=true` (default): Uses `.env.local` → Local PostgreSQL
- `DEV_MODE=false`: Uses `.env.production` → Neon database

---

## Technology Stack

### Frontend
- Next.js 15 (App Router), TypeScript (strict mode)
- TailwindCSS, shadcn/ui
- React Context for state management
- Zod for schema validation
- Use server actions instead of API routes

### Backend
- PostgreSQL with Drizzle ORM
- Better Auth with Google One Tap
- Stripe (via Better Auth plugin)
- Cloudflare R2 storage (bucket: `markethawkeye`)

### Video Pipeline
- **Transcription:** WhisperX 3.3.1 (speaker diarization + word-level timestamps)
- **Insights:** OpenAI GPT-4o with structured outputs
- **Rendering:** Remotion 4.0+ (H.264 MP4, 1080p, 30fps)
- **GPU:** Primary rendering on sushi (Linux), fallback to Remotion Lambda

### APIs
- YouTube Data API v3 (upload, analytics, metadata)
- Rapid API (YouTube download, audio extraction)

---

## Project Structure

### Monorepo Layout

```
markethawk/
├── package.json          # Root monorepo, defines workspaces
├── node_modules/         # Hoisted dependencies & binaries
│
├── web/                  # Next.js frontend (SaaS platform)
│   ├── app/              # Next.js App Router
│   ├── components/       # React components
│   ├── lib/              # Utilities (db, auth, youtube, r2)
│   ├── package.json
│   ├── .env.local        # Local environment variables (NOT in git)
│   ├── .env.production   # Production variables (NOT in git)
│   └── drizzle.config.ts
│
├── lens/                 # Python video processing pipeline
│   ├── job.py            # Job manager (create, list, process)
│   ├── workflow.py       # Workflow executor (use this, not process_job_pipeline.py)
│   ├── workflows/        # Workflow YAML definitions
│   ├── steps/            # Step handlers
│   ├── transcribe_whisperx.py
│   ├── extract_insights_structured.py
│   ├── refine_timestamps.py
│   └── scripts/
│       ├── download_source.py
│       ├── upload_youtube.py
│       └── migrate_companies_db.py
│
├── studio/               # Remotion video compositions
│   ├── src/
│   │   ├── compositions/  # Video templates (NVDA_Q3_2026.tsx)
│   │   ├── components/    # Reusable components
│   │   ├── themes/        # Company brand themes
│   │   └── Root.tsx       # Composition registry
│   ├── package.json
│   └── public/
│       └── nebula_youtube_music.mp3
│
├── /var/markethawk/      # Shared storage (NOT in git)
│   └── jobs/
│       └── {JOB_ID}/     # Collocated job directory
│           ├── job.yaml  # Single source of truth
│           ├── input/    # source.mp4
│           ├── transcripts/
│           ├── renders/  # rendered.mp4
│           └── thumbnails/
│
└── PRD/                  # Product requirements & recipes
    ├── README.md
    ├── WEB-APP-GUIDE.md
    ├── SEO-STRATEGY.md
    └── recipes/
        ├── AUDIO-ONLY-EARNINGS-RECIPE.md
        └── THUMBNAIL-OPTIONS.md
```

**Key Points:**
- **Local:** Monorepo with hoisted dependencies in root `node_modules`
- **Deployment:** Web app deployed standalone to Vercel (root: `/web`)
- Drizzle runs from `web/` directory
- `.env` files are package-specific, NOT committed to git
- Video files, transcripts → `/var/markethawk/` (shared, NOT in git)
- Code, compositions → `~/markethawk/` (git repo)

---

## Development Machines

**Two-machine setup:**

1. **Sushi (Linux GPU)** - Heavy processing
   - GPU-accelerated transcription (WhisperX)
   - GPU-accelerated rendering (Remotion)
   - Fast processing (20-30 min per video)

2. **Mac Laptop** - Development & editing
   - Composition editing (React/TypeScript)
   - Remotion Studio preview
   - Git commits, YouTube uploads

**Shared Directory:** `/var/markethawk/` (accessible from both machines via SMB)

---

## Database Schema

### Companies Table

**Source:** SEC company_tickers.json (authoritative source)
**Enrichment:** NASDAQ Screener CSV (market cap, sector, industry)

**Schema:**
```sql
CREATE TABLE markethawkeye.companies (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  cik_str VARCHAR(20) UNIQUE NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**JSONB Metadata:**
```json
{
  "exchange": "NASDAQ",
  "market_cap": 4693788000000,
  "sector": "Technology",
  "industry": "Semiconductors",
  "ipo_year": 1999,
  "country": "United States"
}
```

**Slug Generation:**
- Base: `nvidia` from "NVIDIA CORP"
- Conflicts: Append ticker (e.g., `alphabet-goog`, `alphabet-googl`)

**URL Structure:**
- `/companies/${slug}` (e.g., `/companies/nvidia`)

**Querying JSONB:**
```typescript
const result = await db.execute(sql`
  SELECT * FROM markethawkeye.companies
  WHERE metadata->>'sector' = ${sector}
  ORDER BY (metadata->>'market_cap')::bigint DESC NULLS LAST
`);
```

---

## Video Processing Workflows

### Available Workflows

**Location:** `lens/workflows/*.yaml`

1. **manual-audio** - Manually downloaded MP3/audio files
   - LLM extracts metadata from transcript
   - Interactive confirmation

2. **youtube-video** - YouTube videos (standard pipeline)
   - Download → Transcribe → Insights → Render

3. **audio-batch** - Batch processing multiple videos
   - Auto-detection + fuzzy matching

### Create Job

```bash
cd ~/markethawk

# Manual audio workflow
python lens/job.py create \
  --workflow manual-audio \
  --audio /path/to/earnings_call.mp3

# YouTube video workflow
python lens/job.py create \
  --workflow youtube-video \
  --ticker NVDA \
  --quarter Q3 \
  --url "https://youtube.com/watch?v=..."
```

### Run Workflow

**Use `lens/workflow.py` (recommended):**

```bash
# Run all steps
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml

# Run single step
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step transcribe

# Run from specific step onwards
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --from-step extract_insights

# List available handlers
python lens/workflow.py --list-handlers
```

**Common Workflow Steps:**
1. Download / Copy Audio
2. Transcribe (WhisperX with diarization)
3. Extract metadata (LLM or manual)
4. Extract insights (OpenAI structured outputs)
5. Refine timestamps (word-level precision)
6. Upload artifacts (R2)
7. Render video (Remotion)
8. Generate thumbnails
9. Upload to YouTube
10. Update database

### Start Media Server

**Required for Remotion preview and rendering:**

```bash
cd /var/markethawk
screen -S media-server
npx serve . --cors -p 8080
# Ctrl+A then D to detach
```

### Preview in Remotion Studio

```bash
cd ~/markethawk/studio
screen -S remotion-studio
npm run start
# Ctrl+A then D to detach
```

Access at: `http://localhost:3000`

### Render Video

**Use workflow.py (recommended):**

```bash
# Render via pipeline (updates job.yaml automatically)
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step render
```

**Manual render (background):**

```bash
cd ~/markethawk/studio
screen -S render
npx remotion render TICKER-Q3-2025 /var/markethawk/jobs/{JOB_ID}/renders/rendered.mp4
# Ctrl+A then D to detach
```

**Why background rendering:**
- Renders take 15-30 minutes
- Prevents lost progress from terminal shutdown

### Generate Thumbnails

```bash
python lens/smart_thumbnail_generator.py \
  /var/markethawk/jobs/{JOB_ID}/renders/rendered.mp4 \
  /var/markethawk/jobs/{JOB_ID}/job.yaml \
  /var/markethawk/jobs/{JOB_ID}/thumbnails/
```

### Upload to YouTube

```bash
python lens/scripts/upload_youtube.py \
  --video /var/markethawk/jobs/{JOB_ID}/renders/rendered.mp4 \
  --thumbnail /var/markethawk/jobs/{JOB_ID}/thumbnails/thumbnail_1.jpg \
  --metadata /var/markethawk/jobs/{JOB_ID}/job.yaml
```

---

## R2 Storage & Rclone

### Rclone Remotes

- **Development:** `r2-markethawkeye-dev:dev-markethawkeye/`
- **Production:** `r2-markethawk-prod:markethawkeye/`

### Environment Detection

Controlled by `DEV_MODE` variable:
- `DEV_MODE=true` (default) → `dev-markethawkeye` bucket
- `DEV_MODE=false` → `markethawkeye` bucket

### Rclone Commands

**Development:**
```bash
# List files
rclone ls r2-markethawkeye-dev:dev-markethawkeye/

# Upload
rclone copy video.mp4 r2-markethawkeye-dev:dev-markethawkeye/company/2025/Q3/

# Check size
rclone size r2-markethawkeye-dev:dev-markethawkeye/
```

**Production:**
```bash
# List files
rclone ls r2-markethawk-prod:markethawkeye/

# Upload
rclone copy video.mp4 r2-markethawk-prod:markethawkeye/company/2025/Q3/

# Sync dev to prod (careful!)
rclone sync r2-markethawkeye-dev:dev-markethawkeye/ r2-markethawk-prod:markethawkeye/ --dry-run
```

### Database URL Format

Store full R2 URLs including bucket name:
- Development: `r2://dev-markethawkeye/path/to/file.mp4`
- Production: `r2://markethawkeye/path/to/file.mp4`

---

## Development Commands

### Setup

```bash
# Install dependencies (from root)
cd /Users/Meera/markethawk
npm install

# Setup environment variables
cd web
cp .env.example .env.local
# Edit .env.local with your credentials
```

### Web Development

```bash
# Start dev server
cd /Users/Meera/markethawk/web
npm run dev

# Test with production database locally
npx dotenv -e .env.production -- npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

### Database

```bash
cd /Users/Meera/markethawk/web

# Generate migrations
npm run db:generate

# Apply migrations
npm run db:migrate

# Push schema directly
npm run db:push

# Open Drizzle Studio
npm run db:studio
```

---

## Deployment

### Vercel Deployment

**Project Structure:**
- Monorepo locally, but **web is deployed standalone** to Vercel
- Vercel project root: `/web` directory
- Drizzle runs from web directory

**Deploy Commands:**
```bash
# Deploy to preview
cd /Users/Meera/markethawk/web
vercel

# Deploy to production
vercel --prod
```

**Environment Variables in Vercel:**
1. Go to Vercel project settings → Environment Variables
2. Add all variables from `.env.production`
3. Set `DEV_MODE=false` for production

**Build Settings in Vercel:**
- Framework Preset: Next.js
- Root Directory: `web`
- Build Command: `npm run build`
- Output Directory: `.next`

---

## Code Style & Guidelines

- TypeScript strict mode
- Validate inputs with Zod
- TailwindCSS utility classes (avoid custom CSS)
- Server components by default (Next.js)
- No emojis unless explicitly requested
- Use server actions instead of API routes (Next.js 15)
- Greenfield project - no legacy considerations
- Marketing copy: Focus on user benefits, not product features

---

## Troubleshooting

### Permission Errors on SMB Mount
```bash
# Fix from sushi:
chmod 755 /var/markethawk/jobs/{JOB_ID}/renders
```

### "No video stream found" Error
- You're using `<OffthreadVideo>` on audio-only file
- Switch to `<Audio>` component
- See: `PRD/recipes/AUDIO-ONLY-EARNINGS-RECIPE.md`

### YouTube Upload Port Conflict
- Media server: port 8080
- YouTube OAuth: port 8090
- Keep media server running, OAuth will use 8090

---

## Related Documentation

### Core Documentation
- **PRD:** `PRD/README.md` - Complete product requirements
- **Job Structure:** `PRD/recipes/COLLOCATION-STRUCTURE.md`

### Video Pipeline Recipes
- **Audio-Only Recipe:** `PRD/recipes/AUDIO-ONLY-EARNINGS-RECIPE.md`
- **Thumbnail Guide:** `PRD/recipes/THUMBNAIL-OPTIONS.md`

### SaaS Platform Guides
- **Web App Guide:** `PRD/WEB-APP-GUIDE.md`
- **SEO Strategy:** `PRD/SEO-STRATEGY.md`
- **User Experience:** `PRD/USER-EXPERIENCE.md`
- **Admin Dashboard:** `PRD/ADMIN-DASHBOARD.md`
- **Database Schema:** `PRD/DATABASE-SCHEMA.md`
- **Deployment:** `PRD/DEPLOYMENT.md`

---

**Last Updated:** 2025-11-23
**Project Status:** Active Development - Job-based pipeline with Neon production database
- Application deployed on Vercel Pro tier