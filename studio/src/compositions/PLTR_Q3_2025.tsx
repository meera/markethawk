import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from 'remotion';

/**
 * PLTR Q3 2025 Earnings Video
 *
 * Data source: /var/markethawk/_downloads/jUnV3LiN0_k/
 * - source.trimmed.mp4 (audio)
 * - transcript.json (full transcript)
 * - insights.json (LLM analysis - when ready)
 */

// For now, using placeholder data
// Once insights.json is ready, import it dynamically
const PLTR_DATA = {
  company: 'Palantir Technologies',
  ticker: 'PLTR',
  quarter: 'Q3',
  fiscal_year: 2025,
  call_date: '2025-11-03',

  // TODO: Replace with actual data from insights.json
  financials: {
    revenue: {
      current: 0, // TODO: from insights
      previous: 0,
      yoy_growth: 0,
    },
    eps: {
      current: 0,
      estimate: 0,
      beat_miss: 'beat' as const,
    },
    segments: [
      {name: 'Government', revenue: 0},
      {name: 'Commercial', revenue: 0},
    ],
    margins: {
      gross: 0,
      operating: 0,
      net: 0,
    },
  },
  highlights: [
    'TODO: Extract from insights.json',
    'TODO: Key highlight 2',
    'TODO: Key highlight 3',
  ],
};

const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const opacity = interpolate(frame, [0, 30], [0, 1]);
  const scale = interpolate(frame, [0, 30], [0.8, 1]);

  return (
    <AbsoluteFill className="bg-gradient-to-br from-indigo-900 via-gray-900 to-black flex items-center justify-center">
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
        }}
        className="text-center"
      >
        <h1 className="text-8xl font-bold text-white mb-6">
          {PLTR_DATA.company}
        </h1>
        <div className="text-6xl text-indigo-300 mb-8 font-mono">
          ${PLTR_DATA.ticker}
        </div>
        <h2 className="text-5xl text-gray-300">
          {PLTR_DATA.quarter} {PLTR_DATA.fiscal_year} Earnings Call
        </h2>
      </div>
    </AbsoluteFill>
  );
};

const SimpleBanner: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Simple fade in at start
  const opacity = interpolate(frame, [0, 30], [0, 1], {extrapolateRight: 'clamp'});

  // Calculate elapsed time
  const totalSeconds = Math.floor(frame / fps);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  const timeDisplay = `${minutes}:${seconds.toString().padStart(2, '0')}`;

  return (
    <AbsoluteFill style={{opacity}}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        height: '100%',
      }}>
        {/* Centered white box with blue border */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '48px',
          border: '12px solid #2563eb',
          padding: '80px 120px',
          textAlign: 'center',
          minWidth: '1200px',
        }}>
          {/* Company Name */}
          <div style={{
            fontSize: '96px',
            fontWeight: 'bold',
            color: '#111827',
            marginBottom: '24px',
          }}>
            {PLTR_DATA.company}
          </div>

          {/* Ticker and Quarter */}
          <div style={{
            fontSize: '64px',
            color: '#2563eb',
            fontFamily: 'monospace',
            fontWeight: 'bold',
            marginBottom: '32px',
          }}>
            ${PLTR_DATA.ticker} · {PLTR_DATA.quarter} {PLTR_DATA.fiscal_year}
          </div>

          {/* Call Date */}
          <div style={{
            fontSize: '40px',
            color: '#374151',
            marginBottom: '40px',
          }}>
            Earnings Call · {new Date(PLTR_DATA.call_date).toLocaleDateString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric',
            })}
          </div>

          {/* Time Display */}
          <div style={{
            fontSize: '48px',
            fontFamily: 'monospace',
            color: '#4b5563',
            marginBottom: '40px',
          }}>
            {timeDisplay}
          </div>

          {/* Branding */}
          <div style={{
            borderTop: '6px solid #2563eb',
            paddingTop: '32px',
          }}>
            <div style={{
              fontSize: '72px',
              fontWeight: 'bold',
              color: '#2563eb',
            }}>
              EarningLens
            </div>
            <div style={{
              fontSize: '32px',
              color: '#4b5563',
              marginTop: '12px',
            }}>
              Earnings Call Analysis
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const PLTR_Q3_2025: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();

  return (
    <AbsoluteFill className="bg-black">
      {/* Audio Track - Full earnings call (trimmed) */}
      {/* MVP: Copied to public/audio/ directory */}
      <Audio src={staticFile('audio/PLTR_Q3_2025.mp4')} />

      {/* Simple Banner Overlay - Full Duration from start */}
      <Sequence from={0} durationInFrames={durationInFrames}>
        <SimpleBanner />
      </Sequence>

      {/*
        MVP: Simple banner overlay only

        Future enhancements (after fixing context length):
        - Transcript subtitles
        - Key quotes from CEO/CFO
        - Revenue charts
        - EPS visualization
        - Guidance highlights
        - Q&A segments
      */}
    </AbsoluteFill>
  );
};
