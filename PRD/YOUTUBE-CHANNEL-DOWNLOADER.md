# YouTube Channel Downloader

**Status:** Active Development
**Last Updated:** 2025-11-12
**Environment:** Sushi (Linux GPU machine)

---

## Overview

Bulk download YouTube channel videos using Rapid API for earnings call content acquisition. Designed for investor relations channels (e.g., BrookfieldIR, ParamountIR) with hundreds of videos.

**Key Requirements:**
- Download 100+ videos per channel
- Resume capability (network failures, interruptions)
- Run in background on sushi (screen sessions)
- Paid Rapid API tier (bypass quota limits)
- CSV-based workflow (simple, human-editable)

---

## Architecture: 3-Script Approach

### Design Philosophy
Separate concerns into independent, resilient scripts that can be run/debugged individually.

```
Script 1: List Videos → CSV
Script 2: Download Single Video (atomic operation)
Script 3: Process CSV → Batch download with state management
```

---

## Script 1: `list_channel_videos.py`

**Purpose:** Fetch all videos from YouTube channel and save to CSV

**API:** YouTube Data API v3 (OAuth, 10,000 units/day quota)

### Features
- Accept channel name/ID/URL (normalize to channel ID)
- Paginated API calls (fetch all videos)
- Optional filtering:
  - `--filter-title "earnings"` - Keyword search
  - `--min-duration 600` - Minimum 10 minutes
  - `--after-date 2024-01-01` - Recent videos only
- Save to: `/var/markethawk/youtube/{channel_name}_videos.csv`

### CSV Format
```csv
video_id,title,description,published_at,duration,view_count,thumbnail_url,channel_name
abc123,Q3 2025 Earnings Call,Full transcript...,2025-10-15T10:00:00Z,PT45M23S,1234,https://i.ytimg.com/...,BrookfieldIR
def456,Q2 2025 Earnings Call,Full transcript...,2025-07-10T10:00:00Z,PT52M15S,5678,https://i.ytimg.com/...,BrookfieldIR
```

**Fields:**
- `video_id` - YouTube video ID (required for download)
- `title` - Video title
- `description` - Full description text
- `published_at` - ISO 8601 timestamp
- `duration` - ISO 8601 duration (PT45M23S = 45 min 23 sec)
- `view_count` - Number of views
- `thumbnail_url` - Default thumbnail URL
- `channel_name` - Source channel

### CLI Usage
```bash
# List all videos from channel
python scripts/list_channel_videos.py --channel "BrookfieldIR"

# Filter for earnings calls only
python scripts/list_channel_videos.py --channel "@ParamountIR" --filter-title "earnings"

# Recent videos only (10+ minutes)
python scripts/list_channel_videos.py --channel "UCxxx..." --after-date 2024-01-01 --min-duration 600
```

### Output
- CSV file: `/var/markethawk/youtube/{channel_name}_videos.csv`
- Log file: `/var/markethawk/youtube/{channel_name}_list.log`

---

## Script 2: `download_single_video.py`

**Purpose:** Download one video using Rapid API (atomic operation)

**API:** Rapid API - YouTube Media Downloader (paid tier)

### Features
- Download best quality MP4 with audio
- File validation (size > 1MB, ffprobe check)
- Save metadata alongside video
- Exit code: 0 (success), 1 (failure)
- Detailed error logging

### Implementation
Copy `YouTubeVideoDownloader` class from VideotoBe:
- Source: `/Users/Meera/videotobe/platform/transcription-server/app/services/youtube_downloader_rapidapi.py`
- API endpoint: `https://youtube-media-downloader.p.rapidapi.com/v2/video/details`
- Quality priority: 1080p → 720p → 480p (best available with audio)

### Directory Structure
```
/var/markethawk/youtube/{video_id}/
├── {video_id}.mp4                 # Downloaded video
├── rapidapi_metadata.json         # Rapid API response
├── youtube_metadata.json          # YouTube metadata from CSV
└── download.log                   # Download log
```

