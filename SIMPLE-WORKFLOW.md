# MarketHawk Simple Workflow

**KISS - Keep It Simple, Stupid**

One YAML file. Four commands. That's it.

---

## The One File: job.yaml

```yaml
job_id: PLTR_Q3_2025_20251109_043000
status: pending

input:
  type: youtube_url
  value: "https://youtube.com/watch?v=jUnV3LiN0_k"

company:
  ticker: PLTR
  quarter: Q3-2025

processing:
  download:
    status: completed
    video_id: jUnV3LiN0_k
    file: /var/markethawk/_downloads/jUnV3LiN0_k/source.mp4

  transcribe:
    status: completed
    transcript_file: /var/markethawk/_downloads/jUnV3LiN0_k/transcript.json

  detect_trim:
    status: completed
    trim_start_seconds: 23.58  # ← Edit this to adjust start point
    first_speech_at: 28.58

  insights:
    status: completed
    highlights:
      - timestamp: 107
        text: "Revenue $725.5M, up 30% YoY"
    chapters:
      - timestamp: 0
        title: "Opening Remarks"
    youtube_title: "Palantir Q3 2025 Earnings Call"
    youtube_description: "..."

outputs:
  full_video: /var/markethawk/PLTR/Q3-2025/final.mp4
  youtube_url: https://youtube.com/watch?v=abc123

notes: |
  2025-11-09: Processed video
  2025-11-10: Rendered, uploaded to YouTube

  Great highlight at 12:30 about AI growth
```

---

## Four Commands

```bash
# 1. Create job
python lens/job.py create \
  --url "https://youtube.com/watch?v=..." \
  --ticker PLTR \
  --quarter Q3-2025

# 2. Process (download, transcribe, insights)
python lens/job.py process PLTR_Q3_2025_20251109_043000

# 3. Check status
python lens/job.py status PLTR_Q3_2025_20251109_043000

# 4. List all jobs
python lens/job.py list
```

**That's it. No more commands needed.**

---

## File Structure

```
/var/markethawk/
├── jobs/
│   └── PLTR_Q3_2025_20251109_043000.yaml  # ← Single source of truth
│
├── _downloads/jUnV3LiN0_k/
│   ├── source.mp4              # Original (no trimming!)
│   ├── transcript.json
│   ├── insights.raw.json       # OpenAI backup (read-only)
│   └── usage.json              # Token tracking (read-only)
│
└── PLTR/Q3-2025/
    └── final.mp4
```

---

## Workflow

### Day 1: Process Video

```bash
# Create job
python lens/job.py create \
  --url "https://youtube.com/watch?v=jUnV3LiN0_k" \
  --ticker PLTR \
  --quarter Q3-2025

# Output:
# ✓ Job created: PLTR_Q3_2025_20251109_043000
#   File: /var/markethawk/jobs/PLTR_Q3_2025_20251109_043000.yaml
#   Next: python lens/job.py process PLTR_Q3_2025_20251109_043000

# Process
python lens/job.py process PLTR_Q3_2025_20251109_043000

# Takes ~20-30 min on sushi GPU
# Downloads → Transcribes → Detects trim point → Extracts insights
```

### Day 2: Review & Edit

```bash
# Check what was found
python lens/job.py status PLTR_Q3_2025_20251109_043000

# Output:
# Job: PLTR_Q3_2025_20251109_043000
# Status: completed
# Company: PLTR Q3-2025
#
# Processing:
#   ✓ download        completed
#   ✓ transcribe      completed
#   ✓ detect_trim     completed
#   ✓ insights        completed
#
# Notes:
#   Created: 2025-11-09
#   TODO: Render video

# Edit job.yaml if needed
nano /var/markethawk/jobs/PLTR_Q3_2025_20251109_043000.yaml

# Common edits:
# - Adjust trim_start_seconds
# - Fix highlights
# - Update YouTube title/description
# - Add notes
```

### Day 3: Render (Manual)

```bash
# Render with Remotion
cd studio
npx remotion render PLTR-Q3-2025 /var/markethawk/PLTR/Q3-2025/final.mp4

# Update job.yaml manually
nano /var/markethawk/jobs/PLTR_Q3_2025_20251109_043000.yaml
# Set: outputs.full_video: /var/markethawk/PLTR/Q3-2025/final.mp4
```

