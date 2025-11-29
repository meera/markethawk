'use client';

import { useMediaPlayer } from './MediaPlayerContext';

interface Chapter {
  title: string;
  timestamp: number;
  summary?: string;
}

export function TableOfContents({ chapters }: { chapters: Chapter[] }) {
  const { seekTo } = useMediaPlayer();

  if (chapters.length === 0) return null;

  return (
    <div className="bg-gray-800/50 dark:bg-gray-800/50 border border-gray-700/50 dark:border-gray-700/50 rounded-lg p-6">
      <h2 className="text-lg font-semibold mb-4 text-white dark:text-white">Table of Contents</h2>
      <nav className="space-y-2">
        {chapters.map((chapter, index) => (
          <button
            key={index}
            onClick={() => seekTo(chapter.timestamp)}
            className="block w-full text-left text-sm text-primary hover:text-primary-light dark:text-primary dark:hover:text-primary-light hover:underline transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            {chapter.title}
          </button>
        ))}
      </nav>
    </div>
  );
}
