import React from 'react';
import { AbsoluteFill, Sequence } from 'remotion';
import { SubscribeLowerThird, SubscribeLowerThirdCompact } from '../../components/SubscribeLowerThird';

/**
 * Example composition showing Subscribe lower third animations
 */
export const SubscribeExample: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {/* Demo background */}
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 48,
          color: 'white',
          fontWeight: 'bold',
        }}
      >
        Earnings Call Video
      </div>

      {/* Full version - appears at frame 30 (1 second at 30fps) */}
      <Sequence from={30} durationInFrames={150}>
        <SubscribeLowerThird channelName="EarningLens" />
      </Sequence>

      {/* Compact version - appears at frame 210 (7 seconds) */}
      <Sequence from={210} durationInFrames={120}>
        <SubscribeLowerThirdCompact />
      </Sequence>

      {/* Custom positioned version */}
      <Sequence from={360} durationInFrames={120}>
        <SubscribeLowerThird
          channelName="EarningLens"
          style={{
            bottom: 40,
            left: 40,
            right: 'auto',
          }}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
