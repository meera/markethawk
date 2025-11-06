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
 * Data source: /var/earninglens/_downloads/jUnV3LiN0_k/
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
  call_date: '2025-11-05',

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

const PlaceholderCard: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 20], [0, 1]);

  return (
    <AbsoluteFill className="bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
      <div style={{opacity}} className="text-center px-20">
        <div className="text-4xl text-yellow-400 mb-8">⚠️ Work in Progress</div>
        <div className="text-3xl text-gray-300">{text}</div>
        <div className="text-xl text-gray-500 mt-8">
          Waiting for insights extraction to complete
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const PLTR_Q3_2025: React.FC = () => {
  const {fps, durationInFrames} = useVideoConfig();

  // Audio path - using the trimmed video from _downloads
  const audioPath = '/var/earninglens/_downloads/jUnV3LiN0_k/source.trimmed.mp4';

  return (
    <AbsoluteFill>
      {/* Audio Track - Full earnings call (trimmed) */}
      <Audio src={audioPath} />

      {/* Title Card: 0-5s */}
      <Sequence from={0} durationInFrames={fps * 5}>
        <TitleCard />
      </Sequence>

      {/* Revenue Card: 5-13s */}
      <Sequence from={fps * 5} durationInFrames={fps * 8}>
        <PlaceholderCard text="Revenue metrics will appear here" />
      </Sequence>

      {/* EPS Card: 13-21s */}
      <Sequence from={fps * 13} durationInFrames={fps * 8}>
        <PlaceholderCard text="EPS and earnings beat/miss" />
      </Sequence>

      {/*
        TODO: Add more sequences based on transcript timestamps
        - Key quotes from CEO/CFO
        - Revenue breakdown
        - Guidance
        - Q&A highlights
      */}

      {/* Brand Watermark - always visible */}
      <AbsoluteFill>
        <div className="absolute top-8 right-8 text-gray-400 text-2xl font-bold">
          EarningLens
        </div>
        <div className="absolute bottom-8 left-8 text-gray-500 text-lg">
          {PLTR_DATA.ticker} {PLTR_DATA.quarter} {PLTR_DATA.fiscal_year}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
