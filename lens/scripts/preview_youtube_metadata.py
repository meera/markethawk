#!/usr/bin/env python3
"""
Preview YouTube metadata (title, description, tags) without uploading

Usage:
    python preview_youtube_metadata.py /var/markethawk/jobs/{JOB_ID}/job.yaml
"""

import sys
from pathlib import Path

# Add parent to path
LENS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(LENS_DIR))

from scripts.upload_youtube import build_description


def preview_youtube_metadata(job_yaml_path: str):
    """
    Generate and display YouTube metadata without uploading

    Args:
        job_yaml_path: Path to job.yaml
    """
    import yaml
    import json

    job_file = Path(job_yaml_path)
    job_dir = job_file.parent

    # Load job config
    with open(job_file) as f:
        job_data = yaml.safe_load(f)

    # Load insights
    insights_file = job_data.get('processing', {}).get('extract_insights', {}).get('insights_file')
    insights = {}
    if insights_file and Path(insights_file).exists():
        with open(insights_file, 'r') as f:
            insights_data = json.load(f)
            insights = insights_data.get('insights', {})

    # Get metadata
    confirmed = job_data.get('processing', {}).get('confirm_metadata', {}).get('confirmed', {})
    match_result = job_data.get('processing', {}).get('match_company', {})
    company_match = match_result.get('company_match', {})

    name = confirmed.get('company') or company_match.get('name') or 'Company'
    ticker = confirmed.get('ticker') or company_match.get('symbol') or 'N/A'
    slug = company_match.get('slug') or ticker.lower()
    quarter = confirmed.get('quarter') or 'Q3-2025'

    # Generate title
    title = insights.get('youtube_title') or f"{name} ({ticker}) - {quarter} Earnings Call Analysis"

    # Generate description
    description = build_description(job_data)

    # Generate tags
    tags = [ticker, name, 'earnings call', 'financial analysis', quarter]
    if insights.get('sentiment'):
        tags.append('investor relations')

    print("=" * 80)
    print("YouTube Metadata Preview")
    print("=" * 80)
    print()

    print("TITLE:")
    print("-" * 80)
    print(title)
    print(f"({len(title)}/100 characters)")
    print()

    print("DESCRIPTION:")
    print("-" * 80)
    print(description)
    print()

    print("TAGS:")
    print("-" * 80)
    print(", ".join(tags))
    print()

    print("SLUG FOR URL:")
    print("-" * 80)
    print(f"https://markethawkeye.com/earnings/{slug}/{quarter.lower()}")
    print()

    print("=" * 80)
    print(f"Description character count: {len(description)}/5000")
    print("=" * 80)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python preview_youtube_metadata.py <job.yaml>")
        sys.exit(1)

    preview_youtube_metadata(sys.argv[1])
