import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { CompanyTheme } from '../themes/types';

interface SubscribeLowerThirdProps {
  channelName?: string;
  style?: React.CSSProperties;
  theme?: CompanyTheme;
}

export const SubscribeLowerThird: React.FC<SubscribeLowerThirdProps> = ({
  channelName = 'MarketHawk',
  style,
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Use theme colors or defaults
  const primaryColor = theme?.colors.primary || '#FF0000';
  const textColor = theme?.colors.text || '#ffffff';
  const textSecondary = theme?.colors.textSecondary || 'rgba(255, 255, 255, 0.7)';

  // Slide in from right with spring animation
  const slideIn = spring({
    frame,
    fps,
    config: {
      damping: 20,
      mass: 0.5,
    },
  });

  const translateX = interpolate(slideIn, [0, 1], [400, 0]);
  const opacity = interpolate(frame, [0, 10], [0, 1]);

  // Bell wiggle animation (starts after slide-in)
  const bellWiggle = interpolate(
    frame % 60, // Wiggle every 2 seconds (60 frames at 30fps)
    [0, 5, 10, 15, 20],
    [0, -15, 15, -10, 0],
    { extrapolateRight: 'clamp' }
  );

  const bellRotation = frame > 30 ? bellWiggle : 0;

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 80,
        right: 40,
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        background: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(10px)',
        padding: '16px 24px',
        borderRadius: 50,
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
        border: '2px solid rgba(255, 255, 255, 0.1)',
        transform: `translateX(${translateX}px)`,
        opacity,
        ...style,
      }}
    >
      {/* Bell Icon */}
      <div
        style={{
          fontSize: 32,
          transform: `rotate(${bellRotation}deg)`,
          transformOrigin: 'center top',
          filter: `drop-shadow(0 2px 4px ${primaryColor}66)`, // 66 = 40% opacity
        }}
      >
        🔔
      </div>

      {/* Text Content */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            color: textColor,
            letterSpacing: '0.5px',
          }}
        >
          Subscribe to {channelName}
        </div>
        <div
          style={{
            fontSize: 12,
            color: textSecondary,
            fontWeight: 500,
          }}
        >
          Never miss an earnings call
        </div>
      </div>

      {/* Subscribe Button (uses theme primary color) */}
      <button
        style={{
          background: primaryColor,
          color: 'white',
          border: 'none',
          borderRadius: 24,
          padding: '10px 20px',
          fontSize: 14,
          fontWeight: 700,
          cursor: 'pointer',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          boxShadow: `0 2px 8px ${primaryColor}66`, // 66 = 40% opacity
        }}
      >
        Subscribe
      </button>
    </div>
  );
};

// Alternative: Compact version (smaller)
export const SubscribeLowerThirdCompact: React.FC<SubscribeLowerThirdProps> = ({
  channelName = 'MarketHawk',
  style,
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Use theme colors or defaults
  const primaryColor = theme?.colors.primary || '#FF0000';
  const textColor = theme?.colors.text || '#ffffff';

  const slideIn = spring({
    frame,
    fps,
    config: {
      damping: 20,
    },
  });

  const translateX = interpolate(slideIn, [0, 1], [300, 0]);
  const opacity = interpolate(frame, [0, 10], [0, 1]);

  // Pulse animation for bell
  const scale = interpolate(
    Math.sin((frame / 30) * Math.PI * 2),
    [-1, 1],
    [1, 1.2]
  );

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 60,
        right: 40,
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        background: `${primaryColor}F2`, // F2 = 95% opacity
        padding: '12px 20px',
        borderRadius: 30,
        boxShadow: `0 4px 20px ${primaryColor}80`, // 80 = 50% opacity
        transform: `translateX(${translateX}px)`,
        opacity,
        ...style,
      }}
    >
      <div
        style={{
          fontSize: 24,
          transform: `scale(${scale})`,
        }}
      >
        🔔
      </div>
      <div
        style={{
          fontSize: 16,
          fontWeight: 700,
          color: textColor,
          letterSpacing: '0.5px',
        }}
      >
        Subscribe
      </div>
    </div>
  );
};
