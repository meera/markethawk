'use client';

import { MediaPlayerProvider } from './MediaPlayerContext';
import { TableOfContents } from './TableOfContents';
import { EarningsCallViewer } from './EarningsCallViewer';
import Link from 'next/link';

interface Props {
  company: string;
  companyName: string;
  call: any;
  summary: string;
  sentiment: any;
  chapters: any[];
  highlights: any[];
  financialMetrics: any[];
  mediaSignedUrl: string | null;
  transcriptData: any;
  speakers: any[];
  processedAt: string;
}

export function EarningsCallPageClient({
  company,
  companyName,
  call,
  summary,
  sentiment,
  chapters,
  highlights,
  financialMetrics,
  mediaSignedUrl,
  transcriptData,
  speakers,
  processedAt,
}: Props) {
  return (
    <MediaPlayerProvider>
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/companies/${company}`}
            className="text-gray-400 hover:text-gray-100 dark:text-gray-400 dark:hover:text-gray-100 mb-4 inline-block transition-colors"
          >
            ← Back to {companyName}
          </Link>
          <h1 className="text-4xl font-bold mb-2 text-white dark:text-white">{companyName}</h1>
          <div className="flex flex-wrap gap-4 text-gray-400 dark:text-gray-400">
            <span className="text-2xl font-medium">
              {call.symbol} | {call.quarter} {call.year}
            </span>
          </div>
        </div>

        {/* Sentiment & Key Themes (before video) */}
        {(sentiment.management_tone || (sentiment.key_themes && sentiment.key_themes.length > 0)) && (
          <div className="bg-gradient-to-r from-blue-900/30 to-indigo-900/30 dark:from-blue-900/30 dark:to-indigo-900/30 border border-blue-800/50 dark:border-blue-700/50 rounded-lg p-6 mb-8">
            {/* Sentiment */}
            {sentiment.management_tone && (
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-gray-200 dark:text-gray-200">Management Tone:</span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    sentiment.management_tone === 'bullish'
                      ? 'bg-green-900/40 text-green-300 dark:bg-green-900/40 dark:text-green-300'
                      : sentiment.management_tone === 'bearish'
                      ? 'bg-red-900/40 text-red-300 dark:bg-red-900/40 dark:text-red-300'
                      : 'bg-gray-800/60 text-gray-300 dark:bg-gray-800/60 dark:text-gray-300'
                  }`}
                >
                  {sentiment.management_tone.charAt(0).toUpperCase() + sentiment.management_tone.slice(1)}
                </span>

                {sentiment.confidence_level && (
                  <>
                    <span className="text-sm font-medium text-gray-200 dark:text-gray-200">Confidence:</span>
                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-900/40 text-blue-300 dark:bg-blue-900/40 dark:text-blue-300">
                      {sentiment.confidence_level.charAt(0).toUpperCase() + sentiment.confidence_level.slice(1)}
                    </span>
                  </>
                )}
              </div>
            )}

            {/* Key Themes */}
            {sentiment.key_themes && sentiment.key_themes.length > 0 && (
              <div className={sentiment.management_tone ? 'mt-4' : ''}>
                <h3 className="text-sm font-semibold text-gray-200 dark:text-gray-200 mb-2">Key Themes:</h3>
                <div className="flex flex-wrap gap-2">
                  {sentiment.key_themes.map((theme: string, index: number) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-gray-800/60 dark:bg-gray-800/60 border border-blue-700/40 dark:border-blue-700/40 rounded-full text-sm text-gray-200 dark:text-gray-200"
                    >
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - 2 columns */}
          <div className="lg:col-span-2 space-y-8">
            {/* Media Player */}
            <EarningsCallViewer mediaUrl={mediaSignedUrl} />

            {/* Link to Transcript Page */}
            {transcriptData && (
              <div className="bg-gray-800/50 dark:bg-gray-800/50 border border-gray-700/50 dark:border-gray-700/50 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold mb-2 text-white dark:text-white">Full Transcript</h2>
                    <p className="text-gray-300 dark:text-gray-300 text-sm">
                      Read the complete earnings call transcript with search and download options.
                    </p>
                  </div>
                  <Link
                    href={`/earnings/${company}/${call.quarter.toLowerCase()}-${call.year}/transcript`}
                    className="px-4 py-2 bg-primary hover:bg-primary-hover dark:bg-primary dark:hover:bg-primary-hover text-white rounded-lg transition-colors text-sm font-medium whitespace-nowrap"
                  >
                    View Transcript
                  </Link>
                </div>
              </div>
            )}

            {/* Executive Summary (after video) */}
            {summary && (
              <div className="bg-gray-800/50 dark:bg-gray-800/50 border border-gray-700/50 dark:border-gray-700/50 rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4 text-white dark:text-white">Executive Summary</h2>
                <p className="text-gray-200 dark:text-gray-200 leading-relaxed whitespace-pre-line">{summary}</p>
              </div>
            )}

            {/* Highlights */}
            {highlights.length > 0 && (
              <div className="bg-gray-800/50 dark:bg-gray-800/50 border border-gray-700/50 dark:border-gray-700/50 rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4 text-white dark:text-white">Key Highlights</h2>
                <div className="space-y-4">
                  {highlights.map((highlight: any, index: number) => (
                    <div key={index} className="border-l-4 border-yellow-500 dark:border-yellow-500 pl-4 py-2">
                      <div className="flex items-center gap-2 mb-1">
                        {highlight.category && (
                          <span className="text-xs font-medium px-2 py-1 bg-yellow-900/40 text-yellow-300 dark:bg-yellow-900/40 dark:text-yellow-300 rounded">
                            {highlight.category}
                          </span>
                        )}
                        {highlight.speaker && (
                          <span className="text-xs text-gray-400 dark:text-gray-400">— {highlight.speaker}</span>
                        )}
                      </div>
                      <p className="text-gray-200 dark:text-gray-200">{highlight.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-6">
            {/* Table of Contents */}
            <TableOfContents chapters={chapters} />

            {/* Financial Metrics */}
            {financialMetrics.length > 0 && (
              <div className="bg-gray-800/50 dark:bg-gray-800/50 border border-gray-700/50 dark:border-gray-700/50 rounded-lg p-6">
                <h2 className="text-lg font-semibold mb-4 text-white dark:text-white">Key Metrics</h2>
                <div className="space-y-3">
                  {financialMetrics.map((metric: any, index: number) => (
                    <div key={index} className="border-b border-gray-700/50 dark:border-gray-700/50 pb-3 last:border-b-0">
                      <p className="text-xs font-medium text-gray-400 dark:text-gray-400 mb-1">{metric.metric}</p>
                      <p className="text-lg font-bold text-white dark:text-white">{metric.value}</p>
                      {metric.change && (
                        <p
                          className={`text-xs ${
                            metric.change.startsWith('+') || metric.change.includes('up')
                              ? 'text-green-400 dark:text-green-400'
                              : metric.change.startsWith('-') || metric.change.includes('down')
                              ? 'text-red-400 dark:text-red-400'
                              : 'text-gray-400 dark:text-gray-400'
                          }`}
                        >
                          {metric.change}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Call Details */}
            <div className="bg-gray-800/50 dark:bg-gray-800/50 border border-gray-700/50 dark:border-gray-700/50 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4 text-white dark:text-white">Details</h2>
              <dl className="space-y-3">
                <div>
                  <dt className="text-xs font-medium text-gray-400 dark:text-gray-400">Company</dt>
                  <dd className="mt-1 text-sm text-white dark:text-white">{companyName}</dd>
                </div>
                <div>
                  <dt className="text-xs font-medium text-gray-400 dark:text-gray-400">Symbol</dt>
                  <dd className="mt-1 text-sm text-white dark:text-white">{call.symbol}</dd>
                </div>
                <div>
                  <dt className="text-xs font-medium text-gray-400 dark:text-gray-400">Period</dt>
                  <dd className="mt-1 text-sm text-white dark:text-white">
                    {call.quarter} {call.year}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-medium text-gray-400 dark:text-gray-400">Processed</dt>
                  <dd className="mt-1 text-sm text-white dark:text-white">{processedAt}</dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </MediaPlayerProvider>
  );
}
