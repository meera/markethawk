import { getEarningsCallBySlug } from '../../../actions';
import { getTranscriptFromR2 } from '../../../components/transcript-actions';
import { TranscriptPageClient } from './TranscriptPageClient';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';

// Helper to parse quarter-year slug (e.g., "q3-2025" -> { quarter: "Q3", year: 2025 })
function parseQuarterYear(slug: string): { quarter: string; year: number } | null {
  const match = slug.match(/^q(\d)-(\d{4})$/i);
  if (!match) return null;
  return {
    quarter: `Q${match[1]}`,
    year: parseInt(match[2], 10),
  };
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ company: string; 'quarter-year': string }>;
}): Promise<Metadata> {
  const { company, 'quarter-year': quarterYear } = await params;

  const parsed = parseQuarterYear(quarterYear);
  if (!parsed) {
    return {
      title: 'Transcript Not Found | MarketHawk',
    };
  }

  const { quarter, year } = parsed;
  const result = await getEarningsCallBySlug(company, quarter, year);

  if (!result.success || !result.data) {
    return {
      title: 'Transcript Not Found | MarketHawk',
    };
  }

  const call = result.data;
  const insights = call.insights || {};
  const companyName = call.companyName || insights.company_name || call.symbol;

  return {
    title: `${companyName} ${quarter} ${year} Earnings Call Transcript | MarketHawk`,
    description: `Full transcript of ${companyName}'s ${quarter} ${year} earnings call with search functionality.`,
  };
}

export default async function TranscriptPage({
  params,
}: {
  params: Promise<{ company: string; 'quarter-year': string }>;
}) {
  const { company, 'quarter-year': quarterYear } = await params;

  // Parse quarter and year from slug
  const parsed = parseQuarterYear(quarterYear);
  if (!parsed) {
    notFound();
  }

  const { quarter, year } = parsed;

  // Use company slug for lookup
  const result = await getEarningsCallBySlug(company, quarter, year);

  if (!result.success || !result.data) {
    notFound();
  }

  const call = result.data;
  const transcripts = call.transcripts || {};
  const insights = call.insights || {};

  // Fetch transcript paragraphs from R2
  let transcriptData = null;
  let speakers = [];

  if (transcripts.paragraphs_url) {
    const r2Path = transcripts.paragraphs_url.replace(/^r2:\/\/[^/]+\//, '');
    const transcriptResult = await getTranscriptFromR2(r2Path);

    if (transcriptResult.success) {
      transcriptData = transcriptResult.data;
    }
  }

  // Get speakers from insights
  if (insights.speakers) {
    speakers = insights.speakers;
  }

  const companyName = call.companyName || insights.company_name || 'Unknown Company';

  return (
    <TranscriptPageClient
      company={company}
      companyName={companyName}
      call={call}
      transcriptData={transcriptData}
      speakers={speakers}
      quarterYear={quarterYear}
    />
  );
}
