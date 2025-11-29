"""
Transcribe Step - Wrapper for transcribe_whisperx that conforms to step handler interface
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent to path
LENS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(LENS_DIR))

from transcribe_whisperx import transcribe_earnings_call


def transcribe_step(job_dir: Path, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transcribe audio with WhisperX (step handler wrapper)

    Args:
        job_dir: Job directory path
        job_data: Job data dict

    Returns:
        Result dict with transcript path
    """
    # Find audio file in input directory
    input_dir = job_dir / "input"

    # Look for source.* files (source.mp3, source.mp4, etc.)
    audio_files = list(input_dir.glob("source.*"))

    if not audio_files:
        raise FileNotFoundError(f"No source audio file found in {input_dir}")

    audio_file = audio_files[0]

    # Output directory for transcripts
    output_dir = job_dir / "transcripts"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🎤 Transcribing: {audio_file.name}")

    # Call WhisperX transcription
    result = transcribe_earnings_call(
        video_file=audio_file,
        output_dir=output_dir,
        model_size="medium",
        language="en"
    )

    # Return result for job.yaml
    return {
        'transcript_file': str(output_dir / "transcript.json"),
        'paragraphs_file': str(output_dir / "transcript.paragraphs.json"),
        'audio_file': str(audio_file),
        'model': 'medium',
        'language': 'en'
    }
