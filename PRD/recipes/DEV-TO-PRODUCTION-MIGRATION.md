# Dev to Production Migration Recipe

**How to test locally in dev environment, then migrate to production**

## Overview

MarketHawk uses environment-based configuration (like Next.js) to separate dev and production:

- **Dev Environment**: Local PostgreSQL + dev-markethawkeye R2 bucket
- **Production Environment**: Neon PostgreSQL + markeyhawkeye R2 bucket

Environment files:
- `.env` - Common variables + dev overrides (DATABASE_URL, R2_BUCKET_NAME)
- `.env.production` - Production overrides only

## Workflow: YouTube Video → Local Testing → Production

### Step 1: Process in Dev Environment

**Set dev mode (default):**
```bash
export DEV_MODE=true  # or leave unset
```

**Create and run job:**
```bash
cd ~/markethawk
source .venv/bin/activate

# Create job for YouTube video
python lens/job.py create --workflow youtube-ffmpeg --url "https://youtube.com/watch?v=VIDEO_ID"

# Run complete workflow (transcribe, insights, render, upload to dev)
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml
```

**What happens in dev:**
1. Downloads/transcribes/extracts insights
2. Uploads to `dev-markethawkeye` R2 bucket
3. Inserts into local PostgreSQL database
4. Uses `DEV_DATABASE_URL` and `R2_BUCKET_NAME=dev-markethawkeye` from `.env`

### Step 2: Verify in Dev Database

```bash
export DEV_MODE=true
psql $DEV_DATABASE_URL -c "SELECT id, cik_str, symbol, quarter, year, media_url FROM markethawkeye.earnings_calls WHERE symbol = 'PLBY';"
```

**Check:**
- Record exists with correct data
- CIK is populated
- R2 URLs point to `dev-markethawkeye`
- Insights and transcripts columns have data

### Step 3: Migrate to Production

Once verified in dev, migrate to production by switching environment and re-running upload steps:

**Set production mode:**
```bash
export DEV_MODE=false
```

**Re-run upload steps with production environment:**
```bash
# Upload artifacts (transcripts, insights, job.json) to production R2
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step upload_artifacts --force

# Upload media (rendered video) to production R2
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step upload_r2 --force

# Insert into production database
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step update_database --force
```

**What happens in production:**
1. Reads `.env` (common variables)
2. Loads `.env.production` (overrides DATABASE_URL and R2_BUCKET_NAME)
3. Uploads all files to `markeyhawkeye` (production bucket)
4. Inserts record into Neon production database
5. Database record has production R2 URLs

### Step 4: Verify in Production

```bash
export DEV_MODE=false
psql $DATABASE_URL -c "SELECT id, cik_str, symbol, quarter, year, media_url FROM markethawkeye.earnings_calls WHERE symbol = 'PLBY';"
```

**Check:**
- Record exists in production database
- R2 URLs point to `markeyhawkeye` (production bucket)
- All data matches dev record

## Environment Configuration

### .env (Dev + Common)
```bash
# Database (Local PostgreSQL)
DATABASE_URL=postgresql://postgres:postgres@192.168.86.250:54322/markethawk

# R2 Storage (Dev)
R2_BUCKET_NAME=dev-markethawkeye

# Common variables
OPENAI_API_KEY=sk-...
YOUTUBE_CLIENT_SECRETS_FILE=...
```

### .env.production (Production Overrides Only)
```bash
# Database (Production - Neon)
DATABASE_URL=postgresql://neondb_owner:...@ep-twilight-leaf-a4dgbd70.us-east-1.aws.neon.tech/neondb?sslmode=require

# R2 Storage (Production)
R2_BUCKET_NAME=markeyhawkeye
```

## Key Commands

### Dev Environment
```bash
export DEV_MODE=true  # or unset
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml
```

### Production Environment
```bash
export DEV_MODE=false
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step upload_artifacts --force
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step upload_r2 --force
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step update_database --force
```

## Workflow Steps Explained

### upload_artifacts
Uploads to R2:
- `transcripts/transcript.json` - WhisperX full transcript
- `transcripts/transcript.paragraphs.json` - Paragraph-grouped transcript
- `insights.json` - Full LLM output with all entities
- `job.json` - Job metadata

### upload_r2
Uploads to R2:
- `ffmpeg_render.mp4` - Rendered video file

### update_database
Inserts/updates `earnings_calls` table:
- `id`, `cik_str`, `symbol`, `quarter`, `year`
- `media_url` - R2 URL to rendered video
- `transcripts` - JSONB with transcript URLs
- `insights` - JSONB with full LLM insights
- `metadata` - Job metadata

## Common Workflow

**Typical development flow:**
1. Test 10+ videos in dev environment
2. Verify data quality, insights, transcripts
3. Once pipeline is stable, switch to production
4. Process all jobs directly in production (`DEV_MODE=false`)

**Migration is only needed during development/testing phase.**

## Database Schema

### earnings_calls table
```sql
CREATE TABLE markethawkeye.earnings_calls (
  id VARCHAR(255) PRIMARY KEY,              -- PLBY-Q3-2025-b6v4
  cik_str VARCHAR(20) NOT NULL,             -- 1803914
  symbol VARCHAR(10) NOT NULL,              -- PLBY
  quarter VARCHAR(10) NOT NULL,             -- Q3
  year INTEGER NOT NULL,                    -- 2025
  media_url VARCHAR(512),                   -- r2://markeyhawkeye/.../ffmpeg_render.mp4
  youtube_id VARCHAR(50),                   -- YouTube video ID
  metadata JSONB DEFAULT '{}',              -- Job metadata
  transcripts JSONB,                        -- {transcript_url, paragraphs_url}
  insights JSONB,                           -- Full LLM insights with entities
  is_latest BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### transcripts column structure
```json
{
  "transcript_url": "r2://markeyhawkeye/.../transcripts/transcript.json",
  "paragraphs_url": "r2://markeyhawkeye/.../transcripts/transcript.paragraphs.json"
}
```

### insights column structure
```json
{
  "company_name": "Playboy Incorporated",
  "company_ticker": "PLBY",
  "quarter": "Q3",
  "year": 2025,
  "speakers": [...],
  "financial_metrics": [...],
  "highlights": [...],
  "chapters": [...],
  "companies_mentioned": [...],
  "products_mentioned": [...],
  "geographic_regions": [...],
  "executives_mentioned": [...],
  "strategic_initiatives": [...],
  "guidance_metrics": [...],
  "risk_factors": [...],
  "analyst_concerns": [...],
  "sentiment": {...},
  "summary": "...",
  "youtube_title": "...",
  "youtube_description": "..."
}
```

## Troubleshooting

### Record exists but missing CIK
```bash
# Re-run match_company (only needed once per job)
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step match_company --force

# Re-run database update
python lens/workflow.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step update_database --force
```

### Wrong R2 bucket
Check environment:
```bash
echo $DEV_MODE  # Should be 'false' for production
env | grep DATABASE_URL
env | grep R2_BUCKET_NAME
```

### Database connection issues
```bash
# Test dev connection
export DEV_MODE=true
psql $DEV_DATABASE_URL -c "SELECT 1;"

# Test production connection
export DEV_MODE=false
psql $DATABASE_URL -c "SELECT 1;"
```

---

**Last Updated:** 2025-01-17
**Related:** [Audio-Only Recipe](./AUDIO-ONLY-EARNINGS-RECIPE.md), [Workflow System](../../CLAUDE.md)