### CLI Usage
```bash
# Download by video ID
python scripts/download_single_video.py --video-id abc123

# With metadata passthrough from CSV
python scripts/download_single_video.py \
  --video-id abc123 \
  --title "Q3 2025 Earnings" \
  --published-at "2025-10-15T10:00:00Z" \
  --output /var/markethawk/youtube
```

### File Validation
```python
# Check file size
if os.path.getsize(video_path) < 1_000_000:  # < 1MB
    raise ValueError("File too small - download failed")

# Verify MP4 format
subprocess.run(['ffprobe', video_path], check=True)
```

---

## Script 3: `process_channel_csv.py`

**Purpose:** Batch download manager with state persistence and resume capability

### Features
- Read CSV from Script 1
- Track download state in JSON
- Call Script 2 for each video (subprocess)
- Resume from last position (idempotent)
- Retry failed videos (max 3 attempts)
- Parallel downloads (configurable workers)
- Rate limiting (configurable delay)

### State Management

**State File:** `{csv_basename}_state.json`

```json
{
  "csv_file": "/var/markethawk/youtube/brookfield_videos.csv",
  "total_videos": 150,
  "started_at": "2025-11-12T10:00:00Z",
  "last_updated": "2025-11-12T11:30:00Z",
  "videos": {
    "abc123": {
      "status": "completed",
      "file": "/var/markethawk/youtube/abc123/abc123.mp4",
      "file_size_mb": 245.3,
      "downloaded_at": "2025-11-12T10:30:00Z"
    },
    "def456": {
      "status": "failed",
      "error": "Rapid API timeout",
      "attempts": 3,
      "last_attempt": "2025-11-12T11:00:00Z"
    },
    "ghi789": {
      "status": "pending"
    },
    "jkl012": {
      "status": "downloading",
      "attempts": 1,
      "started_at": "2025-11-12T11:30:00Z"
    }
  },
  "summary": {
    "completed": 120,
    "failed": 5,
    "pending": 24,
    "downloading": 1
  }
}
```

**Status Values:**
- `pending` - Not yet started
- `downloading` - Currently in progress
- `completed` - Successfully downloaded
- `failed` - Failed after max retries

### Resilience Strategy

**1. Resume Capability:**
- Load state file on startup
- Skip `completed` videos
- Continue from last position
- Idempotent (safe to run multiple times)

**2. Failure Isolation:**
- One video failure doesn't stop entire job
- Failed videos tracked in state
- Continue to next video

**3. Retry Logic:**
- Max 3 attempts per video
- Exponential backoff: 5s → 15s → 45s
- Track attempt count in state

**4. State Persistence:**
- Save state after each video
- Atomic writes (write to temp, then rename)
- Survive process crashes

### Rate Limiting

**Rapid API Paid Tier:**
- Check your plan limits (e.g., 100 requests/min, 10,000/day)
- Default delay: 2 seconds between videos
- Configurable via `--delay` flag

**Implementation:**
```python
import time
time.sleep(delay_seconds)  # Between downloads
```

### Parallel Downloads

**Thread Pool:**
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=workers) as executor:
    futures = {executor.submit(download_video, vid): vid for vid in pending}
```

**Considerations:**
- Default workers: 3
- Respect Rapid API rate limits
- Each worker saves state independently

### CLI Usage

```bash
# Initial run (download all)
python scripts/process_channel_csv.py \
  --csv /var/markethawk/youtube/brookfield_videos.csv \
  --workers 3 \
  --delay 2

# Resume after interruption (auto-detects state)
python scripts/process_channel_csv.py \
  --csv /var/markethawk/youtube/brookfield_videos.csv

# Retry only failed videos
python scripts/process_channel_csv.py \
  --csv /var/markethawk/youtube/brookfield_videos.csv \
  --retry-failed

# Fresh start (ignore existing state)
python scripts/process_channel_csv.py \
  --csv /var/markethawk/youtube/brookfield_videos.csv \
  --fresh

