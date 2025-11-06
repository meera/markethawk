#!/usr/bin/env python3
"""
Remove initial silence from video using ffmpeg.
Detects silence at the beginning and trims it.
"""

import sys
import os
import subprocess
import argparse
import json
from pathlib import Path


class SilenceRemover:
    """Remove initial silence from video files"""

    def __init__(self, input_path: str, output_path: str, threshold: str = "-50dB", min_duration: float = 0.5):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.threshold = threshold
        self.min_duration = min_duration

    def detect_silence_end(self) -> float:
        """Detect when initial silence ends"""

        print(f"🔍 Detecting initial silence...")
        print(f"  Threshold: {self.threshold}")
        print(f"  Min duration: {self.min_duration}s")

        # Use ffmpeg silencedetect filter
        cmd = [
            "ffmpeg",
            "-i", str(self.input_path),
            "-af", f"silencedetect=noise={self.threshold}:d={self.min_duration}",
            "-f", "null",
            "-"
        ]

        result = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

        # Parse ffmpeg output for silence_end
        silence_end = 0.0
        for line in result.stderr.split('\n'):
            if 'silence_end:' in line:
                # Extract timestamp from line like: [silencedetect @ 0x...] silence_end: 3.456 | silence_duration: 3.456
                parts = line.split('silence_end:')[1].split('|')[0].strip()
                silence_end = float(parts)
                print(f"✓ Silence ends at: {silence_end}s")
                break

        if silence_end == 0.0:
            print(f"  No initial silence detected (or audio starts immediately)")

        return silence_end

    def trim_video(self, start_time: float) -> bool:
        """Trim video from start_time onwards"""

        if start_time <= 0:
            print(f"  No trimming needed")
            # Just copy the file
            subprocess.run(["cp", str(self.input_path), str(self.output_path)])
            return True

        print(f"✂️  Trimming video from {start_time}s onwards...")

        # Use ffmpeg to trim
        cmd = [
            "ffmpeg",
            "-i", str(self.input_path),
            "-ss", str(start_time),  # Start time
            "-c", "copy",  # Copy codec (fast, no re-encoding)
            "-y",  # Overwrite output
            str(self.output_path)
        ]

        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        if result.returncode == 0:
            print(f"✓ Trimmed video saved to: {self.output_path}")
            return True
        else:
            print(f"❌ Error trimming video:")
            print(result.stderr.decode())
            return False

    def process(self) -> dict:
        """Detect and remove initial silence"""

        # Detect silence
        silence_end = self.detect_silence_end()

        # Trim video
        success = self.trim_video(silence_end)

        # Get file sizes
        input_size = self.input_path.stat().st_size / (1024 * 1024)  # MB
        output_size = self.output_path.stat().st_size / (1024 * 1024) if self.output_path.exists() else 0  # MB

        return {
            "success": success,
            "silence_duration": silence_end,
            "input_path": str(self.input_path),
            "output_path": str(self.output_path),
            "input_size_mb": round(input_size, 2),
            "output_size_mb": round(output_size, 2),
        }


def remove_silence(input_path: str, output_path: str, threshold: str = "-50dB", min_duration: float = 0.5) -> dict:
    """
    Remove initial silence from video.

    Args:
        input_path: Path to input video
        output_path: Path to output video
        threshold: Silence threshold (default: -50dB)
        min_duration: Minimum silence duration in seconds (default: 0.5)

    Returns:
        Dictionary with processing results including silence duration and file sizes
    """
    # Check if ffmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("ffmpeg not found. Please install ffmpeg.")

    # Process video
    remover = SilenceRemover(input_path, output_path, threshold=threshold, min_duration=min_duration)
    result = remover.process()

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Remove initial silence from video"
    )
    parser.add_argument("input", help="Input video path")
    parser.add_argument("output", help="Output video path")
    parser.add_argument(
        "--threshold",
        default="-50dB",
        help="Silence threshold (default: -50dB)"
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=0.5,
        help="Minimum silence duration in seconds (default: 0.5)"
    )

    args = parser.parse_args()

    # Process video
    try:
        result = remove_silence(
            args.input,
            args.output,
            threshold=args.threshold,
            min_duration=args.min_duration
        )

        print()
        print("✓ Processing complete!")
        print(f"  Silence removed: {result['silence_duration']}s")
        print(f"  Input size: {result['input_size_mb']} MB")
        print(f"  Output size: {result['output_size_mb']} MB")

        # Output JSON for scripting
        print()
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
