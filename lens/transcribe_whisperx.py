#!/usr/bin/env python3
"""
MarketHawk Transcription with WhisperX
Speaker-diarized transcription for earnings calls

Adapted from VideotoBe's x_whisper_service.py
"""

import whisperx
import gc
import os
import torch
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def transcribe_earnings_call(
    video_file: Path,
    output_dir: Path,
    model_size: str = "medium",
    language: str = "en",
    device: Optional[str] = None
) -> Dict:
    """
    Transcribe earnings call with speaker diarization

    Args:
        video_file: Path to video/audio file
        output_dir: Directory to save transcripts
        model_size: WhisperX model size (tiny, base, small, medium, large-v2)
        language: Language code (default: en)
        device: cuda or cpu (auto-detected if None)

    Returns:
        Dictionary with transcription results
    """
    logger.info(f"Transcribing: {video_file}")

    # Auto-detect device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info(f"Using device: {device}")

    # Compute type for GPU
    compute_type = "float16" if device == "cuda" else "int8"

    # 1. Load WhisperX model
    logger.info(f"Loading WhisperX model: {model_size}")
    model = whisperx.load_model(model_size, device, compute_type=compute_type)

    # 2. Load audio
    logger.info("Loading audio...")
    audio = whisperx.load_audio(str(video_file))

    # 3. Transcribe
    logger.info("Transcribing...")
    batch_size = 16  # Reduce if low on GPU memory
    result = model.transcribe(audio, batch_size=batch_size, language=language)

    # Clear GPU memory
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
    del model

    # 4. Align whisper output (for supported languages)
    language_code = result["language"]
    if language_code in {"en", "fr", "de", "es", "it"}:
        logger.info(f"Aligning transcription for language: {language_code}")
        model_a, metadata = whisperx.load_align_model(
            language_code=language_code,
            device=device
        )
        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            device,
            return_char_alignments=False
        )

        # Clear GPU memory
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()
        del model_a

        # 5. Speaker diarization
        logger.info("Running speaker diarization...")
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            logger.warning("HF_TOKEN not found. Skipping diarization.")
        else:
            diarize_model = whisperx.DiarizationPipeline(
                use_auth_token=hf_token,
                device=device
            )
            diarize_segments = diarize_model(audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)

            # Clear GPU memory
            gc.collect()
            if device == "cuda":
                torch.cuda.empty_cache()
            del diarize_model

    # 6. Save outputs
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON (full transcript with timestamps and speakers)
    transcript_json = output_dir / "transcript.json"
    with open(transcript_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved JSON: {transcript_json}")

    # Save SRT (subtitles)
    from whisperx.utils import get_writer
    srt_writer = get_writer("srt", str(output_dir))
    srt_writer(result, str(video_file.stem))
    logger.info(f"Saved SRT: {output_dir / video_file.stem}.srt")

    # Save VTT (web captions)
    vtt_writer = get_writer("vtt", str(output_dir))
    vtt_writer(result, str(video_file.stem))
    logger.info(f"Saved VTT: {output_dir / video_file.stem}.vtt")

    # Save TXT (plain text)
    txt_writer = get_writer("txt", str(output_dir))
    txt_writer(result, str(video_file.stem))
    logger.info(f"Saved TXT: {output_dir / video_file.stem}.txt")

    logger.info("Transcription complete!")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Transcribe earnings call with WhisperX")
    parser.add_argument("video_file", help="Path to video/audio file")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: same as video)")
    parser.add_argument("--model", default="medium", choices=["tiny", "base", "small", "medium", "large-v2"])
    parser.add_argument("--language", default="en", help="Language code")
    parser.add_argument("--device", choices=["cuda", "cpu"], help="Device (auto-detected if not specified)")

    args = parser.parse_args()

    video_file = Path(args.video_file)

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = video_file.parent / "transcripts"

    transcribe_earnings_call(
        video_file=video_file,
        output_dir=output_dir,
        model_size=args.model,
        language=args.language,
        device=args.device
    )
