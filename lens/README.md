# Lens Pipeline - Earnings Video Processing

Complete Python-based pipeline for processing earnings call videos. Works on both Mac and Linux.

**Supports parallel processing** - process multiple videos simultaneously with automatic state management.

## Hybrid Workflow: Automated Prep + Manual Composition

**Steps 1-5:** Automated asset preparation (this pipeline)
**Step 6:** Manual creative work in Remotion Studio
**Step 7:** Automated YouTube upload

## Quick Start

```bash
# Setup (one time)
cd ~/earninglens
source .venv/bin/activate
pip install -r requirements.txt

# Process video through insights (Steps 1-5)
python lens/process_earnings.py --url "https://www.youtube.com/watch?v=jUnV3LiN0_k" --to insights

# Then work on composition in Remotion Studio
npm run remotion

# Upload when ready
python lens/process_earnings.py --url "https://www.youtube.com/watch?v=jUnV3LiN0_k" --step upload
```

## What It Does

### Automated Steps (1-5)
1. **Download** - YouTube video via RapidAPI
2. **Parse** - Auto-detect company, ticker, quarter
3. **Remove Silence** - Trim initial silence from video
4. **Transcribe** - Whisper GPU transcription → JSON, SRT, VTT, TXT
5. **Extract Insights** - LLM analysis → key metrics, highlights

### Manual Step (6)
6. **Compose** - Custom visuals in Remotion Studio (not automated)
   - Each video needs unique creative work
   - Design charts, animations, timing
   - Render when satisfied (take1, take2, etc.)

### Automated Step (7)
7. **Upload** - YouTube upload with optimized metadata

---

## Recommended Workflow

```bash
# 1. Automated prep (Steps 1-5)
python lens/process_earnings.py --url "..." --to insights

# 2. Manual composition (Step 6) - open Remotion Studio
npm run remotion

# 3. Upload when ready (Step 7)
python lens/process_earnings.py --url "..." --step upload
```

## Individual Steps (Advanced)

```bash
# Run individual steps
python lens/process_earnings.py --url "..." --step download
python lens/process_earnings.py --url "..." --step parse
python lens/process_earnings.py --url "..." --step remove-silence
python lens/process_earnings.py --url "..." --step transcribe
python lens/process_earnings.py --url "..." --step insights

# Skip render step (manual in Studio)
# python lens/process_earnings.py --url "..." --step render

# Upload manually after rendering
python lens/process_earnings.py --url "..." --step upload
```

---

## Resume from Step

```bash
# Resume from transcription onwards
python process_earnings.py --url "..." --from transcribe

# Resume from render onwards
python process_earnings.py --url "..." --from render
```

---

## File Structure

**Permanent Archive (`_downloads/`):** All source data tied to video_id
**Organized Outputs (`PLTR/`, etc.):** Only final rendered videos

```
/var/earninglens/
├── _downloads/                    # Permanent archive (source of truth)
│   └── <video_id>/
│       ├── input/
│       │   ├── source.mp4        # Original download (with silence)
│       │   └── metadata.json     # RapidAPI metadata
│       ├── processed/
│       │   └── trimmed.mp4       # Silence removed
│       ├── transcripts/          # All transcript formats
│       │   ├── transcript.json   # Full Whisper output
│       │   ├── transcript.srt    # Captions
│       │   ├── transcript.vtt    # WebVTT
│       │   ├── transcript.txt    # Plain text
│       │   └── paragraphs.json   # LLM-friendly format
│       ├── insights/
│       │   └── insights.json     # LLM-extracted insights
│       └── .state.json           # Processing state
│
├── PLTR/                          # Organized by company (final outputs only)
│   └── Q3-2024/                   # Auto-detected quarter
│       ├── take1/                 # Rendered video versions
│       │   ├── final.mp4
│       │   └── thumbnail.jpg
│       ├── take2/
│       └── metadata.json          # Parsed metadata
```

