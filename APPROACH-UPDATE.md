# EarningLens Approach - Updated

## What Changed

Based on your clarification, the video production approach has been significantly updated.

---

## Original Approach (INCORRECT)

**What I initially built:**
- 50-second summary videos
- No earnings call audio
- Static visualizations
- Pre-rendered charts

**Problem:** This wasn't what you wanted!

---

## NEW Approach (CORRECT) ✅

**What you actually want:**
- **30-60 minute full earnings call videos**
- **Use actual audio** from earnings calls (YouTube or company website)
- **Visual overlays synchronized to audio:**
  - Speaker identification (Tim Cook, Luca Maestri, etc.)
  - Dynamic metrics (when CEO says "revenue up 9000%", show ↑ 9000%)
  - Company branding (Apple logo)
  - Charts from SEC filings
- **Speaker diarization** technology you already have

---

## Pipeline (Revised)

```
1. Download earnings call audio
   - YouTube: yt-dlp
   - Company website: Direct download
   ↓
2. Transcribe with speaker identification
   - Your speaker diarization technology
   - Or: AssemblyAI, Deepgram, Whisper
   ↓
3. Identify key metrics in transcript
   - Revenue, EPS, growth mentioned
   - Mark timestamps
   ↓
4. Download speaker photos
   - Apple leadership page
   - LinkedIn profiles
   ↓
5. Create data JSON
   - Audio file path
   - Full transcript with timing
   - Speaker info
   - Key metrics
   ↓
6. Render with Remotion
   - Audio plays throughout
   - Visuals overlay on audio
   - Speaker shows when speaking
   - Metrics popup when mentioned
   ↓
7. Upload to R2 + YouTube
```

---

## Two Video Types Now Available

### 1. Summary Video (50 seconds)
**Use:** Quick highlights for social media
- Composition: `EarningsVideo`
- Command: `npm run render:aapl`
- Duration: 50 seconds
- Audio: None
- Content: Key metrics only

### 2. Full Call Video (30-60 minutes) ✅ **PRIMARY**
**Use:** Main YouTube video for monetization
- Composition: `EarningsCallVideo`
- Command: `npm run render:aapl:full`
- Duration: 30-60 minutes
- Audio: Full earnings call
- Content: Complete call with overlays

---

## What's Built

### ✅ Complete
1. **Remotion composition** for full audio video
   - Location: `studio/src/compositions/EarningsVideoFull/`
   - Features:
     - Audio playback
     - Speaker overlay (photo + name)
     - Dynamic metric popups
     - Company branding
     - Progress bar

2. **Data structure** for full videos
   - Template: `studio/data/AAPL-Q4-2024-FULL.json`
   - Includes:
     - Audio file path
     - Speaker definitions
     - Full transcript with timing
     - Key metrics with timestamps

3. **Documentation**
   - `studio/AUDIO-VIDEO-GUIDE.md` - Complete guide
   - `APPROACH-UPDATE.md` - This file

### 📁 Directory Structure
```
studio/
├── public/
│   ├── audio/              ← Earnings call audio files
│   │   └── AAPL-Q4-2024.m4a
│   └── speakers/           ← Executive photos
│       ├── tim-cook.jpg
│       └── luca-maestri.jpg
├── src/
│   └── compositions/
│       ├── EarningsVideo/        ← 50s summary
│       └── EarningsVideoFull/    ← Full audio video ✅
└── data/
    ├── AAPL-Q4-2024.json          ← Summary data
    └── AAPL-Q4-2024-FULL.json     ← Full call data ✅
```

---

## How Visual Overlays Work

### Speaker Identification
```
When Tim Cook speaks (0:15 - 0:45):
┌────────────────────────────────────┐
│                                    │
│  [Apple Logo] AAPL                 │
│                                    │
│     [AUDIO PLAYING]                │
│     "Revenue was $94.9B..."        │
│                                    │
│  [Tim Cook Photo]                  │
│  Tim Cook                          │
│  CEO                               │
└────────────────────────────────────┘
```

