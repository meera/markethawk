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
            <video
              ref={videoRef}
              controls
              className="w-full rounded max-h-96"
              preload="metadata"
              src={mediaUrl}
            >
              Your browser does not support the video element.
            </video>
          )}
        </div>
      )}
    </div>
  );
}
