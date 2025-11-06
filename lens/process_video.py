#!/usr/bin/env python3
"""
Complete video processing pipeline for EarningLens on sushi GPU machine

Runs:
1. Whisper transcription (GPU accelerated)
2. LLM insights extraction (OpenAI API)

Usage:
    python sushi/process_video.py <video_file>

Example:
    python sushi/process_video.py uploads/jUnV3LiN0_k.mp4

Environment Variables Required:
    OPENAI_API_KEY - OpenAI API key for insights generation
"""

import os
import sys
import json
import time
from pathlib import Path
import logging

# Import local modules
from transcribe import transcribe_file
from insights_generator import extract_insights_from_paragraphs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_video_complete(
    filepath: str,
    whisper_model: str = "medium",
    llm_model: str = "gpt-4o-mini"
) -> bool:
    """
    Complete processing pipeline:
    1. Transcribe with Whisper
    2. Extract insights with LLM

    Args:
        filepath: Path to video/audio file
        whisper_model: Whisper model name (tiny, base, small, medium, large)
        llm_model: OpenAI model name (gpt-4o-mini, gpt-4o, etc.)

    Returns:
        bool: Success status
    """

    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return False

    base_filename = os.path.splitext(os.path.basename(filepath))[0]
    output_dir = os.path.dirname(filepath)

    logger.info("="*60)
    logger.info("EarningLens Video Processing Pipeline")
    logger.info("="*60)
    logger.info(f"Input file: {filepath}")
    logger.info(f"Whisper model: {whisper_model}")
    logger.info(f"LLM model: {llm_model}")
    logger.info("="*60)

    # Step 1: Transcription
    logger.info("\n🎙️  STEP 1: Whisper Transcription")
    logger.info("-" * 60)

    transcribe_start = time.time()
    success = transcribe_file(filepath, model_name=whisper_model)

    if not success:
        logger.error("Transcription failed")
        return False

    transcribe_duration = time.time() - transcribe_start
    logger.info(f"✅ Transcription completed in {transcribe_duration:.1f}s")

    # Step 2: LLM Insights Extraction
    logger.info("\n🤖 STEP 2: LLM Insights Extraction")
    logger.info("-" * 60)

    # Load paragraphs.json
    paragraphs_path = os.path.join(output_dir, f"{base_filename}.paragraphs.json")

    if not os.path.exists(paragraphs_path):
        logger.error(f"paragraphs.json not found: {paragraphs_path}")
        return False

    with open(paragraphs_path, 'r', encoding='utf-8') as f:
        paragraphs = json.load(f)

    # Extract insights
    llm_start = time.time()

    insights_result = extract_insights_from_paragraphs(
        paragraphs=paragraphs,
        filename=base_filename,
        input_context="Earnings call transcription",
        job_data={'llm_model': llm_model}
    )

    if not insights_result:
        logger.error("LLM insights extraction failed")
        return False

    llm_duration = time.time() - llm_start

    # Save insights to file
    insights_path = os.path.join(output_dir, f"{base_filename}.insights.json")

    with open(insights_path, 'w', encoding='utf-8') as f:
        json.dump(insights_result['result'], f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Insights extraction completed in {llm_duration:.1f}s")
    logger.info(f"📄 Insights saved to: {insights_path}")

    # Print summary
    logger.info("\n" + "="*60)
    logger.info("PROCESSING COMPLETE")
    logger.info("="*60)

    result_data = insights_result['result']

    logger.info(f"\n📋 Metadata:")
    logger.info(f"  Title: {result_data.get('metadata', {}).get('title')}")
    logger.info(f"  Content Type: {result_data.get('metadata', {}).get('content_type')}")
    logger.info(f"  Participants: {result_data.get('metadata', {}).get('participants_count')}")

    logger.info(f"\n👥 Identified Speakers:")
    for speaker_id, name in result_data.get('speaker_names', {}).items():
        if name:
            logger.info(f"  {speaker_id}: {name}")

    logger.info(f"\n📊 Insights:")
    insights = result_data.get('insights', {})
    logger.info(f"  Key Takeaways: {len(insights.get('key_takeaways', []))} points")
    logger.info(f"  Keywords: {len(insights.get('keywords', []))} terms")
    logger.info(f"  Table of Contents: {len(result_data.get('table_of_contents', []))} sections")

    logger.info(f"\n💰 API Usage:")
    usage = insights_result.get('usage', {})
    logger.info(f"  Model: {insights_result.get('model')}")
    logger.info(f"  Tokens: {usage.get('total_tokens', 0):,}")
    logger.info(f"  Prompt: {usage.get('prompt_tokens', 0):,}")
    logger.info(f"  Completion: {usage.get('completion_tokens', 0):,}")

    logger.info(f"\n⏱️  Total Time: {transcribe_duration + llm_duration:.1f}s")
    logger.info("="*60)

    # List all generated files
    logger.info(f"\n📁 Generated Files:")
    for ext in ['.json', '.srt', '.vtt', '.txt', '.paragraphs.json', '.insights.json']:
        file_path = os.path.join(output_dir, f"{base_filename}{ext}")
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / 1024  # KB
            logger.info(f"  ✓ {base_filename}{ext} ({file_size:.1f} KB)")

    return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python sushi/process_video.py <video_file> [whisper_model] [llm_model]")
        print("\nExamples:")
        print("  python sushi/process_video.py uploads/video.mp4")
        print("  python sushi/process_video.py uploads/video.mp4 medium gpt-4o-mini")
        print("\nWhisper Models: tiny, base, small, medium, large")
        print("LLM Models: gpt-4o-mini, gpt-4o, gpt-4-turbo")
        print("\nEnvironment Variables:")
        print("  OPENAI_API_KEY - Required for LLM insights")
        sys.exit(1)

    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY environment variable not set")
        logger.error("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    filepath = sys.argv[1]
    whisper_model = sys.argv[2] if len(sys.argv) > 2 else "medium"
    llm_model = sys.argv[3] if len(sys.argv) > 3 else "gpt-4o-mini"

    success = process_video_complete(filepath, whisper_model, llm_model)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
