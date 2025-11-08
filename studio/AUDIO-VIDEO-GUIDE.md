# Audio-Based Earnings Video Guide

This guide explains how to create full earnings call videos with audio and visual overlays.

## Overview

**Approach:** Use actual earnings call audio (30-60 minutes) and overlay:
- Speaker identification (photo + name)
- Dynamic metrics when mentioned (revenue, EPS, growth)
- Company branding
- Progress tracking

## Pipeline

```
1. Download earnings call audio (YouTube or company website)
   ↓
2. Extract transcript with speaker diarization
   ↓
3. Identify key metrics mentioned in transcript
   ↓
4. Download speaker images
   ↓
5. Create data JSON file
   ↓
6. Render video with Remotion
   ↓
7. Upload to R2 and YouTube
```

---

## Step 1: Download Audio

### Option A: From YouTube
```bash
# Install yt-dlp if not installed
brew install yt-dlp

# Download audio only
yt-dlp -f 'bestaudio[ext=m4a]' \
  -o 'studio/public/audio/AAPL-Q4-2024.m4a' \
  'https://www.youtube.com/watch?v=VIDEO_ID'
```

### Option B: From Company Website
1. Go to Apple Investor Relations: https://investor.apple.com
2. Find Q4 2024 earnings call
3. Download audio file
4. Convert to M4A if needed:
   ```bash
   ffmpeg -i input.mp3 -c:a aac studio/public/audio/AAPL-Q4-2024.m4a
   ```

### Check Audio Duration
```bash
ffprobe -i studio/public/audio/AAPL-Q4-2024.m4a -show_entries format=duration -v quiet -of csv="p=0"
```

---

## Step 2: Transcript with Speaker Diarization

You mentioned you have technology for speaker identification. Here's how to structure it:

### Option A: Manual Transcript (First Video)
1. Listen to call and note timestamps
2. Identify when each speaker talks
3. Note key metrics mentioned

### Option B: Automated Speaker Diarization
Tools that can help:
- **AssemblyAI** - Speaker diarization API
- **Deepgram** - Real-time transcription with speaker labels
- **Whisper + pyannote.audio** - Open source (Python)

Example with AssemblyAI:
```python
import assemblyai as aai

aai.settings.api_key = "YOUR_API_KEY"

transcriber = aai.Transcriber()
transcript = transcriber.transcribe(
    "studio/public/audio/AAPL-Q4-2024.m4a",
    config=aai.TranscriptionConfig(
        speaker_labels=True
    )
)

# Extract speaker segments
for utterance in transcript.utterances:
    print(f"Speaker {utterance.speaker}: {utterance.text}")
    print(f"  Start: {utterance.start / 1000}s, End: {utterance.end / 1000}s")
```

---

## Step 3: Identify Key Metrics

Manually scan transcript for mentions of:
- Revenue numbers (e.g., "$94.9 billion")
- Growth percentages (e.g., "up 6%")
- EPS figures (e.g., "$1.64")
- Guidance numbers

Mark the timestamp when each is mentioned:

```json
{
  "speaker": "tim-cook",
  "text": "Revenue was $94.9 billion, up 6% year over year",
  "start_time": 15,
  "end_time": 22,
  "key_metrics": [
    {"type": "revenue", "value": "$94.9B", "direction": "up"},
    {"type": "growth", "value": "+6%", "direction": "up"}
  ]
}
```

---

## Step 4: Download Speaker Images

### Find Images
1. **Apple Executive Bios**: https://www.apple.com/leadership/
2. **LinkedIn profiles**
3. **Company press photos**

### Download and Prepare
```bash
# Download Tim Cook photo
curl -o studio/public/speakers/tim-cook.jpg \
  "https://www.apple.com/leadership/images/tim-cook.jpg"

# Download Luca Maestri photo
curl -o studio/public/speakers/luca-maestri.jpg \
  "https://www.apple.com/leadership/images/luca-maestri.jpg"

# Resize to square (400x400)
magick studio/public/speakers/tim-cook.jpg \
  -resize 400x400^ -gravity center -extent 400x400 \
  studio/public/speakers/tim-cook.jpg
```

---

## Step 5: Create Data JSON

Use `AAPL-Q4-2024-FULL.json` as template:

```json
{
  "company": "Apple Inc.",
  "ticker": "AAPL",
  "audio_url": "public/audio/AAPL-Q4-2024.m4a",
  "duration_seconds": 3600,
  "speakers": {
    "tim-cook": {
      "name": "Tim Cook",
      "title": "CEO",
      "image_url": "public/speakers/tim-cook.jpg"
    }
  },
  "transcript": [
    {
      "speaker": "tim-cook",
      "text": "Revenue was $94.9 billion...",
      "start_time": 15,
      "end_time": 22,
      "key_metrics": [...]
    }
  ]
}
```

