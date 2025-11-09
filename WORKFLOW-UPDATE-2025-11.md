# MarketHawk Workflow Update - November 2025

## Major Changes

### 1. Job-Based Processing (Single Source of Truth)

**OLD:** Multiple state files scattered across directories
```
/_downloads/<video_id>/.state.json
/PLTR/Q3-2025/production.json
/PLTR/Q3-2025/insights.json
```

**NEW:** One YAML file per job
```
/jobs/PLTR_Q3_2025_20251109_043000.yaml  ← Everything here!
```

**Benefits:**
- ✅ Human-editable (YAML with comments)
- ✅ Single source of truth
- ✅ Easy to review/modify
- ✅ Git-friendly diffs
- ✅ No scattered state

---

### 2. No Video Trimming (Use Remotion startFrom)

**OLD:** Create trimmed video file
```bash
# Step 4: Smart trim
ffmpeg -i source.mp4 -ss 23.58 source.trimmed.mp4  # Creates duplicate file
```

**NEW:** Detect trim point, use in Remotion
```bash
# Step 4: Detect trim (no file creation)
trim_start_seconds: 23.58  # Saved in job.yaml
```

```tsx
// Remotion composition
<OffthreadVideo
  src="source.mp4"           // Original file
  startFrom={23.58 * fps}    // Skip to start point
/>
```

**Benefits:**
- ✅ No re-encoding (faster)
- ✅ No quality loss
- ✅ Less disk space
- ✅ Easy to adjust (edit YAML, re-render)

---

### 3. Pipeline Steps

**Updated Pipeline:**

1. **Download** - Get video from YouTube or local file
   - Output: `source.mp4` (original, unmodified)

2. **Parse** - Extract company/quarter from metadata
   - Auto-detect ticker and quarter

3. **Transcribe** - Run Whisper
   - Output: `transcript.json`
   - GPU-accelerated (15-20 min for 46-min video)

4. **Detect Trim** - Find start point
   - Detects first speech
   - Calculates: `first_speech - 5s` (keeps intro music)
   - Saves to job.yaml (NO file creation)

5. **Insights** - Extract with OpenAI GPT-4o
   - Input: transcript + company metadata
   - Output: Highlights, chapters, speakers
   - Backup: `insights.raw.json` (read-only)
   - Main: Merged into job.yaml

6. **Render** - Remotion (manual for now)
7. **Upload** - YouTube (manual for now)

---

### 4. File Structure

```
/var/markethawk/
├── jobs/                                      # Job definitions
│   ├── PLTR_Q3_2025_20251109_043000.yaml    # ← SINGLE SOURCE OF TRUTH
│   ├── HOOD_Q3_2025_20251109_050000.yaml
│   └── AAPL_Q4_2024_20251110_120000.yaml
│
├── _downloads/                                # Raw processing files
│   └── jUnV3LiN0_k/                          # By YouTube video ID
│       ├── source.mp4                         # Original (no trimming!)
│       ├── metadata.json                      # YouTube metadata
│       ├── transcript.json                    # Whisper output
│       ├── transcript.paragraphs.json         # Optimized for GPT
│       ├── transcript.srt                     # Subtitles
│       ├── transcript.vtt                     # WebVTT
│       ├── insights.raw.json                  # OpenAI backup (read-only)
│       └── usage.json                         # Token usage (read-only)
│
└── PLTR/Q3-2025/                             # Final outputs (by company/quarter)
    ├── take1/
    │   └── final.mp4                          # First render
    └── take2/
        └── final.mp4                          # Fixed render
```

**Removed Files:**
- ❌ `.state.json` (replaced by job.yaml)
- ❌ `production.json` (merged into job.yaml)
- ❌ `insights.json` (merged into job.yaml)
- ❌ `source.trimmed.mp4` (no longer needed)

**New Files:**
- ✅ `jobs/<job_id>.yaml` - Single source of truth
- ✅ `insights.raw.json` - OpenAI response backup
- ✅ `usage.json` - Token usage tracking

---

### 5. CLI Commands

```bash
# Create job
python lens/job.py create \
  --url "https://youtube.com/watch?v=..." \
  --ticker PLTR \
  --quarter Q3-2025

# Process job (all steps)
python lens/job.py process PLTR_Q3_2025_20251109_043000

# Run single step
python lens/job.py process <job_id> --step transcribe

# Run from step onwards
python lens/job.py process <job_id> --from-step insights

# Check status
python lens/job.py status <job_id>

# List all jobs
python lens/job.py list
```

---

### 6. Manual Editing Workflow

**Scenario:** Trim point is wrong, need to adjust

**OLD:**
```bash
# Re-run entire trim step
python process_earnings.py --step smart-trim --start-time 25.0
# Creates new trimmed file
# Need to re-run insights to adjust timestamps
```

**NEW:**
```bash
# 1. Edit job YAML
nano /var/markethawk/jobs/PLTR_Q3_2025_20251109_043000.yaml

# Change:
trim_start_seconds: 23.58  →  25.0

# 2. Re-render (Remotion reads updated value)
cd studio
npx remotion render PLTR-Q3-2025 output.mp4
```

**Benefits:**
- ✅ No re-processing
- ✅ Instant update
- ✅ Just re-render

---

### 7. Dependencies

**Added:**
```
PyYAML
```

**Install:**
```bash
cd ~/markethawk
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 8. Migration Path

**For existing videos:**

1. No migration needed - old files still work
2. New videos use job.yaml workflow
3. Gradually deprecate old scripts

**Cleanup (optional):**
```bash
# Remove old state files
find /var/markethawk/_downloads -name ".state.json" -delete
find /var/markethawk -name "production.json" -delete
find /var/markethawk -name "source.trimmed.mp4" -delete
```

---

### 9. Remotion Integration

**Compositions read job.yaml:**

```tsx
// studio/src/utils/loadJob.ts
import yaml from 'js-yaml';
import fs from 'fs';

export function loadJob(ticker: string, quarter: string) {
  // Find latest job for this ticker/quarter
  const jobsDir = '/var/markethawk/jobs';
  const jobFiles = fs.readdirSync(jobsDir)
    .filter(f => f.startsWith(`${ticker}_${quarter}`))
    .sort()
    .reverse();

  const jobFile = `${jobsDir}/${jobFiles[0]}`;
  return yaml.load(fs.readFileSync(jobFile, 'utf8'));
}

// In composition
const job = loadJob('PLTR', 'Q3-2025');
const trimStart = job.processing.detect_trim.output.trim_start_seconds;
const highlights = job.processing.insights.output.highlights;

<OffthreadVideo
  src={mediaServerUrl + '/source.mp4'}
  startFrom={trimStart * fps}
/>
```

---

### 10. Benefits Summary

**Faster:**
- ✅ No video re-encoding (trim step removed)
- ✅ Instant edits (just update YAML)

**Simpler:**
- ✅ One file to manage
- ✅ Easy to understand
- ✅ Less code to maintain

**More Flexible:**
- ✅ Edit any value in YAML
- ✅ Multiple input types (YouTube, file, URL)
- ✅ Add supplementary files/notes

**More Reliable:**
- ✅ No scattered state
- ✅ No sync issues
- ✅ Audit trail in git

---

## Documentation

- **JOB-WORKFLOW.md** - Complete usage guide
- **lens/job.yaml.template** - Job schema with comments
- **lens/job.py** - CLI reference
- **lens/process_job_pipeline.py** - Pipeline implementation

---

**Status:** Implemented
**Date:** 2025-11-09
**Breaking Changes:** None (old workflow still works)
