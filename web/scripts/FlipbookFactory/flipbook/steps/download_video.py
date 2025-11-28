"""
Download video from YouTube using RapidAPI.

This step fetches a video from YouTube and saves it to the experiment's input directory.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from flipbook.step import Step, StepRegistry

load_dotenv()


@StepRegistry.register
class DownloadVideo(Step):
    """
    Download video from YouTube using RapidAPI.

    Parameters:
        url: YouTube URL or video ID (required)
        output_dir: Where to save the video (default: data/inputs)
        overwrite: Whether to overwrite existing file (default: False)

    Returns:
        output: Path to downloaded video file
        video_id: Extracted YouTube video ID
        metadata: Video metadata (title, duration, etc.)
    """

    def process(self, **params) -> Dict[str, Any]:
        """Download video from YouTube"""
        self.params = params

        # Get parameters
        url_or_id = params.get('url')
        if not url_or_id:
            raise ValueError("'url' parameter is required")

        output_dir = Path(params.get('output_dir', 'data/inputs'))
        overwrite = params.get('overwrite', False)

        # Get API key
        api_key = os.getenv("RAPID_API_KEY")
        if not api_key:
            raise ValueError("RAPID_API_KEY not found in environment")

        # Extract video ID
        video_id = self._extract_video_id(url_or_id)
        print(f"📹 Video ID: {video_id}")

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Check if file already exists
        video_path = output_dir / f"{video_id}.mp4"
        metadata_path = output_dir / f"{video_id}_metadata.json"

        if not overwrite and video_path.exists():
            print(f"✅ Video {video_id}.mp4 already exists. Skipping download.")

            # Load existing metadata if available
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)

            return {
                'output': str(video_path),
                'video_id': video_id,
                'metadata_path': str(metadata_path),
                'metadata': metadata,
                'skipped': True
            }

        # Fetch video details from RapidAPI
        print(f"📡 Fetching video details from RapidAPI...")
        video_data = self._get_video_details(video_id, api_key)
        if not video_data:
            raise RuntimeError("Failed to fetch video details from RapidAPI")

        # Save metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, indent=2, ensure_ascii=False)
        print(f"📄 Metadata saved: {metadata_path}")

        # Find best MP4 URL with audio
        mp4_url = self._find_best_mp4_url(video_data)
        if not mp4_url:
            raise RuntimeError("No suitable MP4 format with audio found")

        # Download the video
        print(f"⬇️  Downloading video...")
        self._download_file(mp4_url, video_path)

        # Get video info
        file_size = video_path.stat().st_size / (1024 * 1024)  # MB
        title = video_data.get('title', 'Unknown')
        duration = video_data.get('lengthSeconds', 0)

        print(f"✅ Downloaded: {title}")
        print(f"   Size: {file_size:.1f} MB, Duration: {duration}s")

        return {
            'output': str(video_path),
            'video_id': video_id,
            'metadata_path': str(metadata_path),
            'metadata': {
                'title': title,
                'duration': duration,
                'file_size_mb': round(file_size, 2)
            }
        }

    def _extract_video_id(self, url_or_id: str) -> str:
        """Extract video ID from URL or return ID if already provided"""
        url_or_id = url_or_id.strip()

        # Already a video ID (11 characters, no slashes)
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

    def _get_video_details(self, video_id: str, api_key: str) -> Optional[dict]:
        """Fetch video details from RapidAPI"""
        url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
        headers = {
            'x-rapidapi-host': 'youtube-media-downloader.p.rapidapi.com',
            'x-rapidapi-key': api_key
        }
        params = {
            'videoId': video_id,
            'urlAccess': 'normal',
            'videos': 'auto',
            'audios': 'auto'
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error fetching video details: {e}")
            return None

    def _find_best_mp4_url(self, video_data: dict) -> Optional[str]:
        """Find best MP4 format with audio"""
        videos = video_data.get('videos', {}).get('items', [])

        # Filter for MP4 with audio
        mp4_videos_with_audio = [
            v for v in videos
            if v.get('extension') == 'mp4' and v.get('hasAudio', False)
        ]

        if not mp4_videos_with_audio:
            print("❌ No MP4 videos with audio found")
            return None

        # Prefer 720p for shorts, then 480p, 360p
        quality_order = ['720p', '480p', '360p', '1080p', '240p', '144p']

        for quality in quality_order:
            for video in mp4_videos_with_audio:
                if video.get('quality') == quality:
                    print(f"✅ Selected: {quality} MP4 with audio")
                    return video.get('url')

        # Fallback to first available
        selected = mp4_videos_with_audio[0]
        print(f"✅ Using: {selected.get('quality', 'unknown')} MP4 with audio")
        return selected.get('url')

    def _download_file(self, url: str, file_path: Path):
        """Download file with progress indicator"""
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb = downloaded / (1024 * 1024)
                        print(f"\r  Progress: {percent:.1f}% ({mb:.1f} MB)", end='', flush=True)
        print()  # New line after progress

    def get_schema(self) -> Dict[str, Any]:
        """Return parameter schema for validation"""
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "YouTube URL or video ID"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory (default: data/inputs)",
                    "default": "data/inputs"
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite existing file",
                    "default": False
                }
            },
            "required": ["url"]
        }