# Limit for testing (first 5 videos)
python scripts/process_channel_csv.py \
  --csv /var/markethawk/youtube/brookfield_videos.csv \
  --limit 5 \
  --workers 1
```

### Progress Monitoring

```bash
# View state file
cat /var/markethawk/youtube/brookfield_videos_state.json | jq '.summary'

# Watch log file
tail -f /var/markethawk/youtube/download.log

# Check specific video status
cat brookfield_videos_state.json | jq '.videos["abc123"]'
```

---

## Directory Structure

```
/var/markethawk/youtube/
├── brookfield_videos.csv              # Script 1 output
├── brookfield_videos_state.json       # Script 3 state
├── brookfield_videos_list.log         # Script 1 log
├── download.log                       # Script 3 consolidated log
│
├── abc123/                            # Video 1
│   ├── abc123.mp4                     # Downloaded video (245 MB)
│   ├── rapidapi_metadata.json         # Full Rapid API response
│   ├── youtube_metadata.json          # YouTube metadata from CSV
│   └── download.log                   # Individual download log
│
├── def456/                            # Video 2
│   ├── def456.mp4
│   ├── rapidapi_metadata.json
│   ├── youtube_metadata.json
│   └── download.log
│
└── ...                                # 150+ video directories
```

---

## Test Plan

### Phase 1: Single Video Test
**Goal:** Validate Rapid API download works on sushi

**Script:** `scripts/test_download_video.py`
- Simple standalone script
- Download one video
- Validate file integrity
- Test paid API key

**CLI:**
```bash
cd ~/markethawk
source .venv/bin/activate
python scripts/test_download_video.py --video-id abc123
```

**Success Criteria:**
- ✅ Video downloads successfully
- ✅ File size > 1MB
- ✅ MP4 playable (ffprobe validates)
- ✅ Metadata saved correctly

**PAUSE for human review:**
- Rapid API speed acceptable?
- File quality good?
- Rate limit issues?

### Phase 2: Full Implementation
After Phase 1 approval, build 3 scripts:
1. `list_channel_videos.py`
2. `download_single_video.py`
3. `process_channel_csv.py`

### Phase 3: Integration Test
```bash
# 1. List videos (limit to 5 for testing)
python scripts/list_channel_videos.py --channel "TestChannel" --limit 5

# 2. Download first 5 videos
python scripts/process_channel_csv.py \
  --csv /var/markethawk/youtube/testchannel_videos.csv \
  --workers 2 \
  --limit 5

# 3. Test resume (interrupt and restart)
# Ctrl+C during download, then re-run same command

# 4. Test retry failed
# Manually mark one as failed in state file, then:
python scripts/process_channel_csv.py \
  --csv /var/markethawk/youtube/testchannel_videos.csv \
  --retry-failed
```

---

## Production Workflow

### Typical Usage (on sushi)

```bash
# Step 1: List videos from channel
cd ~/markethawk
source .venv/bin/activate

python scripts/list_channel_videos.py \
  --channel "@BrookfieldIR" \
  --filter-title "earnings"

# Output: /var/markethawk/youtube/brookfieldir_videos.csv (150 videos)

# Step 2: Review CSV (optional)
head /var/markethawk/youtube/brookfieldir_videos.csv
# Manually remove unwanted videos if needed

# Step 3: Download all videos (in screen)
screen -S youtube-brookfield
cd ~/markethawk
source .venv/bin/activate

python scripts/process_channel_csv.py \
  --csv /var/markethawk/youtube/brookfieldir_videos.csv \
  --workers 3 \
  --delay 2

# Ctrl+A, D to detach

# Step 4: Monitor progress (anytime)
screen -r youtube-brookfield  # Reattach

# Or check state file
cat /var/markethawk/youtube/brookfieldir_videos_state.json | jq '.summary'

# Step 5: Handle failures (if any)
python scripts/process_channel_csv.py \
  --csv /var/markethawk/youtube/brookfieldir_videos.csv \
  --retry-failed
