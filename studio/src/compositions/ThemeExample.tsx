import React from 'react';
import { AbsoluteFill, Sequence, useVideoConfig } from 'remotion';
import { SubscribeLowerThird, SubscribeLowerThirdCompact } from '../components/SubscribeLowerThird';
import { getTheme } from '../themes';

/**
 * Theme System Example
 *
 * Demonstrates how components automatically adapt to company brand colors.
 *
 * - First 5 seconds: Default YouTube red theme
 * - Next 5 seconds: Robinhood green theme
 * - Next 5 seconds: Palantir blue theme
 * - Last 5 seconds: Compact version with Robinhood theme
 */
export const ThemeExample: React.FC = () => {
  const { fps } = useVideoConfig();
  const sequenceDuration = fps * 5; // 5 seconds each

  // Load company themes
  const robinhoodTheme = getTheme('HOOD');
  const palantirTheme = getTheme('PLTR');

  return (
    <AbsoluteFill style={{ background: '#1a1a1a' }}>
      {/* Title Card */}
      <div
        style={{
          position: 'absolute',
          top: 60,
          left: 60,
          right: 60,
          textAlign: 'center',
        }}
      >
        <h1
          style={{
            fontSize: 64,
            fontWeight: 800,
            color: 'white',
            marginBottom: 20,
          }}
        >
          Theme System Demo
        </h1>
        <p
          style={{
            fontSize: 24,
            color: 'rgba(255, 255, 255, 0.7)',
            maxWidth: 800,
            margin: '0 auto',
          }}
        >
          Subscribe button automatically adapts to company brand colors
        </p>
      </div>

      {/* Sequence 1: Default (YouTube Red) */}
      <Sequence from={0} durationInFrames={sequenceDuration}>
        <div
          style={{
            position: 'absolute',
            top: 300,
            left: 60,
            fontSize: 32,
            fontWeight: 700,
            color: 'white',
          }}
        >
          Default Theme (YouTube Red)
        </div>
        <SubscribeLowerThird channelName="EarningLens" />
      </Sequence>

      {/* Sequence 2: Robinhood Theme (Green) */}
      <Sequence from={sequenceDuration} durationInFrames={sequenceDuration}>
        <div
          style={{
            position: 'absolute',
            top: 300,
            left: 60,
            fontSize: 32,
            fontWeight: 700,
            color: robinhoodTheme.colors.primary,
          }}
        >
          Robinhood Theme (Signature Green)
        </div>
        <SubscribeLowerThird
          channelName="EarningLens"
          theme={robinhoodTheme}
        />
      </Sequence>

      {/* Sequence 3: Palantir Theme (Blue) */}
      <Sequence from={sequenceDuration * 2} durationInFrames={sequenceDuration}>
        <div
          style={{
            position: 'absolute',
            top: 300,
            left: 60,
            fontSize: 32,
            fontWeight: 700,
            color: palantirTheme.colors.primary,
          }}
        >
          Palantir Theme (Corporate Blue)
        </div>
        <SubscribeLowerThird
          channelName="EarningLens"
          theme={palantirTheme}
        />
      </Sequence>

      {/* Sequence 4: Compact Version with Robinhood Theme */}
      <Sequence from={sequenceDuration * 3} durationInFrames={sequenceDuration}>
        <div
          style={{
            position: 'absolute',
            top: 300,
            left: 60,
            fontSize: 32,
            fontWeight: 700,
            color: robinhoodTheme.colors.primary,
          }}
        >
          Compact Version (Robinhood)
        </div>
        <SubscribeLowerThirdCompact
          channelName="EarningLens"
          theme={robinhoodTheme}
        />
      </Sequence>

      {/* Usage Code Display */}
      <div
        style={{
          position: 'absolute',
          bottom: 180,
          left: 60,
          right: 60,
          background: 'rgba(0, 0, 0, 0.8)',
          padding: 30,
          borderRadius: 12,
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 18,
          color: '#00ff00',
        }}
      >
        <div style={{ marginBottom: 10, color: '#888' }}>// Example usage:</div>
        <div>const theme = getTheme('HOOD'); // Robinhood</div>
        <div>&lt;SubscribeLowerThird theme={'{'}{'{'}theme{'}'} /&gt;</div>
      </div>
    </AbsoluteFill>
  );
};
