# Quick Start Guide - Generate Your First Video

This guide will walk you through generating your first EarningLens video in **under 10 minutes**.

## Prerequisites

- Node.js 18+ installed
- GPU machine (you have one!)
- rclone configured with r2-public remote (already set up)

## Step 1: Install Dependencies

```bash
cd /Users/Meera/earninglens/studio
npm install
```

This installs Remotion and all necessary dependencies.

## Step 2: Preview the Video

```bash
npm start
```

This opens Remotion Studio at http://localhost:3000 where you can:
- Preview the Apple Q4 2024 video
- See all 5 sequences (Title, Revenue, EPS, Segments, Highlights)
- Make adjustments to the composition

**Close the studio when done (Ctrl+C)**

## Step 3: Render the Video

```bash
npm run render:aapl
```

This will:
- Read data from `data/AAPL-Q4-2024.json`
- Render 50-second video at 1080p, 30fps
- Output to `out/AAPL-Q4-2024.mp4`
- Takes 2-5 minutes on GPU

**Expected output:**
```
Rendering frames...
████████████████████████████████████████ 100%
Done in 3m 24s
✅ Video rendered: out/AAPL-Q4-2024.mp4
```

## Step 4: Verify the Video

```bash
# Check file exists and size
ls -lh out/AAPL-Q4-2024.mp4

# Play the video (macOS)
open out/AAPL-Q4-2024.mp4

# Or use VLC/other player
```

You should see:
- Title card with Apple logo and Q4 2024 earnings
- Revenue: $94.9B (+6% YoY)
- EPS: $1.64 (beat by $0.04)
- Segments breakdown (iPhone, Services, Mac, iPad, Wearables)
- Key highlights

## Step 5: Upload to R2

From the root directory:

```bash
cd /Users/Meera/earninglens
node scripts/upload-to-r2.js --ticker=AAPL --quarter=Q4 --year=2024
```

This will:
1. Create `earninglens/AAPL/videos/` in R2
2. Upload video as `2024-Q4-full.mp4`
3. Verify upload

**Expected output:**
```
📤 Uploading to R2...
1️⃣ Creating R2 directory structure...
✅ Directories created

2️⃣ Uploading video...
[Progress bar]
✅ Upload complete

3️⃣ Verifying upload...
✅ Upload verified successfully!
```

## Step 6: Upload to YouTube

### Manual Upload (Recommended for First Video)

1. Go to YouTube Studio: https://studio.youtube.com
2. Click **Create** → **Upload videos**
3. Select `studio/out/AAPL-Q4-2024.mp4`
4. Fill in metadata:

**Title:**
```
Apple (AAPL) Q4 2024 Earnings - Revenue Beats by 6% | EarningLens
```

**Description:**
```
Apple Q4 2024 (FY2024) earnings call with visual charts and financial analysis.

📊 Key Metrics:
- Revenue: $94.9B (+6% YoY)
- EPS: $1.64 (beat estimates by $0.04)
- iPhone: $46.2B (+6%)
- Services: $25.0B (record, +12%)

💡 Highlights:
- Active devices exceed 2.2 billion
- Strong growth in emerging markets
- Record September quarter for Mac

⏱️ Timestamps:
0:00 Introduction
0:05 Revenue Overview
0:13 EPS Analysis
0:21 Segment Breakdown
0:35 Key Highlights

🔗 Full analysis: https://earninglens.com/aapl/q4-2024

#AAPL #Apple #earnings #investing #stocks #technology
```

**Tags:**
```
AAPL, Apple, earnings, Q4 2024, investing, stocks, earnings call, financial analysis, technology stocks
```

5. Set **Visibility** to **Public**
6. Click **Publish**
7. **Copy the YouTube video ID** from the URL (e.g., `dQw4w9WgXcQ`)

## Step 7: What's Next?

You now have:
- ✅ Working video pipeline (Remotion → R2 → YouTube)
- ✅ First video published
- ✅ Template for future videos

### Next Videos to Generate

Follow the same process for:

1. **Microsoft (MSFT) Q1 FY2025** - Oct 30, 2024
2. **Alphabet (GOOGL) Q3 2024** - Oct 29, 2024
3. **Amazon (AMZN) Q3 2024** - Oct 31, 2024
4. **Meta (META) Q3 2024** - Oct 30, 2024

For each:
```bash
# 1. Create data file (copy AAPL template)
cp studio/data/AAPL-Q4-2024.json studio/data/MSFT-Q1-2025.json
# Edit with actual data

# 2. Render
cd studio
npm run render -- --props='@./data/MSFT-Q1-2025.json'

# 3. Upload to R2
cd ..
node scripts/upload-to-r2.js --ticker=MSFT --quarter=Q1 --year=2025

# 4. Upload to YouTube (manual)
```

### Upload Schedule (from YOUTUBE-FIRST-STRATEGY.md)

**Week 1:** 3 videos (AAPL, MSFT, GOOGL)
- Upload Mon, Wed, Fri

**Week 2:** 5 videos (AMZN, META, NVDA, TSLA, NFLX)
- Upload Mon-Fri

**Weeks 3-4:** 7 videos/week
**Weeks 5-6:** 10 videos/week

**Goal:** 1000 subscribers + 4000 watch hours by Week 8

## Troubleshooting

### Render Fails
```bash
# Check GPU
nvidia-smi

# Try simpler render
npm start  # Preview in studio first
```

### Video Quality Issues
- Increase bitrate in `remotion.config.ts`
- Check GPU memory (close other apps)

### R2 Upload Fails
```bash
# Check rclone config
rclone config show r2-public

# Test connection
rclone ls r2-public:earninglens
```

### YouTube Upload Slow
- Upload during off-peak hours
- Check internet speed
- Use YouTube Studio (more reliable than API)

## Summary

You've successfully:
1. ✅ Set up video production pipeline
2. ✅ Rendered first video (Apple Q4 2024)
3. ✅ Uploaded to R2 backup
4. ✅ Published to YouTube

**Now repeat for 49 more companies! 🚀**

Read `YOUTUBE-FIRST-STRATEGY.md` for the complete 6-week growth plan.
