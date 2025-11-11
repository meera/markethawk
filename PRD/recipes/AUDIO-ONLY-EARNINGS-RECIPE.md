# Audio-Only Earnings Call Video Recipe

When the earnings call source is **audio-only** (no video), use this recipe to create a professional-looking video with static branded background.

## Problem

Many earnings calls are:
- Audio-only streams (HLS .m3u8)
- Conference call recordings (no video)
- Webcast audio tracks

Simply playing audio with a black screen looks unprofessional and boring.

---

## Solution: Static Branded Background

Create a visually appealing static background with:
1. Company branding (colors, ticker)
2. Large watermark (subtle, centered)
3. Earnings call info (bottom)
4. Metric overlays (timed to audio)

---

## Recipe

### 1. Visual Design

```tsx
// Main background - company brand gradient
<AbsoluteFill
  style={{
    background: 'linear-gradient(135deg, #001f5f 0%, #000000 50%, #001f5f 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  }}
>
  {/* Large centered ticker watermark */}
  <div
    style={{
      fontSize: 240,
      fontWeight: 'bold',
      color: 'rgba(255, 184, 28, 0.3)', // Use company accent color
      fontFamily: 'monospace',
      letterSpacing: '20px',
      textShadow: '0 0 40px rgba(255, 184, 28, 0.5)', // Glow effect
    }}
  >
    TICKER
  </div>

  {/* Earnings call info - two lines */}
  <div
    style={{
      position: 'absolute',
      bottom: 120,
      left: 0,
      right: 0,
      textAlign: 'center',
    }}
  >
    <div
      style={{
        fontSize: 72,
        fontWeight: '700',
        color: 'rgba(255, 255, 255, 0.8)',
        letterSpacing: '3px',
        marginBottom: '16px',
      }}
    >
      Q3 2025 Earnings Call
    </div>
    <div
      style={{
        fontSize: 48,
        fontWeight: '500',
        color: 'rgba(255, 255, 255, 0.5)',
        letterSpacing: '2px',
      }}
    >
      Company Name
    </div>
  </div>
</AbsoluteFill>
```

### 2. Audio Handling

**IMPORTANT:** Use `<Audio>` component for audio-only files, NOT `<OffthreadVideo>`!

```tsx
// Audio fade component for smooth transitions
const FadedAudio: React.FC<{
  src: string;
  startFrom?: number;
  fadeInDuration?: number;
  fadeOutDuration?: number;
}> = ({src, startFrom = 0, fadeInDuration = 30, fadeOutDuration = 0}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  // Fade in at start
  const fadeIn = interpolate(
    frame,
    [0, fadeInDuration],
    [0, 1],
    {extrapolateRight: 'clamp'}
  );

  // Fade out at end (if specified)
  const fadeOut = fadeOutDuration > 0
    ? interpolate(
        frame,
        [durationInFrames - fadeOutDuration, durationInFrames],
        [1, 0],
        {extrapolateLeft: 'clamp'}
      )
    : 1;

  const volume = Math.min(fadeIn, fadeOut);

  return <Audio src={src} startFrom={startFrom} volume={volume} />;
};

// Usage: Earnings call audio with fade in
<Sequence from={fps * 5} durationInFrames={durationInFrames - fps * 15}>
  <FadedAudio
    src={audioPath}
    startFrom={Math.floor(firstSpeechTimestamp * fps)} // Skip silence
    fadeInDuration={45} // 1.5 second fade in
  />
</Sequence>
```

**Why `<Audio>` not `<OffthreadVideo>`:**
- Audio-only files have no video stream
- `<OffthreadVideo>` will fail with "No video stream found"
- `<Audio>` component is designed for audio-only sources

### 3. Title Card Music with Smooth Fade

**CRITICAL:** Fade out title music and fade in earnings audio for smooth transition!

```tsx
{/* Title card with intro music (0-5s) */}
<Sequence from={0} durationInFrames={fps * 5}>
  {/* Intro music with fade out at end */}
  <Sequence from={0} durationInFrames={fps * 5}>
    <FadedAudio
      src={staticFile('intro-music.mp3')}
      fadeInDuration={15}      // 0.5s fade in
      fadeOutDuration={30}     // 1.0s fade out (smooth ending)
    />
  </Sequence>
  <AnimatedTitle ... />
</Sequence>

{/* Earnings audio with fade in (overlaps with music fade out) */}
<Sequence from={fps * 5} durationInFrames={durationInFrames - fps * 15}>
  <FadedAudio
    src={audioPath}
    startFrom={Math.floor(firstSpeechTimestamp * fps)}
    fadeInDuration={45}  // 1.5s fade in (smooth start)
  />
</Sequence>
```

**Why fading is critical:**
- ❌ Without fades: Abrupt cut between music and audio (jarring)
- ✅ With fades: Professional crossfade transition (smooth)

### 4. Metric Overlays

```tsx
{/* Overlay metrics at specific timestamps */}
<Sequence from={fps * (timestamp + 5)} durationInFrames={fps * 10}>
  <MetricDisplay
    metric="Revenue"
    value="$654M"
    change="+9% YoY"
    changeType="positive"
    brandColors={brandColors}
    position="center"
    animationStyle="bounce"
  />
</Sequence>
```

---

## Design Principles

### Colors

1. **Background gradient:**
   - Use company primary color (dark shade)
   - Gradient from color → black → color
   - Creates depth without distraction

2. **Watermark ticker:**
   - Large (240px)
   - Subtle opacity (0.2-0.3)
   - Use accent color (gold, green, blue)
   - Add glow effect (`textShadow`)

