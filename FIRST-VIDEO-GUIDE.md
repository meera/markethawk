# First Video Generation Guide

## Goal: Generate Your FIRST Custom Earnings Video

**Timeline:** 1-2 days
**Target:** Recent earnings call (Late Oct/Early Nov 2024)

---

## Recommended First Video: Apple Q4 FY2024

**Details:**
- **Company:** Apple Inc. (AAPL)
- **Earnings Date:** November 1, 2024
- **Quarter:** Q4 FY2024 (ended September 28, 2024)
- **Fiscal Year Note:** Apple's fiscal year ends in September

**Why Apple First:**
- ✅ Highest market interest (most popular)
- ✅ Clean, simple business model
- ✅ Abundant public data available
- ✅ Strong visuals (product images, charts)
- ✅ Recent (just happened)

---

## Alternative Options (If Apple Blocked/Difficult)

### Microsoft Q1 FY2025
- **Date:** October 30, 2024
- **Strong:** Cloud growth (Azure), AI narrative
- **Data:** Segment breakdown (Cloud, Windows, Gaming)

### Alphabet (Google) Q3 2024
- **Date:** October 29, 2024
- **Strong:** Search, YouTube, Cloud growth
- **Data:** Advertising revenue, cloud metrics

### Amazon Q3 2024
- **Date:** October 31, 2024
- **Strong:** AWS, e-commerce, Prime
- **Data:** Retail vs. AWS breakdown

### Meta Q3 2024
- **Date:** October 30, 2024
- **Strong:** Ad revenue, Reality Labs spending
- **Data:** DAU/MAU metrics, metaverse investments

---

## Step-by-Step: Generate Apple Q4 2024 Video

### Step 1: Gather Data (Via Exa.ai)

```bash
# Run Exa.ai seed script
npm run seed:company -- --ticker=AAPL --quarter=Q4 --year=2024
```

**What This Does:**
```typescript
// Fetches:
1. Earnings call transcript (full text)
2. Financial data (revenue, EPS, margins)
3. SEC 10-K filing (annual report)
4. Press release
5. Investor presentation slides
```

**Manual Backup (if Exa.ai fails):**
- Transcript: https://investor.apple.com/investor-relations/default.aspx
- 10-K: https://sec.gov/edgar (search "Apple Inc. 10-K")
- Press Release: Google "Apple Q4 2024 earnings release"

### Step 2: Prepare Data for Remotion

**Create data file:**
```json
// studio/data/AAPL-Q4-2024.json

{
  "company": "Apple Inc.",
  "ticker": "AAPL",
  "quarter": "Q4",
  "fiscal_year": 2024,
  "call_date": "2024-11-01",

  "financials": {
    "revenue": {
      "current": 94928000000,
      "previous": 89498000000,
      "yoy_growth": 6.1
    },
    "eps": {
      "current": 1.64,
      "estimate": 1.60,
      "beat_miss": "beat"
    },
    "segments": [
      {"name": "iPhone", "revenue": 46220000000},
      {"name": "Services", "revenue": 24973000000},
      {"name": "Mac", "revenue": 7740000000},
      {"name": "iPad", "revenue": 6950000000},
      {"name": "Wearables", "revenue": 9045000000}
    ],
    "margins": {
      "gross": 46.2,
      "operating": 30.7,
      "net": 23.9
    }
  },

  "highlights": [
    "Revenue up 6% to $94.9B",
    "iPhone revenue grew 6% to $46.2B",
    "Services hit record $25B",
    "Active devices exceed 2 billion"
  ],

  "transcript_highlights": [
    {
      "speaker": "Tim Cook",
      "text": "We're pleased to report another strong quarter...",
      "timestamp": 0
    },
    {
      "speaker": "Luca Maestri",
      "text": "Revenue grew 6% year over year to $94.9 billion...",
      "timestamp": 120
    }
  ]
}
```

### Step 3: Create Remotion Composition

**File:** `studio/src/compositions/EarningsVideo/index.tsx`

```tsx
import {AbsoluteFill, Audio, Img, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';

export const EarningsVideo = ({data}) => {
  const {fps} = useVideoConfig();

  return (
    <AbsoluteFill className="bg-gradient-to-br from-gray-900 to-black">
      {/* Title Card (0-5s) */}
      <Sequence from={0} durationInFrames={fps * 5}>
        <AbsoluteFill className="flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-6xl font-bold text-white mb-4">
              {data.company}
            </h1>
            <h2 className="text-4xl text-gray-400">
              {data.quarter} {data.fiscal_year} Earnings
            </h2>
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* Revenue Chart (5-15s) */}
      <Sequence from={fps * 5} durationInFrames={fps * 10}>
        <RevenueChart data={data.financials} />
      </Sequence>

      {/* Segment Breakdown (15-25s) */}
      <Sequence from={fps * 15} durationInFrames={fps * 10}>
        <SegmentChart segments={data.financials.segments} />
      </Sequence>

      {/* Key Highlights (25-35s) */}
      <Sequence from={fps * 25} durationInFrames={fps * 10}>
        <Highlights items={data.highlights} />
      </Sequence>

      {/* Logo Watermark */}
      <div className="absolute top-8 left-8">
        <Img src="/logos/AAPL.png" className="w-24 h-24" />
      </div>
    </AbsoluteFill>
  );
};
```

