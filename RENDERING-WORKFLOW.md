# Video Rendering Workflow

## Manual Rendering Steps

This document describes the manual steps for rendering earnings call videos after the composition has been created in Remotion Studio.

---

## Directory Structure

All rendered videos follow this structure:

```
/var/earninglens/
├── PLTR/
│   └── Q3-2025/
│       ├── input/           # Source files
│       ├── transcripts/     # Generated transcripts
│       ├── take1.mp4        # First render
│       ├── take2.mp4        # Second render (if needed)
│       └── metadata.json
├── AAPL/
│   └── Q4-2024/
│       ├── input/
│       ├── transcripts/
│       └── take1.mp4
└── [TICKER]/
    └── [QUARTER]-[YEAR]/
        └── take[N].mp4
```

**Naming Convention:**
- Company: Use ticker symbol (PLTR, AAPL, MSFT, etc.)
- Quarter: Format as `Q3-2025`, `Q4-2024`, etc.
- Video files: `take1.mp4`, `take2.mp4`, etc.

---

## Rendering a Video

### Prerequisites

1. **Remotion composition created** in `studio/src/compositions/`
2. **Composition registered** in `studio/src/Root.tsx`
3. **Audio files symlinked** to `studio/public/audio/` (if using audio)
4. **Remotion Studio running** at http://localhost:8082 (for preview)

### Render Command

```bash
cd /Users/Meera/earninglens/studio

npx remotion render src/index.ts [COMPOSITION-ID] [OUTPUT-PATH]
```

### Example: PLTR Q3 2025

**Composition ID:** `PLTR-Q3-2025` (from Root.tsx)

**Output Path:** `/var/earninglens/PLTR/Q3-2025/take1.mp4`

**Full Command:**
```bash
cd /Users/Meera/earninglens/studio

npx remotion render src/index.ts PLTR-Q3-2025 /var/earninglens/PLTR/Q3-2025/take1.mp4
```

**Expected Duration:**
- 44-minute video (79,000 frames at 30fps)
- Render time on Mac CPU: ~20-30 minutes
- Render time on GPU machine: ~5-10 minutes

---

## Render Parameters

### Basic Render
```bash
npx remotion render src/index.ts [COMPOSITION-ID] [OUTPUT]
```

### With Props (for data-driven videos)
```bash
npx remotion render src/index.ts [COMPOSITION-ID] [OUTPUT] \
  --props='@./data/AAPL-Q4-2024.json'
```

### Custom Quality Settings
```bash
npx remotion render src/index.ts [COMPOSITION-ID] [OUTPUT] \
  --quality=80 \
  --codec=h264
```

### Parallel Rendering (faster)
```bash
npx remotion render src/index.ts [COMPOSITION-ID] [OUTPUT] \
  --concurrency=4
```

---

## Output Specifications

**Video Settings:**
- **Resolution:** 1920x1080 (1080p)
- **Frame Rate:** 30 fps
- **Codec:** H.264
- **Format:** MP4
- **Audio:** AAC, 192kbps

**File Size (approximate):**
- 1-minute video: ~50-100 MB
- 5-minute video: ~250-500 MB
- 44-minute video: ~2-4 GB

---

## Post-Render Steps

### 1. Verify Video
```bash
# Check file exists
ls -lh /var/earninglens/PLTR/Q3-2025/take1.mp4

# Play video to verify (Mac)
open /var/earninglens/PLTR/Q3-2025/take1.mp4
```

### 2. Upload to R2 (Backup)
```bash
# Upload to Cloudflare R2
rclone copy /var/earninglens/PLTR/Q3-2025/take1.mp4 \
  r2-public:videotobe-public/earnings/PLTR/Q3-2025/ -P
```

### 3. Upload to YouTube
See [YOUTUBE-UPLOAD.md](./YOUTUBE-UPLOAD.md) for detailed instructions.

**Quick Upload:**
```bash
# Manual upload via YouTube Studio
# URL: https://studio.youtube.com/channel/YOUR_CHANNEL/videos/upload
```

---

## Troubleshooting

### Render Failed: "Cannot find module"
**Issue:** Missing dependencies or wrong working directory

**Fix:**
```bash
cd /Users/Meera/earninglens/studio
npm install
npm start  # Verify Remotion Studio works first
```

### Render Failed: "Audio file not found"
**Issue:** Audio file path incorrect or symlink broken

