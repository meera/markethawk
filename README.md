# Market Hawk Eye

**Transform earnings calls into visually-enhanced YouTube videos.**

🌐 **Website:** [markethawkeye.com](https://markethawkeye.com)

## 🎯 **YOUTUBE FIRST!**

**Primary Goal:** Enable YouTube monetization (1000 subs + 4000 watch hours)

**Timeline:** 6-8 weeks

**Revenue:** $500-2,000/month from YouTube ads

**Website comes along the way**

---

## Quick Start

### Generate First Video (START HERE)

**⚠️ IMPORTANT:** We use **full earnings call audio** (30-60 min) with visual overlays, not summary videos.

**Full guide:** See `PRD/recipes/AUDIO-ONLY-EARNINGS-RECIPE.md`

```bash
# 1. Create a job
cd ~/markethawk
source .venv/bin/activate
python lens/job.py create \
  --ticker AAPL \
  --quarter Q4-2024 \
  --company "Apple Inc." \
  --url "https://youtube.com/watch?v=..."

# 2. Process the job (download, transcribe, insights)
python lens/process_job_pipeline.py /var/markethawk/jobs/{JOB_ID}/job.yaml

# 3. Render video (run in background with screen)
cd ~/markethawk
screen -S render
npx remotion render AAPL-Q4-2024 /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4
# Press Ctrl+A then D to detach

# 4. Generate thumbnails
python lens/smart_thumbnail_generator.py \
  --video /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4 \
  --data /var/markethawk/jobs/{JOB_ID}/job.yaml \
  --output /var/markethawk/jobs/{JOB_ID}/thumbnails/

# 5. Upload to YouTube
python lens/scripts/upload_youtube.py \
  --video /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4 \
  --thumbnail /var/markethawk/jobs/{JOB_ID}/thumbnails/thumbnail_1.jpg \
  --metadata /var/markethawk/jobs/{JOB_ID}/job.yaml
```

### YouTube Growth Strategy
```bash
# Read the complete 6-week strategy
cat YOUTUBE-FIRST-STRATEGY.md
```

---

## Project Structure

```
markethawk/
├── web/               # Website (hawkeyemarket.com)
├── studio/            # Video production (Remotion)
├── lens/              # Python processing pipeline
├── PRD/               # Documentation
│   ├── recipes/       # Video production recipes
│   ├── WEB-APP-GUIDE.md
│   ├── SEO-STRATEGY.md
│   └── ...
└── CLAUDE.md          # Main guidance document
```

---

## Documentation

### Core Documents

| Document | Purpose | Priority |
|----------|---------|----------|
| **[CLAUDE.md](CLAUDE.md)** | Governing principles & job-based workflow | ⚠️ **READ FIRST** |
| **[PRD/INDEX.md](PRD/INDEX.md)** | Complete documentation index | 📋 **Navigation** |
| **[PRD/recipes/AUDIO-ONLY-EARNINGS-RECIPE.md](PRD/recipes/AUDIO-ONLY-EARNINGS-RECIPE.md)** | Audio-only video production | 🎬 **START HERE** |
| **[PRD/recipes/THUMBNAIL-OPTIONS.md](PRD/recipes/THUMBNAIL-OPTIONS.md)** | Thumbnail generation | 🖼️ **Thumbnails** |
| **[YOUTUBE-FIRST-STRATEGY.md](YOUTUBE-FIRST-STRATEGY.md)** | 6-week plan to hit monetization | 🔥 **Strategy** |

**SaaS Platform Documentation** (for later):
- `PRD/WEB-APP-GUIDE.md` - Next.js, Better Auth, Stripe
- `PRD/SEO-STRATEGY.md` - YouTube + website SEO
- `PRD/USER-EXPERIENCE.md` - Free tier, paywalls
- `PRD/ADMIN-DASHBOARD.md` - Monitoring dashboard
- `PRD/DATABASE-SCHEMA.md` - Drizzle ORM schema
- `PRD/DEPLOYMENT.md` - Vercel deployment

---

## Landing Page

**Simple, complete-looking landing page ready to deploy:**

```bash
cd ~/markethawk/web
npm install
npm run dev
```

Visit: http://localhost:3000

**Features:**
- ✅ Vision statement (no "coming soon")
- ✅ Newsletter subscription
- ✅ Professional design
- ✅ Mobile responsive
- ✅ Ready for production

**Deploy to Vercel:**
```bash
cd ~/markethawk/web
vercel --prod
```

Set domain: **hawkeyemarket.com**

---

## Key Features

### 1. Audio is Sacred
- Use ACTUAL earnings call audio (30-60 minutes, unaltered)
- NEVER synthesize, paraphrase, or alter what was said
- Three pillars of truth: **Original audio + SEC filings + Initial prompt**

### 2. Visual Enhancement
- Dynamic overlays sync with audio
- Speaker identification (photo + name)
- Metrics appear when mentioned
- Company branding throughout

### 3. Automated Pipeline
- Job-based workflow with `job.yaml` as single source of truth
- WhisperX transcription with speaker diarization
- OpenAI structured insights extraction
- Background rendering with screen/nohup
- Automated YouTube upload

### 4. Collocated Storage
```
/var/markethawk/jobs/{JOB_ID}/
├── job.yaml           # Single source of truth
├── input/             # source.mp4
├── transcripts/       # transcript.json, paragraphs.json
├── renders/           # take1.mp4, take2.mp4
└── thumbnails/        # Generated thumbnails
```

---

## Tech Stack

### Video Pipeline (Python)
- **WhisperX 3.3.1** - Transcription with speaker diarization
- **OpenAI GPT-4o** - Structured insights extraction
- **Remotion 4.0+** - Video composition and rendering
- **GPU Rendering** - Sushi (Linux) for fast processing

### Website (Next.js)
- **Framework:** Next.js 14+ (App Router)
- **Styling:** TailwindCSS
- **Database:** PostgreSQL with Drizzle ORM
- **Auth:** Better Auth (Google One Tap)
- **Payments:** Stripe
- **Storage:** Cloudflare R2
- **Deployment:** Vercel (hawkeyemarket.com)

---

## Monetization

**Three Revenue Streams:**

1. **YouTube Ad Revenue**
   - Goal: 1000+ subscribers, 4000+ watch hours
   - Est: $500-2,000/month

2. **SaaS Subscriptions**
   - Free tier: Limited access
   - Pro: $29/month (unlimited videos, interactive charts)
   - Team: $99/month (10 members, API access)

3. **Direct Orders**
   - Companies pay to generate their earnings videos
   - Custom branding, priority processing
   - Est: $500-1,000 per video

---

## R2 Bucket Organization

**Bucket:** `markethawk` (Cloudflare R2)

```
r2:markethawk/
├── AAPL/
│   ├── Q4-2024/
│   │   ├── take1.mp4
│   │   ├── take2.mp4
│   │   ├── audio.m4a
│   │   ├── transcript.json
│   │   └── insights.json
├── MSFT/
├── PLTR/
└── shared/
    └── logos/
```

**Key Principle:** Flat structure - all files for a quarter in one directory

---

## Development Workflow

### Two-Machine Setup

1. **Sushi (Linux GPU)** - Heavy processing
   - GPU transcription (WhisperX)
   - GPU rendering (Remotion)
   - Fast: 20-30 min per video

2. **Mac Laptop** - Development
   - Code editing
   - Remotion Studio preview
   - Git commits
   - YouTube uploads

**Shared Directory:** `/var/markethawk/` (accessible from both)

---

## Environment Variables

```bash
# Database
DATABASE_URL="postgresql://..."

# YouTube API
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

# OpenAI
OPENAI_API_KEY="sk-..."

# Remotion Media Server
MEDIA_SERVER_URL="http://192.168.1.101:8080"

# Better Auth (for web app)
AUTH_SECRET="..."
AUTH_GOOGLE_CLIENT_ID="..."
AUTH_GOOGLE_CLIENT_SECRET="..."

# Stripe (for web app)
STRIPE_SECRET_KEY="sk_live_..."
STRIPE_PUBLISHABLE_KEY="pk_live_..."
```

---

## Next Steps

**1. Start Producing Videos:**
```bash
# Read the complete guide
cat PRD/recipes/AUDIO-ONLY-EARNINGS-RECIPE.md

# Create your first job
python lens/job.py create --ticker AAPL --quarter Q4-2024 --url "..."
```

**2. Launch Website:**
```bash
cd web
npm install
npm run dev
# Deploy when ready: vercel --prod
```

**3. Scale:**
- 1 video per day
- Build to 50+ videos
- Hit 1000 YouTube subscribers
- Enable monetization

---

**Built with:** Next.js, Remotion, WhisperX, OpenAI, Drizzle ORM, Cloudflare R2

**Website:** [hawkeyemarket.com](https://hawkeyemarket.com)

**License:** Proprietary
