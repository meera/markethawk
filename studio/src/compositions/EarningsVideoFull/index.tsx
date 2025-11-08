import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Composition,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Img,
  staticFile,
} from 'remotion';
import '../EarningsVideo/style.css';

/**
 * Full Earnings Call Video with Audio
 *
 * This composition uses the actual earnings call audio (30-60 minutes)
 * and overlays visual elements synchronized to the transcript.
 */

export interface Speaker {
  name: string;
  title: string;
  image_url: string;
}

export interface TranscriptSegment {
  speaker: string;
  text: string;
  start_time: number; // seconds
  end_time: number; // seconds
  key_metrics?: Array<{
    type: 'revenue' | 'eps' | 'growth' | 'guidance';
    value: string;
    direction?: 'up' | 'down' | 'neutral';
  }>;
}

export interface EarningsCallData {
  company: string;
  ticker: string;
  quarter: string;
  fiscal_year: number;
  call_date: string;
  audio_url: string; // Path to audio file in R2 or local
  duration_seconds: number; // Total audio duration
  speakers: Record<string, Speaker>; // Speaker ID -> Speaker info
  transcript: TranscriptSegment[];
  financials: {
    revenue: {
      current: number;
      previous: number;
      yoy_growth: number;
    };
    eps: {
      current: number;
      estimate: number;
      beat_miss: 'beat' | 'miss';
    };
  };
}

interface EarningsCallVideoProps {
  data: EarningsCallData;
}

/**
 * Speaker Overlay Component
 * Shows speaker's image and name in bottom-left corner
 */
const SpeakerOverlay: React.FC<{
  speaker: Speaker;
  opacity?: number;
}> = ({speaker, opacity = 1}) => {
  return (
    <div
      style={{opacity}}
      className="absolute bottom-8 left-8 flex items-center gap-4 bg-black/80 rounded-2xl px-6 py-4 backdrop-blur-sm"
    >
      <div className="w-16 h-16 rounded-full overflow-hidden bg-gray-700">
        {speaker.image_url ? (
          <Img src={speaker.image_url} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-2xl text-gray-400">
            {speaker.name.charAt(0)}
          </div>
        )}
      </div>
      <div>
        <div className="text-xl font-bold text-white">{speaker.name}</div>
        <div className="text-sm text-gray-400">{speaker.title}</div>
      </div>
    </div>
  );
};

/**
 * Metric Popup Component
 * Shows dynamic metrics when mentioned (e.g., "Revenue up 9%")
 */
