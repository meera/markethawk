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

    # Save paragraphs.json (compact format for LLM - saves tokens)
    paragraphs = create_paragraph_format(result)
    paragraphs_json = output_dir / "transcript.paragraphs.json"
    with open(paragraphs_json, 'w', encoding='utf-8') as f:
        json.dump(paragraphs, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved paragraphs: {paragraphs_json}")

    logger.info("Transcription complete!")

    return result


def create_paragraph_format(result: Dict, min_words: int = 100, max_words: int = 160) -> Dict:
    """
    Create compact paragraph format for LLM processing

    Groups consecutive segments by speaker into paragraphs with word-based chunking.
    Breaks paragraphs at sentence boundaries when word count thresholds are met.

    Args:
        result: WhisperX transcription result with segments
        min_words: Minimum words before considering sentence break (default: 100)
        max_words: Maximum words before forcing break (default: 160)

    Returns:
        Dict with 'language' and 'paragraphs' (list of dicts with text, start, end, speaker)

    Algorithm:
    1. Force new paragraph on speaker change
    2. Break at sentence endings (., !, ?) when word count >= min_words
    3. Force break when word count > max_words (hard limit)

    Benefits over old approach:
    - Reduces transcript size by 50-70% (more manageable chunks for LLM)
    - Better timestamp granularity for refinement (1-2 min vs 5-10 min)
    - Natural sentence breaks improve readability
    """
    segments = result.get("segments", [])

    paragraphs = []
    current_para = []
    word_count = 0
    para_start = None
    para_end = None
    current_speaker = None

    for segment in segments:
        speaker = segment.get("speaker", "UNKNOWN")
        segment_text = segment.get("text", "").strip()
        segment_start = segment.get("start", 0)
        segment_end = segment.get("end", 0)

        # Force new paragraph on speaker change
        if current_speaker is not None and current_speaker != speaker:
            if current_para:
                paragraphs.append({
                    "speaker": current_speaker,
                    "start": para_start,
                    "end": para_end,
                    "text": " ".join(current_para)
                })
                current_para = []
                word_count = 0

        current_speaker = speaker

        # Split segment text into words
        words = segment_text.split()

        for word in words:
            if word_count == 0:
                # Start new paragraph
                para_start = segment_start

            current_para.append(word)
            word_count += 1
            para_end = segment_end

            # Check if word ends with sentence-ending punctuation
            is_end_of_sentence = any(word.endswith(p) for p in ['.', '!', '?'])

            # Create new paragraph if:
            # 1. Word count >= min AND end of sentence reached
            # 2. OR word count > max (force break)
            if (word_count >= min_words and is_end_of_sentence) or word_count > max_words:
                paragraphs.append({
                    "speaker": current_speaker,
                    "start": para_start,
                    "end": para_end,
                    "text": " ".join(current_para)
                })
                current_para = []
                word_count = 0

    # Add remaining text as final paragraph
    if current_para:
        paragraphs.append({
            "speaker": current_speaker,
            "start": para_start,
            "end": segments[-1]["end"] if segments else para_end,
            "text": " ".join(current_para)
        })

    return {
        "language": result.get("language", "en"),
        "paragraphs": paragraphs
    }


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