```

---

## Error Handling

### Common Failures

**1. Rapid API Rate Limit**
- Error: `429 Too Many Requests`
- Solution: Increase `--delay` or reduce `--workers`
- State: Mark as `failed`, retry later

**2. Network Timeout**
- Error: `requests.exceptions.Timeout`
- Solution: Automatic retry with backoff
- Max retries: 3

**3. Invalid Video ID**
- Error: `Video not found`
- Solution: Mark as permanently failed (no retry)

**4. Disk Space Full**
- Error: `OSError: No space left on device`
- Solution: Pause job, free space, resume

**5. Corrupted Download**
- Error: `File size < 1MB` or `ffprobe fails`
- Solution: Delete partial file, retry

### Logging Strategy

**Levels:**
- INFO: Progress updates (video 50/150 completed)
- WARNING: Retry attempts (video abc123 failed, retry 2/3)
- ERROR: Permanent failures (video def456 failed after 3 attempts)

**Log Files:**
- `/var/markethawk/youtube/download.log` - Consolidated log
- `/var/markethawk/youtube/{video_id}/download.log` - Per-video log

---

## Environment Setup

### Dependencies

```bash
# Python packages
pip install google-api-python-client google-auth-oauthlib requests python-dotenv

# System packages (already on sushi)
ffprobe  # For file validation
```

### Environment Variables

**File:** `.env` or `.env.sushi`

```bash
# YouTube Data API (OAuth)
YOUTUBE_CLIENT_SECRET_FILE="/Users/Meera/markethawk/Youtube-MarketHawk-OAuth.json"

# Rapid API (Paid Tier)
RAPID_API_KEY="3f1bb5e065msh90a5e46cb63b48ap1df86fjsnf05311ceb523"
```

### Storage Requirements

**Estimate for 150 videos:**
- Average video: 45 minutes
- MP4 bitrate: ~4 Mbps
- Size per video: ~135 MB
- Total: 150 × 135 MB = **~20 GB**

**Current availability:** 243 GB (sufficient)

---

## Success Criteria

### Functional Requirements
- ✅ Download 100+ videos from channel
- ✅ Resume after interruption (network, manual)
- ✅ Retry failed downloads (max 3 attempts)
- ✅ Parallel downloads (3 workers default)
- ✅ Track state persistently (JSON file)
- ✅ Validate file integrity (size, format)

### Non-Functional Requirements
- ✅ Run in background (screen session)
- ✅ Idempotent (safe to re-run)
- ✅ Comprehensive logging
- ✅ Human-readable CSV format
- ✅ Respect Rapid API rate limits

### Performance Targets
- Download speed: 2-5 videos/minute (with 3 workers, 2s delay)
- 150 videos: ~30-75 minutes total
- Resume overhead: < 5 seconds (state file load)

---

## Future Enhancements

**Not in MVP, consider later:**

1. **Audio Extraction**
   - Add `--audio-only` flag to Script 2
   - Use ffmpeg to extract MP3: `ffmpeg -i video.mp4 -vn -acodec libmp3lame audio.mp3`

2. **Database Integration**
   - Store video metadata in PostgreSQL
   - Link to companies table (match channel to ticker)

3. **Automatic Channel Discovery**
   - Scrape company IR pages for YouTube links
   - Auto-generate channel list from companies table

4. **Duplicate Detection**
   - Check if video already processed (different channel, same content)
   - Use video hash or YouTube video ID

5. **Metadata Enrichment**
   - Extract earnings quarter from title (regex)
   - Parse date from description
   - Auto-tag videos (Q1, Q2, Q3, Q4)

6. **Web UI**
   - Dashboard to monitor downloads
   - Manually mark videos as "skip"
   - View download progress in real-time

---

## Related Documentation

- **Main CLAUDE.md:** Project overview and architecture
- **WEB-APP-GUIDE.md:** Next.js web app integration
- **DATABASE-SCHEMA.md:** Companies table and metadata structure

---

**Last Updated:** 2025-11-12
**Status:** Ready for Phase 1 testing
