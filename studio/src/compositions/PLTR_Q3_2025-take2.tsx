import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  OffthreadVideo,
} from 'remotion';

/**
 * PLTR Q3 2025 Earnings Video - Take 2
 *
 * Data source: /var/markethawk/_downloads/jUnV3LiN0_k/
 * - source.trimmed.mp4 (audio)
 * - transcript.json (full transcript)
 * - insights.json (LLM analysis)
 *
 * Changes from take1:
 * - Fixed date to November 3, 2025
 * - Banner shows from beginning (no blank start)
 */

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

const SimpleBanner: React.FC = () => {
  return (
    <AbsoluteFill style={{zIndex: 10}}>
      {/* Black background behind white box */}
      <AbsoluteFill style={{backgroundColor: 'black', zIndex: 10}} />

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        height: '100%',
        position: 'relative',
        zIndex: 11,
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
            Earnings Call · November 3, 2025
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
              EarningLens.com
            </div>
            <div style={{
              fontSize: '32px',
              color: '#4b5563',
              marginTop: '12px',
            }}>
              Earnings Call Insights & Visualization
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const PLTR_Q3_2025_take2: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();
  const bannerDuration = fps * 5; // 5 seconds

  return (
    <AbsoluteFill className="bg-black">
      {/* Audio Track - Full earnings call (trimmed) */}
      {/* MVP: Copied to public/audio/ directory */}
      <Audio src={staticFile('audio/PLTR_Q3_2025.mp4')} />

      {/* Video Track - Plays from start, but covered by banner for first 5 seconds */}
      <Sequence from={0} durationInFrames={durationInFrames}>
        <AbsoluteFill style={{zIndex: 1}}>
          <OffthreadVideo
            src={staticFile('audio/PLTR_Q3_2025.mp4')}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
            }}
          />
        </AbsoluteFill>
      </Sequence>

      {/* Simple Banner - Only shows for first 5 seconds, then disappears */}
      <Sequence from={0} durationInFrames={bannerDuration}>
        <SimpleBanner />
      </Sequence>

      {/*
        Take 2 changes:
        - Banner shows for first 5 seconds only (opaque, covers video)
        - Correct date: November 3, 2025
        - Video plays throughout, visible after banner disappears

        Future enhancements:
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
