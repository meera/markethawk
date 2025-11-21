import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';
import { useAudioData, visualizeAudio } from '@remotion/media-utils';

interface AudioWaveformProps {
  audioUrl: string;
}

export const AudioWaveform: React.FC<AudioWaveformProps> = ({ audioUrl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const audioData = useAudioData(audioUrl);

  if (!audioData) {
    return null;
  }

  const visualization = visualizeAudio({
    fps,
    frame,
    audioData,
    numberOfSamples: 64, // Number of bars
  });

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 920,
        left: 0,
        right: 0,
        height: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 3,
        padding: '0 60px',
        zIndex: 15,
      }}
    >
      {visualization.map((amplitude, index) => (
        <div
          key={index}
          style={{
            flex: 1,
            height: `${amplitude * 90}px`,
            backgroundColor: '#FFD700',
            borderRadius: 2,
            boxShadow: '0 0 8px rgba(255,215,0,0.4)',
            transition: 'height 0.1s ease',
          }}
        />
      ))}
    </div>
  );
};
