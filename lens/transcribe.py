#!/usr/bin/env python3
"""
Whisper transcription service for EarningLens on sushi GPU machine

Usage:
    python sushi/transcribe.py <video_or_audio_file>

Example:
    python sushi/transcribe.py uploads/jUnV3LiN0_k.mp4
"""

import os
import sys
import json
import logging
import torch
import whisper
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def transcribe_file(filepath: str, model_name: str = "medium", language: str = None) -> bool:
    """
    Transcribe audio/video file using Whisper.

    Args:
        filepath: Path to audio or video file
        model_name: Whisper model (tiny, base, small, medium, large)
        language: Optional language code (en, es, etc.)

    Returns:
        bool: Success status
    """

    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return False

    # Get output directory (same as input file)
    output_dir = os.path.dirname(filepath)
    base_filename = os.path.splitext(os.path.basename(filepath))[0]

    try:
        logger.info(f"Starting transcription for {filepath}")
        logger.info(f"Using model: {model_name}")

        # Check for GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")

        # Load Whisper model
        model = whisper.load_model(model_name).to(device)

        # Run transcription
        with torch.no_grad():
            if language:
                result = model.transcribe(
                    filepath,
                    word_timestamps=True,
                    language=language,
                    verbose=True
                )
            else:
                result = model.transcribe(
                    filepath,
                    word_timestamps=True,
                    verbose=True
                )

        # Write standard Whisper outputs (.srt, .vtt, .txt, .json)
        writer = whisper.utils.get_writer("all", output_dir)
        writer(result, filepath)

        # Write paragraphs.json (simplified format for LLM processing)
        paragraphs_path = os.path.join(output_dir, f"{base_filename}.paragraphs.json")
        write_paragraphs_json(result, paragraphs_path)

        logger.info(f"✅ Transcription completed successfully!")
        logger.info(f"Generated files:")
        logger.info(f"  - {base_filename}.json (full Whisper output)")
        logger.info(f"  - {base_filename}.srt (SubRip subtitles)")
        logger.info(f"  - {base_filename}.vtt (WebVTT subtitles)")
        logger.info(f"  - {base_filename}.txt (plain text)")
        logger.info(f"  - {base_filename}.paragraphs.json (for LLM)")

        return True

    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        return False

    finally:
        # Clean up GPU memory
        if 'model' in locals():
            del model
        if device == "cuda":
            torch.cuda.empty_cache()


def write_paragraphs_json(result: dict, output_path: str):
    """
    Write simplified JSON format for LLM processing.

    Format:
    {
        "segments": [
            {
                "start": 0.0,
                "end": 5.2,
                "speaker": "SPEAKER_00",
                "text": "Welcome to the earnings call."
            },
            ...
        ]
    }
    """

    segments = []

    for i, segment in enumerate(result.get('segments', [])):
        segments.append({
            "start": segment.get('start', 0),
            "end": segment.get('end', 0),
            "speaker": f"SPEAKER_{i:02d}",  # Placeholder speaker labels
            "text": segment.get('text', '').strip()
        })

    output_data = {
        "segments": segments,
        "language": result.get('language', 'en'),
        "duration": result.get('segments', [{}])[-1].get('end', 0) if result.get('segments') else 0
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Wrote paragraphs.json: {output_path}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python sushi/transcribe.py <video_or_audio_file> [model_name] [language]")
        print("\nExamples:")
        print("  python sushi/transcribe.py uploads/video.mp4")
        print("  python sushi/transcribe.py uploads/video.mp4 medium")
        print("  python sushi/transcribe.py uploads/video.mp4 medium en")
        print("\nModels: tiny, base, small, medium, large")
        sys.exit(1)

    filepath = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "medium"
    language = sys.argv[3] if len(sys.argv) > 3 else None

    success = transcribe_file(filepath, model_name, language)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
