#!/usr/bin/env python3
"""
Download YouTube video using RapidAPI for FlipbookFactory experiments

Usage:
    python download_video.py <youtube_url_or_video_id>

Example:
    python download_video.py https://www.youtube.com/shorts/iYsOFDa4DDU
    python download_video.py iYsOFDa4DDU
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class YouTubeVideoDownloader:
    def __init__(self, api_key: str = None):
        """Initialize YouTube downloader with RapidAPI credentials"""
        self.api_key = api_key or os.getenv("RAPID_API_KEY")
        if not self.api_key:
            raise ValueError("RAPID_API_KEY not found in environment")
        self.base_url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
        self.headers = {
            'x-rapidapi-host': 'youtube-media-downloader.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }

    def extract_video_id(self, url_or_id: str) -> str:
        """Extract video ID from URL or return ID if already provided"""
        url_or_id = url_or_id.strip()

        # Already a video ID
        if len(url_or_id) == 11 and '/' not in url_or_id:
            return url_or_id

        # youtu.be short URL
        if "youtu.be/" in url_or_id:
            return url_or_id.split("youtu.be/")[1].split("?")[0]

        # Standard YouTube URL
        if "youtube.com/watch?v=" in url_or_id:
            return url_or_id.split("v=")[1].split("&")[0]

        # YouTube Shorts URL
        if "youtube.com/shorts/" in url_or_id:
            return url_or_id.split("shorts/")[1].split("?")[0]

        raise ValueError(f"Could not extract video ID from: {url_or_id}")

    def get_video_details(self, video_id: str) -> Optional[dict]:
        """Fetch video details from RapidAPI"""
        try:
            params = {
                'videoId': video_id,
                'urlAccess': 'normal',
                'videos': 'auto',
                'audios': 'auto'
            }

            print(f"📡 Fetching video details for {video_id}...")
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"❌ Error fetching video details: {e}")
            return None

    def find_best_mp4_url(self, video_data: dict) -> Optional[str]:
        """Find the best MP4 video URL with audio from the response"""
        try:
            videos = video_data.get('videos', {}).get('items', [])

            # Filter for MP4 videos WITH AUDIO ONLY
            mp4_videos_with_audio = [
                v for v in videos
                if v.get('extension') == 'mp4' and v.get('hasAudio', False)
            ]

            if not mp4_videos_with_audio:
                print("❌ No MP4 videos with audio found in response")
                print("Available videos:")
                for video in videos:
                    ext = video.get('extension', 'unknown')
                    quality = video.get('quality', 'unknown')
                    has_audio = video.get('hasAudio', False)
                    print(f"  - {ext} {quality} (audio: {has_audio})")
                return None

            # Select best quality MP4 with audio (prefer 720p for shorts)
            quality_order = ['720p', '480p', '360p', '1080p', '240p', '144p']

            for quality in quality_order:
                for video in mp4_videos_with_audio:
                    if video.get('quality') == quality:
                        print(f"✅ Selected MP4 with audio: {quality}")
                        return video.get('url')

            # Fallback to first MP4 with audio found
            if mp4_videos_with_audio:
                selected = mp4_videos_with_audio[0]
                print(f"✅ Using fallback MP4 with audio: {selected.get('quality', 'unknown')}")
                return selected.get('url')

            return None

        except Exception as e:
            print(f"❌ Error finding MP4 URL: {e}")
            return None

    def download_video_file(self, url: str, file_path: str) -> bool:
        """Download video file from URL with progress"""
        try:
            print(f"⬇️  Downloading video to {file_path}...")

            # Stream download with progress
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
                            print(f"\rProgress: {progress:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='', flush=True)

            print(f"\n✅ Download completed: {file_path}")
            return True

        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            return False

    def save_json_response(self, data: dict, file_path: str) -> bool:
        """Save JSON response to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            print(f"📄 JSON response saved: {file_path}")
            return True

        except Exception as e:
            print(f"❌ Error saving JSON response: {e}")
            return False

    def download_video(self, url_or_id: str, download_dir: str = "data/inputs", overwrite: bool = False) -> bool:
        """
        Main function to download YouTube video

        Args:
            url_or_id: YouTube URL or video ID
            download_dir: Download directory (default: data/inputs)
            overwrite: Whether to overwrite existing files

        Returns:
            bool: Success status
        """
        try:
            # Extract video ID
            video_id = self.extract_video_id(url_or_id)

            # Ensure download directory exists
            os.makedirs(download_dir, exist_ok=True)

            # Check if file already exists
            video_path = os.path.join(download_dir, f"{video_id}.mp4")
            if not overwrite and os.path.exists(video_path):
                print(f"✅ Video {video_id}.mp4 already exists. Skipping download.")
                print("   Use --overwrite to force re-download.")
                return True

            # Get video details from API
            video_data = self.get_video_details(video_id)
            if not video_data:
                return False

            # Save JSON response (doing this early in case download fails)
            json_path = os.path.join(download_dir, f"{video_id}_metadata.json")
            self.save_json_response(video_data, json_path)

            # Find and download MP4
            mp4_url = self.find_best_mp4_url(video_data)
            if not mp4_url:
                print("❌ No suitable MP4 URL found")
                return False

            # Download the video
            success = self.download_video_file(mp4_url, video_path)

            if success:
                # Get file size and metadata
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                title = video_data.get('title', 'Unknown')
                duration = video_data.get('lengthSeconds', 0)

                print(f"\n{'='*60}")
                print(f"✅ Successfully downloaded video")
                print(f"📹 Title: {title}")
                print(f"🆔 Video ID: {video_id}")
                print(f"⏱️  Duration: {duration}s")
                print(f"📁 Location: {video_path}")
                print(f"📦 Size: {file_size:.1f} MB")
                print(f"📄 Metadata: {json_path}")
                print(f"{'='*60}")

            return success

        except Exception as e:
            print(f"❌ Error in download_video: {e}")
            return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python download_video.py <youtube_url_or_video_id>")
        print("\nExample:")
        print("  python download_video.py https://www.youtube.com/shorts/iYsOFDa4DDU")
        print("  python download_video.py iYsOFDa4DDU")
        sys.exit(1)

    url_or_id = sys.argv[1].strip()
    overwrite = "--overwrite" in sys.argv

    print(f"{'='*60}")
    print(f"FlipbookFactory YouTube Downloader")
    print(f"{'='*60}\n")

    downloader = YouTubeVideoDownloader()
    success = downloader.download_video(
        url_or_id=url_or_id,
        download_dir="data/inputs",
        overwrite=overwrite
    )

    if success:
        print("\n✅ Download completed successfully!")
        print(f"\nNext steps:")
        print(f"1. Extract frames: python -m flipbook.steps.extract_frames")
        print(f"2. Create experiment config: experiments/exp_001.yaml")
        print(f"3. Run experiment: python run.py experiments/exp_001.yaml")
    else:
        print("\n❌ Download failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
