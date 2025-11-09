"""
MarketHawk Job Pipeline Processor
Reads job.yaml and executes processing steps
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add scripts to path
LENS_DIR = Path(__file__).parent
sys.path.insert(0, str(LENS_DIR / "scripts"))

from job import JobManager
from download_source import download_video
from parse_metadata import parse_video_metadata
from download_hls import download_hls_stream
from transcribe_whisperx import transcribe_earnings_call
from extract_insights_structured import extract_earnings_insights

# Directories
DOWNLOADS_DIR = Path(os.getenv("DOWNLOADS_DIR", "/var/markethawk/_downloads"))
ORGANIZED_DIR = Path(os.getenv("ORGANIZED_DIR", "/var/markethawk"))


class JobPipeline:
    """Process job through all pipeline steps"""

    def __init__(self, job_file: Path):
        self.job = JobManager(job_file)
        self.job_dir = job_file.parent  # Job directory for collocated files

    def run_all(self):
        """Run all pipeline steps"""
        print(f"Processing job: {self.job.job['job_id']}")
        print("-" * 60)

        self.job.set_status("processing")

        try:
            self.step_download()
            self.step_parse()
            self.step_transcribe()
            self.step_detect_trim()
            self.step_insights()
            # Note: render and upload are manual for now

            self.job.set_status("completed")
            print("\n✓ Job completed successfully!")

        except Exception as e:
            self.job.set_status("failed")
            print(f"\n✗ Job failed: {e}")
            raise

    def run_step(self, step_name: str):
        """Run single step"""
        steps = {
            "download": self.step_download,
            "parse": self.step_parse,
            "transcribe": self.step_transcribe,
            "detect_trim": self.step_detect_trim,
            "insights": self.step_insights,
        }

        if step_name not in steps:
            raise ValueError(f"Unknown step: {step_name}")

        print(f"Running step: {step_name}")
        steps[step_name]()

    def run_from_step(self, step_name: str):
        """Run from specific step onwards"""
        all_steps = ["download", "parse", "transcribe", "detect_trim", "insights"]

        try:
            start_idx = all_steps.index(step_name)
        except ValueError:
            raise ValueError(f"Unknown step: {step_name}")

        for step in all_steps[start_idx:]:
            self.run_step(step)

    def step_download(self):
        """Step 1: Download video"""
        print("\n[1/5] Downloading video...")

        step_data = self.job.get_step("download")
        if step_data.get('status') == 'completed':
            print("  Already downloaded, skipping")
            return

        # Get input
        input_data = self.job.job['input']
        input_type = input_data['type']
        input_value = input_data['value']

        if input_type == 'youtube_url':
            # Download from YouTube to job_dir/input/
            result = download_video(input_value, str(self.job_dir / "input"))
            video_file = self.job_dir / "input" / "source.mp4"

            self.job.update_step("download", "completed",
                file=str(video_file)
            )

            print(f"  ✓ Downloaded: {video_file}")

        elif input_type == 'hls_stream':
            # Download HLS stream with ffmpeg to job_dir/input/
            result = download_hls_stream(input_value, str(self.job_dir))
            video_file = result['file']

            self.job.update_step("download", "completed",
                file=str(video_file)
            )

            print(f"  ✓ Downloaded: {video_file}")

        elif input_type == 'local_file':
            raise NotImplementedError("Local file support coming soon")
        else:
            raise ValueError(f"Unsupported input type: {input_type}")

    def step_parse(self):
        """Step 2: Parse metadata (YouTube only, skip for HLS)"""
        print("\n[2/5] Parsing metadata...")

        step_data = self.job.get_step("parse")
        if step_data.get('status') == 'completed':
            print("  Already parsed, skipping")
            return

        # Skip for HLS streams (metadata provided at job creation)
        input_type = self.job.job['input']['type']
        if input_type == 'hls_stream':
            print("  ✓ Skipping (HLS stream - metadata from job)")
            self.job.update_step("parse", "completed", output={
                'ticker_detected': self.job.job['company']['ticker'],
                'quarter_detected': self.job.job['company']['quarter'],
                'company_name': self.job.job['company']['name']
            })
            return

        self.job.update_step("parse", "running")

        # For YouTube: Parse metadata from downloaded file
        metadata_file = self.job_dir / "input" / "metadata.json"

        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        # Parse
        result = parse_video_metadata(str(metadata_file))

        self.job.update_step("parse", "completed", output={
            'ticker_detected': result.get('ticker'),
            'quarter_detected': result.get('quarter'),
            'company_name': result.get('company_name')
        })

        print(f"  ✓ Detected: {result.get('ticker')} {result.get('quarter')}")

    def step_transcribe(self):
        """Step 3: Transcribe with Whisper"""
        print("\n[3/5] Transcribing with Whisper...")

        step_data = self.job.get_step("transcribe")
        if step_data.get('status') == 'completed':
            print("  Already transcribed, skipping")
            return

        self.job.update_step("transcribe", "running")

        # Get video file from job directory
        video_file = self.job_dir / "input" / "source.mp4"

        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_file}")

        # Run WhisperX transcription with speaker diarization
        transcripts_dir = self.job_dir / "transcripts"

        try:
            result = transcribe_earnings_call(
                video_file=video_file,
                output_dir=transcripts_dir,
                model_size="medium",
                language="en"
            )
        except Exception as e:
            self.job.update_step("transcribe", "failed", error=str(e))
            raise RuntimeError(f"Transcription failed: {e}")

        transcript_file = transcripts_dir / "transcript.json"

        # Get duration from segments
        segments = result.get('segments', [])
        duration = segments[-1].get('end', 0) if segments else 0

        # Count words
        word_count = sum(len(seg.get('text', '').split()) for seg in segments)

        self.job.update_step("transcribe", "completed", output={
            'transcript_file': str(transcript_file),
            'word_count': word_count,
            'duration_seconds': duration,
            'model_used': 'whisperx-medium',
            'has_speaker_diarization': True
        })

        print(f"  ✓ Transcribed: {transcript_file}")

    def step_detect_trim(self):
        """Step 4: Detect trim point (no actual trimming!)"""
        print("\n[4/5] Detecting trim point...")

        step_data = self.job.get_step("detect_trim")
        if step_data.get('status') == 'completed':
            print("  Already detected, skipping")
            return

        # Get transcript from job directory
        transcript_file = self.job_dir / "transcripts" / "transcript.json"

        if not transcript_file.exists():
            raise FileNotFoundError("Transcript not found. Run transcribe step first.")

        # Find first speech
        with open(transcript_file, 'r') as f:
            transcript = json.load(f)

        first_segment = transcript.get('segments', [{}])[0]
        first_speech_time = first_segment.get('start', 0)

        # Keep 5 seconds before first speech (for intro music)
        pre_speech_buffer = 5.0
        trim_start = max(0, first_speech_time - pre_speech_buffer)

        # Update both top-level (human-editable) and processing section
        self.job.job['trim_start_seconds'] = trim_start
        self.job.update_step("detect_trim", "completed",
            first_speech_at=first_speech_time
        )

        print(f"  ✓ Video will start at: {trim_start:.2f}s (first speech at {first_speech_time:.2f}s)")
        print(f"  ✓ Edit 'trim_start_seconds' in job.yaml to adjust")

    def step_insights(self):
        """Step 5: Extract insights with OpenAI"""
        print("\n[5/5] Extracting insights with OpenAI...")

        step_data = self.job.get_step("insights")
        if step_data.get('status') == 'completed':
            print("  Already extracted, skipping")
            return

        self.job.update_step("insights", "running")

        # Get data from job
        company_name = self.job.job['company']['name']
        ticker = self.job.job['company']['ticker']
        quarter = self.job.job['company']['quarter']

        # Transcript file in job directory
        transcript_file = self.job_dir / "transcripts" / "transcript.json"

        if not transcript_file.exists():
            raise FileNotFoundError("Transcript not found. Run transcribe step first.")

        # Run insights extraction with OpenAI structured outputs
        raw_output = self.job_dir / "insights.raw.json"

        try:
            insights = extract_earnings_insights(
                transcript_file=transcript_file,
                company_name=company_name,
                ticker=ticker,
                quarter=quarter,
                output_file=raw_output
            )
        except Exception as e:
            self.job.update_step("insights", "failed", error=str(e))
            raise RuntimeError(f"Insights extraction failed: {e}")

        # Save usage stats
        with open(raw_output, 'r') as f:
            raw_data = json.load(f)
            if 'usage' in raw_data:
                usage_file = self.job_dir / "usage.json"
                with open(usage_file, 'w') as f:
                    json.dump(raw_data['usage'], f, indent=2)

        # Merge insights into job.yaml
        self.job.update_step("insights", "completed", output=insights.model_dump())

        print(f"  ✓ Insights extracted")
        print(f"    Raw backup: {raw_output}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python process_job_pipeline.py <job_file>")
        sys.exit(1)

    from pathlib import Path
    job_file = Path(sys.argv[1])

    pipeline = JobPipeline(job_file)
    pipeline.run_all()
