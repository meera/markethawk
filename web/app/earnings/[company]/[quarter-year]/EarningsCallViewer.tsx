'use client';

import { useRef, useEffect } from 'react';
import { useMediaPlayer } from './MediaPlayerContext';

export function EarningsCallViewer({
  mediaUrl,
}: {
  mediaUrl: string | null;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const { registerPlayer } = useMediaPlayer();

  // Register the media player with context
  useEffect(() => {
    if (videoRef.current) {
      registerPlayer(videoRef.current);
    }
  }, [mediaUrl, registerPlayer]);

  // Detect if media is audio or video based on file extension
  const isAudio = mediaUrl?.match(/\.(mp3|m4a|wav|aac)(\?|$)/i);

  return (
    <div>
      {/* Video/Audio Player */}
      {mediaUrl && (
        <div className="bg-gray-800/50 dark:bg-gray-800/50 border border-gray-700/50 dark:border-gray-700/50 rounded-lg p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-4 text-white dark:text-white">Recording</h2>
          {isAudio ? (
            <audio
              ref={videoRef as any}
              controls
              className="w-full"
              preload="metadata"
              src={mediaUrl}
            >
              Your browser does not support the audio element.
            </audio>
          ) : (
            // TODO: Add poster={thumbnailUrl} to video element
            // 1. Generate thumbnail in pipeline workflow (extract frame or use banner)
            // 2. Upload to R2 alongside rendered.mp4, add thumbnail_url column to earnings_calls schema
            // 3. Pass thumbnailUrl prop to this component and use as poster
            <div className="relative aspect-video bg-gray-900 rounded overflow-hidden">
              <video
                ref={videoRef}
                controls
                className="absolute inset-0 w-full h-full object-contain"
                preload="metadata"
                src={mediaUrl}
              >
                Your browser does not support the video element.
              </video>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
