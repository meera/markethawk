#!/usr/bin/env python3
"""
Refine timestamps in insights using word-level transcript data

Searches word-level transcript within +window_seconds of LLM-suggested
timestamps to find exact moment keywords are spoken.

TODO: Improve number matching
- Add number-to-word conversion: "30" → "thirty", "79" → "seventy nine"
- Numbers in transcript are spoken as words, not digits
- Examples: "$30 billion" spoken as "thirty billion", "3.5" as "three point five"
- Expand stop words: add "the", "this", "that", "with", "from"
- Fix incorrect matches on common words
"""

import json
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any


def extract_keywords_from_metric(metric: Dict) -> List[str]:
    """
    Extract searchable keywords from a financial metric

    Args:
        metric: Metric dict with 'metric', 'value', 'change' fields

    Returns:
        List of keywords to search for in word-level transcript
    """
    keywords = []

    # Extract metric name words (e.g., "Paramount Plus" -> ["paramount", "plus"])
    metric_words = re.findall(r'\w+', metric.get('metric', '').lower())
    keywords.extend(metric_words)

    # Extract value components (e.g., "$94.9B" -> ["94", "billion"])
    value_clean = re.sub(r'[$,%]', '', metric.get('value', '').lower())
    value_words = re.findall(r'\w+', value_clean)
    keywords.extend(value_words)

    # Extract change keywords if present (e.g., "+24% YoY" -> ["24", "percent"])
    if metric.get('change'):
        change_clean = re.sub(r'[+\-%]', '', metric['change'].lower())
        change_words = re.findall(r'\w+', change_clean)
        keywords.extend(change_words)

    # Remove very common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    keywords = [k for k in keywords if k not in stop_words and len(k) > 1]

    return keywords


def extract_keywords_from_highlight(highlight: Dict) -> List[str]:
    """
    Extract searchable keywords from a highlight

    Prioritizes:
    1. Numbers (most distinctive - "200", "2.9", "4000")
    2. Long words (6+ chars - more unique)
    3. Medium words (4-5 chars)

    Args:
        highlight: Highlight dict with 'text' field

    Returns:
        List of keywords to search for (up to 8)
    """
    text = highlight.get('text', '').lower()

    # Extract numbers first (very distinctive)
    numbers = re.findall(r'\d+(?:\.\d+)?', text)

    # Clean text and extract words
    text_clean = re.sub(r'[^\w\s]', '', text)
    words = text_clean.split()

    # Expanded stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'is', 'was', 'are', 'its', 'with', 'from', 'this', 'that', 'now',
        'can', 'run', 'part', 'per', 'new', 'hps', 'has', 'have', 'been', 'were',
        'will', 'would', 'could', 'should', 'than', 'then', 'also', 'just', 'more',
        'most', 'some', 'such', 'into', 'over', 'only', 'year', 'years'
    }

    # Filter words: exclude stop words and short words
    content_words = [w for w in words if w not in stop_words and len(w) >= 4]

    # Prioritize longer words (more distinctive)
    long_words = [w for w in content_words if len(w) >= 6]
    medium_words = [w for w in content_words if 4 <= len(w) < 6]

    # Build keyword list: numbers first, then long words, then medium words
    keywords = numbers[:3] + long_words[:4] + medium_words[:3]

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            unique_keywords.append(k)

    return unique_keywords[:8]


def is_number_keyword(keyword: str) -> bool:
    """Check if keyword is a number or contains digits"""
    return any(c.isdigit() for c in keyword) or keyword in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


