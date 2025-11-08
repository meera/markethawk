/**
 * ID Generation Utilities
 *
 * Stripe-like ID format: <prefix>_<humanreadable>_<4chars>
 *
 * Examples:
 * - comp_aapl_a1b2
 * - vid_aapl_q4_2024_x9z3
 * - avd_audio_yt_k8m2
 * - art_chart_revenue_a2b8
 */

const CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789';

/**
 * Generate random 4-character suffix
 */
function generateRandomSuffix(): string {
  let result = '';
  for (let i = 0; i < 4; i++) {
    result += CHARS.charAt(Math.floor(Math.random() * CHARS.length));
  }
  return result;
}

/**
 * Slugify a string for use in IDs
 */
function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

/**
 * Generate a company ID
 * @param ticker - Stock ticker (e.g., "AAPL")
 * @returns ID like "comp_aapl_a1b2"
 */
export function generateCompanyId(ticker: string): string {
  const slug = slugify(ticker);
  const suffix = generateRandomSuffix();
  return `comp_${slug}_${suffix}`;
}

/**
 * Generate a video ID
 * @param ticker - Stock ticker (e.g., "AAPL")
 * @param quarter - Quarter (e.g., "Q4")
 * @param year - Year (e.g., 2024)
 * @returns ID like "vid_aapl_q4_2024_x9z3"
 */
export function generateVideoId(ticker: string, quarter: string, year: number): string {
  const tickerSlug = slugify(ticker);
  const quarterSlug = slugify(quarter);
  const suffix = generateRandomSuffix();
  return `vid_${tickerSlug}_${quarterSlug}_${year}_${suffix}`;
}

/**
 * Generate a source ID (audio/video/document from internet)
 * @param type - Source type (e.g., "audio", "video", "document", "transcript")
 * @param description - Human-readable description (e.g., "yt", "sec10q", "transcript")
 * @returns ID like "avd_audio_yt_k8m2"
 */
export function generateSourceId(type: string, description: string): string {
  const typeSlug = slugify(type);
  const descSlug = slugify(description);
  const suffix = generateRandomSuffix();
  return `avd_${typeSlug}_${descSlug}_${suffix}`;
}

/**
 * Generate an artifact ID
 * @param type - Artifact type (e.g., "chart", "thumbnail", "audio_clip")
 * @param description - Human-readable description (e.g., "revenue", "main", "ceo")
 * @returns ID like "art_chart_revenue_a2b8"
 */
export function generateArtifactId(type: string, description: string): string {
  const typeSlug = slugify(type);
  const descSlug = slugify(description);
  const suffix = generateRandomSuffix();
  return `art_${typeSlug}_${descSlug}_${suffix}`;
}

/**
 * Generate a video view ID
 * @returns ID like "view_m8n9_p2q7"
 */
export function generateVideoViewId(): string {
  const suffix1 = generateRandomSuffix();
  const suffix2 = generateRandomSuffix();
  return `view_${suffix1}_${suffix2}`;
}

/**
 * Generate an engagement event ID
 * @returns ID like "eng_k4m8_x2y9"
 */
export function generateEngagementId(): string {
  const suffix1 = generateRandomSuffix();
  const suffix2 = generateRandomSuffix();
  return `eng_${suffix1}_${suffix2}`;
}

/**
 * Generate a click-through ID
 * @returns ID like "ct_a1b2_c3d4"
 */
export function generateClickThroughId(): string {
  const suffix1 = generateRandomSuffix();
  const suffix2 = generateRandomSuffix();
  return `ct_${suffix1}_${suffix2}`;
}

/**
 * Generate a video slug for URLs
 * @param ticker - Stock ticker (e.g., "AAPL")
 * @param quarter - Quarter (e.g., "Q4")
 * @param year - Year (e.g., 2024)
 * @returns Slug like "aapl-q4-2024"
 */
export function generateVideoSlug(ticker: string, quarter: string, year: number): string {
  const tickerSlug = ticker.toLowerCase();
  const quarterSlug = quarter.toLowerCase();
  return `${tickerSlug}-${quarterSlug}-${year}`;
}

/**
 * Parse a video ID to extract components
 * @param id - Video ID like "vid_aapl_q4_2024_x9z3"
 * @returns Object with ticker, quarter, year, suffix
 */
export function parseVideoId(id: string): {
  ticker: string;
  quarter: string;
  year: number;
  suffix: string;
} | null {
  const match = id.match(/^vid_([a-z0-9]+)_([a-z0-9]+)_(\d{4})_([a-z0-9]{4})$/);
  if (!match) return null;

  return {
    ticker: match[1],
    quarter: match[2],
    year: parseInt(match[3], 10),
    suffix: match[4],
  };
}

/**
 * Validate an ID format
 * @param id - ID to validate
 * @param prefix - Expected prefix (e.g., "comp", "vid", "avd")
 * @returns true if valid
 */
export function validateId(id: string, prefix: string): boolean {
  const pattern = new RegExp(`^${prefix}_[a-z0-9_]+_[a-z0-9]{4}$`);
  return pattern.test(id);
}

/**
 * Extract prefix from an ID
 * @param id - ID like "comp_aapl_a1b2"
 * @returns Prefix like "comp"
 */
export function extractPrefix(id: string): string | null {
  const match = id.match(/^([a-z]+)_/);
  return match ? match[1] : null;
}