### Day 5: Upload (Manual)

```bash
# Upload to YouTube (manual for now)
python lens/scripts/upload_youtube.py \
  --video /var/markethawk/PLTR/Q3-2025/final.mp4 \
  --metadata /var/markethawk/jobs/PLTR_Q3_2025_20251109_043000.yaml

# Update job.yaml
# Set: outputs.youtube_url: https://youtube.com/watch?v=abc123
# Set: status: completed
```

---

## "Resume 5 Days Later" Workflow

```bash
# See all jobs
python lens/job.py list

# Output:
# Job ID                          Status      Company         Created
# -------------------------------------------------------------------------------
# PLTR_Q3_2025_20251109_043000   completed   PLTR Q3-2025    2025-11-09 04:30
# HOOD_Q3_2025_20251107_120000   processing  HOOD Q3-2025    2025-11-07 12:00

# Check specific job
python lens/job.py status PLTR_Q3_2025_20251109_043000

# Read notes to remember what's pending
cat /var/markethawk/jobs/PLTR_Q3_2025_20251109_043000.yaml | grep -A 10 "notes:"

# Continue where you left off
```

---

## What's Removed (Over-Engineering)

❌ Status tracking for every output
❌ Planned vs actual outputs
❌ Todo auto-generation
❌ Dashboard TUI
❌ Complex CLI subcommands
❌ Shorts management system

**Just add notes manually. That's enough.**

---

## What's Kept (Essential)

✅ Single YAML file (job.yaml)
✅ No video trimming (use Remotion startFrom)
✅ Simple CLI (create, process, status, list)
✅ OpenAI raw backup (insights.raw.json)
✅ Manual notes field

---

## Example job.yaml (Real)

```yaml
job_id: PLTR_Q3_2025_20251109_043000
created_at: "2025-11-09T04:30:00Z"
status: completed

input:
  type: youtube_url
  value: "https://youtube.com/watch?v=jUnV3LiN0_k"

company:
  name: "Palantir Technologies"
  ticker: "PLTR"
  quarter: "Q3-2025"
  year: 2025

processing:
  download:
    status: completed
    video_id: jUnV3LiN0_k
    file: /var/markethawk/_downloads/jUnV3LiN0_k/source.mp4

  transcribe:
    status: completed
    transcript_file: /var/markethawk/_downloads/jUnV3LiN0_k/transcript.json

  detect_trim:
    status: completed
    trim_start_seconds: 23.58
    first_speech_at: 28.58

  insights:
    status: completed
    highlights:
      - timestamp: 107
        text: "Revenue $725.5M, up 30% YoY"
        category: financial
      - timestamp: 320
        text: "Government revenue up 40%"
        category: financial
      - timestamp: 850
        text: "AI Platform showing strong adoption"
        category: product
    chapters:
      - timestamp: 0
        title: "Opening Remarks"
      - timestamp: 180
        title: "Financial Results"
      - timestamp: 600
        title: "Product Updates"
      - timestamp: 1200
        title: "Q&A Session"
    youtube_title: "Palantir Q3 2025 Earnings Call - Full Analysis"
    youtube_description: |
      Palantir Q3 2025 earnings call with visual enhancements.

      Key highlights:
      - Revenue: $725.5M (+30% YoY)
      - Government revenue up 40%
      - AI Platform adoption growing

      Full analysis: https://market-hawk.com/pltr/q3-2025

outputs:
  full_video: /var/markethawk/PLTR/Q3-2025/final.mp4
  youtube_url: https://youtube.com/watch?v=abc123xyz

notes: |
  2025-11-09 04:30: Created job, started processing
  2025-11-09 05:15: Processing complete (35 min on sushi GPU)
  2025-11-10 14:00: Rendered video (7 min)
  2025-11-10 15:30: Uploaded to YouTube

  DONE!

  Ideas for shorts:
  - Revenue highlight (1:47)
  - Government growth (5:20)
  - AI Platform demo (14:10)
```

---

**This is all you need. Start simple, add complexity only when you actually need it.**
