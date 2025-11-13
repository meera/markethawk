#!/usr/bin/env python3
"""
Test script to download a single YouTube video using Rapid API.
Validates that Rapid API integration works before building full solution.

Usage:
    python scripts/test_download_video.py --video-id abc123
    python scripts/test_download_video.py --url "https://www.youtube.com/watch?v=abc123"
"""

import os
import sys
import json
import argparse
import requests
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()


class YouTubeVideoDownloader:
    """
    Download YouTube videos using Rapid API.
    Copied from VideotoBe implementation.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('RAPID_API_KEY')
        if not self.api_key:
            raise ValueError("RAPID_API_KEY not found in environment")

        self.base_url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
        self.headers = {
            'x-rapidapi-host': 'youtube-media-downloader.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }

    def get_video_details(self, video_id: str) -> Optional[dict]:
        """Fetch video details from Rapid API."""
        try:
            params = {
                'videoId': video_id,
                'urlAccess': 'normal',
                'videos': 'auto',
                'audios': 'auto'
            }

            print(f"📡 Fetching video details from Rapid API...")
            print(f"   Video ID: {video_id}")

            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            print(f"✓ Video details fetched successfully")

            return data

        except requests.RequestException as e:
            print(f"❌ Error fetching video details: {e}")
            return None

    def find_best_mp4_url(self, video_data: dict) -> Optional[str]:
        """Find the best MP4 video URL with audio."""
        try:
            videos = video_data.get('videos', {}).get('items', [])

            # Filter for MP4 videos WITH AUDIO ONLY
            mp4_videos_with_audio = [
                v for v in videos
                if v.get('extension') == 'mp4' and v.get('hasAudio', False)
            ]

            if not mp4_videos_with_audio:
                print("❌ No MP4 videos with audio found")
                print("Available formats:")
                for video in videos:
                    ext = video.get('extension', 'unknown')
                    quality = video.get('quality', 'unknown')
                    has_audio = video.get('hasAudio', False)
                    print(f"  - {ext} {quality} (audio: {has_audio})")
                return None

            # Select best quality (priority order)
            quality_order = ['1080p', '720p', '480p', '360p', '240p', '144p']

            for quality in quality_order:
                for video in mp4_videos_with_audio:
                    if video.get('quality') == quality:
                        print(f"✓ Selected: MP4 {quality} with audio")
                        return video.get('url')

            # Fallback to first MP4 with audio
            if mp4_videos_with_audio:
                selected = mp4_videos_with_audio[0]
                quality = selected.get('quality', 'unknown')
                print(f"✓ Using fallback: MP4 {quality} with audio")
                return selected.get('url')

            return None

        except Exception as e:
            print(f"❌ Error finding MP4 URL: {e}")
            return None

    def download_video_file(self, url: str, file_path: str) -> bool:
        """Download video file from URL with progress indicator."""
        try:
            print(f"⬇️  Downloading video...")
            print(f"   Destination: {file_path}")

            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)

                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            mb_downloaded = downloaded_size / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            print(f"\r   Progress: {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                                  end='', flush=True)

            print()  # New line after progress
            print(f"✓ Download completed")
            return True

        except Exception as e:
            print(f"\n❌ Error downloading video: {e}")
            return False

    def validate_video_file(self, file_path: str) -> bool:
        """Validate downloaded video file."""
        try:
            # Check file exists
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False

            # Check file size
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            print(f"📊 Validating video file...")
            print(f"   File size: {file_size_mb:.2f} MB")

            if file_size < 1_000_000:  # < 1MB
                print(f"❌ File too small ({file_size_mb:.2f} MB) - likely corrupted")
                return False

            # Validate with ffprobe
            print(f"   Running ffprobe validation...")
            result = subprocess.run(
                ['ffprobe', '-v', 'error', file_path],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"❌ ffprobe validation failed: {result.stderr}")
                return False

            print(f"✓ Video file validated successfully")
            return True

        except FileNotFoundError:
            print(f"⚠️  ffprobe not found - skipping format validation")
            print(f"   (File size check passed)")
            return True  # Don't fail if ffprobe not available
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False

    def download_video(self, video_id: str, output_dir: str) -> bool:
        """
        Main function to download YouTube video.

        Args:
            video_id: YouTube video ID
            output_dir: Base output directory (e.g., /var/markethawk/youtube)

        Returns:
            bool: Success status
        """
        try:
            # Create video directory
            video_dir = os.path.join(output_dir, video_id)
            os.makedirs(video_dir, exist_ok=True)

            print(f"\n{'='*60}")
            print(f"DOWNLOADING VIDEO: {video_id}")
            print(f"{'='*60}")

            # Get video details from Rapid API
            video_data = self.get_video_details(video_id)
            if not video_data:
                return False

            # Save Rapid API metadata
            metadata_path = os.path.join(video_dir, 'rapidapi_metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(video_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Metadata saved: {metadata_path}")

            # Find best MP4 URL
            mp4_url = self.find_best_mp4_url(video_data)
            if not mp4_url:
                print("❌ No suitable MP4 URL found")
                return False

            # Download video
            video_path = os.path.join(video_dir, f"{video_id}.mp4")

            # Skip if already exists
            if os.path.exists(video_path):
                print(f"⚠️  Video already exists: {video_path}")
                print(f"   Skipping download")
                if self.validate_video_file(video_path):
                    return True
                else:
                    print(f"   Existing file invalid, re-downloading...")
                    os.remove(video_path)

            success = self.download_video_file(mp4_url, video_path)
            if not success:
                return False

            # Validate downloaded file
            if not self.validate_video_file(video_path):
                print(f"❌ Downloaded file validation failed")
                os.remove(video_path)  # Clean up invalid file
                return False

            # Create download log
            log_data = {
                'video_id': video_id,
                'downloaded_at': datetime.now().isoformat(),
                'file_path': video_path,
                'file_size_mb': round(os.path.getsize(video_path) / (1024 * 1024), 2),
                'rapid_api_key_used': self.api_key[:10] + '...',  # Partial key for verification
                'success': True
            }

            log_path = os.path.join(video_dir, 'download.log')
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)

            print(f"\n{'='*60}")
            print(f"✅ SUCCESS!")
            print(f"{'='*60}")
            print(f"Video: {video_path}")
            print(f"Size: {log_data['file_size_mb']} MB")
            print(f"Metadata: {metadata_path}")
            print(f"Log: {log_path}")
            print(f"{'='*60}\n")

            return True

        except Exception as e:
            print(f"\n❌ Error in download_video: {e}")
            import traceback
            traceback.print_exc()
            return False


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from URL or return as-is if already an ID."""
    # If it's already just an ID (no slashes or special chars), return it
    if '/' not in url_or_id and '?' not in url_or_id:
        return url_or_id

    # Extract from various URL formats
    if 'youtube.com/watch?v=' in url_or_id:
        return url_or_id.split('watch?v=')[1].split('&')[0]
    elif 'youtu.be/' in url_or_id:
        return url_or_id.split('youtu.be/')[1].split('?')[0]
    elif 'youtube.com/shorts/' in url_or_id:
        return url_or_id.split('shorts/')[1].split('?')[0]

    # Fallback - assume it's already an ID
    return url_or_id


