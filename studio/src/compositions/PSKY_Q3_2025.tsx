import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
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

// Customize for Paramount Global
const paramountBrand: BrandProfile = {
  ...brand,
  name: 'Paramount Global',
  ticker: 'PSKY',
  brandColors: {
    primary: '#0064D2',      // Paramount blue
    secondary: '#00A8E1',    // Light blue
    accent: '#FFD700',       // Gold accent
    background: 'linear-gradient(to bottom right, #001f3f, #000000)',
    text: '#FFFFFF',
    textSecondary: '#E0E0E0',
  },
};

/**
 * Paramount Global (PSKY) Q3 2025 Earnings Call Video
 *
 * Data from: /var/markethawk/jobs/PSKY_Q3_2025_20251110_230817/job.yaml
 *
 * Key speakers:
 * - David Ellison (Chairman and CEO)
 * - Jeff Schell (President)
 * - Andy Warren (Interim CFO)
 * - Kevin Creighton (EVP of Corporate Finance and Investor Relations)
 *
 * Financial highlights:
 * - 2026 Revenue Guidance: $30B
 * - 2026 Adjusted EBITDA: $3.5B
 * - Run Rate Efficiency: $3B (up from $2B)
 * - Total Subscribers: 79M (+1.4M in Q3)
 * - Paramount Plus Growth: +24%
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

export const PSKY_Q3_2025: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();

  // Audio path - served via npx serve --cors
  const mediaServerUrl = process.env.MEDIA_SERVER_URL || 'http://192.168.1.101:8080';
  const audioPath = `${mediaServerUrl}/jobs/PSKY_Q3_2025_20251110_230817/input/source.mp4`;

  return (
    <AbsoluteFill
      style={{
        background: paramountBrand.brandColors.background,
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
          company={paramountBrand.name}
          quarter="Q3"
          year={2025}
          brandColors={paramountBrand.brandColors}
        />
      </Sequence>

      {/* 2. MAIN CONTENT - Static branded background (audio-only call) */}
      <Sequence from={fps * 5} durationInFrames={durationInFrames - fps * 15}>
        <AbsoluteFill
          style={{
            background: 'linear-gradient(135deg, #001f3f 0%, #000000 50%, #001f3f 100%)',
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
              fontSize: 140,
              fontWeight: '700',
              color: 'rgba(255, 255, 255, 0.9)',
              letterSpacing: '4px',
              textAlign: 'center',
              lineHeight: 1.2,
            }}
          >
            Paramount Global
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
              color: 'rgba(0, 100, 210, 0.4)', // Paramount blue with transparency
              fontFamily: 'monospace',
              letterSpacing: '16px',
              textShadow: '0 0 40px rgba(0, 100, 210, 0.5)',
              marginTop: 40,
            }}
          >
            PSKY
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* Audio track (audio-only source) with fade in */}
      <Sequence from={fps * 5} durationInFrames={durationInFrames - fps * 15}>
        <FadedAudio
          src={audioPath}
          startFrom={0}
          fadeInDuration={45} // 1.5 second fade in
        />
      </Sequence>

      {/* 3. KEY METRICS (at specific timestamps from insights) */}
      {/* All timestamps are adjusted by +5s to account for title card */}

      {/* David Ellison transformative vision at 172s → 177s */}
      <Sequence from={fps * 177} durationInFrames={fps * 10}>
        <SpeakerLabel
          name="David Ellison"
          title="Chairman and CEO"
          brandColors={paramountBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Content Investment: $1.5B at 320s → 325s */}
      <Sequence from={fps * 325} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Content Investment"
          value="$1.5B"
          change="Theatrical & DTC"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* 2026 Revenue Guidance: $30B at 335s → 340s */}
      <Sequence from={fps * 340} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="2026 Revenue Guidance"
          value="$30B"
          change="Strong DTC growth"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Adjusted EBITDA: $3.5B at 337s → 342s */}
      <Sequence from={fps * 342} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="2026 Adjusted EBITDA"
          value="$3.5B"
          change="Target for 2026"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="top-right"
          animationStyle="slide-up"
        />
      </Sequence>

      {/* Run Rate Efficiency: $3B at 337s → 342s (staggered) */}
      <Sequence from={fps * 345} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Efficiency Target"
          value="$3B"
          change="Increased from $2B"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="bottom-left"
          animationStyle="scale"
        />
      </Sequence>

      {/* Paramount Plus Growth: 24% at 531s → 536s */}
      <Sequence from={fps * 536} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Paramount Plus Growth"
          value="+24%"
          change="Revenue Growth"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Total Subscribers: 79M at 569s → 574s */}
      <Sequence from={fps * 574} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Total Subscribers"
          value="79M"
          change="+1.4M in Q3"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* UFC Investment at 760s → 765s */}
      <Sequence from={fps * 765} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="UFC Investment"
          value="Strategic"
          change="Drive subscriber growth"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="bottom-right"
          animationStyle="scale"
        />
      </Sequence>

      {/* Largest US subscription growth at 800s → 805s */}
      <Sequence from={fps * 805} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="US Subscription Growth"
          value="#1"
          change="Largest among streamers"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Theatrical releases: 15 movies/year at 942s → 947s */}
      <Sequence from={fps * 947} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Theatrical Releases"
          value="15 Movies/Year"
          change="Starting 2026"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* Investment grade by 2027 at 1964s → 1969s */}
      <Sequence from={fps * 1969} durationInFrames={fps * 10}>
        <MetricDisplay
          metric="Investment Grade"
          value="2027 Target"
          change="Long-term cash flow"
          changeType="positive"
          brandColors={paramountBrand.brandColors}
          position="center"
          animationStyle="bounce"
        />
      </Sequence>

      {/* 4. PERSISTENT SPEAKER LABELS (Audio-only: Keep visible to fill canvas) */}
      {/* All timestamps adjusted by +5s */}

      {/* Opening - Nadia (Conference Operator) 0-60s */}
      <Sequence from={fps * 5} durationInFrames={fps * 55}>
        <SpeakerLabel
          name="Nadia"
          title="Conference Operator"
          brandColors={paramountBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Kevin Creighton 60-172s */}
      <Sequence from={fps * 65} durationInFrames={fps * 107}>
        <SpeakerLabel
          name="Kevin Creighton"
          title="EVP of Corporate Finance & IR"
          brandColors={paramountBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* David Ellison (CEO) 172-822s (main presentation) */}
      <Sequence from={fps * 177} durationInFrames={fps * 645}>
        <SpeakerLabel
          name="David Ellison"
          title="Chairman and CEO"
          brandColors={paramountBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* Q&A Session 822s onwards */}
      <Sequence from={fps * 827} durationInFrames={durationInFrames - fps * 827 - fps * 10}>
        <SpeakerLabel
          name="Q&A Session"
          title="Analyst Questions"
          brandColors={paramountBrand.brandColors}
          position="bottom-left"
          showPhoto={false}
        />
      </Sequence>

      {/* 5. CALL TO ACTION (last 10s) */}
      <Sequence from={durationInFrames - fps * 10} durationInFrames={fps * 10}>
        <CallToAction
          message="Subscribe for more earnings call analysis"
          url=""
          brandColors={paramountBrand.brandColors}
          showSubscribe={true}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
