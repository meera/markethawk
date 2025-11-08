#!/usr/bin/env python3
"""
Download YouTube video using yt-dlp (more reliable than RapidAPI)

Usage:
    python scripts/download-youtube-ytdlp.py <youtube_url_or_video_id>

Examples:
    python scripts/download-youtube-ytdlp.py https://www.youtube.com/watch?v=i2IQv6zfgA8
    python scripts/download-youtube-ytdlp.py i2IQv6zfgA8
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as-is if already an ID"""
    if 'youtube.com/watch?v=' in url_or_id:
        return url_or_id.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url_or_id:
        return url_or_id.split('youtu.be/')[1].split('?')[0]
    else:
        # Assume it's already a video ID
        return url_or_id


def download_video(video_id: str, output_dir: str, ticker: str = "PLTR"):
    """Download YouTube video using yt-dlp"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Full YouTube URL
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    # Output template (save as video_id.mp4)
    output_template = os.path.join(output_dir, f"{video_id}.%(ext)s")

    print(f"{'='*60}")
    print(f"EarningLens YouTube Downloader (yt-dlp)")
    print(f"{'='*60}")
    print(f"Video URL: {youtube_url}")
    print(f"Video ID: {video_id}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}\n")

    # yt-dlp command
    # Download best video+audio in mp4 format
    cmd = [
        'yt-dlp',
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '--merge-output-format', 'mp4',
        '-o', output_template,
        '--write-info-json',  # Save metadata
        '--no-playlist',
        youtube_url
    ]

    print(f"⬇️  Downloading video...")
    print(f"Running: {' '.join(cmd)}\n")

    try:
        # Run yt-dlp
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)

        # Check if file was created
        video_path = os.path.join(output_dir, f"{video_id}.mp4")

        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB

            print(f"\n{'='*60}")
            print(f"✅ Successfully downloaded video {video_id}")
            print(f"📁 Location: {video_path}")
            print(f"📦 Size: {file_size:.1f} MB")

            # Check for metadata JSON
            json_path = os.path.join(output_dir, f"{video_id}.info.json")
            if os.path.exists(json_path):
                print(f"📄 Metadata: {json_path}")

                # Read metadata to get video info
                with open(json_path, 'r') as f:
                    metadata = json.load(f)
                    print(f"📹 Title: {metadata.get('title', 'N/A')}")
                    print(f"⏱️  Duration: {metadata.get('duration', 'N/A')} seconds")
                    print(f"📅 Upload Date: {metadata.get('upload_date', 'N/A')}")

            print(f"{'='*60}")

            # Print next steps
            audio_dir = os.path.join(os.path.dirname(output_dir), 'audio', ticker)
            print(f"\n✅ Next steps:")
            print(f"1. Extract audio track:")
            print(f"   mkdir -p {audio_dir}")
            print(f"   ffmpeg -i {video_path} -vn -acodec copy {audio_dir}/{video_id}.m4a")
            print(f"2. Create Remotion composition")
            print(f"3. Render video\n")

            return True
        else:
            print(f"❌ Error: Video file not created at {video_path}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading video: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/download-youtube-ytdlp.py <youtube_url_or_video_id>")
        print("\nExamples:")
        print("  python scripts/download-youtube-ytdlp.py https://www.youtube.com/watch?v=i2IQv6zfgA8")
        print("  python scripts/download-youtube-ytdlp.py i2IQv6zfgA8")
        sys.exit(1)

    url_or_id = sys.argv[1].strip()
    video_id = extract_video_id(url_or_id)

    # Ticker can be passed as second argument (default: PLTR)
    ticker = sys.argv[2] if len(sys.argv) > 2 else "PLTR"

    # Determine download directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    download_dir = os.path.join(base_dir, "public", "videos", ticker)

    success = download_video(video_id, download_dir, ticker)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
