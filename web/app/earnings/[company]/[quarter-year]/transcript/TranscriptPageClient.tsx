'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Download, Copy, Check } from 'lucide-react';

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
}

export function TranscriptPageClient({
  company,
  companyName,
  call,
  transcriptData,
  speakers,
  quarterYear,
}: Props) {
  const [searchTerm, setSearchTerm] = useState('');
  const [copied, setCopied] = useState(false);

  // Create speaker name mapping
  const speakerMap = speakers.reduce((acc, speaker) => {
    acc[speaker.speaker_id] = speaker.speaker_name || speaker.speaker_id;
    return acc;
  }, {} as Record<string, string>);

  // Format timestamp (seconds to MM:SS)
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Filter paragraphs based on search
  const filteredParagraphs = transcriptData?.paragraphs.filter(p =>
    searchTerm === '' ||
    p.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (speakerMap[p.speaker] || p.speaker).toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  // Generate full transcript text
  const generateTranscriptText = () => {
    if (!transcriptData) return '';

    let text = `${companyName} ${call.quarter} ${call.year} Earnings Call Transcript\n\n`;
    text += `Source: MarketHawk (https://markethawkeye.com/earnings/${company}/${quarterYear})\n\n`;
    text += '---\n\n';

    transcriptData.paragraphs.forEach((paragraph) => {
      const speakerName = speakerMap[paragraph.speaker] || paragraph.speaker;
      const timestamp = formatTime(paragraph.start);
      text += `[${timestamp}] ${speakerName}:\n${paragraph.text}\n\n`;
    });

    return text;
  };

  // Copy to clipboard
  const handleCopy = async () => {
    const text = generateTranscriptText();
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Download as text file
  const handleDownload = () => {
    const text = generateTranscriptText();
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${company}-${call.quarter}-${call.year}-transcript.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <Link
          href={`/earnings/${company}/${quarterYear}`}
          className="text-gray-600 hover:text-gray-900 mb-4 inline-block"
        >
          ← Back to earnings call
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">{companyName}</h1>
            <div className="flex flex-wrap gap-4 text-gray-600">
              <span className="text-2xl font-medium">
                {call.symbol} | {call.quarter} {call.year} Transcript
              </span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              title="Copy to clipboard"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium text-green-600">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span className="text-sm font-medium">Copy</span>
                </>
              )}
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              title="Download as text file"
            >
              <Download className="w-4 h-4" />
              <span className="text-sm font-medium">Download</span>
            </button>
          </div>
        </div>
      </div>

      {/* Transcript */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Full Transcript</h2>

        {/* Search */}
        <div className="sticky top-0 bg-white z-10 pb-4">
          <input
            type="text"
            placeholder="Search transcript..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {searchTerm && (
            <p className="text-sm text-gray-600 mt-2">
              Found {filteredParagraphs.length} of {transcriptData.paragraphs.length} segments
            </p>
          )}
        </div>

        {/* Transcript segments */}
        <div className="space-y-4 mt-4">
          {filteredParagraphs.map((paragraph, index) => (
            <div
              key={index}
              className="border-l-4 border-blue-500 pl-4 py-2"
            >
              <div className="flex items-center gap-3 mb-2">
                <span className="text-xs font-mono text-gray-500 bg-gray-50 px-2 py-1 rounded">
                  {formatTime(paragraph.start)}
                </span>
                <span className="text-sm font-medium text-gray-700">
                  {speakerMap[paragraph.speaker] || paragraph.speaker}
                </span>
              </div>
              <p className="text-gray-900 leading-relaxed">
                {paragraph.text}
              </p>
            </div>
          ))}
        </div>

        {filteredParagraphs.length === 0 && searchTerm && (
          <div className="text-center py-12">
            <p className="text-gray-500">No results found for &quot;{searchTerm}&quot;</p>
          </div>
        )}
      </div>
    </div>
  );
}
