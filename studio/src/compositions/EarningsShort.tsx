import React from 'react';
import { AbsoluteFill, Audio, useCurrentFrame, useVideoConfig } from 'remotion';
import { TikTokCaption } from './shorts/TikTokCaption';
import { SpeakerFrame } from './shorts/SpeakerFrame';
import { AudioWaveform } from './shorts/AudioWaveform';
import { Watermark } from './shorts/Watermark';

export interface WordTimestamp {
  word: string;
  start: number;
  end: number;
}

export interface Highlight {
  text: string;
  speaker: string;
  timestamp: number;
  duration: number;
  category: 'financial' | 'product' | 'guidance' | 'strategy' | 'qa';
}

export interface EarningsShortProps {
  highlight: Highlight;
  audioUrl: string;
  audioStartTime?: number; // Start time in seconds for audio playback
  speakerPhotoUrl?: string;
  words: WordTimestamp[];
  companyName: string;
  ticker: string;
}

export const EarningsShort: React.FC<EarningsShortProps> = ({
  highlight,
  audioUrl,
  audioStartTime = 0,
  speakerPhotoUrl,
  words,
  companyName,
  ticker,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {/* Audio track */}
      <Audio src={audioUrl} startFrom={audioStartTime * fps} />

      {/* Speaker photo frame (top center) */}
      {speakerPhotoUrl && (
        <SpeakerFrame
          photoUrl={speakerPhotoUrl}
          name={highlight.speaker}
        />
      )}

      {/* Audio waveform visualization */}
      <AudioWaveform audioUrl={audioUrl} />

      {/* TikTok-style captions (center) */}
      <TikTokCaption words={words} currentFrame={frame} fps={fps} />

      {/* Company branding (bottom) */}
      <Watermark companyName={companyName} ticker={ticker} />
    </AbsoluteFill>
  );
};
