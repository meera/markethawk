"""
Refine Timestamps Step - Wrapper for refine_timestamps
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent to path
LENS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(LENS_DIR))

from refine_timestamps import refine_job_timestamps


def refine_timestamps_step(job_dir: Path, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refine timestamps to word-level precision (step handler wrapper)

    Args:
        job_dir: Job directory path
        job_data: Job data dict

    Returns:
        Result dict with refinement statistics
    """
    # Find job.yaml path
    job_yaml_path = job_dir / "job.yaml"
    if not job_yaml_path.exists():
        raise FileNotFoundError(f"job.yaml not found: {job_yaml_path}")

    # Find transcript.json path (convention-based)
    transcript_path = job_dir / "transcripts" / "transcript.json"
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    # Call refine_timestamps
    result = refine_job_timestamps(
        job_yaml_path=job_yaml_path,
        transcript_path=transcript_path,
        window_seconds=30
    )

    # Return result
    return result