3. **Text hierarchy:**
   - Line 1 (Earnings call): Larger, brighter, bolder
   - Line 2 (Company): Smaller, dimmer, lighter weight

### Typography

- **Watermark:** Monospace font (clean, technical)
- **Earnings text:** Sans-serif, bold
- **Company name:** Sans-serif, medium weight
- **Letter spacing:** Add 2-3px for readability

### Positioning

- **Watermark:** Dead center
- **Earnings text:** Bottom, centered
- **Metrics:** Varied positions (center, top-right, bottom-left)
- **Margin:** 120px from bottom edge

---

## Brand Color Examples

### Blue (Financial/Enterprise)
```tsx
background: 'linear-gradient(135deg, #001f5f 0%, #000000 50%, #001f5f 100%)',
watermarkColor: 'rgba(255, 184, 28, 0.3)', // Gold accent
```

### Green (Fintech)
```tsx
background: 'linear-gradient(135deg, #003d1a 0%, #000000 50%, #003d1a 100%)',
watermarkColor: 'rgba(0, 200, 5, 0.3)', // Brand green
```

### Purple (Tech)
```tsx
background: 'linear-gradient(135deg, #1a0033 0%, #000000 50%, #1a0033 100%)',
watermarkColor: 'rgba(138, 43, 226, 0.3)', // Purple accent
```

---

## Checklist

Before rendering:

- [ ] Company brand colors configured
- [ ] Ticker watermark visible but subtle
- [ ] Earnings call text split into two lines
- [ ] Background gradient matches brand
- [ ] Audio starts at first speech (skip silence)
- [ ] Intro music added (optional, 5 seconds)
- [ ] Metric timestamps prepared (will adjust after take1)
- [ ] No top-corner logo (too cluttered)

---

## Common Mistakes to Avoid

❌ **Black empty screen** - Looks unprofessional
❌ **Watermark too bright** - Distracting
❌ **Text too small** - Not readable on mobile
❌ **Single long line** - Hard to read
❌ **No brand colors** - Generic, forgettable
❌ **Corner logos** - Cluttered, dated look

✅ **Clean centered design**
✅ **Subtle branding**
✅ **Clear text hierarchy**
✅ **Company colors**
✅ **Professional polish**

---

## Example Usage

**See:** `studio/src/compositions/BIP_Q3_2025.tsx`

- Brookfield Infrastructure Partners (BIP)
- Blue/gold brand colors
- Q3 2025 earnings call
- 30-minute audio-only stream

**Result:**
- Professional static background
- Clear branding
- Metric overlays at key moments
- Ready for YouTube upload

---

## Future Enhancements (Optional)

### Audio Waveform Visualization

```bash
# Generate animated waveform
ffmpeg -i input/source.mp4 \
  -filter_complex "[0:a]showwaves=s=1920x1080:mode=cline:colors=0x0033A0[v]" \
  -map "[v]" -map 0:a \
  output/waveform.mp4
```

Then use as background instead of static gradient.

### Stock B-roll Footage

- Add subtle corporate stock footage
- Set opacity to 0.2-0.3 (very subtle)
- Creates movement without distraction

### Particle Effects

- Subtle floating particles
- Use company accent color
- Very slow animation (not distracting)

---

---

## Thumbnail Generation

### Current Approach (No CEO Images)

Since we don't have a CEO/executive image database yet, use **text-focused thumbnails** extracted from the rendered video:

```bash
# 1. First render the video
npx remotion render TICKER-Q3-2025 /var/markethawk/jobs/TICKER_Q3_2025_DATE/renders/take1.mp4

# 2. Generate thumbnails from rendered video
cd ~/markethawk
source .venv/bin/activate
python lens/smart_thumbnail_generator.py \
  --video /var/markethawk/jobs/TICKER_Q3_2025_DATE/renders/take1.mp4 \
  --data /var/markethawk/jobs/TICKER_Q3_2025_DATE/job.yaml \
  --output /var/markethawk/jobs/TICKER_Q3_2025_DATE/thumbnails/
```

**Current limitations:**
- Can't extract frames from audio-only source (no video stream)
- Must render video first, then generate thumbnails
- No executive photos (just text + branding)

### Future: CEO/Executive Image Database

When we have executive photos, thumbnails will be much more compelling:

**Option A: Manual Collection**
- Create `/var/markethawk/executives/` directory
- Download CEO/CFO headshots from company websites
- Name: `{TICKER}_CEO.jpg`, `{TICKER}_CFO.jpg`
- Use in thumbnails

**Option B: Automated Scraping**
- Scrape from company investor relations pages
- Use LinkedIn API (requires authentication)
- Store in database with metadata

**Option C: Third-Party API**
- Clearbit Logo API (has executive photos)
- PeopleDataLabs API
- LinkedIn scraping services

**Thumbnail templates with executive photos:**

```python
# Future thumbnail generator
def generate_thumbnail_with_executive(
    executive_photo: str,  # Path to CEO headshot
    metric: str,           # "Revenue: $654M"
    company: str,          # "Brookfield Infrastructure"
    ticker: str            # "BIP"
):
    # Layout:
    # - Left 40%: CEO photo (circular crop, professional)
    # - Right 60%: Metric + company name + ticker
    # - Bottom: "Q3 2025 Earnings" banner
    pass
```

**For now:** Use text-only thumbnails, plan for executive photos in Phase 2.

---

**Last Updated:** 2025-11-09
**Used In:** BIP Q3-2025, and future audio-only earnings calls
**Next Enhancement:** CEO/Executive image database