const MetricPopup: React.FC<{
  metric: {
    type: string;
    value: string;
    direction?: 'up' | 'down' | 'neutral';
  };
  frame: number;
  startFrame: number;
}> = ({metric, frame, startFrame}) => {
  const relativeFrame = frame - startFrame;
  const duration = 90; // Show for 3 seconds at 30fps

  if (relativeFrame < 0 || relativeFrame > duration) {
    return null;
  }

  // Animate entrance (slide up)
  const translateY = interpolate(relativeFrame, [0, 20], [50, 0], {
    extrapolateRight: 'clamp',
  });

  // Animate exit (fade out)
  const opacity = interpolate(relativeFrame, [duration - 20, duration], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const bgColor =
    metric.direction === 'up'
      ? 'bg-green-500'
      : metric.direction === 'down'
      ? 'bg-red-500'
      : 'bg-blue-500';

  const arrow =
    metric.direction === 'up' ? '↑' : metric.direction === 'down' ? '↓' : '';

  return (
    <div
      style={{
        transform: `translateY(${translateY}px)`,
        opacity,
      }}
      className="absolute top-1/3 right-12"
    >
      <div
        className={`${bgColor} text-white px-8 py-6 rounded-2xl shadow-2xl flex items-center gap-4`}
      >
        {arrow && <div className="text-5xl">{arrow}</div>}
        <div>
          <div className="text-xl text-white/80 uppercase tracking-wide">
            {metric.type}
          </div>
          <div className="text-5xl font-bold">{metric.value}</div>
        </div>
      </div>
    </div>
  );
};

/**
 * Company Branding Overlay
 * Shows company logo and ticker in top-left corner
 */
const BrandingOverlay: React.FC<{
  company: string;
  ticker: string;
  logoUrl?: string;
}> = ({company, ticker, logoUrl}) => {
  return (
    <div className="absolute top-8 left-8 flex items-center gap-4">
      {logoUrl && (
        <div className="w-16 h-16 bg-white rounded-xl p-2">
          <Img src={logoUrl} className="w-full h-full object-contain" />
        </div>
      )}
      <div>
        <div className="text-2xl font-bold text-white">{ticker}</div>
        <div className="text-sm text-gray-400">{company}</div>
      </div>
    </div>
  );
};

/**
 * Main Video Component
 */
const EarningsCallVideoComponent: React.FC<EarningsCallVideoProps> = ({data}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const currentTime = frame / fps;

  // Find current speaker based on transcript timing
  const currentSegment = data.transcript.find(
    (seg) => currentTime >= seg.start_time && currentTime < seg.end_time
  );

  const currentSpeaker = currentSegment
    ? data.speakers[currentSegment.speaker]
    : null;

  // Find metrics to display in current time window
  const activeMetrics =
    currentSegment?.key_metrics?.map((metric, idx) => ({
      metric,
      // Stagger metrics if multiple in same segment
      startFrame: Math.floor(
        (currentSegment.start_time + idx * 2) * fps
      ),
    })) || [];

  return (
    <AbsoluteFill className="bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Audio Track */}
      <Audio src={data.audio_url} />

      {/* Company Branding - Always visible */}
      <BrandingOverlay
        company={data.company}
        ticker={data.ticker}
        logoUrl={staticFile(`logos/${data.ticker}.png`)}
      />

      {/* Speaker Overlay - Shows current speaker */}
      {currentSpeaker && <SpeakerOverlay speaker={currentSpeaker} />}

      {/* Metric Popups - Show when metrics are mentioned */}
      {activeMetrics.map((item, idx) => (
        <MetricPopup
          key={idx}
          metric={item.metric}
          frame={frame}
          startFrame={item.startFrame}
        />
      ))}

      {/* EarningLens Branding - Top Right */}
      <div className="absolute top-8 right-8 text-gray-500 text-xl font-bold">
        EarningLens
      </div>

      {/* Progress Bar - Bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-800">
        <div
          style={{
            width: `${(currentTime / data.duration_seconds) * 100}%`,
          }}
          className="h-full bg-blue-500"
        />
      </div>
    </AbsoluteFill>
  );
};

/**
 * Remotion Composition Registration
 */
export const EarningsCallVideo: React.FC = () => {
  return (
    <Composition
      id="EarningsCallVideo"
      component={EarningsCallVideoComponent}
      durationInFrames={54000} // 30 minutes at 30fps (adjust based on audio)
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        data: {
          company: 'Apple Inc.',
          ticker: 'AAPL',
          quarter: 'Q4',
          fiscal_year: 2024,
          call_date: '2024-11-01',
          audio_url: staticFile('audio/AAPL-Q4-2024.m4a'),
          duration_seconds: 1800, // 30 minutes
          speakers: {
            'tim-cook': {
              name: 'Tim Cook',
              title: 'CEO',
              image_url: staticFile('speakers/tim-cook.jpg'),
            },
            'luca-maestri': {
              name: 'Luca Maestri',
              title: 'CFO',
              image_url: staticFile('speakers/luca-maestri.jpg'),
            },
          },
          transcript: [
            {
              speaker: 'tim-cook',
              text: "Thank you. Good afternoon and thank you for joining us. Today, Apple is reporting revenue of $94.9 billion, up 6 percent from a year ago.",
              start_time: 0,
              end_time: 12,
              key_metrics: [
                {
                  type: 'revenue',
                  value: '$94.9B',
                  direction: 'up',
                },
                {
                  type: 'growth',
                  value: '+6%',
                  direction: 'up',
                },
              ],
            },
            {
              speaker: 'luca-maestri',
              text: "iPhone revenue was $46.2 billion, up 6 percent year over year, driven by strong demand for iPhone 16.",
              start_time: 12,
              end_time: 22,
              key_metrics: [
                {
                  type: 'revenue',
                  value: '$46.2B',
                  direction: 'up',
                },
              ],
            },
            // More segments...
          ],
          financials: {
            revenue: {
              current: 94900000000,
              previous: 89498000000,
              yoy_growth: 6.1,
            },
            eps: {
              current: 1.64,
              estimate: 1.6,
              beat_miss: 'beat',
            },
          },
        },
      }}
    />
  );
};
