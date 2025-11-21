#!/usr/bin/env python3
"""
Generate YouTube Shorts data from pipeline insights

Pipeline Step: generate_shorts
- Reads insights.raw.json (LLM-generated highlights optimized for shorts)
- Filters highlights for short-worthy content (12-20 seconds)
- Auto-detects speakers from transcript at each timestamp
- Extracts word-level timing for captions
- Generates speaker photo URLs
- Outputs structured JSON for each short

Output: shorts/ directory with:
  - short_1.json, short_2.json, ... (one per short)
  - metadata.json (list of all shorts with summary)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional


def get_speaker_at_timestamp(transcript: Dict, insights: Dict, timestamp: int) -> Optional[str]:
    """
    Auto-detect actual speaker from transcript at given timestamp

    Args:
        transcript: Full transcript.json from WhisperX
        insights: insights.raw.json with speaker mappings
        timestamp: Timestamp in seconds

    Returns:
        Speaker name or None if not found
    """
    # Create speaker map from insights
    speaker_map = {}
    for speaker in insights.get('insights', {}).get('speakers', []):
        speaker_map[speaker['speaker_id']] = speaker['speaker_name']

    # Find segment containing this timestamp
    for segment in transcript.get('segments', []):
        if segment.get('start', 0) <= timestamp <= segment.get('end', 0):
            speaker_id = segment.get('speaker', 'Unknown')
            return speaker_map.get(speaker_id, 'Unknown')

    return None


def extract_words_for_highlight(transcript: Dict, start_time: float, duration: float) -> List[Dict]:
    """
    Extract word-level timing for a highlight segment

    Args:
        transcript: Full transcript.json
        start_time: Start timestamp in seconds
        duration: Duration in seconds

    Returns:
        List of word objects with relative timing: [{"word": "Revenue", "start": 0.5, "end": 0.8}, ...]
    """
    end_time = start_time + duration
    words = []

    for segment in transcript.get('segments', []):
        seg_start = segment.get('start', 0)
        seg_end = segment.get('end', 0)

        # Check if segment overlaps with our time range
        if seg_start <= end_time and seg_end >= start_time:
            for word_obj in segment.get('words', []):
                word_start = word_obj.get('start', 0)
                word_end = word_obj.get('end', 0)

                # Check if word is within our time range
                if start_time <= word_start <= end_time:
                    # Convert to relative timing (offset from start_time)
                    words.append({
                        'word': word_obj.get('word', ''),
                        'start': word_start - start_time,
                        'end': word_end - start_time
                    })

    return words


def filter_highlights_for_shorts(highlights: List[Dict],
                                 min_duration: float = 12.0,
                                 max_duration: float = 20.0,
                                 max_shorts: int = 5) -> List[Dict]:
    """
    Filter and prioritize highlights for YouTube shorts

    Args:
        highlights: List of highlight objects from insights
        min_duration: Minimum duration in seconds (default: 12s)
        max_duration: Maximum duration in seconds (default: 20s)
        max_shorts: Maximum number of shorts to generate

    Returns:
        Filtered and sorted list of highlights
    """
    # Skip phrases that are not short-worthy
    skip_phrases = [
        "earnings call commenced",
        "welcome to",
        "good morning",
        "thank you for joining",
        "operator"
    ]

    filtered = []
    for h in highlights:
        # Skip very early timestamps (intro/boilerplate)
        if h.get('timestamp', 0) < 30:
            continue

        # Skip generic phrases
        text = h.get('text', '').lower()
        if any(phrase in text for phrase in skip_phrases):
            continue

        # Estimate duration (will be refined with actual audio)
        # Rough estimate: 150 words per minute = 2.5 words per second
        word_count = len(h.get('text', '').split())
        estimated_duration = word_count / 2.5

        # Filter by duration
        if min_duration <= estimated_duration <= max_duration:
            h['estimated_duration'] = estimated_duration
            filtered.append(h)

    # Sort by category priority
    category_priority = {
        'financial': 1,
        'strategy': 2,
        'product': 3,
        'guidance': 4,
        'qa': 5
    }

    sorted_highlights = sorted(
        filtered,
        key=lambda h: (category_priority.get(h.get('category', 'qa'), 10), h.get('timestamp', 0))
    )

    return sorted_highlights[:max_shorts]


def generate_speaker_photo_url(job_dir: Path, speaker_name: str, short_index: int) -> str:
    """
    Generate speaker photo URL

    Args:
        job_dir: Job directory path
        speaker_name: Speaker name
        short_index: Short index (1-based)

    Returns:
        Photo URL (either existing or placeholder path)
    """
    # Check if speaker photo already exists
    photo_path = job_dir / 'shorts' / f'speaker_{short_index}.jpg'
    if photo_path.exists():
        return f'http://192.168.1.101:8080/jobs/{job_dir.name}/shorts/speaker_{short_index}.jpg'

    # Return placeholder URL (will need to be added manually)
    return f'http://192.168.1.101:8080/jobs/{job_dir.name}/shorts/speaker_{short_index}.jpg'


def generate_shorts(job_yaml_path: str) -> Dict:
    """
    Pipeline step: Generate YouTube Shorts from insights

    Args:
        job_yaml_path: Path to job.yaml

    Returns:
        Status dict
    """
    import yaml

    job_file = Path(job_yaml_path)
    job_dir = job_file.parent

    # Load job config
    with open(job_file) as f:
        job = yaml.safe_load(f)

    # Check dependencies
    transcript_file = job_dir / 'transcripts' / 'transcript.json'
    insights_file = job_dir / 'insights.raw.json'

    if not transcript_file.exists():
        return {'status': 'error', 'message': 'transcript.json not found'}

    if not insights_file.exists():
        return {'status': 'error', 'message': 'insights.raw.json not found'}

    # Load data
    with open(transcript_file) as f:
        transcript = json.load(f)

    with open(insights_file) as f:
        insights_data = json.load(f)
        insights = insights_data.get('insights', {})

    # Get company info
    company_name = insights.get('company_name', 'Unknown')
    ticker = insights.get('company_ticker', 'UNK')

    # Filter highlights for shorts
    highlights = insights.get('highlights', [])
    selected_highlights = filter_highlights_for_shorts(highlights)

    if not selected_highlights:
        return {'status': 'error', 'message': 'No suitable highlights found for shorts'}

    # Create output directory
    shorts_dir = job_dir / 'shorts'
    shorts_dir.mkdir(exist_ok=True)

    # Generate shorts data
    shorts_metadata = []

    for i, highlight in enumerate(selected_highlights, start=1):
        timestamp = highlight.get('timestamp', 0)
        duration = highlight.get('estimated_duration', 15.0)

        # Auto-detect speaker
        actual_speaker = get_speaker_at_timestamp(transcript, insights_data, timestamp)
        speaker_name = actual_speaker if actual_speaker else highlight.get('speaker', 'Unknown')

        # Warn if speaker correction made
        if actual_speaker and actual_speaker != highlight.get('speaker'):
            print(f"⚠️  Short {i}: Speaker corrected from '{highlight.get('speaker')}' to '{actual_speaker}'")

        # Extract word-level timing
        words = extract_words_for_highlight(transcript, timestamp, duration)

        # Calculate actual duration from words
        if words:
            actual_duration = words[-1]['end']
            duration_frames = int(actual_duration * 30)  # 30fps
        else:
            actual_duration = duration
            duration_frames = int(duration * 30)

        # Generate speaker photo URL
        photo_url = generate_speaker_photo_url(job_dir, speaker_name, i)

        # Build short data
        short_data = {
            'highlight': {
                'text': highlight.get('text', ''),
                'speaker': speaker_name,
                'timestamp': timestamp,
                'duration': actual_duration,
                'category': highlight.get('category', 'financial')
            },
            'audioUrl': f'http://192.168.1.101:8080/jobs/{job_dir.name}/renders/rendered.mp4',
            'audioStartTime': timestamp,
            'speakerPhotoUrl': photo_url,
            'words': words,
            'companyName': company_name,
            'ticker': ticker,
            'durationInFrames': duration_frames
        }

        # Save individual short JSON
        short_file = shorts_dir / f'short_{i}.json'
        with open(short_file, 'w') as f:
            json.dump(short_data, f, indent=2)

        # Add to metadata
        shorts_metadata.append({
            'index': i,
            'text': highlight.get('text', ''),
            'speaker': speaker_name,
            'duration': actual_duration,
            'category': highlight.get('category', 'financial'),
            'file': f'short_{i}.json'
        })

        print(f"✓ Generated Short {i}: {speaker_name} - \"{highlight.get('text', '')[:60]}...\" ({actual_duration:.1f}s)")

    # Save metadata file
    metadata_file = shorts_dir / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump({
            'company_name': company_name,
            'ticker': ticker,
            'total_shorts': len(shorts_metadata),
            'shorts': shorts_metadata
        }, f, indent=2)

    print(f"\n✅ Generated {len(shorts_metadata)} YouTube Shorts")
    print(f"   Output: {shorts_dir}")

    return {
        'status': 'completed',
        'total_shorts': len(shorts_metadata),
        'output_dir': str(shorts_dir)
    }


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_shorts.py <job.yaml>")
        sys.exit(1)

    result = generate_shorts(sys.argv[1])

    if result['status'] == 'error':
        print(f"Error: {result['message']}")
        sys.exit(1)
