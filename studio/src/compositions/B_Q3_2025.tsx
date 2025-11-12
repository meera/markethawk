import {AbsoluteFill, Audio, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {
  AnimatedTitle,
  CallToAction,
  MetricDisplay,
  SpeakerLabel,
} from '../components/enhancements';
import {BrandProfile} from '../types/brand';

// Load default brand profile
import defaultBrandData from '../../../lens/companies/_default.json';

const brand: BrandProfile = defaultBrandData as BrandProfile;

// Customize for Barrick Mining Corporation
const barrickBrand: BrandProfile = {
  ...brand,
  name: 'Barrick Mining Corporation',
  ticker: 'B',
  brandColors: {
    primary: '#C5A05A',      // Gold
    secondary: '#8B7355',    // Bronze
    accent: '#FFD700',       // Bright gold accent
    background: 'linear-gradient(to bottom right, #2C1810, #000000)',
    text: '#FFFFFF',
    textSecondary: '#E0E0E0',
  },
};

/**
 * Barrick Mining Corporation (B) Q3 2025 Earnings Call Video
 *
 * Data from: /var/markethawk/jobs/B_Q3_2025_20251110_220309/job.yaml
 *
 * Key speakers:
 * - Mark Hill (Interim CEO and Group COO)
 * - Graham Shuttleworth (Senior EVP and CFO)
 * - Cleve Rickert (Head of Investor Relations)
 *
 * Financial highlights:
 * - Gold Production: +4% QoQ
 * - Free Cash Flow: +274% QoQ
 * - Base Dividend: +25%
 * - EBITDA: +20% QoQ
 *
 * NOTE: All timestamps are adjusted by +5s (150 frames) to account for title card
 */

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

export const B_Q3_2025: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();

  // Video path - served via npx serve --cors
  const mediaServerUrl = process.env.MEDIA_SERVER_URL || 'http://192.168.1.101:8080';
  const videoPath = `${mediaServerUrl}/jobs/B_Q3_2025_20251110_220309/input/source.mp4`;

  return (
    <AbsoluteFill
      style={{
        background: barrickBrand.brandColors.background,
      }}
    >
      {/* 1. TITLE CARD (0-5s) with intro music */}
      <Sequence from={0} durationInFrames={fps * 5}>
        {/* Intro music with fade out */}
        <Audio
          src={staticFile('nebula_youtube_music.mp3')}
          volume={(f) => {
            const fadeOutStart = fps * 4; // Start fading at 4s
            const fadeOutEnd = fps * 5;   // End at 5s

            if (f < fadeOutStart) {
              return 1; // Full volume until 4s
            }
            if (f >= fadeOutEnd) {
              return 0; // Silent after 5s
            }
            // Linear fade from 1 to 0 between 4s and 5s
            return 1 - ((f - fadeOutStart) / (fadeOutEnd - fadeOutStart));
          }}
        />
        <AnimatedTitle
          company={barrickBrand.name}
          quarter="Q3"
          year={2025}
          brandColors={barrickBrand.brandColors}
        />
      </Sequence>

      {/* 2. MAIN VIDEO - Actual earnings call video */}
      <Sequence from={fps * 5} durationInFrames={durationInFrames - fps * 15}>
        <OffthreadVideo
          src={videoPath}
          startFrom={0}
        />
      </Sequence>

      {/* 3. KEY METRICS (at specific timestamps from insights) */}
      {/* All timestamps are adjusted by +5s to account for title card */}

      {/* Mark Hill announced as Interim CEO at 74s → 79s */}
      <Sequence from={fps * 79} durationInFrames={fps * 8}>
        <MetricDisplay
          metric="Leadership Announcement"
          value="Mark Hill"
          change="Interim CEO & Group COO"
          changeType="neutral"
          brandColors={barrickBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Gold Production: +4% at 221s → 226s */}
      <Sequence from={fps * 226} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Gold Production"
          value="+4%"
          change="vs Q2 2025"
          changeType="positive"
          brandColors={barrickBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Copper Production (slightly down) at 286s → 291s */}
      <Sequence from={fps * 291} durationInFrames={fps * 8}>
        <MetricDisplay
          metric="Copper Production"
          value="Slightly Down"
          change="Due to Lamarna shutdown"
          changeType="negative"
          brandColors={barrickBrand.brandColors}
          position="top-right"
          animationStyle="slide-up"
        />
      </Sequence>

      {/* Free Cash Flow: +274% at 320s → 325s */}
      <Sequence from={fps * 325} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Free Cash Flow"
          value="+274%"
          change="Quarter over Quarter"
          changeType="positive"
          brandColors={barrickBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Four Mile discovery at 337s → 342s */}
      <Sequence from={fps * 342} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Four Mile Discovery"
          value="Significant"
          change="Exploration budget +$10M"
          changeType="positive"
          brandColors={barrickBrand.brandColors}
          position="bottom-left"
          animationStyle="scale"
        />
      </Sequence>

      {/* Base Dividend Increase: +25% at 479s → 484s */}
      <Sequence from={fps * 484} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Base Dividend"
          value="+25%"
          change="Quarterly Dividend Increase"
          changeType="positive"
          brandColors={barrickBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Net Cash Position: $598M at 482s → 487s */}
      <Sequence from={fps * 487} durationInFrames={fps * 8}>
        <MetricDisplay
          metric="Net Cash Position"
          value="$598M"
          change="Increased by quarter end"
          changeType="positive"
          brandColors={barrickBrand.brandColors}
          position="top-right"
          animationStyle="slide-up"
        />
      </Sequence>

      {/* Q3 Record Cash Returns at 564s → 569s */}
      <Sequence from={fps * 569} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Cash Returns"
          value="Record Q3"
          change="Record cash returns to shareholders"
          changeType="positive"
          brandColors={barrickBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* EBITDA: +20% at 657s → 662s */}
      <Sequence from={fps * 662} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="EBITDA"
          value="+20%"
          change="Quarter over Quarter"
          changeType="positive"
          brandColors={barrickBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* 4. SPEAKER LABELS (at chapter transitions) */}
      {/* All timestamps adjusted by +5s */}

      {/* Opening Remarks - Cleve Rickert at 2s → 7s */}
      <Sequence from={fps * 7} durationInFrames={fps * 10}>
        <SpeakerLabel
          name="Cleve Rickert"
          title="Head of Investor Relations"
          brandColors={barrickBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Financial Results - Mark Hill at 94s → 99s */}
      <Sequence from={fps * 99} durationInFrames={fps * 10}>
        <SpeakerLabel
          name="Mark Hill"
          title="Interim CEO & Group COO"
          brandColors={barrickBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Business Update at 117s → 122s */}
      <Sequence from={fps * 122} durationInFrames={fps * 10}>
        <SpeakerLabel
          name="Mark Hill"
          title="Interim CEO & Group COO"
          brandColors={barrickBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Guidance/Outlook - Graham Shuttleworth at 482s → 487s */}
      <Sequence from={fps * 487} durationInFrames={fps * 10}>
        <SpeakerLabel
          name="Graham Shuttleworth"
          title="Senior EVP & CFO"
          brandColors={barrickBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Q&A Session at 900s → 905s */}
      <Sequence from={fps * 905} durationInFrames={fps * 10}>
        <SpeakerLabel
          name="Q&A Session"
          title="Analyst Questions"
          brandColors={barrickBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* 5. CALL TO ACTION (last 10s) */}
      <Sequence from={durationInFrames - fps * 10} durationInFrames={fps * 10}>
        <CallToAction
          message="Subscribe for more earnings call analysis"
          url=""
          brandColors={barrickBrand.brandColors}
          showSubscribe={true}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