### Dynamic Metrics
```
When "up 9000%" mentioned:
┌────────────────────────────────────┐
│                                    │
│                  ┌────────────┐    │
│                  │ ↑  9000%   │ ←  Popup
│                  │  GROWTH    │    │
│                  └────────────┘    │
│                                    │
│  [Tim Cook speaking...]            │
└────────────────────────────────────┘
```

---

## First Video Steps (Apple Q4 2024)

### 1. Download Audio
```bash
# Option A: From YouTube
yt-dlp -f 'bestaudio[ext=m4a]' \
  -o 'studio/public/audio/AAPL-Q4-2024.m4a' \
  'https://www.youtube.com/watch?v=VIDEO_ID'

# Option B: From Apple IR
# Visit https://investor.apple.com
# Download Q4 2024 earnings call audio
```

### 2. Get Transcript with Timing
Use your speaker diarization technology to get:
- Who spoke when
- What they said
- Start/end timestamps

Format:
```json
{
  "speaker": "tim-cook",
  "text": "Revenue was $94.9 billion, up 6%",
  "start_time": 15,
  "end_time": 22
}
```

### 3. Download Speaker Photos
```bash
# Tim Cook
curl -o studio/public/speakers/tim-cook.jpg \
  "https://www.apple.com/leadership/images/tim-cook.jpg"

# Luca Maestri
curl -o studio/public/speakers/luca-maestri.jpg \
  "https://www.apple.com/leadership/images/luca-maestri.jpg"
```

### 4. Update Data JSON
Edit `studio/data/AAPL-Q4-2024-FULL.json`:
- Add all transcript segments
- Mark key metrics with timestamps
- Verify audio path
- Update duration

### 5. Render
```bash
cd studio
npm start  # Preview first
npm run render:aapl:full  # Then render
```

**Output:** `studio/out/AAPL-Q4-2024-full.mp4`

### 6. Upload
```bash
# R2
cd ..
node scripts/upload-to-r2.js --ticker=AAPL --quarter=Q4 --year=2024

# YouTube
# Manual upload via YouTube Studio
```

---

## Estimated Time

### First Video (Learning)
- Download audio: 5 minutes
- Transcribe + speaker ID: 2-3 hours (with your tech)
- Download photos: 10 minutes
- Create data JSON: 1 hour
- Render video: 30-60 minutes
- Upload: 20 minutes
**Total: 4-6 hours**

### Subsequent Videos (Once process is refined)
- Download audio: 5 minutes
- Transcribe: 30 minutes (automated)
- Create JSON: 20 minutes (template)
- Render: 30-60 minutes
- Upload: 20 minutes
**Total: 2-3 hours per video**

---

## YouTube Strategy (Updated)

### Video Format
**Title:**
```
Apple (AAPL) Q4 2024 Earnings Call - Enhanced with Visual Data | EarningLens
```

**Description:**
```
Full Apple Q4 FY2024 earnings call (60 minutes) with enhanced visual overlays including:
- Real-time speaker identification
- Dynamic financial metrics
- Revenue, EPS, and growth visualizations
- Key highlights and guidance

📊 Key Metrics:
- Revenue: $94.9B (+6% YoY)
- EPS: $1.64 (beat by $0.04)
- iPhone: $46.2B
- Services: $25.0B (record)

⏱️ Timestamps:
[Auto-generated by YouTube]

Original audio © Apple Inc.
Visual enhancements by EarningLens
```

### Why This Works for YouTube
1. **Long watch time** (30-60 min) = Great for monetization
2. **High CPM** (finance content = $5-20 CPM)
3. **Searchable** (people search "apple earnings call")
4. **Professional** (enhances existing content, doesn't replace)
5. **Repeatable** (every company, every quarter)

---

## Summary

### Old Approach ❌
- Short summary videos
- No audio
- Static charts

### New Approach ✅
- **Full earnings call audio**
- **Dynamic visual overlays**
- **Speaker identification**
- **Metrics when mentioned**

### Next Step
**Generate your first full audio video:**
1. Read `studio/AUDIO-VIDEO-GUIDE.md`
2. Download Apple Q4 2024 audio
3. Create transcript with your speaker tech
4. Render full video
5. Upload to YouTube

**Focus:** YouTube monetization (1000 subs + 4000 watch hours)
