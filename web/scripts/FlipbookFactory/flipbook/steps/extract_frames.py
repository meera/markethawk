"""
Extract frames from video using ffmpeg.

This step converts a video file into a sequence of image frames.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any
import json

from flipbook.step import Step, StepRegistry


@StepRegistry.register
class ExtractFrames(Step):
    """
    Extract frames from video using ffmpeg.

    Parameters:
        input: Path to input video file (required)
        output_dir: Directory to save frames (default: auto-generated in experiment dir)
        fps: Frames per second to extract (default: use video's native fps)
        format: Output image format (default: 'jpg', options: 'jpg', 'png')
        quality: JPEG quality 1-31, lower is better (default: 2)

    Returns:
        output: Path to directory containing extracted frames
        frame_count: Number of frames extracted
        fps: Actual FPS used
    """

    def process(self, **params) -> Dict[str, Any]:
        """Extract frames from video"""
        self.params = params

        # Get parameters
        input_path = Path(params.get('input'))
        if not input_path or not input_path.exists():
            raise ValueError(f"Input video not found: {input_path}")

        # Determine output directory
        if params.get('output_dir'):
            output_dir = Path(params['output_dir'])
        elif self.experiment_dir:
            output_dir = self.experiment_dir / 'frames'
        else:
            # Fallback: create next to video file
            output_dir = input_path.parent / f"{input_path.stem}_frames"

        output_dir.mkdir(parents=True, exist_ok=True)

        fps = params.get('fps')  # None means use native fps
        img_format = params.get('format', 'jpg')
        quality = params.get('quality', 2)

        print(f"📹 Extracting frames from: {input_path.name}")
        print(f"📁 Output directory: {output_dir}")

        # Build ffmpeg command
        # frame_%04d.jpg produces: frame_0001.jpg, frame_0002.jpg, etc.
        output_pattern = output_dir / f"frame_%04d.{img_format}"

        cmd = ['ffmpeg', '-i', str(input_path)]

        # Set FPS if specified
        if fps:
            cmd.extend(['-vf', f'fps={fps}'])
            print(f"🎞️  Target FPS: {fps}")
        else:
            # Get native FPS for reporting
            fps = self._get_video_fps(input_path)
            print(f"🎞️  Using native FPS: {fps}")

        # Set quality (for JPEG)
        if img_format == 'jpg':
            cmd.extend(['-qscale:v', str(quality)])

        cmd.append(str(output_pattern))

        # Execute ffmpeg
        print(f"⚙️  Running ffmpeg...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ ffmpeg error: {result.stderr}")
            raise RuntimeError(f"ffmpeg failed with return code {result.returncode}")

        # Count extracted frames
        frames = sorted(output_dir.glob(f"frame_*.{img_format}"))
        frame_count = len(frames)

        print(f"✅ Extracted {frame_count} frames")
        print(f"   Format: {img_format.upper()}, Quality: {quality}")

        return {
            'output': str(output_dir),
            'frame_count': frame_count,
            'fps': fps,
            'format': img_format,
            'first_frame': str(frames[0]) if frames else None,
            'last_frame': str(frames[-1]) if frames else None
        }

    def _get_video_fps(self, video_path: Path) -> float:
        """Get video FPS using ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=r_frame_rate',
            '-of', 'json',
            str(video_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return 24.0  # Default fallback

        try:
            data = json.loads(result.stdout)
            fps_str = data['streams'][0]['r_frame_rate']
            # fps_str is like "30/1" or "30000/1001"
            num, den = map(int, fps_str.split('/'))
            return round(num / den, 2)
        except:
            return 24.0  # Default fallback

    def get_schema(self) -> Dict[str, Any]:
        """Return parameter schema for validation"""
        return {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Path to input video file"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory to save frames"
                },
                "fps": {
                    "type": "number",
                    "description": "Frames per second (default: native fps)"
                },
                "format": {
                    "type": "string",
                    "enum": ["jpg", "png"],
                    "default": "jpg",
                    "description": "Output image format"
                },
                "quality": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 31,
                    "default": 2,
                    "description": "JPEG quality (1-31, lower is better)"
                }
            },
            "required": ["input"]
        }
