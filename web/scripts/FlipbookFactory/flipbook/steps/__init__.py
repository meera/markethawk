"""
FlipbookFactory processing steps.

Import all steps here to register them automatically.
"""

from flipbook.steps.download_video import DownloadVideo
from flipbook.steps.extract_frames import ExtractFrames

# Auto-register all steps when this module is imported
__all__ = ['DownloadVideo', 'ExtractFrames']
