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

    Args:
        highlight: Highlight dict with 'text' field

    Returns:
        List of keywords to search for
    """
    text_clean = re.sub(r'[^\w\s]', '', highlight.get('text', '').lower())
    words = text_clean.split()

    # Remove stop words and keep substantial words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'was', 'are'}
    keywords = [w for w in words if w not in stop_words and len(w) > 3]

    # Take first 5 most distinctive words
    return keywords[:5]


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

    Searches within +window_seconds of LLM suggestion for first keyword match.

    Args:
        llm_timestamp: Timestamp suggested by LLM (from paragraph-level)
        keywords: Keywords to search for
        transcript_data: Full transcript with word-level data
        window_seconds: Search window in seconds (forward from llm_timestamp)

    Returns:
        Refined timestamp (or original if no match found)
    """
    if not keywords:
        return llm_timestamp

    # Get all word-level data from segments
    segments = transcript_data.get("segments", [])

    # Search window: llm_timestamp to llm_timestamp + window_seconds
    search_start = llm_timestamp
    search_end = llm_timestamp + window_seconds

    # Build list of all words with timestamps in search window
    # Separate number matches (higher priority) from text matches
    number_matches = []
    text_matches = []

    for segment in segments:
        segment_start = segment.get("start", 0)
        segment_end = segment.get("end", 0)

        # Skip segments outside search window
        if segment_end < search_start or segment_start > search_end:
            continue

        # Check word-level data if available
        words = segment.get("words", [])
        if words:
            for word_obj in words:
                word_text = word_obj.get("word", "").lower().strip()
                word_start = word_obj.get("start", segment_start)

                # Check if word is in search window
                if search_start <= word_start <= search_end:
                    # Check if word matches any keyword
                    for keyword in keywords:
                        # Skip single-character keywords (too generic: 'a', 'i')
                        if len(keyword) <= 1:
                            continue

                        # Skip very short words unless they're numbers
                        if len(keyword) <= 2 and not is_number_keyword(keyword):
                            continue

                        # Require better match quality
                        is_match = False
                        if len(word_text) >= 3 and len(keyword) >= 3:
                            # For longer words, check if keyword is in word or vice versa
                            is_match = keyword in word_text or word_text in keyword
                        elif keyword == word_text:
                            # For short words, require exact match
                            is_match = True

                        if is_match:
                            match_obj = {
                                'word': word_text,
                                'keyword': keyword,
                                'timestamp': word_start
                            }

                            # Prioritize number keywords
                            if is_number_keyword(keyword):
                                number_matches.append(match_obj)
                            else:
                                text_matches.append(match_obj)

    # Prefer number matches first (more specific)
    all_matches = number_matches + text_matches

    # Return first match timestamp + 0.5s buffer
    if all_matches:
        first_match = min(all_matches, key=lambda x: x['timestamp'])
        refined_timestamp = first_match['timestamp'] + 0.5
        match_type = "number" if first_match in number_matches else "text"
        print(f"    ✓ {llm_timestamp}s → {refined_timestamp:.1f}s (matched '{first_match['word']}' [{match_type}])")
        return refined_timestamp

    # No match found, return original
    print(f"    ⚠ {llm_timestamp}s → no match found, keeping original")
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
