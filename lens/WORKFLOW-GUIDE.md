# Earnings Video Processing Workflow Guide

## Overview

The unified Python orchestrator `process_earnings.py` can run all steps at once OR individual steps separately.

**Key Features:**
- ✅ Pure Python (works on Mac & Linux)
- ✅ State tracking (skips completed steps)
- ✅ Resume from any step
- ✅ Run individual steps for debugging
- ✅ Automatic silence removal
- ✅ Metadata-driven organization

---

## Quick Start

### Process Complete Video (All Steps)

```bash
cd ~/markethawk/sushi
python process_earnings.py --url "https://www.youtube.com/watch?v=jUnV3LiN0_k"
```

**What it does:**
1. Downloads video to `_downloads/<video_id>/`
2. Parses metadata → detects company/quarter
3. Removes initial silence
4. Transcribes with Whisper
5. Extracts insights with LLM
6. Renders video with Remotion
7. Uploads to YouTube

---

## Individual Steps

### 1. Download Only
```bash
python process_earnings.py --url "..." --step download
```

**Creates:**
```
/var/markethawk/_downloads/jUnV3LiN0_k/
├── input/
│   ├── source.mp4
│   └── metadata.json
└── .state.json
```

### 2. Parse Metadata
```bash
python process_earnings.py --url "..." --step parse
```

**Detects:** Company (PLTR), Quarter (Q3-2024)

**Creates:**
```
/var/markethawk/PLTR/Q3-2024/
├── input/
├── transcripts/
├── take1/
└── metadata.json
```

### 3. Remove Silence
```bash
python process_earnings.py --url "..." --step remove-silence
```

**Trims:** Initial silence from video
**Output:** `/var/markethawk/PLTR/Q3-2024/input/source.mp4`

### 4. Transcribe
```bash
python process_earnings.py --url "..." --step transcribe
```

**Output:** `/var/markethawk/PLTR/Q3-2024/transcripts/transcript.json`

### 5. Extract Insights
```bash
python process_earnings.py --url "..." --step insights
```

**Output:** `/var/markethawk/PLTR/Q3-2024/transcripts/insights.json`

### 6. Render Video
```bash
python process_earnings.py --url "..." --step render
```

**Output:** `/var/markethawk/PLTR/Q3-2024/take1/final.mp4`

### 7. Upload to YouTube
```bash
python process_earnings.py --url "..." --step upload
```

---

## Resume from Specific Step

If a step fails, resume from there:

```bash
# Resume from transcription onwards
python process_earnings.py --url "..." --from transcribe

# Resume from render onwards
python process_earnings.py --url "..." --from render
```

---

## Mac vs Sushi (Linux)

### ✅ **Steps That Work Great on Mac**
1. **Download** - Same speed as sushi
2. **Parse** - Instant
3. **Remove silence** - Fast (requires ffmpeg: `brew install ffmpeg`)
4. **Insights** - API call (same speed)
5. **Upload** - API call (same speed)

### ⚠️ **Steps Slower on Mac (Use Sushi)**
4. **Transcribe** - CPU-only (60-90 min vs 15-20 min on sushi)
5. **Render** - CPU-only (20-30 min vs 5-10 min on sushi)

### Recommended Split Workflow

**On Mac (Quick steps):**
```bash
cd ~/markethawk/sushi
python process_earnings.py --url "..." --step download
python process_earnings.py --url "..." --step parse
python process_earnings.py --url "..." --step remove-silence
```

**On Sushi (Heavy processing):**
```bash
ssh meera@192.168.1.101
cd ~/markethawk/sushi
python process_earnings.py --url "..." --from transcribe
```

Since `/var/markethawk/` is mounted on both, files are instantly available!

---

## State Tracking

State is saved in `_downloads/<video_id>/.state.json`

**Example:**
```json
{
  "steps": {
    "download": {
      "status": "completed",
      "timestamp": "2024-11-05T10:30:00",
      "data": {"video_id": "jUnV3LiN0_k", "url": "..."}
    },
    "parse": {
      "status": "completed",
      "timestamp": "2024-11-05T10:30:05",
      "data": {"ticker": "PLTR", "quarter": "Q3-2024"}
    }
  }
}
```

**Benefits:**
- ✅ Rerun command safely (skips completed steps)
- ✅ Resume after failure
- ✅ Track progress

---

## Directory Structure

```
/var/markethawk/
├── _downloads/                    # Permanent archive
│   └── jUnV3LiN0_k/
│       ├── input/
│       │   ├── source.mp4        # Original (with silence)
│       │   └── metadata.json     # Complete RapidAPI data
│       └── .state.json            # Processing state
│
├── PLTR/                          # Auto-organized
│   └── Q3-2024/
│       ├── input/
│       │   └── source.mp4        # Trimmed (silence removed)
│       ├── transcripts/
│       │   ├── transcript.json
│       │   └── insights.json
│       ├── take1/
│       │   ├── final.mp4
│       │   └── thumbnail.jpg
│       └── metadata.json
```

