"""
Step Handlers for MarketHawk Workflow System

Each handler is a function that takes (job_dir: Path, job_data: Dict) and returns result Dict
"""

__all__ = [
    'copy_audio_to_job',
    'extract_metadata_llm',
    'interactive_confirm_metadata',
    'upload_artifacts_r2',
    'upload_media_r2',
    'update_database',
    'notify_seo',
]
