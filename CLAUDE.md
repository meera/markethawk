# CLAUDE.md

Guidance for Claude Code when working with MarketHawk repository.

---

## Project: Markey HawkEye

**Website:** [markethawkeye.com](https://markethawkeye.com)

### Overview
Markey HawkEye transforms earnings call audio into visually-enhanced YouTube videos with an interactive SaaS web platform. The monetization is important goal. Monetization will be in three ways - 
1.Sell subscription to Sass
2. YouTube Monetization
3. Get companies to place orders to generate their videos.  

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

### Approved Data Sources (Trust Hierarchy)

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

## Technology Stack

### Frontend
- Next.js 14+ (App Router), TypeScript (strict mode)
- TailwindCSS, shadcn/ui
- React Context / Zustand

### Backend
- **Database:** PostgreSQL with Drizzle ORM (avoid Neon-specific packages)
- **Authentication:** Better Auth with Google One Tap
- **Payments:** Stripe (via Better Auth plugin)
- **Storage:** Cloudflare R2 (bucket: `earninglens`)

### Video Pipeline
- **Transcription:** WhisperX 3.3.1 (speaker diarization  )
- **Insights:** OpenAI GPT-4o with structured outputs 
- **Rendering:** Remotion 4.0+ (H.264 MP4, 1080p, 30fps)
- **GPU:** Primary rendering on sushi (Linux), fallback to Remotion Lambda

### APIs
- YouTube Data API v3 (upload, analytics, metadata)
- Rapid API (YouTube download, audio extraction)

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

**Shared Directory:** `/var/markethawk/` (accessible from both machines)
- On sushi: `/var/markethawk/`
- On Mac: `/var/markethawk/`

**Key Principle:**
- Video files, transcripts, audio → `/var/markethawk/` (shared, NOT in git)
- Code, compositions, components → `~/markethawk/` (git repo, committed)

---

## Project Structure

```
markethawk/
├── lens/                          # Python video processing pipeline
│   ├── job.py                     # Job manager (create, list, process)
│   ├── job.yaml.template          # Job configuration template
│   ├── process_job_pipeline.py   # Pipeline orchestrator
│   ├── transcribe_whisperx.py    # WhisperX transcription
│   ├── extract_insights_structured.py  # OpenAI insights
│   └── scripts/
│       ├── download_source.py     # YouTube downloader
│       ├── download_hls.py        # HLS stream downloader
│       └── upload_youtube.py      # YouTube uploader
│
├── studio/                        # Remotion video compositions
│   ├── src/
│   │   ├── compositions/          # Video templates (BIP_Q3_2025.tsx, etc.)
│   │   ├── components/            # Reusable components
│   │   ├── themes/                # Company brand themes
│   │   └── Root.tsx               # Composition registry
│   └── public/
│       └── nebula_youtube_music.mp3  # Intro music
│
├── web/                           # Next.js public website
│   ├── app/                       # Next.js App Router
│   ├── components/                # React components
│   └── lib/                       # Utilities (db, auth, youtube, r2)
│
├── /var/markethawk/               # Shared storage (NOT in git)
│   └── jobs/
│       └── {JOB_ID}/              # Collocated job directory
│           ├── job.yaml           # Single source of truth
│           ├── input/             # source.mp4
│           ├── transcripts/       # transcript.json, paragraphs.json
│           ├── renders/           # take1.mp4, take2.mp4, etc.
│           └── thumbnails/        # Generated thumbnails
│
├── AUDIO-ONLY-EARNINGS-RECIPE.md # Recipe for audio-only videos
├── THUMBNAIL-OPTIONS.md           # Thumbnail generation guide
├── COLLOCATION-STRUCTURE.md       # Job directory structure
└── CLAUDE.md                      # This file
```

**Recipes and companion documentation are in PRD/ directory.** 
---

## Job-Based Workflow

**Single source of truth:** `job.yaml` in each job directory

### Create Job
```bash
cd ~/markethawk
source .venv/bin/activate
python lens/job.py create \
  --ticker BIP \
  --quarter Q3-2025 \
  --company "Brookfield Infrastructure Partners LP" \
  --url "https://media.main.pro2.mas.media-server.com/.../audio.m3u8"
```

### Process Job (All Steps)
```bash
python lens/process_job_pipeline.py /var/markethawk/jobs/{JOB_ID}/job.yaml
```

**Pipeline steps:**
1. Download (YouTube or HLS stream or manually downloaded)
2. Parse metadata (ticker, quarter, company)
3. Transcribe (WhisperX with speaker diarization)
4. Detect trim point (skip silence)
5. Extract insights (OpenAI structured outputs)

### Render Video

**CRITICAL:** Always run renders in background to prevent accidental terminal shutdown!

```bash
# Terminal 1: Start media server (keep running)
cd /var/markethawk
npx serve . --cors -p 8080


screen -S render
npx remotion render TICKER-Q3-2025 /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4
# Press Ctrl+A then D to detach
# screen -r render  # to reattach
```

**Why background rendering is critical:**
- Renders take 15-30 minutes
- Accidental terminal close = lost render progress
- Use  `screen` to persist

### Generate Thumbnails

**See:** `PRD/recipes/THUMBNAIL-OPTIONS.md` for detailed thumbnail generation guide.

```bash
python lens/smart_thumbnail_generator.py \
  --video /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4 \
  --data /var/markethawk/jobs/{JOB_ID}/job.yaml \
  --output /var/markethawk/jobs/{JOB_ID}/thumbnails/
```

### Upload to YouTube - this may need to happen on mac -
```bash
python lens/scripts/upload_youtube.py \
  --video /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4 \
  --thumbnail /var/markethawk/jobs/{JOB_ID}/thumbnails/thumbnail_1.jpg \
  --metadata /var/markethawk/jobs/{JOB_ID}/job.yaml
```

---

## Audio-Only Earnings Calls

**See:** `PRD/recipes/AUDIO-ONLY-EARNINGS-RECIPE.md` for complete recipe.

**Key points:**
- Use `<Audio>` component, NOT `<OffthreadVideo>` (audio-only files have no video stream)
- Create static branded background (company colors + ticker watermark)
- Add `FadedAudio` component for smooth transitions between title music and earnings audio
- Generate thumbnails from rendered video (not from source)

**Example:** `studio/src/compositions/BIP_Q3_2025.tsx`

---

## Remotion Media Server

**Required for rendering:** Serve `/var/markethawk` via HTTP with CORS enabled.

```bash
# Start server (keep running during development/rendering)
cd /var/markethawk
npx serve . --cors -p 8080
```

**Environment Variable:**
```bash
# .env
MEDIA_SERVER_URL="http://192.168.1.101:8080"
```

**In Compositions:**
```tsx
const mediaServerUrl = process.env.MEDIA_SERVER_URL || 'http://192.168.1.101:8080';
const videoPath = `${mediaServerUrl}/jobs/{JOB_ID}/input/source.mp4`;
```

---

## Development Commands

### Setup
```bash
npm install
cp .env.example .env.local
# Fill in: DATABASE_URL, YOUTUBE_API_KEY, etc.
```

### Development
```bash
npm run dev                          # Next.js web app
cd studio && npm run start          # Remotion Studio (preview)
```

### Video Processing
```bash
cd ~/markethawk
source .venv/bin/activate
python lens/job.py create --ticker AAPL --quarter Q4-2024 --url "..."
python lens/process_job_pipeline.py /var/markethawk/jobs/{JOB_ID}/job.yaml
```

### Deployment
```bash
vercel deploy                        # Deploy web app
```

---

## Git Workflow

**Only commit code changes, NOT video files.**

```bash
git add lens/ studio/ web/
git commit -m "Add BIP Q3-2025 composition"
git push
```

**Never commit:**
- Video files (*.mp4)
- Audio files (*.mp3, *.m4a)
- Transcripts (*.json in /var/markethawk)
- Job directories (/var/markethawk/jobs/)

---

## Code Style

- TypeScript strict mode
- Validate inputs with Zod
- TailwindCSS utility classes (avoid custom CSS)
- Server components by default (Next.js)
- No emojis unless explicitly requested

---

## Performance Best Practices

- Use `OffthreadVideo` in Remotion (faster rendering)
- Optimize images with next/image
- Cache YouTube API responses (60s TTL)
- Use ISR for video pages (revalidate hourly)

---

## Troubleshooting

### Permission Errors on SMB Mount
```bash
# Directories created on Mac may have restrictive permissions
# Fix from sushi:
chmod 755 /var/markethawk/jobs/{JOB_ID}/renders
```

**Prevention:** `lens/job.py` now creates directories with `mode=0o755`

### "No video stream found" Error
- You're using `<OffthreadVideo>` on audio-only file
- Switch to `<Audio>` component
- See: `AUDIO-ONLY-EARNINGS-RECIPE.md`

### Abrupt Audio Cuts
- Add `FadedAudio` component for smooth transitions
- Fade out title music (30 frames)
- Fade in earnings audio (45 frames)

---

## Related Documentation

### Core Documentation
- **PRD:** `PRD/README.md` - Complete product requirements document
- **Job Structure:** `PRD/recipes/COLLOCATION-STRUCTURE.md` - Directory organization

### Video Pipeline Recipes
- **Audio-Only Recipe:** `PRD/recipes/AUDIO-ONLY-EARNINGS-RECIPE.md` - Complete workflow for audio-only earnings calls
- **Thumbnail Guide:** `PRD/recipes/THUMBNAIL-OPTIONS.md` - Thumbnail generation options

### SaaS Platform Guides (for web app development)
- **Web App Guide:** `PRD/WEB-APP-GUIDE.md` - Next.js, Better Auth, Stripe integration
- **SEO Strategy:** `PRD/SEO-STRATEGY.md` - YouTube + website SEO optimization
- **User Experience:** `PRD/USER-EXPERIENCE.md` - Free tier, paywalls, personalization
- **Admin Dashboard:** `PRD/ADMIN-DASHBOARD.md` - Monitoring, analytics, real-time metrics
- **Database Schema:** `PRD/DATABASE-SCHEMA.md` - Complete schema with Drizzle ORM
- **Deployment:** `PRD/DEPLOYMENT.md` - Vercel deployment, environment variables

### Reference
- **VideotoBe Platform:** `~/videotobe/platform` - Reusable components for web app

---

**Last Updated:** 2025-11-09
**Project Status:** Active Development - Job-based pipeline with audio-only support
- Guidelines for Marketing Copy: Always talk in terms of User Benefits and not Product Features.
- greenfield project - no legacy consideration