def refine_timestamp_with_words(
    llm_timestamp: float,
    keywords: List[str],
    transcript_data: Dict,
    window_seconds: int = 30
) -> float:
    """
    Refine LLM-suggested timestamp using word-level transcript data

    Strategy: Find where multiple keywords CLUSTER together within a short time span.
    This is more robust than single-keyword matching because:
    - Common words like "quarter", "revenue" appear many times
    - The actual highlight location has multiple keywords near each other

    Process:
    1. Find all occurrences of each keyword in the transcript
    2. Group matches into time clusters (within 15 seconds of each other)
    3. Score clusters by: number of distinct keywords matched
    4. Return the start of the highest-scoring cluster

    Args:
        llm_timestamp: Timestamp suggested by LLM (fallback if no cluster found)
        keywords: Keywords to search for
        transcript_data: Full transcript with word-level data
        window_seconds: Cluster window size in seconds (default 30)

    Returns:
        Refined timestamp (start of best keyword cluster, or original if no match)
    """
    if not keywords:
        return llm_timestamp

    CLUSTER_WINDOW = 15  # Seconds - keywords must appear within this window to cluster

    # Get all word-level data from segments
    segments = transcript_data.get("segments", [])

    # Collect ALL matches for each keyword
    all_matches = []

    for segment in segments:
        segment_start = segment.get("start", 0)

        words = segment.get("words", [])
        if words:
            for word_obj in words:
                word_text = word_obj.get("word", "").lower().strip()
                word_start = word_obj.get("start", segment_start)

                for keyword in keywords:
                    if len(keyword) <= 2:
                        continue

                    # Require EXACT match or strong substring match
                    is_match = False
                    # For longer keywords (5+ chars), allow substring
                    if len(keyword) >= 5 and len(word_text) >= 5:
                        is_match = keyword in word_text or word_text in keyword
                    # For shorter keywords, require exact match
                    elif keyword == word_text:
                        is_match = True
                    # Also match if word starts with keyword (e.g., "consecutive" matches "consecutively")
                    elif len(keyword) >= 4 and word_text.startswith(keyword[:4]):
                        is_match = True

                    if is_match:
                        all_matches.append({
                            'word': word_text,
                            'keyword': keyword,
                            'timestamp': word_start,
                            'is_number': is_number_keyword(keyword)
                        })

    if not all_matches:
        print(f"    ⚠ {llm_timestamp}s → no matches found, keeping original")
        return float(llm_timestamp)

    # Sort matches by timestamp
    all_matches.sort(key=lambda x: x['timestamp'])

    # Find clusters: groups of matches within CLUSTER_WINDOW of each other
    clusters = []
    current_cluster = [all_matches[0]]

    for match in all_matches[1:]:
        # If this match is within CLUSTER_WINDOW of the cluster start, add to cluster
        if match['timestamp'] - current_cluster[0]['timestamp'] <= CLUSTER_WINDOW:
            current_cluster.append(match)
        else:
            # Save current cluster and start new one
            clusters.append(current_cluster)
            current_cluster = [match]

    clusters.append(current_cluster)  # Don't forget the last cluster

    # Score clusters by number of DISTINCT keywords matched
    def score_cluster(cluster):
        distinct_keywords = set(m['keyword'] for m in cluster)
        has_number = any(m['is_number'] for m in cluster)
        # Bonus for number matches (more specific)
        return len(distinct_keywords) + (0.5 if has_number else 0)

    # Strategy: Use a tiered approach
    # 1. If there's a STRONG cluster (3+ keywords), take the first one
    # 2. Otherwise, take the cluster with highest score (to avoid false positives from weak early matches)

    scored_clusters = [(c, score_cluster(c)) for c in clusters]
    strong_clusters = [(c, s) for c, s in scored_clusters if s >= 3]
    good_clusters = [(c, s) for c, s in scored_clusters if s >= 2]

    if strong_clusters:
        # Take the first strong cluster (earliest, with 3+ keywords)
        best_cluster, best_score = strong_clusters[0]
        refined_timestamp = best_cluster[0]['timestamp'] + 0.5
        distinct = set(m['keyword'] for m in best_cluster)
        print(f"    ✓ {llm_timestamp}s → {refined_timestamp:.1f}s (strong cluster: {len(distinct)} keywords: {list(distinct)[:3]})")
        return refined_timestamp

    if good_clusters:
        # No strong cluster - take the BEST (highest score) cluster to avoid false positives
        best_cluster, best_score = max(good_clusters, key=lambda x: x[1])
        refined_timestamp = best_cluster[0]['timestamp'] + 0.5
        distinct = set(m['keyword'] for m in best_cluster)
        print(f"    ✓ {llm_timestamp}s → {refined_timestamp:.1f}s (best cluster: {len(distinct)} keywords: {list(distinct)[:3]})")
        return refined_timestamp

    # Fallback: if no good cluster, try to find a number keyword match
    number_matches = [m for m in all_matches if m['is_number']]
    if number_matches:
        first_number = min(number_matches, key=lambda x: x['timestamp'])
        refined_timestamp = first_number['timestamp'] + 0.5
        print(f"    ✓ {llm_timestamp}s → {refined_timestamp:.1f}s (number match: '{first_number['word']}')")
        return refined_timestamp

    # No good cluster or number match - keep original
    print(f"    ⚠ {llm_timestamp}s → weak matches only, keeping original")
    return float(llm_timestamp)


