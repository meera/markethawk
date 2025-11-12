import {AbsoluteFill, Audio, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {
  AnimatedTitle,
  CallToAction,
  CompanyLogo,
  MetricDisplay,
  SpeakerLabel,
} from '../components/enhancements';
import {BrandProfile} from '../types/brand';

// Load default brand profile (create BIP.json later if needed)
import defaultBrandData from '../../../lens/companies/_default.json';

const brand: BrandProfile = defaultBrandData as BrandProfile;

// Customize for Brookfield Infrastructure
const bipBrand: BrandProfile = {
  ...brand,
  name: 'Brookfield Infrastructure Partners',
  ticker: 'BIP',
  brandColors: {
    primary: '#0033A0',      // Brookfield blue
    secondary: '#00A3E0',    // Light blue
    accent: '#FFB81C',       // Gold accent
    background: 'linear-gradient(to bottom right, #001f5f, #000000)',
    text: '#FFFFFF',
    textSecondary: '#E0E0E0',
  },
};

/**
 * Brookfield Infrastructure Partners (BIP) Q3 2025 Earnings Call Video
 * Duration: ~30 minutes (1827 seconds = 30m 27s)
 *
 * Data from: /var/markethawk/jobs/BIP_Q3_2025_20251109_135511/job.yaml
 *
 * Key speakers:
 * - Sam Pollock (CEO)
 * - David Krantz (CFO)
 * - Josh (Moderator)
 *
 * Financial highlights:
 * - FFO: $654M (+9% YoY)
 * - FFO per Unit: $0.83 (+9% YoY)
 * - Data segment: +60% YoY
 * - Liquidity: $5.5B
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

export const BIP_Q3_2025: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();

  // Video path - served via npx serve --cors
  const mediaServerUrl = process.env.MEDIA_SERVER_URL || 'http://192.168.1.101:8080';
  const videoPath = `${mediaServerUrl}/jobs/BIP_Q3_2025_20251109_135511/input/source.mp4`;

  return (
    <AbsoluteFill
      style={{
        background: bipBrand.brandColors.background,
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
          company={bipBrand.name}
          quarter="Q3"
          year={2025}
          brandColors={bipBrand.brandColors}
        />
      </Sequence>

      {/* 2. MAIN CONTENT - Static branded background (audio-only call) */}
      <Sequence from={fps * 5} durationInFrames={durationInFrames - fps * 15}>
        <AbsoluteFill
          style={{
            background: 'linear-gradient(135deg, #001f5f 0%, #000000 50%, #001f5f 100%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 40,
          }}
        >
          {/* Company Name - Large and centered (Primary) */}
          <div
            style={{
              fontSize: 120,
              fontWeight: '700',
              color: 'rgba(255, 255, 255, 0.9)',
              letterSpacing: '3px',
              textAlign: 'center',
              lineHeight: 1.2,
              maxWidth: '90%',
            }}
          >
            Brookfield Infrastructure Partners
          </div>

          {/* Quarterly Earnings Call - Large (Primary) */}
          <div
            style={{
              fontSize: 84,
              fontWeight: '600',
              color: 'rgba(255, 255, 255, 0.7)',
              letterSpacing: '3px',
              textAlign: 'center',
            }}
          >
            Q3 2025 Earnings Call
          </div>

          {/* Stock Symbol - Secondary hierarchy */}
          <div
            style={{
              fontSize: 120,
              fontWeight: 'bold',
              color: 'rgba(255, 184, 28, 0.4)', // Gold accent with transparency
              fontFamily: 'monospace',
              letterSpacing: '16px',
              textShadow: '0 0 40px rgba(255, 184, 28, 0.5)',
              marginTop: 40,
            }}
          >
            BIP
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* Audio track (audio-only source) with fade in */}
      <Sequence from={fps * 5} durationInFrames={durationInFrames - fps * 15}>
        <FadedAudio
          src={videoPath}
          startFrom={Math.floor(0.873 * fps)} // Start from first speech
          fadeInDuration={45} // 1.5 second fade in
        />
      </Sequence>

      {/* 3. KEY METRICS (at specific timestamps from insights) */}
      {/*
        TODO: ADJUST TIMESTAMPS AFTER FIRST RENDER

        Process:
        1. Render video: npx remotion render BIP-Q3-2025 /Volumes/markethawk/jobs/BIP_Q3_2025_20251109_135511/renders/take1.mp4
        2. Watch take1.mp4 and note actual times when metrics are spoken
        3. Update timestamps below (current values are from LLM - may be off by ±10-20s)
        4. Re-render as take2.mp4

        Example adjustment:
        - LLM says FFO mentioned at 180s
        - You hear it actually at 195s
        - Change: fps * (180 + 5) → fps * (195 + 5)
      */}

      {/* FFO: $654M at 180s (3m 0s) - TODO: Verify timing */}
      <Sequence from={fps * (180 + 5)} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Funds from Operations"
          value="$654M"
          change="+9% YoY"
          changeType="positive"
          brandColors={bipBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* FFO per Unit: $0.83 at 180s */}
      <Sequence from={fps * (190 + 5)} durationInFrames={fps * 8}>
        <MetricDisplay
          metric="FFO per Unit"
          value="$0.83"
          change="+9% YoY"
          changeType="positive"
          brandColors={bipBrand.brandColors}
          position="top-right"
          animationStyle="slide-up"
        />
      </Sequence>

      {/* Data segment: $138M at 342s (5m 42s) */}
      <Sequence from={fps * (342 + 5)} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Data Segment FFO"
          value="$138M"
          change="+60% YoY"
          changeType="positive"
          brandColors={bipBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Medium-term notes at 432s (7m 12s) */}
      <Sequence from={fps * (432 + 5)} durationInFrames={fps * 8}>
        <MetricDisplay
          metric="Medium-term Notes"
          value="$700M"
          change="4% Interest Rate"
          changeType="neutral"
          brandColors={bipBrand.brandColors}
          position="bottom-left"
          animationStyle="scale"
        />
      </Sequence>

      {/* Liquidity at 460s (7m 40s) */}
      <Sequence from={fps * (460 + 5)} durationInFrames={fps * 8}>
        <MetricDisplay
          metric="Liquidity"
          value="$5.5B"
          change="Strong Position"
          changeType="positive"
          brandColors={bipBrand.brandColors}
          position="top-right"
          animationStyle="slide-up"
        />
      </Sequence>

      {/* AI Infrastructure at 632s (10m 32s) */}
      <Sequence from={fps * (632 + 5)} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="AI Infrastructure Deal"
          value="$5B"
          change="1GW Power Solutions"
          changeType="positive"
          brandColors={bipBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Capital Recycling at 642s (10m 42s) */}
      <Sequence from={fps * (642 + 5)} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Capital Recycling"
          value="$3B+"
          change="Target: $3B more in 12-18mo"
          changeType="positive"
          brandColors={bipBrand.brandColors}
          position="bottom-right"
          animationStyle="slide-up"
        />
      </Sequence>

      {/* 4. SPEAKER LABELS (at chapter transitions) */}

      {/* Opening Remarks - Josh (Moderator) at 0s */}
      <Sequence from={fps * 5} durationInFrames={fps * 8}>
        <SpeakerLabel
          name="Josh"
          title="Moderator"
          brandColors={bipBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Financial Results - David Krantz (CFO) at 180s */}
      <Sequence from={fps * (180 + 5)} durationInFrames={fps * 8}>
        <SpeakerLabel
          name="David Krantz"
          title="CFO"
          brandColors={bipBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Business Update - Sam Pollock (CEO) at 570s */}
      <Sequence from={fps * (570 + 5)} durationInFrames={fps * 8}>
        <SpeakerLabel
          name="Sam Pollock"
          title="CEO"
          brandColors={bipBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Q&A Session starts at 1527s (25m 27s) */}
      <Sequence from={fps * (1527 + 5)} durationInFrames={fps * 8}>
        <SpeakerLabel
          name="Q&A Session"
          title="Analyst Questions"
          brandColors={bipBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* 5. PERSISTENT ELEMENTS (throughout video) */}

      {/* Company logo watermark - REMOVED per user request */}

      {/* 6. CALL TO ACTION (last 10s) */}
      <Sequence from={durationInFrames - fps * 10} durationInFrames={fps * 10}>
        <CallToAction
          message="View full interactive analysis with charts and insights"
          url="MarketHawk.com/BIP/Q3-2025"
          brandColors={bipBrand.brandColors}
          showSubscribe={true}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
