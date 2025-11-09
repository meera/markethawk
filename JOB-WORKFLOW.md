# MarketHawk Job Workflow

**Single Source of Truth:** `job.yaml`

No more scattered state files (.state.json, production.json, insights.json).
Everything lives in one human-editable YAML file.

---

## Quick Start

### 1. Create Job

```bash
cd ~/markethawk

# From YouTube URL
python lens/job.py create \
  --url "https://youtube.com/watch?v=jUnV3LiN0_k" \
  --ticker PLTR \
  --quarter Q3-2025

# From local file
python lens/job.py create \
  --file "/Downloads/earnings_call.mp4" \
  --ticker HOOD \
  --quarter Q3-2025

# With additional context
python lens/job.py create \
  --url "https://youtube.com/watch?v=..." \
  --ticker AAPL \
  --quarter Q4-2024 \
  --company "Apple Inc." \
  --text "Focus on iPhone 15 sales and China market"
```

**Output:**
```
✓ Job created: PLTR_Q3_2025_20251109_043000
  File: /var/markethawk/jobs/PLTR_Q3_2025_20251109_043000.yaml
  Input: youtube_url - https://youtube.com/watch?v=jUnV3LiN0_k
  Company: PLTR Q3-2025

Process with: python lens/job.py process PLTR_Q3_2025_20251109_043000
```

---

### 2. Process Job

```bash
# Run all steps
python lens/job.py process PLTR_Q3_2025_20251109_043000

# Run specific step
python lens/job.py process PLTR_Q3_2025_20251109_043000 --step transcribe

# Run from step onwards
python lens/job.py process PLTR_Q3_2025_20251109_043000 --from-step insights
```

**Pipeline Steps:**
1. **Download** - Download from YouTube or copy local file
2. **Parse** - Extract ticker/quarter from metadata
3. **Transcribe** - Run Whisper on video
4. **Detect Trim** - Find start point (5s before first speech)
5. **Insights** - Extract with OpenAI GPT-4o

---

### 3. Check Status

```bash
# Single job status
python lens/job.py status PLTR_Q3_2025_20251109_043000

# List all jobs
python lens/job.py list
```

**Output:**
```
Job: PLTR_Q3_2025_20251109_043000
Status: processing
Company: Palantir Technologies (PLTR) Q3-2025
Created: 2025-11-09T04:30:00

Pipeline Steps:
Step                 Status       Started              Completed
--------------------------------------------------------------------------------
download             completed    2025-11-09T04:30:15  2025-11-09T04:32:00
parse                completed    2025-11-09T04:32:05  2025-11-09T04:32:10
transcribe           running      2025-11-09T04:32:15  -
detect_trim          pending      -                    -
insights             pending      -                    -
```

---

## Manual Adjustments

### Edit Trim Point

Open job file: `/var/markethawk/jobs/PLTR_Q3_2025_20251109_043000.yaml`

```yaml
processing:
  detect_trim:
    output:
      # Edit this to change where video starts in Remotion
      trim_start_seconds: 23.58  # ← Change this!
      first_speech_detected_at: 28.58
      pre_speech_buffer_seconds: 5.0
```

**Re-render after editing:**
```bash
# Remotion will read the updated trim_start_seconds
cd studio
npx remotion render PLTR-Q3-2025 /var/markethawk/PLTR/Q3-2025/take2/final.mp4
```

---

### Edit Insights

All OpenAI-extracted data is in job.yaml:

```yaml
processing:
  insights:
    output:
      title: "Palantir Q3 2025 Earnings Call"
      summary: "..."

      highlights:
        - timestamp: 107
          text: "Revenue $725.5M, up 30% YoY"
          category: "financial"

      chapters:
        - timestamp: 0
          title: "Opening Remarks"
          description: "CEO introduces Q3 results"
```

**Edit directly in YAML!** Remotion reads from job.yaml.

---

## File Structure

```
/var/markethawk/
├── jobs/
│   └── PLTR_Q3_2025_20251109_043000.yaml  # ← SINGLE SOURCE OF TRUTH
│
├── _downloads/
│   └── jUnV3LiN0_k/
│       ├── source.mp4                      # Original video (no trimming!)
│       ├── transcript.json                 # Whisper output
│       ├── transcript.paragraphs.json      # Optimized for GPT
│       ├── insights.raw.json               # OpenAI raw response (backup)
│       └── usage.json                      # Token usage tracking
│
└── PLTR/Q3-2025/
    ├── take1/
    │   └── final.mp4                       # Rendered video
    └── take2/
        └── final.mp4                       # Second render
```

---

## What Changed from Old Workflow

### ❌ Removed Files:
- `.state.json` - Processing state (now in job.yaml)
- `production.json` - Render tracking (now in job.yaml)
- `insights.json` - Insights data (now in job.yaml)
- `source.trimmed.mp4` - Trimmed video (no longer needed!)

### ✅ New Files:
- `jobs/<job_id>.yaml` - Single source of truth
- `insights.raw.json` - OpenAI backup (read-only)
- `usage.json` - Token tracking (read-only)

### ✅ New Approach:
- **No video trimming** - Use Remotion `startFrom` prop
- **One YAML file** - All state in job.yaml
- **Human-editable** - YAML format with comments
- **Job-based** - Track entire lifecycle

---

## Remotion Integration

Compositions read job.yaml to get:
- Trim start point
- Insights/highlights
- Chapter markers
- Company metadata

```tsx
// In composition
import yaml from 'js-yaml';
import fs from 'fs';

const jobFile = '/var/markethawk/jobs/PLTR_Q3_2025_20251109_043000.yaml';
const job = yaml.load(fs.readFileSync(jobFile, 'utf8'));

const trimStart = job.processing.detect_trim.output.trim_start_seconds;
const highlights = job.processing.insights.output.highlights;

<OffthreadVideo
  src={videoPath}
  startFrom={trimStart * fps}  // Skip to first speech!
/>
```

---

## Tips

### Resume Failed Jobs
If a step fails, fix the issue and re-run:
```bash
python lens/job.py process <job_id> --from-step <failed_step>
```

### Skip Steps
If you already have a transcript, manually mark steps as completed in job.yaml:
```yaml
processing:
  download:
    status: completed
  transcribe:
    status: completed  # ← Mark as done
```

### Add Notes
Use the notes section for anything:
```yaml
notes: |
  This video has unusual intro - trim point adjusted manually.
  Revenue highlight at 2:15 is critical for YouTube Short.
```

---

## Next Steps

1. ✅ Process job through insights
2. 📝 Manual review/edits in job.yaml
3. 🎬 Render with Remotion (reads job.yaml)
4. 🚀 Upload to YouTube