**Why this structure?**
- `_downloads/<video_id>/` = Permanent, tied to video_id, never changes
- `PLTR/Q3-2024/` = Organized output for rendered videos only
- If company/quarter gets re-parsed, transcripts don't move
- Single source of truth for all source data

---

## State Tracking

- State is saved in `_downloads/<video_id>/.state.json`
- Rerun safely - completed steps are skipped
- Resume from any step after failure

**Example state:**
```json
{
  "steps": {
    "download": {"status": "completed", "timestamp": "2024-11-05T10:30:00"},
    "parse": {"status": "completed", "data": {"ticker": "PLTR", "quarter": "Q3-2024"}},
    "transcribe": {"status": "in_progress"}
  }
}
```

---

## Mac + Linux Workflow

Works on both! Fast steps on Mac, heavy processing on Linux GPU.

**On Mac (Quick steps):**
```bash
cd ~/earninglens/sushi
source .venv/bin/activate

# Download multiple videos
python process_earnings.py --url "video1" --step download
python process_earnings.py --url "video2" --step download

# Parse them all
python process_earnings.py --url "video1" --step parse
python process_earnings.py --url "video2" --step parse
```

**On Sushi (GPU processing):**
```bash
ssh meera@192.168.1.101
cd ~/earninglens/sushi
source .venv/bin/activate

# Process from transcribe onwards (GPU-accelerated)
python process_earnings.py --url "video1" --from transcribe
python process_earnings.py --url "video2" --from transcribe
```

Since `/var/earninglens/` is mounted on both, files are instantly available!

---

## Performance (46-min video)

| Step | Mac (CPU) | Sushi (GPU) |
|------|-----------|-------------|
| Download | 1-2 min | 1-2 min |
| Parse | <1 sec | <1 sec |
| Remove Silence | 5-10 sec | 5-10 sec |
| **Transcribe** | **60-90 min** | **15-20 min** ⚡ |
| Insights | 30 sec | 30 sec |
| **Render** | **20-30 min** | **5-10 min** ⚡ |
| Upload | 2-3 min | 2-3 min |
| **Total** | **~90-120 min** | **~25-35 min** |

**3-4x faster on GPU!**

---

## Individual Scripts

All scripts can be run directly:

- `scripts/download-source.py` - Download from YouTube
- `scripts/parse-metadata.py` - Parse company/quarter
- `scripts/remove-silence.py` - Remove initial silence
- `transcribe.py` - Whisper transcription
- `process_video.py` - LLM insights extraction

---

## Setup

### On Mac
```bash
cd ~/earninglens/sushi

# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install ffmpeg
brew install ffmpeg

# Mount /var/earninglens
sudo ln -sf /Volumes/earninglens /var/earninglens

# Copy .env
cp ../.env .env
```

### On Sushi
```bash
cd ~/earninglens/sushi

# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install ffmpeg
sudo apt install ffmpeg

# Fix permissions
sudo chown -R meera:meera /var/earninglens

# Copy .env
cp ../.env .env
```

---

## Troubleshooting

**"Metadata not found"**
```bash
python process_earnings.py --url "..." --step download
```

**"Could not parse company/quarter"**
```bash
# Check metadata
cat /var/earninglens/_downloads/<video_id>/input/metadata.json

# Add ticker to TICKER_MAP in scripts/parse-metadata.py
```

**Reset state**
```bash
rm /var/earninglens/_downloads/<video_id>/.state.json
python process_earnings.py --url "..."
```

---

## Documentation

- **Complete Guide:** [WORKFLOW-GUIDE.md](./WORKFLOW-GUIDE.md)
- **Network Storage:** [NETWORK-STORAGE.md](./NETWORK-STORAGE.md)
- **Pipeline Setup:** [PIPELINE-SETUP.md](./PIPELINE-SETUP.md)

---

**Process your first video:**
```bash
python process_earnings.py --url "https://www.youtube.com/watch?v=jUnV3LiN0_k"
```