def refine_job_timestamps(
    job_yaml_path: Path,
    transcript_path: Path,
    window_seconds: int = 30
) -> Dict[str, Any]:
    """
    Refine all timestamps in a job's insights using word-level data

    Args:
        job_yaml_path: Path to job.yaml
        transcript_path: Path to transcript.json
        window_seconds: Search window in seconds

    Returns:
        Dictionary with refinement statistics
    """
    print(f"\n🔍 Refining timestamps with word-level data...")
    print(f"   Window: +{window_seconds}s from LLM suggestion\n")

    # Load job.yaml
    with open(job_yaml_path, 'r') as f:
        job_data = yaml.safe_load(f)

    # Load transcript
    with open(transcript_path, 'r') as f:
        transcript_data = json.load(f)

    # Get insights from job
    insights = job_data.get('processing', {}).get('insights', {})

    # Track statistics
    stats = {
        'metrics_refined': 0,
        'metrics_unchanged': 0,
        'highlights_refined': 0,
        'highlights_unchanged': 0,
        'search_window_seconds': window_seconds
    }

    # Refine financial metrics
    metrics = insights.get('financial_metrics', [])
    if metrics:
        print(f"Refining {len(metrics)} financial metrics:")
        for metric in metrics:
            keywords = extract_keywords_from_metric(metric)
            original_ts = metric.get('timestamp', 0)

            preview = f"{metric.get('metric', 'Unknown')}: {metric.get('value', '')}"
            print(f"  {preview}")
            print(f"    Keywords: {', '.join(keywords[:3])}")

            refined_ts = refine_timestamp_with_words(
                original_ts,
                keywords,
                transcript_data,
                window_seconds
            )

            if refined_ts != original_ts:
                metric['timestamp'] = refined_ts
                stats['metrics_refined'] += 1
            else:
                stats['metrics_unchanged'] += 1
        print()

    # Refine highlights
    highlights = insights.get('highlights', [])
    if highlights:
        print(f"Refining {len(highlights)} highlights:")
        for highlight in highlights:
            keywords = extract_keywords_from_highlight(highlight)
            original_ts = highlight.get('timestamp', 0)

            preview = highlight.get('text', '')[:60]
            if len(highlight.get('text', '')) > 60:
                preview += "..."
            print(f"  {preview}")
            print(f"    Keywords: {', '.join(keywords[:3])}")

            refined_ts = refine_timestamp_with_words(
                original_ts,
                keywords,
                transcript_data,
                window_seconds
            )

            if refined_ts != original_ts:
                highlight['timestamp'] = refined_ts
                stats['highlights_refined'] += 1
            else:
                stats['highlights_unchanged'] += 1
        print()

    # Save updated job.yaml
    with open(job_yaml_path, 'w') as f:
        yaml.safe_dump(job_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"✅ Timestamp refinement complete!")
    print(f"   Metrics: {stats['metrics_refined']} refined, {stats['metrics_unchanged']} unchanged")
    print(f"   Highlights: {stats['highlights_refined']} refined, {stats['highlights_unchanged']} unchanged\n")

    return stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Refine timestamps in job.yaml using word-level transcript")
    parser.add_argument("job_yaml", help="Path to job.yaml")
    parser.add_argument("--transcript", help="Path to transcript.json (default: auto-detect from job.yaml)")
    parser.add_argument("--window", type=int, default=30, help="Search window in seconds (default: 30)")

    args = parser.parse_args()

    job_yaml_path = Path(args.job_yaml)

    # Auto-detect transcript path if not provided
    if args.transcript:
        transcript_path = Path(args.transcript)
    else:
        # Load job to get transcript path
        with open(job_yaml_path, 'r') as f:
            job_data = yaml.safe_load(f)
        transcript_file = job_data.get('processing', {}).get('transcribe', {}).get('output', {}).get('transcript_file')
        if not transcript_file:
            print("❌ Error: Could not find transcript path in job.yaml")
            print("   Use --transcript to specify path manually")
            exit(1)
        transcript_path = Path(transcript_file)

    if not transcript_path.exists():
        print(f"❌ Error: Transcript not found: {transcript_path}")
        exit(1)

    stats = refine_job_timestamps(
        job_yaml_path=job_yaml_path,
        transcript_path=transcript_path,
        window_seconds=args.window
    )

    print("Stats:", stats)
