#!/usr/bin/env python3
"""
Multi-source video downloader for earnings calls.
Supports: YouTube, Company IR websites (manual)
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Optional, Dict
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
RAPID_API_KEY = os.getenv("RAPID_API_KEY")


class VideoSourceDownloader:
    """Download videos from multiple sources"""

    def __init__(self, video_id: str, output_dir: str):
        self.video_id = video_id
        self.output_dir = Path(output_dir)
        self.input_dir = self.output_dir / "input"
        self.input_dir.mkdir(parents=True, exist_ok=True)

    def download_from_youtube(self, youtube_url: str) -> Dict:
        """Download video from YouTube using RapidAPI"""
        print(f"📥 Downloading from YouTube: {youtube_url}")

        # Extract video ID from URL
        video_id = self._extract_youtube_id(youtube_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {youtube_url}")

        # Call RapidAPI
        api_url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
        headers = {
            "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com",
            "x-rapidapi-key": RAPID_API_KEY,
        }
        params = {"videoId": video_id}

        print(f"  Fetching video details from RapidAPI...")
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Save complete metadata
        metadata_path = self.input_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✓ Metadata saved to: {metadata_path}")

        # Find best MP4 with audio
        download_url = self._find_best_mp4_url(data)
        if not download_url:
            raise ValueError("No suitable MP4 format with audio found")

        # Download video
        output_path = self.input_dir / "source.mp4"
        print(f"  Downloading video...")
        self._download_file(download_url, output_path)

        print(f"✓ Downloaded to: {output_path}")
        return {
            "source": "youtube",
            "url": youtube_url,
            "video_id": video_id,
            "file_path": str(output_path),
            "metadata_path": str(metadata_path),
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "channel": data.get("channel", {}),
            "duration": data.get("lengthSeconds", 0),
        }

    def use_manual_upload(self) -> Dict:
        """Use manually uploaded file"""
        print(f"📂 Using manual upload")
        expected_path = self.input_dir / "source.mp4"

        if not expected_path.exists():
            print(f"❌ No file found at: {expected_path}")
            print(f"   Please upload video to: {expected_path}")
            print(f"   Example: scp video.mp4 sushi:{expected_path}")
            sys.exit(1)

        print(f"✓ Found file: {expected_path}")
        return {
            "source": "manual",
            "file_path": str(expected_path),
        }

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        if "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        elif "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif len(url) == 11:  # Direct video ID
            return url
        return None

    def _find_best_mp4_url(self, video_data: dict) -> Optional[str]:
        """Find best MP4 format with audio"""
        videos = video_data.get("videos", {}).get("items", [])

        # Filter for MP4 with audio
        mp4_videos_with_audio = [
            v
            for v in videos
            if v.get("extension") == "mp4" and v.get("hasAudio", False)
        ]

        if not mp4_videos_with_audio:
            return None

        # Sort by quality (height), prefer 720p or 360p
        sorted_videos = sorted(
            mp4_videos_with_audio, key=lambda x: abs(x.get("height", 0) - 720)
        )

        return sorted_videos[0].get("url")

    def _download_file(self, url: str, output_path: Path):
        """Download file with progress"""
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(
                            f"\r  Progress: {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB)",
                            end="",
                        )
        print()  # New line after progress


def download_video(url: str, downloads_dir: str = "/var/earninglens/_downloads") -> Dict:
    """
    Download video from YouTube URL.

    Args:
        url: YouTube video URL
        downloads_dir: Base directory for downloads

    Returns:
        Dictionary with download results including file paths and metadata
    """
    # Extract video ID from URL
    video_id = None
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    elif "youtube.com/watch?v=" in url:
        video_id = url.split("v=")[1].split("&")[0]

    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {url}")

    # Create downloader - save to _downloads/<video_id>/
    output_dir = Path(downloads_dir) / video_id
    downloader = VideoSourceDownloader(video_id, str(output_dir))

    # Download
    result = downloader.download_from_youtube(url)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Download earnings call videos from YouTube"
    )
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument(
        "--downloads-dir",
        default="/var/earninglens/_downloads",
        help="Downloads directory (default: /var/earninglens/_downloads)",
    )

    args = parser.parse_args()

    try:
        result = download_video(args.url, args.downloads_dir)

        print(f"✓ Download complete!")
        print(f"  Video: {result['file_path']}")
        print(f"  Metadata: {result['metadata_path']}")
        print(f"  Title: {result['title']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
