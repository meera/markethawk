# MarketHawk Workflow

**Single Source of Truth:** `job.yaml` in each job directory

---

## Quick Reference

```bash
# 1. Create job
python lens/job.py create \
  --url "https://youtube.com/watch?v=..." \
  --ticker BIP \
  --quarter Q3-2025

# 2. Process job (download → transcribe → insights)
python lens/process_job_pipeline.py /var/markethawk/jobs/{JOB_ID}/job.yaml

# 3. Check status
python lens/job.py list

# 4. Render (ALWAYS in background)
screen -S render
npx remotion render BIP-Q3-2025 /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4
# Ctrl+A then D to detach

# 5. Preview
http://192.168.1.101:8080/preview-chapters.html?job={JOB_ID}&take=take1.mp4

# 6. Generate thumbnails
python lens/smart_thumbnail_generator.py \
  --video /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4 \
  --data /var/markethawk/jobs/{JOB_ID}/job.yaml \
  --output /var/markethawk/jobs/{JOB_ID}/thumbnails/

# 7. Upload to YouTube
python lens/scripts/upload_youtube.py \
  --video /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4 \
  --thumbnail /var/markethawk/jobs/{JOB_ID}/thumbnails/thumbnail_1.jpg \
  --metadata /var/markethawk/jobs/{JOB_ID}/job.yaml
```

---

## Complete Workflow

### Step 1: Create Job

```bash
cd ~/markethawk
source .venv/bin/activate

# From YouTube URL
python lens/job.py create \
  --url "https://youtube.com/watch?v=jUnV3LiN0_k" \
  --ticker BIP \
  --quarter Q3-2025 \
  --company "Brookfield Infrastructure Partners LP"

# From HLS stream
python lens/job.py create \
  --url "https://media.server.com/.../audio.m3u8" \
  --ticker PLTR \
  --quarter Q3-2025
```

**Output:**
```
✓ Job created: BIP_Q3_2025_20251109_135511
  Directory: /var/markethawk/jobs/BIP_Q3_2025_20251109_135511
  Job file: /var/markethawk/jobs/BIP_Q3_2025_20251109_135511/job.yaml
  Input: youtube_url
  Company: BIP Q3-2025

Next: python lens/process_job_pipeline.py /var/markethawk/jobs/BIP_Q3_2025_20251109_135511/job.yaml
```

---

### Step 2: Process Job

```bash
python lens/process_job_pipeline.py /var/markethawk/jobs/{JOB_ID}/job.yaml
```

**Pipeline steps:**
1. Download - YouTube or HLS stream
2. Parse metadata - Extract ticker/quarter
3. Transcribe - WhisperX with speaker diarization
4. Detect trim point - Skip silence (5s before first speech)
5. Extract insights - OpenAI GPT-4o structured outputs

**Takes:** 20-30 min on GPU machine (sushi)

**Check progress:**
```bash
python lens/job.py list
```

---

### Step 3: Manual Review

```bash
# View job status
python lens/job.py list

# Edit job.yaml if needed
nano /var/markethawk/jobs/{JOB_ID}/job.yaml
```

**Common edits:**
- Adjust `trim_start_seconds` for timing
- Fix highlight timestamps
- Update YouTube title/description
- Add notes

---

### Step 4: Render Video (Background!)

**CRITICAL: Always run renders in background to prevent accidental terminal shutdown!**

```bash
# Terminal 1: Start media server (keep running)
cd /var/markethawk
npx serve . --cors -p 8080

# Terminal 2: Render in background with screen
screen -S render
cd ~/markethawk/studio
npx remotion render BIP-Q3-2025 /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4

# Press Ctrl+A then D to detach
# screen -r render  # to reattach and check progress
```

**Why background rendering is critical:**
- Renders take 15-30 minutes
- Accidental terminal close = lost render progress
- Use `screen` to persist session

---

### Step 5: Preview Before Upload

**Preview video, chapters, and thumbnails BEFORE uploading to YouTube:**

```bash
# Ensure media server is running
cd /var/markethawk
npx serve . --cors -p 8080

# Open in browser:
http://192.168.1.101:8080/preview-chapters.html?job={JOB_ID}&take=take1.mp4
```

