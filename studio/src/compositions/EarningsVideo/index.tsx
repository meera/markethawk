import React from 'react';
import {
  AbsoluteFill,
  Composition,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from 'remotion';
import './style.css';

export interface EarningsData {
  company: string;
  ticker: string;
  quarter: string;
  fiscal_year: number;
  call_date: string;
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
    segments: Array<{
      name: string;
      revenue: number;
    }>;
    margins: {
      gross: number;
      operating: number;
      net: number;
    };
  };
  highlights: string[];
  transcript_highlights?: Array<{
    speaker: string;
    text: string;
    timestamp: number;
  }>;
}

interface EarningsVideoProps {
  data: EarningsData;
}

const TitleCard: React.FC<{data: EarningsData}> = ({data}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: {
      damping: 100,
    },
  });

  const opacity = interpolate(frame, [0, 15], [0, 1]);

  return (
    <AbsoluteFill className="bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
        }}
        className="text-center"
      >
        <h1 className="text-7xl font-bold text-white mb-6">
          {data.company}
        </h1>
        <div className="text-5xl text-gray-300 mb-4">
          {data.ticker}
        </div>
        <h2 className="text-4xl text-gray-400">
          {data.quarter} {data.fiscal_year} Earnings
        </h2>
        <div className="text-2xl text-gray-500 mt-4">
          {new Date(data.call_date).toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const RevenueCard: React.FC<{data: EarningsData}> = ({data}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const revenue = data.financials.revenue;
  const revenueBillions = (revenue.current / 1_000_000_000).toFixed(1);
  const previousBillions = (revenue.previous / 1_000_000_000).toFixed(1);
  const growth = revenue.yoy_growth;

  const numberOpacity = interpolate(frame, [0, 20], [0, 1]);
  const slideUp = interpolate(frame, [0, 30], [100, 0]);

  return (
    <AbsoluteFill className="bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
      <div style={{transform: `translateY(${slideUp}px)`}}>
        <div className="text-center">
          <div className="text-3xl text-gray-400 mb-4">Revenue</div>
          <div
            style={{opacity: numberOpacity}}
            className="text-8xl font-bold text-white mb-6"
          >
            ${revenueBillions}B
          </div>
          <div className="flex items-center justify-center gap-8 text-2xl">
            <div className="text-gray-500">
              Previous: ${previousBillions}B
            </div>
            <div
              className={`font-bold ${
                growth >= 0 ? 'text-green-400' : 'text-red-400'
              }`}
            >
              {growth >= 0 ? '+' : ''}
              {growth.toFixed(1)}% YoY
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const EPSCard: React.FC<{data: EarningsData}> = ({data}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const eps = data.financials.eps;
  const beat = eps.current - eps.estimate;
  const isBeat = eps.beat_miss === 'beat';

  const opacity = interpolate(frame, [0, 20], [0, 1]);

  return (
    <AbsoluteFill className="bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
      <div style={{opacity}}>
        <div className="text-center">
          <div className="text-3xl text-gray-400 mb-4">
            Earnings Per Share (EPS)
          </div>
          <div className="text-8xl font-bold text-white mb-6">
            ${eps.current.toFixed(2)}
          </div>
          <div className="flex items-center justify-center gap-8 text-2xl">
            <div className="text-gray-500">Estimate: ${eps.estimate.toFixed(2)}</div>
            <div
              className={`font-bold ${
                isBeat ? 'text-green-400' : 'text-red-400'
              }`}
            >
              {isBeat ? '✓' : '✗'} {isBeat ? 'Beat' : 'Miss'} by $
              {Math.abs(beat).toFixed(2)}
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SegmentsCard: React.FC<{data: EarningsData}> = ({data}) => {
  const frame = useCurrentFrame();

  const segments = data.financials.segments;
  const maxRevenue = Math.max(...segments.map((s) => s.revenue));

  return (
    <AbsoluteFill className="bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center px-20">
      <div className="w-full max-w-5xl">
        <div className="text-4xl text-white font-bold mb-12 text-center">
          Revenue by Segment
        </div>
        <div className="space-y-6">
          {segments.map((segment, idx) => {
            const barWidth = (segment.revenue / maxRevenue) * 100;
            const animatedWidth = interpolate(
              frame,
              [idx * 10, idx * 10 + 20],
              [0, barWidth],
              {extrapolateRight: 'clamp'}
            );

            return (
              <div key={segment.name} className="space-y-2">
                <div className="flex justify-between text-xl">
                  <span className="text-gray-300">{segment.name}</span>
                  <span className="text-white font-bold">
                    ${(segment.revenue / 1_000_000_000).toFixed(1)}B
                  </span>
                </div>
                <div className="w-full bg-gray-700 h-8 rounded-full overflow-hidden">
                  <div
                    style={{width: `${animatedWidth}%`}}
                    className="h-full bg-gradient-to-r from-blue-500 to-blue-400 rounded-full transition-all duration-300"
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const HighlightsCard: React.FC<{data: EarningsData}> = ({data}) => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill className="bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center px-20">
      <div className="w-full max-w-5xl">
        <div className="text-4xl text-white font-bold mb-12 text-center">
          Key Highlights
        </div>
        <div className="space-y-6">
          {data.highlights.map((highlight, idx) => {
            const opacity = interpolate(
              frame,
              [idx * 15, idx * 15 + 15],
              [0, 1],
              {extrapolateRight: 'clamp'}
            );

            return (
              <div
                key={idx}
                style={{opacity}}
                className="flex items-start gap-4"
              >
                <div className="w-3 h-3 bg-blue-400 rounded-full mt-2 flex-shrink-0" />
                <div className="text-2xl text-gray-200">{highlight}</div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const EarningsVideoComponent: React.FC<EarningsVideoProps> = ({data}) => {
  const {fps} = useVideoConfig();

  return (
    <AbsoluteFill>
      {/* Title Card: 0-5s */}
      <Sequence from={0} durationInFrames={fps * 5}>
        <TitleCard data={data} />
      </Sequence>

      {/* Revenue Card: 5-13s */}
      <Sequence from={fps * 5} durationInFrames={fps * 8}>
        <RevenueCard data={data} />
      </Sequence>

      {/* EPS Card: 13-21s */}
      <Sequence from={fps * 13} durationInFrames={fps * 8}>
        <EPSCard data={data} />
      </Sequence>

      {/* Segments: 21-35s */}
      <Sequence from={fps * 21} durationInFrames={fps * 14}>
        <SegmentsCard data={data} />
      </Sequence>

      {/* Highlights: 35-50s */}
      <Sequence from={fps * 35} durationInFrames={fps * 15}>
        <HighlightsCard data={data} />
      </Sequence>

      {/* Brand Watermark - always visible */}
      <AbsoluteFill>
        <div className="absolute top-8 right-8 text-gray-500 text-xl font-bold">
          EarningLens
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const EarningsVideo: React.FC = () => {
  return (
    <Composition
      id="EarningsVideo"
      component={EarningsVideoComponent}
      durationInFrames={1500} // 50 seconds at 30fps
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        data: {
          company: 'Sample Company',
          ticker: 'SMPL',
          quarter: 'Q1',
          fiscal_year: 2024,
          call_date: '2024-01-01',
          financials: {
            revenue: {
              current: 50000000000,
              previous: 45000000000,
              yoy_growth: 11.1,
            },
            eps: {
              current: 1.5,
              estimate: 1.4,
              beat_miss: 'beat',
            },
            segments: [
              {name: 'Product A', revenue: 25000000000},
              {name: 'Product B', revenue: 15000000000},
              {name: 'Services', revenue: 10000000000},
            ],
            margins: {
              gross: 40,
              operating: 25,
              net: 20,
            },
          },
          highlights: [
            'Record quarterly revenue',
            'Strong segment growth',
            'Positive guidance for next quarter',
          ],
        },
      }}
    />
  );
};
