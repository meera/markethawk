# YouTube Shorts Strategy

## Goal: Drive Traffic from Shorts → Full Videos → Web App

YouTube Shorts (30-60 second vertical videos) are the traffic driver for full earnings call videos.

---

## Why Shorts?

### YouTube Algorithm Advantages
- **High discovery:** Shorts get 10-100x more views than regular videos
- **Viral potential:** One short can get 1M+ views
- **Separate feed:** Doesn't compete with long-form content
- **Monetization:** YouTube Shorts Fund ($100M/year distributed)
- **Conversion:** 5-10% of Short viewers click through to channel

### Perfect for Earnings Highlights
- Revenue announcement (15 seconds)
- EPS beat/miss (10 seconds)
- Key guidance (20 seconds)
- Analyst Q&A moment (30 seconds)

---

## Content Formula

### Anatomy of a Great Earnings Short

**Example: Apple Q4 2024 Revenue**

```
[0-2s]  Hook: "Apple just reported..."
[2-8s]  Key Metric: "$94.9B revenue, up 6%"
[8-12s] Visual: Large numbers, up arrow
[12-15s] Context: "Driven by iPhone 16 demand"
[15-18s] CTA: "Watch full analysis (link in bio)"
```

**Format:**
- Vertical (9:16 aspect ratio)
- 1080x1920 resolution
- Under 60 seconds
- Text overlays (readable without sound)
- Dynamic visuals

---

## 10 Short Types per Earnings Call

From each 60-minute earnings call, extract 10 Shorts:

### 1. Revenue Announcement
"[Company] Q4 Revenue: $XX.XB"
- Show revenue number
- YoY growth %
- Beat/miss estimates

### 2. EPS Beat/Miss
"[Company] Beats Earnings Estimates"
- Show EPS actual vs. estimate
- Visual: ✓ or ✗
- Stock reaction

### 3. Segment Breakdown
"iPhone Revenue Hits $XX.XB"
- Highlight top segment
- Growth rate
- Context (new product launch)

### 4. Guidance
"[Company] Raises FY2025 Guidance"
- Show guidance numbers
- Up/down from previous
- Market implications

### 5. Key Quote
"CEO: 'Best Quarter in Company History'"
- Show CEO speaking
- Pull quote overlay
- Context

### 6. Analyst Question
"Analyst Asks About AI Strategy"
- Interesting Q&A moment
- CEO response
- Why it matters

### 7. Surprise Announcement
"[Company] Announces $10B Buyback"
- Unexpected news
- What it means
- Market reaction

### 8. Comparison
"[Company] vs. Competitors"
- Show metric comparison
- Industry context
- Why it matters

### 9. Historical Context
"Highest Revenue in 10 Years"
- Long-term chart
- Historical milestone
- Trend analysis

### 10. Market Reaction
"Stock Jumps 5% After Earnings"
- Stock price movement
- Why market reacted
- Outlook

---

## Production Workflow

### Option A: Manual (Week 1)
1. Watch full earnings video
2. Note 10 best moments with timestamps
3. Export 30-60s clips using video editor
4. Add text overlays, transitions
5. Upload to YouTube Shorts

**Time:** 2-3 hours per earnings call

### Option B: Semi-Automated (Week 2+)
1. Use Remotion to render key moments as Shorts
2. Template: `ShortClip` composition
3. Input: timestamp, metric, text
4. Output: 1080x1920 vertical MP4
5. Batch upload

**Time:** 30 minutes per earnings call

### Option C: Fully Automated (Month 2+)
1. NLP identifies key moments in transcript
2. Auto-generate 10 Shorts from each call
3. Review and approve
4. Batch upload

**Time:** 10 minutes per earnings call

---

## Short Template (Remotion)

```tsx
// studio/src/compositions/ShortClip.tsx

interface ShortClipProps {
  company: string;
  ticker: string;
  metric: {
    label: string;
    value: string;
    direction: 'up' | 'down' | 'neutral';
  };
  quote?: string;
  speaker?: string;
  audio_clip_url: string;
  duration_seconds: number;
}

export const ShortClip: React.FC<ShortClipProps> = ({
  company,
  ticker,
  metric,
  quote,
  speaker,
  audio_clip_url,
}) => {
  return (
    <AbsoluteFill className="bg-black">
      {/* Audio from earnings call */}
      <Audio src={audio_clip_url} />

      {/* Company branding - top */}
      <div className="absolute top-8 left-0 right-0 text-center">
        <div className="text-2xl font-bold text-white">{ticker}</div>
        <div className="text-sm text-gray-400">{company}</div>
      </div>

      {/* Main metric - center */}
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-3xl text-gray-400 mb-4">{metric.label}</div>
          <div className="text-8xl font-bold text-white mb-6">
            {metric.value}
          </div>
          {metric.direction === 'up' && (
            <div className="text-6xl text-green-400">↑</div>
          )}
          {metric.direction === 'down' && (
            <div className="text-6xl text-red-400">↓</div>
          )}
        </div>
      </div>

      {/* Quote - bottom */}
      {quote && (
        <div className="absolute bottom-20 left-8 right-8 text-center">
          <div className="text-xl text-gray-300 italic">"{quote}"</div>
          {speaker && (
            <div className="text-sm text-gray-500 mt-2">— {speaker}</div>
          )}
        </div>
      )}

      {/* CTA - very bottom */}
      <div className="absolute bottom-8 left-0 right-0 text-center">
        <div className="text-sm text-blue-400">
          Watch full earnings call ↗
        </div>
        <div className="text-xs text-gray-500 mt-1">EarningLens.com</div>
      </div>
    </AbsoluteFill>
  );
};
```

