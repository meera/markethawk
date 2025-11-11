# MarketHawk Collocation Structure

**Philosophy:** Everything for a job lives in ONE directory. No scattered files.

## Directory Structure

```
/var/markethawk/jobs/
└── BIP_Q3_2025_20251109_132857/      # Job directory (all assets here)
    ├── job.yaml                       # Single source of truth
    ├── input/
    │   └── source.mp4                 # Downloaded video (original, untrimmed)
    ├── transcript.json                # Full Whisper transcript
    ├── transcript.paragraphs.json     # Optimized for GPT
    ├── transcript.srt                 # Subtitles (if generated)
    ├── transcript.vtt                 # WebVTT captions (if generated)
    ├── insights.raw.json              # OpenAI raw response (backup)
    └── usage.json                     # OpenAI token usage tracking
```

## Benefits of Collocation

✅ **Everything in one place** - No hunting across multiple directories
✅ **Easy to backup** - Just copy the job directory
✅ **Easy to delete** - Remove one directory to clean up
✅ **Easy to share** - tar/zip the job directory
✅ **Simple to understand** - One job = one directory

## Job Creation

```bash
# Create new job
python lens/job.py create \
  --url "https://..." \
  --ticker BIP \
  --quarter Q3-2025 \
  --company "Brookfield Infrastructure"

# Creates:
# /var/markethawk/jobs/BIP_Q3_2025_20251109_132857/
# └── job.yaml
```

## Processing Pipeline

```bash
# Process job (downloads to job directory)
python lens/job.py process BIP_Q3_2025_20251109_132857

# Files created in job directory:
# - input/source.mp4
# - transcript.json
# - transcript.paragraphs.json
# - insights.raw.json
# - usage.json
```

## File Paths in Code

```python
# OLD (scattered across multiple directories):
DOWNLOADS_DIR / video_id / "source.mp4"
DOWNLOADS_DIR / video_id / "transcript.json"
ORGANIZED_DIR / ticker / quarter / "insights.json"

# NEW (collocated in job directory):
job_dir / "input" / "source.mp4"
job_dir / "transcript.json"
job_dir / "insights.raw.json"
job_dir / "job.yaml"  # Contains all metadata, no separate insights.json
```

## Migration from Old Structure

If you have old jobs in `/var/markethawk/_downloads/`, they can be migrated:

```bash
# Move old job to new structure
OLD_DIR="/var/markethawk/_downloads/hls_06c95197d7ac"
NEW_DIR="/var/markethawk/jobs/BIP_Q3_2025_20251109_132857"

mkdir -p $NEW_DIR/input
mv $OLD_DIR/source.mp4 $NEW_DIR/input/
mv $OLD_DIR/*.json $NEW_DIR/
```

## Key Changes

1. **No more video_id** - Job ID is the directory name
2. **No more separate metadata.json** - All metadata in job.yaml
3. **No trimmed video** - Use Remotion's `startFrom` prop with `trim_start_seconds`
4. **Renders tracked in job.yaml** - Latest first in `renders:` array

## Renders

When rendering videos, store them in the job directory:

```yaml
renders:
  - take: 2
    file: /var/markethawk/jobs/BIP_Q3_2025_20251109_132857/renders/take2.mp4
    rendered_at: "2025-11-10T16:30:00Z"
    notes: "Fixed trim point to 25.0"

  - take: 1
    file: /var/markethawk/jobs/BIP_Q3_2025_20251109_132857/renders/take1.mp4
    rendered_at: "2025-11-09T14:00:00Z"
    notes: "Initial render"
```

---

**Remember:** One job = one directory. Everything collocated. Simple.
