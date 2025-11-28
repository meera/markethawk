'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Download, Copy, Check, ChevronLeft, Play, Pause } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import { Breadcrumbs } from './Breadcrumbs';

interface Paragraph {
  speaker: string;
  start: number;
  text: string;
}

interface TranscriptData {
  language: string;
  paragraphs: Paragraph[];
}

interface Speaker {
  speaker_id: string;
  speaker_name: string;
  role: string | null;
}

interface Props {
  company: string;
  companyName: string;
  call: any;
  transcriptData: TranscriptData | null;
  speakers: Speaker[];
  quarterYear: string;
  mediaSignedUrl: string | null;
}

export function TranscriptPageClient({
  company,
  companyName,
  call,
  transcriptData,
  speakers,
  quarterYear,
  mediaSignedUrl,
}: Props) {
  const [searchTerm, setSearchTerm] = useState('');
  const [copied, setCopied] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Detect if media is audio or video
  const isAudio = mediaSignedUrl?.match(/\.(mp3|m4a|wav|aac)(\?|$)/i);

  // Create speaker name mapping with roles
  const speakerMap = speakers.reduce((acc, speaker) => {
    const name = speaker.speaker_name || speaker.speaker_id;
    const role = speaker.role ? ` (${speaker.role})` : '';
    acc[speaker.speaker_id] = { name, role, fullName: `${name}${role}` };
    return acc;
  }, {} as Record<string, { name: string; role: string; fullName: string }>);

  // Format timestamp (seconds to MM:SS)
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Highlight search terms in text
  const highlightText = (text: string, search: string) => {
    if (!search.trim()) return text;

    const parts = text.split(new RegExp(`(${search})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === search.toLowerCase() ? (
        <mark key={index} className="bg-yellow-200 text-gray-900">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  // Filter paragraphs based on search
  const filteredParagraphs = transcriptData?.paragraphs.filter(p =>
    searchTerm === '' ||
    p.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (speakerMap[p.speaker]?.name || p.speaker).toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  // Seek to timestamp in media
  const seekTo = (seconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      if (!isPlaying) {
        videoRef.current.play();
      }
      // Scroll media player into view
      videoRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });

      toast.success(`Jumped to ${formatTime(seconds)}`, {
        icon: '⏩',
        duration: 2000,
      });
    }
  };

  // Update current time
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const updateTime = () => setCurrentTime(video.currentTime);
    const updatePlayState = () => setIsPlaying(!video.paused);

    video.addEventListener('timeupdate', updateTime);
    video.addEventListener('play', updatePlayState);
    video.addEventListener('pause', updatePlayState);

    return () => {
      video.removeEventListener('timeupdate', updateTime);
      video.removeEventListener('play', updatePlayState);
      video.removeEventListener('pause', updatePlayState);
    };
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+K or Ctrl+K to focus search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }

      // Escape to clear search
      if (e.key === 'Escape' && searchTerm) {
        setSearchTerm('');
        searchInputRef.current?.blur();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [searchTerm]);

  // Generate full transcript text
  const generateTranscriptText = () => {
    if (!transcriptData) return '';

    let text = `${companyName} ${call.quarter} ${call.year} Earnings Call Transcript\n\n`;
    text += `Source: MarketHawk (https://markethawkeye.com/earnings/${company}/${quarterYear})\n\n`;
    text += '---\n\n';

    transcriptData.paragraphs.forEach((paragraph) => {
      const speaker = speakerMap[paragraph.speaker];
      const speakerName = speaker?.fullName || paragraph.speaker;
      const timestamp = formatTime(paragraph.start);
      text += `[${timestamp}] ${speakerName}:\n${paragraph.text}\n\n`;
    });

    return text;
  };

  // Copy to clipboard with error handling
  const handleCopy = async () => {
    const text = generateTranscriptText();
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast.success('Transcript copied to clipboard!', {
        icon: '📋',
        duration: 3000,
      });
      setTimeout(() => setCopied(false), 3000);
    } catch (err) {
      console.error('Failed to copy:', err);
      toast.error('Failed to copy. Please try again or check permissions.', {
        duration: 4000,
      });
    }
  };

  // Download as text file with better filename
  const handleDownload = () => {
    try {
      const text = generateTranscriptText();
      const blob = new Blob([text], { type: 'text/plain; charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Better filename format: Company-Name-Q3-2026-Earnings-Transcript.txt
      const cleanName = companyName.replace(/[^a-z0-9]/gi, '-').replace(/-+/g, '-');
      a.download = `${cleanName}-${call.quarter}-${call.year}-Earnings-Transcript.txt`;

      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success('Transcript downloaded!', {
        icon: '💾',
        duration: 3000,
      });
    } catch (err) {
      console.error('Failed to download:', err);
      toast.error('Failed to download. Please try again.', {
        duration: 4000,
      });
    }
  };

  if (!transcriptData) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="text-center py-12">
          <p className="text-gray-500">Transcript not available for this earnings call.</p>
          <Link
            href={`/earnings/${company}/${quarterYear}`}
            className="text-gray-600 hover:text-gray-900 mt-4 inline-block"
          >
            ← Back to earnings call
          </Link>
        </div>
      </div>
    );
  }

  return (
    <>
      <Toaster position="top-center" />

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Breadcrumbs */}
        <Breadcrumbs
          company={company}
          companyName={companyName}
          quarter={call.quarter}
          year={call.year}
          quarterYear={quarterYear}
        />

        {/* Back Link */}
        <Link
          href={`/earnings/${company}/${quarterYear}`}
          className="inline-flex items-center gap-2 text-gray-400 hover:text-gray-100 dark:text-gray-400 dark:hover:text-gray-100 mb-6 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to earnings call
        </Link>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold mb-3 text-gray-900 dark:text-white">{companyName}</h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
            {call.symbol} | {call.quarter} {call.year} Earnings Call Transcript
          </p>

          {/* Action buttons below title */}
          <div className="flex gap-3">
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              title="Copy transcript to clipboard (Ctrl+C)"
              aria-label="Copy transcript to clipboard"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-600" aria-hidden="true" />
                  <span className="text-sm font-medium text-green-600">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 text-gray-700 dark:text-gray-300" aria-hidden="true" />
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Copy</span>
                </>
              )}
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              title="Download transcript as text file"
              aria-label="Download transcript as text file"
            >
              <Download className="w-4 h-4" aria-hidden="true" />
              <span className="text-sm font-medium">Download</span>
            </button>
          </div>
        </div>

        {/* Media Player (if available) - Compact size */}
        {mediaSignedUrl && (
          <div className="bg-gray-800/50 dark:bg-gray-800/50 border border-gray-700/50 dark:border-gray-700/50 rounded-lg p-6 mb-8 shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-white dark:text-white">Recording</h2>
            {isAudio ? (
              <audio
                ref={videoRef as any}
                controls
                className="w-full"
                preload="metadata"
                src={mediaSignedUrl}
              >
                Your browser does not support the audio element.
              </audio>
            ) : (
              <video
                ref={videoRef}
                controls
                className="w-full rounded max-h-96"
                preload="metadata"
                src={mediaSignedUrl}
              >
                Your browser does not support the video element.
              </video>
            )}
            <p className="text-xs text-gray-400 dark:text-gray-400 mt-2">
              Click timestamps below to jump to that moment in the recording
            </p>
          </div>
        )}

        {/* Transcript */}
        <div className="bg-gray-800/50 dark:bg-gray-800/50 border border-gray-700/50 dark:border-gray-700/50 rounded-lg p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-4 text-white dark:text-white">Full Transcript</h2>

          {/* Search with keyboard shortcut hint */}
          <div className="sticky top-0 bg-gray-800/50 dark:bg-gray-800/50 z-10 pb-4 border-b border-gray-700/50 dark:border-gray-700/50 mb-4">
            <div className="relative">
              <input
                ref={searchInputRef}
                type="text"
                placeholder={`Search ${transcriptData.paragraphs.length} segments... (Cmd+K)`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900/50 dark:bg-gray-900/50 border border-gray-600 dark:border-gray-600 text-gray-100 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                aria-label="Search transcript"
              />
            </div>
            {searchTerm && (
              <p className="text-sm text-gray-400 dark:text-gray-400 mt-2" role="status" aria-live="polite">
                Found {filteredParagraphs.length} of {transcriptData.paragraphs.length} segments
              </p>
            )}
          </div>

          {/* Transcript segments */}
          <div className="space-y-4">
            {filteredParagraphs.map((paragraph, index) => {
              const speaker = speakerMap[paragraph.speaker];
              const isCurrentSegment = mediaSignedUrl && currentTime >= paragraph.start &&
                (index === filteredParagraphs.length - 1 || currentTime < filteredParagraphs[index + 1].start);

              return (
                <div
                  key={index}
                  className={`border-l-4 pl-4 py-2 transition-colors ${
                    isCurrentSegment ? 'border-blue-500 bg-blue-900/20 dark:border-blue-500 dark:bg-blue-900/20' : 'border-gray-600 dark:border-gray-600'
                  }`}
                >
                  <div className="flex items-center gap-3 mb-2">
                    {mediaSignedUrl ? (
                      <button
                        onClick={() => seekTo(paragraph.start)}
                        className="text-sm font-mono text-primary hover:text-primary-light dark:text-primary dark:hover:text-primary-light bg-primary/10 hover:bg-primary/20 dark:bg-primary/10 dark:hover:bg-primary/20 px-2 py-1 rounded transition-colors cursor-pointer focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
                        title={`Click to jump to ${formatTime(paragraph.start)}`}
                        aria-label={`Jump to timestamp ${formatTime(paragraph.start)}`}
                      >
                        {formatTime(paragraph.start)}
                      </button>
                    ) : (
                      <span className="text-sm font-mono text-gray-400 dark:text-gray-400 bg-gray-700/50 dark:bg-gray-700/50 px-2 py-1 rounded">
                        {formatTime(paragraph.start)}
                      </span>
                    )}
                    <span className="text-sm font-medium text-white dark:text-white">
                      {speaker?.name || paragraph.speaker}
                      {speaker?.role && (
                        <span className="text-xs text-gray-400 dark:text-gray-400 font-normal ml-1">
                          {speaker.role}
                        </span>
                      )}
                    </span>
                  </div>
                  <p className="text-gray-200 dark:text-gray-200 leading-relaxed">
                    {searchTerm ? highlightText(paragraph.text, searchTerm) : paragraph.text}
                  </p>
                </div>
              );
            })}
          </div>

          {filteredParagraphs.length === 0 && searchTerm && (
            <div className="text-center py-12">
              <p className="text-gray-400 dark:text-gray-400">No results found for &quot;{searchTerm}&quot;</p>
              <button
                onClick={() => setSearchTerm('')}
                className="text-primary hover:text-primary-light dark:text-primary dark:hover:text-primary-light mt-2 text-sm"
              >
                Clear search
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
