import React from 'react';

interface WatermarkProps {
  companyName: string;
  ticker: string;
}

export const Watermark: React.FC<WatermarkProps> = ({ companyName, ticker }) => {
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 80,
        left: 0,
        right: 0,
        textAlign: 'center',
        zIndex: 20,
      }}
    >
      {/* Company info */}
      <div
        style={{
          fontSize: 32,
          fontWeight: 700,
          color: '#FFFFFF',
          marginBottom: 10,
          textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
        }}
      >
        {companyName} ({ticker})
      </div>

      {/* MarketHawk branding */}
      <div
        style={{
          fontSize: 24,
          fontWeight: 600,
          color: '#FFD700',
          textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
        }}
      >
        @markethawkeye
      </div>
    </div>
  );
};