**What to verify:**
- ✅ Video playback with all overlays
- ✅ Chapter markers (clickable timestamps)
- ✅ YouTube description formatting
- ✅ Thumbnails (4 variations)
- ✅ Hashtags

**If issues found:**
- Edit timestamps in composition (studio/src/compositions/BIP_Q3_2025.tsx)
- Render take2 with corrections
- Preview again before upload

---

### Step 6: Generate Thumbnails

```bash
cd ~/markethawk
source .venv/bin/activate

python lens/smart_thumbnail_generator.py \
  --video /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4 \
  --data /var/markethawk/jobs/{JOB_ID}/job.yaml \
  --output /var/markethawk/jobs/{JOB_ID}/thumbnails/
```

**Output:** 4 thumbnail variations in `thumbnails/` directory

---

### Step 7: Upload to YouTube

```bash
python lens/scripts/upload_youtube.py \
  --video /var/markethawk/jobs/{JOB_ID}/renders/take1.mp4 \
  --thumbnail /var/markethawk/jobs/{JOB_ID}/thumbnails/thumbnail_1.jpg \
  --metadata /var/markethawk/jobs/{JOB_ID}/job.yaml
```

---

## File Structure

```
/var/markethawk/
└── jobs/
    └── BIP_Q3_2025_20251109_135511/    # Collocated job directory
        ├── job.yaml                     # Single source of truth
        ├── input/
        │   └── source.mp4               # Downloaded audio/video
        ├── transcripts/
        │   ├── transcript.json          # WhisperX output
        │   └── paragraphs.json          # Optimized for GPT
        ├── renders/
        │   ├── take1.mp4                # First render
        │   └── take2.mp4                # Second render (corrections)
        └── thumbnails/
            ├── thumbnail_1.jpg
            ├── thumbnail_2.jpg
            ├── thumbnail_3.jpg
            └── thumbnail_4.jpg
```

---

## Audio-Only Earnings Calls

**For HLS streams or audio-only sources:**

See `AUDIO-ONLY-EARNINGS-RECIPE.md` for complete recipe.

**Key points:**
- Use `<Audio>` component, NOT `<OffthreadVideo>` (audio-only files have no video stream)
- Create static branded background (company colors + ticker watermark)
- Add `FadedAudio` component for smooth transitions between title music and earnings audio
- Generate thumbnails from rendered video (not from source)

**Example:** `studio/src/compositions/BIP_Q3_2025.tsx`

---

## Thumbnail Options

See `THUMBNAIL-OPTIONS.md` for complete guide.

**Phase 1 (Current):** Text-focused thumbnails
- Metric-focused: "REVENUE UP 100%" with large numbers
- Company-focused: Company name + key metric
- Question/teaser: "Why did stock surge?"

**Phase 2 (Future):** Executive photos
- Build CEO/CFO photo database for top 50 companies
- Split screen: CEO photo + key metric
- Higher click-through rates with faces

---

## Tips

### Resume Failed Jobs

If a step fails, fix the issue and re-run from that step:
```bash
python lens/process_job_pipeline.py /var/markethawk/jobs/{JOB_ID}/job.yaml --step transcribe
```

### List All Jobs

```bash
python lens/job.py list
```

Output:
```
Job ID                               Status      Company         Created
------------------------------------------------------------------------------------
BIP_Q3_2025_20251109_135511         completed   BIP Q3-2025     2025-11-09 13:55
PLTR_Q3_2025_20251103_120000        processing  PLTR Q3-2025    2025-11-03 12:00
```

### Add Notes to job.yaml

```yaml
notes: |
  2025-11-09: Processed video
  2025-11-10: Rendered take1, uploaded to YouTube

  Great highlight at 12:30 about infrastructure growth
  Consider creating Short from revenue announcement at 3:15
```

---

## Related Documentation

- **AUDIO-ONLY-EARNINGS-RECIPE.md** - Complete workflow for audio-only videos
- **THUMBNAIL-OPTIONS.md** - Thumbnail generation strategies
- **COLLOCATION-STRUCTURE.md** - Job directory organization
- **CLAUDE-STREAMLINED.md** - Project overview and guidelines

---

**Last Updated:** 2025-11-09
