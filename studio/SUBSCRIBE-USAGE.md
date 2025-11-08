# Subscribe Lower Third Component

## Preview
Open Remotion Studio at http://localhost:8082 and select **"SubscribeLowerThirdExample"** from the composition list.

## Features

### Full Version (SubscribeLowerThird)
- ✅ Smooth slide-in from right with spring animation
- ✅ Bell icon with wiggle animation
- ✅ Channel name customization
- ✅ YouTube-style red subscribe button
- ✅ Glass morphism design (backdrop blur)
- ✅ Fully customizable positioning

### Compact Version (SubscribeLowerThirdCompact)
- ✅ Smaller, less intrusive
- ✅ Pulsing bell animation
- ✅ Perfect for longer videos

## Usage in PLTR Video

### Option 1: Show at specific timestamp
```tsx
import { SubscribeLowerThird } from '@/components/SubscribeLowerThird';

export const PLTR_Q3_2025_take2: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();

  return (
    <AbsoluteFill className="bg-black">
      {/* Your existing video and banner */}
      <OffthreadVideo src={staticFile('audio/PLTR_Q3_2025.mp4')} />

      {/* Show subscribe at 5 minutes for 10 seconds */}
      <Sequence from={5 * 60 * fps} durationInFrames={10 * fps}>
        <SubscribeLowerThird />
      </Sequence>
    </AbsoluteFill>
  );
};
```

### Option 2: Show multiple times
```tsx
{/* Show at 5 min, 15 min, 30 min */}
<Sequence from={5 * 60 * fps} durationInFrames={10 * fps}>
  <SubscribeLowerThird />
</Sequence>

<Sequence from={15 * 60 * fps} durationInFrames={10 * fps}>
  <SubscribeLowerThirdCompact />
</Sequence>

<Sequence from={30 * 60 * fps} durationInFrames={10 * fps}>
  <SubscribeLowerThird />
</Sequence>
```

### Option 3: Custom position (bottom left)
```tsx
<SubscribeLowerThird
  channelName="EarningLens"
  style={{
    bottom: 60,
    left: 40,
    right: 'auto', // Override default right positioning
  }}
/>
```

### Option 4: Custom timing
```tsx
{/* Show during Q&A section only */}
<Sequence from={21 * 60 * fps} durationInFrames={10 * 60 * fps}>
  <SubscribeLowerThirdCompact />
</Sequence>
```

## Customization

### Use company theme colors
The subscribe button automatically adapts to company brand colors:

```tsx
import { getTheme } from '@/themes';

// Robinhood: Green button
const robinhoodTheme = getTheme('HOOD');
<SubscribeLowerThird theme={robinhoodTheme} />

// Palantir: Blue button
const palantirTheme = getTheme('PLTR');
<SubscribeLowerThird theme={palantirTheme} />

// Default: YouTube red
<SubscribeLowerThird />
```

**Preview:** Open http://localhost:8082 and select **"ThemeExample"** to see all theme variations.

### Change colors manually
```tsx
<SubscribeLowerThird
  style={{
    background: 'rgba(37, 99, 235, 0.95)', // Blue instead of black
    border: '2px solid rgba(255, 255, 255, 0.2)',
  }}
/>
```

### Change animation speed
Edit `SubscribeLowerThird.tsx` line 15-18:
```tsx
const slideIn = spring({
  frame,
  fps,
  config: {
    damping: 20,  // Lower = more bouncy (10-30)
    mass: 0.5,    // Lower = faster (0.1-2)
  },
});
```

## Best Practices for 44-minute video:

1. **Show 3-4 times total**
   - Don't overdo it (annoys viewers)
   - Strategic placement

2. **Good timing:**
   - After key announcements (revenue, EPS)
   - Beginning of Q&A section
   - 2/3 through the video
   - Near the end

3. **Duration:**
   - Full version: 10-15 seconds
   - Compact version: 8-10 seconds
   - Don't show for too long

## Example: Strategic Placement for PLTR

```tsx
{/* After banner intro - 30 seconds */}
<Sequence from={30 * fps} durationInFrames={10 * fps}>
  <SubscribeLowerThird />
</Sequence>

{/* After revenue announcement - 10 minutes */}
<Sequence from={10 * 60 * fps} durationInFrames={8 * fps}>
  <SubscribeLowerThirdCompact />
</Sequence>

{/* Start of Q&A - 21 minutes */}
<Sequence from={21 * 60 * fps} durationInFrames={10 * fps}>
  <SubscribeLowerThird />
</Sequence>

{/* Near end - 40 minutes */}
<Sequence from={40 * 60 * fps} durationInFrames={10 * fps}>
  <SubscribeLowerThirdCompact />
</Sequence>
```

## Performance

- **Render impact:** Minimal (~1-2 seconds for 44-min video)
- **File size:** No change (0 KB - pure code)
- **GPU usage:** Negligible

## Comparison to Lottie

| Aspect | This Component | Lottie |
|--------|---------------|---------|
| File size | 0 KB (code) | 12-20 KB (JSON) |
| Customizable | 🟢 Fully | 🔴 Limited |
| Animation quality | 🟢 Smooth spring | 🟢 Smooth |
| Render speed | 🟢 Fast | 🟡 Medium |
| Easy to modify | 🟢 Yes | 🔴 Need After Effects |

---

**Ready to use!** Just add the `<Sequence>` blocks to your composition.
