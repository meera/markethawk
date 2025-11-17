"""
Upload YouTube Step - Wrapper for upload_youtube
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent to path
LENS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(LENS_DIR / "scripts"))

from upload_youtube import upload_video


def upload_youtube_step(job_dir: Path, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload video to YouTube (step handler wrapper)

    Args:
        job_dir: Job directory path
        job_data: Job data dict

    Returns:
        Result dict with YouTube video ID and URL
    """
    # Find rendered video (convention-based path)
    renders_dir = job_dir / "renders"

    # Look for ffmpeg_render.mp4 or remotion_render.mp4
    video_file = renders_dir / "ffmpeg_render.mp4"
    if not video_file.exists():
        video_file = renders_dir / "remotion_render.mp4"

    if not video_file.exists():
        # Try any .mp4 in renders
        mp4_files = list(renders_dir.glob("*.mp4"))
        if not mp4_files:
            raise FileNotFoundError(f"No video file found in {renders_dir}")
        video_file = mp4_files[0]

    # Job YAML path
    job_yaml_path = job_dir / "job.yaml"

    # Optional: thumbnail path (banner can be used as thumbnail)
    thumbnail_path = None
    banner_path = renders_dir / "banner.png"
    if banner_path.exists():
        thumbnail_path = str(banner_path)

    print(f"📺 Uploading to YouTube...")
    print(f"   Video: {video_file.name}")
    if thumbnail_path:
        print(f"   Thumbnail: {Path(thumbnail_path).name}")

    # Call upload_video
    result = upload_video(
        video_path=str(video_file),
        job_yaml_path=str(job_yaml_path),
        thumbnail_path=thumbnail_path
    )

    print(f"✅ Uploaded to YouTube!")
    print(f"   Video ID: {result.get('video_id')}")
    print(f"   URL: {result.get('url')}")

    return {
        'video_id': result.get('video_id'),
        'url': result.get('url'),
        'video_file': str(video_file),
        'thumbnail': thumbnail_path
    }
