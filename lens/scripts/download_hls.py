#!/usr/bin/env python3
"""
Download HLS stream (.m3u8) using ffmpeg
"""

import subprocess
import hashlib
from pathlib import Path
from typing import Dict


def download_hls_stream(url: str, job_dir: str) -> Dict:
    """
    Download HLS stream to mp4 using ffmpeg

    Args:
        url: HLS stream URL (m3u8)
        job_dir: Job directory to save video (will save to job_dir/input/source.mp4)

    Returns:
        Dictionary with download info
    """
    job_dir = Path(job_dir)

    # Ensure input directory exists
    input_dir = job_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    output_file = input_dir / "source.mp4"

    print(f"📥 Downloading HLS stream...")
    print(f"  URL: {url}")
    print(f"  Output: {output_file}")

    # Use ffmpeg to download and convert
    cmd = [
        "ffmpeg",
        "-i", url,
        "-c", "copy",  # Copy streams without re-encoding (faster)
        "-bsf:a", "aac_adtstoasc",  # Fix AAC stream
        "-y",  # Overwrite output file
        str(output_file)
    ]

    print(f"  Running: {' '.join(cmd[:4])} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg download failed: {result.stderr}")

    # Get file size
    size_mb = output_file.stat().st_size / (1024 * 1024)

    print(f"✓ Downloaded: {size_mb:.1f} MB")

    return {
        "file": str(output_file),
        "size_mb": size_mb
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download HLS stream")
    parser.add_argument("url", help="HLS stream URL (.m3u8)")
    parser.add_argument("--output-dir", default="/var/markethawk/_downloads",
                       help="Output directory")

    args = parser.parse_args()

    result = download_hls_stream(args.url, args.output_dir)
    print(f"\n✓ Success!")
    print(f"  Video ID: {result['video_id']}")
    print(f"  File: {result['file']}")
