import React from 'react';
import { Img } from 'remotion';

interface SpeakerFrameProps {
  photoUrl: string;
  name: string;
}

export const SpeakerFrame: React.FC<SpeakerFrameProps> = ({ photoUrl, name }) => {
  return (
    <div
      style={{
        position: 'absolute',
        top: 60,
        left: '50%',
        transform: 'translateX(-50%)',
        textAlign: 'center',
        zIndex: 10,
        width: '90%',
      }}
    >
      {/* Large rectangular photo frame */}
      <div
        style={{
          width: '100%',
          height: 820,
          borderRadius: '24px',
          border: '4px solid #FFD700',
          overflow: 'hidden',
          boxShadow: '0 8px 40px rgba(255,215,0,0.4)',
          backgroundColor: '#1a1a1a',
        }}
      >
        <Img
          src={photoUrl}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
      </div>

      {/* Speaker name overlay on image (bottom of image) */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)',
          padding: '40px 20px 20px',
          color: '#FFFFFF',
          fontSize: 36,
          fontWeight: 700,
          textShadow: '2px 2px 6px rgba(0,0,0,0.9)',
          fontFamily: 'Arial, sans-serif',
        }}
      >
        {name}
      </div>
    </div>
  );
};