**Important:**
- `audio_url` must be relative to `studio/` directory
- `duration_seconds` must match audio file duration
- `start_time`/`end_time` in seconds

---

## Step 6: Render Video

### Preview First
```bash
cd studio
npm start
# Open http://localhost:3000
# Select "Full Earnings Calls (30-60min)" → "EarningsCallVideo"
```

### Render Full Video
```bash
npm run render:aapl:full
```

This will:
- Read audio from `public/audio/AAPL-Q4-2024.m4a`
- Read data from `data/AAPL-Q4-2024-FULL.json`
- Render 30-60 minute video
- Output to `out/AAPL-Q4-2024-full.mp4`

**Render time:** 30-60 minutes for 1-hour video (on GPU)

---

## Step 7: Verify Output

```bash
# Check video duration matches audio
ffprobe -i out/AAPL-Q4-2024-full.mp4 -show_entries format=duration

# Play video
open out/AAPL-Q4-2024-full.mp4
```

**What to verify:**
- ✅ Audio plays correctly
- ✅ Speaker overlays appear at correct times
- ✅ Metrics pop up when mentioned in audio
- ✅ Company branding visible throughout
- ✅ Progress bar tracks playback

---

## Comparison: Summary vs. Full Videos

| Feature | Summary Video (50s) | Full Audio Video (30-60min) |
|---------|---------------------|----------------------------|
| **Duration** | 50 seconds | 30-60 minutes |
| **Audio** | No audio | Full earnings call audio |
| **Content** | Highlights only | Complete call |
| **Visuals** | Static charts | Dynamic overlays |
| **Use Case** | Quick overview | Deep dive |
| **Render Time** | 2-5 minutes | 30-60 minutes |
| **File Size** | 50-100 MB | 500-1000 MB |

---

## Production Workflow

### For First 5 Videos
1. **Manual approach** - Transcribe manually, mark key metrics
2. **Learn what works** - See which visuals resonate with FinTwit
3. **Iterate on design** - Improve speaker overlays, metric animations

### After 5 Videos (Week 2+)
1. **Automate transcript** - Use AssemblyAI or similar
2. **NLP for metrics** - Auto-detect numbers mentioned
3. **Template speakers** - Build library of executive photos
4. **Batch rendering** - Render multiple videos overnight

---

## Key Differences from Original Plan

### What Changed
- ✅ **Use actual audio** (not synthetic narration)
- ✅ **30-60 min videos** (not 50-second summaries)
- ✅ **Speaker identification** (your technology)
- ✅ **Dynamic overlays** (metrics when mentioned)

### What Stays Same
- ✅ Upload to YouTube for monetization
- ✅ Use R2 for backup/storage
- ✅ Focus on FinTwit audience
- ✅ Dark aesthetic, professional branding

---

## Next Steps

1. **Download Apple Q4 2024 audio** from YouTube/Apple IR
2. **Create transcript** with speaker timing (manual or automated)
3. **Download speaker photos** (Tim Cook, Luca Maestri)
4. **Fill in data JSON** (`AAPL-Q4-2024-FULL.json`)
5. **Render first full video** (`npm run render:aapl:full`)
6. **Upload to YouTube** (title: "Apple Q4 2024 Earnings Call - Enhanced")

**Estimated time for first video:** 4-6 hours (mostly transcript work)

---

## Troubleshooting

### Audio not playing
- Check file path in JSON: `"audio_url": "public/audio/AAPL-Q4-2024.m4a"`
- Verify file exists: `ls studio/public/audio/`
- Check audio format (M4A or MP3 supported)

### Speaker overlay not showing
- Verify speaker ID matches in JSON
- Check image path: `"image_url": "public/speakers/tim-cook.jpg"`
- Ensure timing: `start_time` < current_time < `end_time`

### Metrics not appearing
- Check `key_metrics` array in transcript segment
- Verify timing overlaps with speaker segment
- Increase metric display duration in code (currently 3s)

### Video duration wrong
- Update `duration_seconds` in JSON to match audio
- Check audio duration: `ffprobe -i audio.m4a`
- Update `durationInFrames` in composition: `duration_seconds * fps`

---

## Future Enhancements

### Week 2+
- Auto-generate thumbnails from key moments
- Add chapter markers for YouTube
- Include Q&A section visualization
- Highlight analyst questions

### Month 2+
- Real-time rendering during live earnings calls
- Interactive web player with synchronized transcript
- Multi-language subtitles
- Downloadable transcript with timestamps
