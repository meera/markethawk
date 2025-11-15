#!/usr/bin/env python3
"""
Download YouTube videos to cache using Rapid API

Reads video IDs from a text file and downloads them to /var/markethawk/_downloads/
using the Rapid API (same as batch processor).

Usage:
    python lens/scripts/download_to_cache_pipeline.py videos.txt [--workers 3] [--skip-existing]

Configuration:
    Create a YAML config file with pipeline settings (optional)

Examples:
    # Download all videos from file
    python lens/scripts/download_to_cache_pipeline.py nvidia_videos.txt

    # Use 5 parallel workers
    python lens/scripts/download_to_cache_pipeline.py nvidia_videos.txt --workers 5

    # Skip videos already in cache
    python lens/scripts/download_to_cache_pipeline.py nvidia_videos.txt --skip-existing

    # Use custom config
    python lens/scripts/download_to_cache_pipeline.py nvidia_videos.txt --config download_config.yaml
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json

# Add lens directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.download_source import download_video


class DownloadPipeline:
    """Pipeline for downloading YouTube videos to cache"""

    def __init__(self, config: Dict):
        """
        Initialize pipeline

        Args:
            config: Pipeline configuration dictionary
        """
        self.config = config
        self.cache_dir = Path(config.get('cache_dir', '/var/markethawk/_downloads'))
        self.workers = config.get('workers', 3)
        self.skip_existing = config.get('skip_existing', True)  # Default: skip cached videos

        self.stats = {
            'total': 0,
            'downloaded': 0,
            'cached': 0,
            'failed': 0,
            'errors': []
        }

    def is_cached(self, video_id: str) -> bool:
        """
        Check if video is already cached

        Args:
            video_id: YouTube video ID

        Returns:
            True if video is cached
        """
        video_cache_dir = self.cache_dir / video_id
        video_file = video_cache_dir / 'source.mp4'
        metadata_file = video_cache_dir / 'metadata.json'

        return video_file.exists() and metadata_file.exists()

    def download_single_video(self, video_id: str) -> Dict:
        """
        Download single video

        Args:
            video_id: YouTube video ID

        Returns:
            Result dictionary
        """
        youtube_url = f'https://www.youtube.com/watch?v={video_id}'

        # Check cache
        if self.skip_existing and self.is_cached(video_id):
            return {
                'video_id': video_id,
                'status': 'cached',
                'message': 'Already in cache'
            }

        # Download
        try:
            result = download_video(youtube_url, str(self.cache_dir))
            return {
                'video_id': video_id,
                'status': 'downloaded',
                'message': 'Successfully downloaded',
                'file_path': result['file_path'],
                'title': result.get('title', 'Unknown')
            }
        except Exception as e:
            return {
                'video_id': video_id,
                'status': 'failed',
                'message': str(e)
            }

    def process_video_list(self, video_ids: List[str]):
        """
        Process list of video IDs

        Args:
            video_ids: List of YouTube video IDs
        """
        self.stats['total'] = len(video_ids)

        print(f"\n{'='*60}")
        print(f"Download Pipeline")
        print(f"{'='*60}")
        print(f"Videos: {len(video_ids)}")
        print(f"Workers: {self.workers}")
        print(f"Cache: {self.cache_dir}")
        print(f"Skip existing: {self.skip_existing}")
        print(f"{'='*60}\n")

        # Download with thread pool
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.download_single_video, video_id): video_id
                for video_id in video_ids
            }

            # Process results as they complete
            for future in as_completed(futures):
                video_id = futures[future]

                try:
                    result = future.result()

                    if result['status'] == 'downloaded':
                        self.stats['downloaded'] += 1
                        print(f"✓ [{self.stats['downloaded']}/{self.stats['total']}] Downloaded: {result['video_id']} - {result.get('title', '')}")
                    elif result['status'] == 'cached':
                        self.stats['cached'] += 1
                        print(f"⊘ [{self.stats['cached']}/{self.stats['total']}] Cached: {result['video_id']}")
                    else:
                        self.stats['failed'] += 1
                        self.stats['errors'].append({
                            'video_id': video_id,
                            'error': result['message']
                        })
                        print(f"✗ [{self.stats['failed']}/{self.stats['total']}] Failed: {result['video_id']} - {result['message']}")

                except Exception as e:
                    self.stats['failed'] += 1
                    self.stats['errors'].append({
                        'video_id': video_id,
                        'error': str(e)
                    })
                    print(f"✗ Failed: {video_id} - {e}")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print pipeline summary"""
        print(f"\n{'='*60}")
        print(f"Pipeline Complete")
        print(f"{'='*60}")
        print(f"Total: {self.stats['total']}")
        print(f"Downloaded: {self.stats['downloaded']}")
        print(f"Cached: {self.stats['cached']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"{'='*60}\n")

        if self.stats['errors']:
            print(f"Errors:")
            for error in self.stats['errors'][:10]:  # Show first 10
                print(f"  - {error['video_id']}: {error['error']}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")

    def save_report(self, output_file: Path):
        """
        Save pipeline report

        Args:
            output_file: Output file path
        """
        report = {
            'pipeline': 'youtube_download_cache',
            'timestamp': datetime.now().isoformat(),
            'config': self.config,
            'stats': self.stats
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Report saved: {output_file}")


def load_video_ids(file_path: Path) -> List[str]:
    """
    Load video IDs from text file

    Args:
        file_path: Path to text file (one video ID per line)

    Returns:
        List of video IDs
    """
    video_ids = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                video_ids.append(line)
    return video_ids


def load_config(config_file: Path) -> Dict:
    """
    Load pipeline config from YAML file

    Args:
        config_file: Path to YAML config file

    Returns:
        Configuration dictionary
    """
    if not config_file.exists():
        return {}

    with open(config_file, 'r') as f:
        return yaml.safe_load(f) or {}


def main():
    parser = argparse.ArgumentParser(
        description='Download YouTube videos to cache using Rapid API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all videos from file
  python lens/scripts/download_to_cache_pipeline.py videos.txt

  # Use 5 parallel workers
  python lens/scripts/download_to_cache_pipeline.py videos.txt --workers 5

  # Skip videos already in cache
  python lens/scripts/download_to_cache_pipeline.py videos.txt --skip-existing

  # Save report to file
  python lens/scripts/download_to_cache_pipeline.py videos.txt --report download_report.json
        """
    )

    parser.add_argument('video_list', type=Path, help='Text file with video IDs (one per line)')
    parser.add_argument('--config', type=Path, help='YAML config file (optional)')
    parser.add_argument('--workers', type=int, help='Number of parallel workers (default: 3)')
    parser.add_argument('--skip-existing', action='store_true', help='Skip videos already in cache')
    parser.add_argument('--cache-dir', type=Path, help='Cache directory (default: /var/markethawk/_downloads)')
    parser.add_argument('--report', type=Path, help='Save report to JSON file')

    args = parser.parse_args()

    # Validate input file
    if not args.video_list.exists():
        print(f"❌ Error: File not found: {args.video_list}")
        return 1

    # Load video IDs
    print(f"📖 Loading video IDs from: {args.video_list}")
    video_ids = load_video_ids(args.video_list)

    if not video_ids:
        print("❌ No video IDs found in file")
        return 1

    print(f"✓ Found {len(video_ids)} video IDs")

    # Load config
    config = {}
    if args.config:
        config = load_config(args.config)

    # Override with CLI args
    if args.workers:
        config['workers'] = args.workers
    if args.skip_existing:
        config['skip_existing'] = True
    if args.cache_dir:
        config['cache_dir'] = str(args.cache_dir)

    # Run pipeline
    pipeline = DownloadPipeline(config)
    pipeline.process_video_list(video_ids)

    # Save report
    if args.report:
        pipeline.save_report(args.report)

    # Exit code based on failures
    if pipeline.stats['failed'] > 0:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
