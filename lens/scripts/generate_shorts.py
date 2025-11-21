#!/usr/bin/env python3
"""
Generate YouTube Shorts from Earnings Call Highlights

Creates props files for Remotion EarningsShort composition
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any


def extract_words_for_highlight(transcript: Dict, highlight: Dict, window_seconds: int = 5) -> List[Dict]:
    """
    Extract word-level timestamps for a highlight segment

    Args:
        transcript: Full transcript with word-level data
        highlight: Highlight dict with timestamp
        window_seconds: Extra seconds before/after highlight (for context)

    Returns:
        List of {word, start, end} dicts
    """
    start_time = highlight['timestamp']
    # Estimate duration based on text length (rough: 2-3 words per second)
    estimated_duration = len(highlight['text'].split()) / 2.5
    end_time = start_time + estimated_duration + window_seconds

    words = []
    segments = transcript.get('segments', [])

    for segment in segments:
        segment_start = segment.get('start', 0)
        segment_end = segment.get('end', 0)

        # Skip segments outside our time window
        if segment_end < start_time - window_seconds or segment_start > end_time:
            continue

        # Extract words from segment
        for word_obj in segment.get('words', []):
            word_start = word_obj.get('start', segment_start)
            word_end = word_obj.get('end', segment_start + 1)
            word_text = word_obj.get('word', '').strip()

            if start_time - window_seconds <= word_start <= end_time:
                # Normalize timestamp to start from 0
                words.append({
                    'word': word_text,
                    'start': word_start - start_time,
                    'end': word_end - start_time
                })

    return words


def generate_shorts(job_dir: Path, max_shorts: int = 5):
    """
    Generate shorts props files from job data

    Args:
        job_dir: Path to job directory
        max_shorts: Maximum number of shorts to generate
    """
    # Load insights
    insights_file = job_dir / 'insights.raw.json'
    if not insights_file.exists():
        raise FileNotFoundError(f"Insights file not found: {insights_file}")

    with open(insights_file, 'r') as f:
        insights_data = json.load(f)
        insights = insights_data.get('insights', {})

    # Load transcript
    transcript_file = job_dir / 'transcripts' / 'transcript.json'
    if not transcript_file.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_file}")

    with open(transcript_file, 'r') as f:
        transcript = json.load(f)

    # Load job.yaml for metadata
    import yaml
    job_yaml = job_dir / 'job.yaml'
    with open(job_yaml, 'r') as f:
        job_data = yaml.safe_load(f)

    # Get company info
    confirmed = job_data.get('processing', {}).get('confirm_metadata', {}).get('confirmed', {})
    company_match = job_data.get('processing', {}).get('match_company', {}).get('company_match', {})

    company_name = confirmed.get('company') or company_match.get('name', 'Company')
    ticker = confirmed.get('ticker') or company_match.get('symbol', 'TICKER')
    job_id = job_data.get('job_id')

    # Media server URL
    media_server = 'http://192.168.1.101:8080'

    # Create shorts directory
    shorts_dir = job_dir / 'shorts'
    shorts_dir.mkdir(exist_ok=True, mode=0o755)

    # Get highlights (prioritize financial and guidance)
    highlights = insights.get('highlights', [])

    # Sort by category priority: financial > guidance > strategy > product > qa
    category_priority = {'financial': 1, 'guidance': 2, 'strategy': 3, 'product': 4, 'qa': 5}
    highlights.sort(key=lambda h: category_priority.get(h.get('category', 'qa'), 10))

    # Generate props for top N highlights
    generated_count = 0
    for i, highlight in enumerate(highlights[:max_shorts]):
        # Extract words for this highlight
        words = extract_words_for_highlight(transcript, highlight)

        if not words:
            print(f"⚠️  Skipping highlight {i+1}: No words found in transcript")
            continue

        # Calculate duration from words
        duration = words[-1]['end'] if words else 30
        duration_frames = int(duration * 30)  # 30 fps

        # Audio URL with time fragment (from rendered video, not source audio)
        audio_start = highlight['timestamp']
        audio_end = audio_start + duration
        audio_url = f"{media_server}/jobs/{job_id}/renders/rendered.mp4#t={audio_start},{audio_end}"

        # Speaker photo placeholder (user will replace)
        speaker_photo_url = f"{media_server}/jobs/{job_id}/shorts/speaker_{i+1}.jpg"

        # Create props
        props = {
            'highlight': {
                'text': highlight['text'],
                'speaker': highlight.get('speaker', 'Speaker'),
                'timestamp': highlight['timestamp'],
                'duration': duration,
                'category': highlight.get('category', 'qa')
            },
            'audioUrl': audio_url,
            'speakerPhotoUrl': speaker_photo_url,
            'words': words,
            'companyName': company_name,
            'ticker': ticker,
            'durationInFrames': duration_frames
        }

        # Save props file
        props_file = shorts_dir / f'short_{i+1}_props.json'
        with open(props_file, 'w') as f:
            json.dump(props, f, indent=2)

        print(f"✅ Created short {i+1}: {highlight['text'][:50]}...")
        print(f"   Speaker: {highlight.get('speaker', 'Unknown')}")
        print(f"   Duration: {duration:.1f}s ({duration_frames} frames)")
        print(f"   Category: {highlight.get('category', 'unknown')}")
        print(f"   Props: {props_file}")
        print(f"   ⚠️  Add speaker photo: {shorts_dir}/speaker_{i+1}.jpg")
        print()

        generated_count += 1

    print(f"✅ Generated {generated_count} shorts props files")
    print(f"📁 Output directory: {shorts_dir}")
    print()
    print("Next steps:")
    print(f"1. Add speaker photos to {shorts_dir}/ (speaker_1.jpg, speaker_2.jpg, etc.)")
    print(f"2. Preview in Remotion Studio: cd ~/markethawk/studio && npm run start")
    print(f"3. Render: npx remotion render EarningsShort {shorts_dir}/short_1.mp4 --props {shorts_dir}/short_1_props.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate YouTube Shorts from earnings highlights")
    parser.add_argument("job_dir", help="Path to job directory")
    parser.add_argument("--max-shorts", type=int, default=5, help="Maximum number of shorts to generate")

    args = parser.parse_args()

    generate_shorts(Path(args.job_dir), args.max_shorts)