### Step 4: Render Video

```bash
# Navigate to studio directory
cd studio

# Render video locally
npx remotion render \
  src/compositions/index.ts \
  EarningsVideo \
  out/AAPL-Q4-2024.mp4 \
  --props='@../data/AAPL-Q4-2024.json'

# This will take 2-5 minutes on GPU machine
```

**Output:**
- File: `studio/out/AAPL-Q4-2024.mp4`
- Duration: ~60 seconds
- Resolution: 1920x1080
- Format: H.264 MP4

### Step 5: Upload to R2

```bash
# Create AAPL directory in R2 bucket
rclone mkdir earninglens:AAPL
rclone mkdir earninglens:AAPL/videos

# Upload video
rclone copy studio/out/AAPL-Q4-2024.mp4 \
  earninglens:AAPL/videos/2024-Q4-full.mp4 -P

# Verify
rclone ls earninglens:AAPL/videos/
```

### Step 6: Upload to YouTube

**Manual (First Time):**
1. Go to YouTube Studio (https://studio.youtube.com)
2. Click "Create" → "Upload videos"
3. Select `AAPL-Q4-2024.mp4`
4. Fill in metadata:
   - **Title:** `Apple (AAPL) Q4 2024 Earnings Call - Visual Summary | EarningLens`
   - **Description:**
     ```
     Apple Q4 2024 (FY2024) earnings call with visual charts and financial analysis.

     📊 Key Metrics:
     - Revenue: $94.9B (+6% YoY)
     - EPS: $1.64 (beat estimates)
     - iPhone: $46.2B
     - Services: $25.0B (record)

     🔗 Full interactive analysis: https://earninglens.com/aapl/q4-2024

     Timestamps:
     0:00 Intro
     0:05 Revenue Overview
     0:15 Segment Breakdown
     0:25 Key Highlights

     #AAPL #Apple #earnings #investing #stocks #technology
     ```
   - **Tags:** AAPL, Apple, earnings, investing, stocks, Q4 2024
5. Click "Publish"

**Copy YouTube ID:**
- After publishing, copy the video ID from the URL
- Example: `https://youtube.com/watch?v=ABC123xyz` → ID is `ABC123xyz`

### Step 7: Update Database

```sql
-- Update video record with YouTube ID
UPDATE videos
SET
  youtube_id = 'ABC123xyz',
  is_custom = true,
  r2_video_url = 'https://pub-xxx.r2.dev/AAPL/videos/2024-Q4-full.mp4',
  status = 'published',
  published_at = NOW()
WHERE slug = 'aapl-q4-2024';
```

---

## Checklist: First Video

- [ ] Choose company (Apple recommended)
- [ ] Gather earnings data (Exa.ai or manual)
- [ ] Create data JSON file
- [ ] Build Remotion composition
- [ ] Render video (2-5 min on GPU)
- [ ] Upload to R2
- [ ] Upload to YouTube
- [ ] Copy YouTube ID
- [ ] Update database
- [ ] Test video page (earninglens.com/aapl/q4-2024)

---

## Expected Results

**After completing all steps:**

1. **Video live on YouTube** (your channel)
2. **Video backed up in R2** (earninglens:AAPL/videos/)
3. **Database updated** (is_custom = true)
4. **Website shows your video** (embedded YouTube player)

**Landing page now shows:**
```
┌────────────────────────────────┐
│  Latest Earnings               │
│  ┌──────┐                      │
│  │ AAPL │ ← Your custom video! │
│  │ +6%  │                      │
│  │94.9B │                      │
│  └──────┘                      │
└────────────────────────────────┘
```

---

## Troubleshooting

### Exa.ai Can't Find Data
- Manually download transcript from investor.apple.com
- Use SEC EDGAR for 10-K filing
- Extract data manually into JSON

### Remotion Render Fails
- Check GPU is available (`nvidia-smi`)
- Verify data JSON is valid
- Try rendering simpler composition first

### YouTube Upload Slow
- Check internet speed
- Upload during off-peak hours
- Use YouTube Studio (more reliable than API for first upload)

### Video Not Showing on Site
- Verify YouTube ID is correct
- Check video is set to "Public" not "Unlisted"
- Clear browser cache

---

## Next Steps

After first video succeeds:
1. **Celebrate!** 🎉 You have a working pipeline
2. **Get feedback** - Share with FinTwit friends
3. **Iterate on template** - Improve based on feedback
4. **Render video #2** - Pick Microsoft or Google
5. **Scale up** - 1 video/day for a week

**Goal:** 5 custom videos by end of week 1