**Fix:**
```bash
# Check symlink exists
ls -la studio/public/audio/

# Recreate symlink if needed
ln -s /var/earninglens/_downloads/[VIDEO_ID]/source.trimmed.mp4 \
  studio/public/audio/PLTR_Q3_2025.mp4
```

### Render Very Slow on Mac
**Issue:** CPU rendering is slower than GPU

**Solutions:**
1. Reduce concurrency: `--concurrency=2`
2. Lower quality: `--quality=60`
3. Render on GPU machine (sushi) via SSH
4. Let it run overnight

### Video Has No Audio
**Issue:** Audio component not properly configured

**Fix:**
```tsx
// Check composition file uses staticFile()
<Audio src={staticFile('audio/PLTR_Q3_2025.mp4')} />

// NOT absolute paths
<Audio src="/var/earninglens/.../source.trimmed.mp4" />  // ❌ Wrong
```

---

## Multiple Takes Workflow

**When to create a new take:**
- Fixing visual bugs
- Updating data
- Changing design
- Different audio edit

**Process:**
1. Make changes in Remotion Studio
2. Preview at http://localhost:8082
3. Render new take:
   ```bash
   npx remotion render src/index.ts PLTR-Q3-2025 \
     /var/earninglens/PLTR/Q3-2025/take2.mp4
   ```
4. Compare takes:
   ```bash
   open /var/earninglens/PLTR/Q3-2025/take1.mp4
   open /var/earninglens/PLTR/Q3-2025/take2.mp4
   ```
5. Upload best take to YouTube

---

## Quick Reference

### Common Compositions

| Composition ID | Output Path | Duration |
|----------------|-------------|----------|
| `PLTR-Q3-2025` | `/var/earninglens/PLTR/Q3-2025/take1.mp4` | 44 min |
| `AAPL-Q4-2024` | `/var/earninglens/AAPL/Q4-2024/take1.mp4` | TBD |
| `MSFT-Q1-2025` | `/var/earninglens/MSFT/Q1-2025/take1.mp4` | TBD |

### Commands Cheat Sheet

```bash
# Start Remotion Studio
cd ~/earninglens/studio && npm start

# Render PLTR Q3 2025
cd ~/earninglens/studio
npx remotion render src/index.ts PLTR-Q3-2025 \
  /var/earninglens/PLTR/Q3-2025/take1.mp4

# Verify output
ls -lh /var/earninglens/PLTR/Q3-2025/take1.mp4
open /var/earninglens/PLTR/Q3-2025/take1.mp4

# Upload to R2
rclone copy /var/earninglens/PLTR/Q3-2025/take1.mp4 \
  r2-public:videotobe-public/earnings/PLTR/Q3-2025/ -P
```

---

## Production Workflow (Render on sushi, Upload on Mac)

**Best Practice:** Render on GPU machine (sushi) for speed, upload from Mac with YouTube credentials.

### Step 1: Render on sushi (GPU machine)

```bash
# SSH to sushi
ssh sushi

# Navigate to project
cd ~/earninglens/studio

# Render video (5-10 minutes with GPU)
npx remotion render src/index.ts PLTR-Q3-2025 \
  /var/earninglens/PLTR/Q3-2025/take1.mp4

# Verify output
ls -lh /var/earninglens/PLTR/Q3-2025/take1.mp4
```

### Step 2: Upload on Mac (with YouTube OAuth)

```bash
# On Mac (where YouTube credentials are stored)
cd ~/earninglens
source .venv/bin/activate

# Upload to YouTube with insights metadata
python lens/scripts/upload_youtube.py \
  /var/earninglens/PLTR/Q3-2025/take1.mp4 \
  /var/earninglens/PLTR/Q3-2025/insights.json
```

**Why this workflow:**
- Sushi has GPU → 5-10 min render time (vs 20-30 min on Mac CPU)
- Mac has YouTube OAuth token saved → no re-authentication needed
- Shared `/var/earninglens/` directory accessible from both machines

---

## Next Steps

After rendering:
1. ✅ Verify video plays correctly
2. ✅ Upload to R2 (backup)
3. ✅ Upload to YouTube
4. ✅ Update database with YouTube video ID
5. ✅ Create YouTube Shorts from key moments
6. ✅ Share on social media

---

**Last Updated:** November 6, 2025
**Maintained By:** Meera
