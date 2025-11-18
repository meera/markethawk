import { getEarningsCall } from '../actions';
import { getSignedUrlForR2Media, getR2PathFromMetadata } from '@/lib/r2';
import { notFound } from 'next/navigation';
import Link from 'next/link';

export const metadata = {
  title: 'Earnings Call | MarketHawk',
};

export default async function EarningsCallDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const result = await getEarningsCall(id);

  if (!result.success || !result.data) {
    notFound();
  }

  const call = result.data;
  const metadata = call.metadata || {};
  const transcripts = call.transcripts || {};
  const insights = call.insights || {};

  // Get audio URL from R2
  let audioSignedUrl: string | null = null;
  let r2Key: string | null = null;

  // Parse media_url: r2://markeyhawkeye/path/to/audio.mp3
  if (call.mediaUrl && call.mediaUrl.startsWith('r2://')) {
    const urlParts = call.mediaUrl.replace('r2://', '').split('/');
    const bucket = urlParts[0]; // markeyhawkeye
    r2Key = urlParts.slice(1).join('/'); // path/to/audio.mp3

    try {
      audioSignedUrl = await getSignedUrlForR2Media(r2Key);
    } catch (error) {
      console.error('Failed to get signed URL:', error);
    }
  }

  const companyName = metadata.company_name || 'Unknown Company';
  const companySlug = metadata.company_slug || null;
  const processedAt = metadata.processed_at
    ? new Date(metadata.processed_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : 'Unknown date';

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/earnings"
          className="text-blue-600 hover:underline mb-4 inline-block"
        >
          ← Back to all earnings calls
        </Link>
        <h1 className="text-3xl font-bold mb-2">{companyName}</h1>
        <div className="flex flex-wrap gap-4 text-gray-600">
          <span className="font-medium text-lg">
            {call.symbol} | {call.quarter} {call.year}
          </span>
        </div>
      </div>

      {/* Audio Player */}
      {audioSignedUrl ? (
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Audio</h2>
          <audio
            controls
            className="w-full"
            preload="metadata"
            src={audioSignedUrl}
          >
            Your browser does not support the audio element.
          </audio>
          <p className="text-sm text-gray-500 mt-2">
            Audio extracted from earnings call video
          </p>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
          <p className="text-yellow-800">Audio file not available</p>
          {call.mediaUrl && (
            <p className="text-sm text-yellow-600 mt-1">
              Media URL: {call.mediaUrl}
            </p>
          )}
          {r2Key && (
            <p className="text-sm text-yellow-600 mt-1">
              R2 Key: {r2Key}
            </p>
          )}
        </div>
      )}

      {/* Metadata */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Details</h2>
        <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">Company</dt>
            <dd className="mt-1 text-sm text-gray-900">{companyName}</dd>
          </div>

          <div>
            <dt className="text-sm font-medium text-gray-500">Symbol</dt>
            <dd className="mt-1 text-sm text-gray-900">{call.symbol}</dd>
          </div>

          <div>
            <dt className="text-sm font-medium text-gray-500">CIK</dt>
            <dd className="mt-1 text-sm text-gray-900">{call.cikStr}</dd>
          </div>

          <div>
            <dt className="text-sm font-medium text-gray-500">Quarter</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {call.quarter} {call.year}
            </dd>
          </div>

          <div>
            <dt className="text-sm font-medium text-gray-500">Processed</dt>
            <dd className="mt-1 text-sm text-gray-900">{processedAt}</dd>
          </div>

          {metadata.youtube_id && (
            <div className="md:col-span-2">
              <dt className="text-sm font-medium text-gray-500">Source</dt>
              <dd className="mt-1">
                <a
                  href={`https://www.youtube.com/watch?v=${metadata.youtube_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                >
                  View on YouTube →
                </a>
              </dd>
            </div>
          )}
        </dl>

        {/* Transcripts & Insights Section */}
        {(transcripts || insights) && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Transcripts & Insights</h3>
            <div className="space-y-3">
              {transcripts && transcripts.r2_url && (
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded">
                  <div>
                    <p className="font-medium text-sm">Transcript</p>
                    <p className="text-xs text-gray-600">
                      {transcripts.word_count} segments • {transcripts.speakers} speakers
                    </p>
                  </div>
                  <a
                    href={transcripts.r2_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline"
                  >
                    Download JSON →
                  </a>
                </div>
              )}
              {insights && insights.r2_url && (
                <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                  <div>
                    <p className="font-medium text-sm">Insights</p>
                    <p className="text-xs text-gray-600">
                      {insights.metrics_count} metrics • {insights.highlights_count} highlights
                    </p>
                  </div>
                  <a
                    href={insights.r2_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-green-600 hover:underline"
                  >
                    Download JSON →
                  </a>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