---

## Upload Strategy

### Week 1: Test Phase (3 earnings calls = 30 Shorts)
- Upload 2-3 Shorts per day
- Test different formats
- Track which types perform best
- Learn optimal posting times

### Week 2-4: Ramp Up (10 earnings calls = 100 Shorts)
- Upload 5-7 Shorts per day
- Focus on best-performing types
- Engage with comments
- Cross-promote to full videos

**Expected Results:**
- 10-50K views per Short
- 5-10% click-through to full video
- 500-1000 new subscribers

### Week 5-8: Scale (20 earnings calls = 200 Shorts)
- Upload 10-15 Shorts per day
- Diversify content types
- Collaborate with FinTwit influencers
- Run YouTube ads on top Shorts

**Expected Results:**
- 50-200K views per Short
- 10-15% click-through
- 2000-5000 new subscribers
- **Hit 1000 subscribers milestone** ✅

---

## SEO for Shorts

### Title Format
```
[Company] Q4 Revenue: $XX.XB ↑ #shorts #earnings
```

Examples:
- ✅ Apple Q4 Revenue: $94.9B ↑ #shorts #earnings
- ✅ Tesla EPS Misses Estimates ↓ #shorts #TSLA
- ✅ Microsoft Cloud Revenue Surges #shorts #MSFT

**Key elements:**
- Company name (searchable)
- Key metric (click-worthy)
- Arrow emoji (visual indicator)
- #shorts hashtag (algorithm)
- Ticker hashtag (community)

### Description
```
Apple Q4 2024 earnings: Revenue grew 6% to $94.9B, beating estimates.

Watch full earnings call analysis: [link to full video]

#AAPL #Apple #earnings #stocks #investing #finance
```

### Hashtags (max 3 in title, more in description)
- #shorts (required)
- Company ticker (#AAPL, #MSFT)
- #earnings
- #stocks
- #investing

---

## Thumbnail (Even for Shorts!)

Shorts show a thumbnail before playing. Make it count:

```
┌────────────────────┐
│                    │
│  AAPL              │
│                    │
│  $94.9B            │
│  ↑ +6%             │
│                    │
└────────────────────┘
```

**Design:**
- Dark background
- Large text (readable on mobile)
- Company ticker prominent
- Metric + arrow
- Minimal clutter

---

## Tracking Success

### Key Metrics (YouTube Analytics)
- **Views:** 10K+ = good, 100K+ = viral
- **Swipe-away rate:** <50% = engaging
- **Click-through to channel:** 5-10% = excellent
- **Subscribers from Shorts:** Track separately

### Goals by Week
| Week | Shorts Uploaded | Total Views | New Subs |
|------|----------------|-------------|----------|
| 1 | 10-15 | 50K | 50 |
| 2 | 30-40 | 150K | 150 |
| 3 | 50-70 | 300K | 300 |
| 4 | 70-100 | 500K | 500 |
| 6 | 150+ | 1M+ | 1000+ ✅ |

---

## Integration with Full Videos

### Funnel Strategy
```
1. User discovers Short in feed
   ↓
2. Watches 15-second clip
   ↓
3. Clicks "Watch full video"
   ↓
4. Views 60-min earnings call
   ↓
5. Subscribes to channel
   ↓
6. Visits EarningLens.com
   ↓
7. Signs up for Pro (later)
```

### Cross-Promotion
- **In Shorts:** "Watch full analysis (link in bio)"
- **In Full Videos:** "See Shorts for quick highlights"
- **On Website:** Embed both Shorts and full videos

---

## Content Calendar

### Daily Routine
- **Morning:** Check which Shorts performed well overnight
- **Midday:** Upload 2-3 new Shorts
- **Evening:** Respond to comments, engage with viewers

### Weekly Planning
- **Monday:** Review last week's analytics
- **Tuesday:** Plan Shorts for upcoming earnings calls
- **Wednesday:** Batch render Shorts
- **Thursday:** Schedule uploads
- **Friday:** Experiment with new format

---

## Best Practices

### ✅ DO:
- Use actual audio from earnings calls
- Show exact numbers (no rounding)
- Add text overlays (many watch muted)
- Include CTA to full video
- Post consistently (2-3 per day minimum)
- Engage with comments quickly

### ❌ DON'T:
- Make up or infer data
- Use clickbait titles
- Repost same Short multiple times
- Ignore negative comments
- Post sporadically
- Forget to link to full video

---

## Future Enhancements

### Month 2+
- Live Shorts during earnings calls
- Multi-language Shorts (Spanish, Mandarin)
- Animated charts in Shorts
- Comparison Shorts (AAPL vs. MSFT)

### Month 6+
- AI-generated Shorts from transcript
- Real-time Shorts (within 1 hour of call)
- Interactive Shorts (polls, questions)
- Sponsored Shorts (partnerships)

---

## Summary

**Shorts = Traffic Driver**
- 10 Shorts per earnings call
- 2-3 uploads per day
- 5-10% click-through to full video
- 1000+ subscribers by Week 6

**Next Steps:**
1. Generate first full earnings video
2. Extract 10 best moments
3. Create 10 Shorts
4. Upload to YouTube
5. Track performance
6. Iterate and scale