def main():
    parser = argparse.ArgumentParser(
        description="Test YouTube video download using Rapid API"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video-id", help="YouTube video ID")
    group.add_argument("--url", help="YouTube video URL")

    parser.add_argument(
        "--output",
        default="/var/markethawk/youtube",
        help="Output directory (default: /var/markethawk/youtube)"
    )

    args = parser.parse_args()

    # Extract video ID
    video_id = args.video_id if args.video_id else extract_video_id(args.url)

    print(f"\n{'='*60}")
    print(f"YOUTUBE VIDEO DOWNLOAD TEST")
    print(f"{'='*60}")
    print(f"Video ID: {video_id}")
    print(f"Output: {args.output}")
    print(f"{'='*60}\n")

    # Check environment
    api_key = os.getenv('RAPID_API_KEY')
    if not api_key:
        print("❌ Error: RAPID_API_KEY not found in environment")
        print("   Set it in .env file or export it:")
        print("   export RAPID_API_KEY='your-key-here'")
        sys.exit(1)

    print(f"✓ Rapid API key found: {api_key[:10]}...")

    # Check output directory
    if not os.path.exists(args.output):
        print(f"\n⚠️  Output directory does not exist: {args.output}")
        print(f"   Creating directory...")
        os.makedirs(args.output, exist_ok=True)

    # Download video
    try:
        downloader = YouTubeVideoDownloader()
        success = downloader.download_video(video_id, args.output)

        if success:
            print("\n✅ TEST PASSED - Video downloaded successfully!")
            print("\nNext steps:")
            print("1. Verify video plays correctly")
            print("2. Check metadata files")
            print("3. Review download speed and quality")
            print("4. Proceed with full implementation if satisfied")
            sys.exit(0)
        else:
            print("\n❌ TEST FAILED - Download unsuccessful")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ TEST FAILED - Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
