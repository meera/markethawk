import React from 'react';
import { AbsoluteFill } from 'remotion';
import { WordTimestamp } from '../EarningsShort';

interface TikTokCaptionProps {
  words: WordTimestamp[];
  currentFrame: number;
  fps: number;
}

export const TikTokCaption: React.FC<TikTokCaptionProps> = ({
  words,
  currentFrame,
  fps,
}) => {
  const currentTime = currentFrame / fps;

  // Find currently active words (show 2-3 words at a time for readability)
  const activeWordIndex = words.findIndex(
    (w) => w.start <= currentTime && currentTime < w.end
  );

  if (activeWordIndex === -1) return null;

  // Show current word + next 1-2 words for context
  const visibleWords = words.slice(activeWordIndex, activeWordIndex + 3);

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 800,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '0 40px',
        zIndex: 20,
      }}
    >
      <div
        style={{
          fontSize: 46,
          fontWeight: 800,
          textAlign: 'center',
          lineHeight: 1.4,
          fontFamily: 'Arial Black, sans-serif',
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          padding: '16px 24px',
          borderRadius: '12px',
        }}
      >
        {visibleWords.map((word, i) => {
          const isActive = i === 0; // First word is always the active one
          return (
            <span
              key={`${word.start}-${i}`}
              style={{
                color: isActive ? '#FFD700' : '#FFFFFF',
                textShadow: isActive
                  ? '3px 3px 6px rgba(0,0,0,0.8), 0 0 20px rgba(255,215,0,0.5)'
                  : '3px 3px 6px rgba(0,0,0,0.8)',
                margin: '0 12px',
                display: 'inline-block',
                transition: 'all 0.1s ease',
                transform: isActive ? 'scale(1.1)' : 'scale(1)',
              }}
            >
              {word.word}
            </span>
          );
        })}
      </div>
    </div>
  );
};