---

## Setup

### On Mac
```bash
cd ~/markethawk/sushi

# 1. Create Python environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install ffmpeg (for silence removal)
brew install ffmpeg

# 4. Mount /var/markethawk
sudo ln -sf /Volumes/markethawk /var/markethawk

# 5. Copy .env
cp ../.env .env

# Ready!
python process_earnings.py --url "..." --step download
```

### On Sushi
```bash
cd ~/markethawk/sushi

# 1. Create Python environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install ffmpeg (if not already)
sudo apt install ffmpeg

# 4. Fix permissions
sudo chown -R meera:meera /var/markethawk

# 5. Copy .env
cp ../.env .env

# Ready!
python process_earnings.py --url "..."
```

---

## Common Workflows

### Debug Single Step
```bash
# Download and parse only
python process_earnings.py --url "..." --step download
python process_earnings.py --url "..." --step parse

# Check what was detected
cat /var/markethawk/_downloads/jUnV3LiN0_k/.state.json | jq .
```

### Re-render Video (Different Take)
```bash
# Transcription/insights already done, just re-render
python process_earnings.py --url "..." --step render

# Manually move to take2
COMPANY_DIR="/var/markethawk/PLTR/Q3-2024"
mkdir -p $COMPANY_DIR/take2
mv $COMPANY_DIR/take1/final.mp4 $COMPANY_DIR/take2/final-v1.mp4
```

### Process Multiple Videos in Parallel
```bash
# Terminal 1
python process_earnings.py --url "https://youtube.com/watch?v=video1"

# Terminal 2
python process_earnings.py --url "https://youtube.com/watch?v=video2"

# Different video IDs = different state files = no conflicts
```

### Queue Downloads on Mac, Process on Sushi
```bash
# On Mac - download multiple videos
python process_earnings.py --url "video1" --step download
python process_earnings.py --url "video2" --step download
python process_earnings.py --url "video3" --step download

# Parse them all
python process_earnings.py --url "video1" --step parse
python process_earnings.py --url "video2" --step parse
python process_earnings.py --url "video3" --step parse

# Later on Sushi - batch process
ssh meera@192.168.1.101
cd ~/markethawk/sushi
source .venv/bin/activate

python process_earnings.py --url "video1" --from transcribe
python process_earnings.py --url "video2" --from transcribe
python process_earnings.py --url "video3" --from transcribe
```

---

## Silence Removal Details

**Settings** (in `remove-silence.py`):
- Threshold: `-50dB` (adjust for quieter/louder videos)
- Min duration: `0.5s` (minimum silence length to detect)

**Customize:**
```bash
# Edit remove-silence.py
nano scripts/remove-silence.py

# Change:
threshold = "-40dB"  # More aggressive
min_duration = 1.0   # Only remove longer silences
```

---

## Troubleshooting

### "Metadata not found"
```bash
# Run download step first
python process_earnings.py --url "..." --step download
```

### "Parse data not found"
```bash
# Run parse step
python process_earnings.py --url "..." --step parse
```

### "Could not parse company/quarter"
```bash
# Check metadata
cat /var/markethawk/_downloads/jUnV3LiN0_k/input/metadata.json | jq .

# Manually add ticker to TICKER_MAP in parse-metadata.py
nano scripts/parse-metadata.py
```

### Reset State (Start Fresh)
```bash
VIDEO_ID="jUnV3LiN0_k"
rm /var/markethawk/_downloads/$VIDEO_ID/.state.json

# Now rerun
python process_earnings.py --url "..."
```

### Module Import Errors
```bash
# Make sure you're in venv
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Performance

### Expected Times (46-min earnings call)

| Step | Mac (CPU) | Sushi (GPU) | Notes |
|------|-----------|-------------|-------|
| Download | 1-2 min | 1-2 min | Network speed |
| Parse | <1 sec | <1 sec | Instant |
| Remove Silence | 5-10 sec | 5-10 sec | Fast (codec copy) |
| Transcribe | 60-90 min | 15-20 min | **GPU wins** |
| Insights | 30 sec | 30 sec | API call |
| Render | 20-30 min | 5-10 min | **GPU wins** |
| Upload | 2-3 min | 2-3 min | Network speed |
| **Total** | **~90-120 min** | **~25-35 min** | **3-4x faster on GPU** |

---

## Import as Module

You can also import and use the processor programmatically:

```python
from process_earnings import EarningsProcessor

# Process video
processor = EarningsProcessor("https://youtube.com/watch?v=...")

# Run all steps
processor.run_all()

# Or run individual steps
processor.step_download()
processor.step_parse()
processor.step_transcribe()

# Get state
ticker = processor.state.get_data("parse", "ticker")
quarter = processor.state.get_data("parse", "quarter")
```

---

## Next Steps

1. Process first video end-to-end
2. Review quality of transcript, insights, render
3. Iterate on video template
4. Scale to multiple videos

---

**Last Updated:** November 5, 2024
