"""
Extract Insights Step - Wrapper for extract_insights_structured
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent to path
LENS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(LENS_DIR))

from extract_insights_structured import extract_earnings_insights


def extract_insights_step(job_dir: Path, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract earnings insights (step handler wrapper)

    Args:
        job_dir: Job directory path
        job_data: Job data dict

    Returns:
        Result dict with insights path
    """
    # Get confirmed metadata from previous step
    confirmed_meta = job_data.get('processing', {}).get('confirm_metadata', {}).get('confirmed', {})

    if not confirmed_meta:
        raise ValueError("No confirmed metadata found. Run 'confirm_metadata' step first.")

    company_name = confirmed_meta.get('company')
    ticker = confirmed_meta.get('ticker')
    quarter_only = confirmed_meta.get('quarter')
    year = confirmed_meta.get('year')

    if not all([company_name, ticker, quarter_only, year]):
        raise ValueError(
            f"Missing required metadata: "
            f"company={company_name}, ticker={ticker}, quarter={quarter_only}, year={year}"
        )

    # Combine quarter and year for insights extraction (e.g., "Q4-2025")
    quarter = f"{quarter_only}-{year}"

    # Find transcript file
    transcript_file = job_dir / "transcripts" / "transcript.json"
    if not transcript_file.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_file}")

    # Output file for insights
    output_file = job_dir / "insights.raw.json"

    print(f"📊 Extracting insights for {company_name} ({ticker}) {quarter}")

    # Call insights extraction
    insights = extract_earnings_insights(
        transcript_file=transcript_file,
        company_name=company_name,
        ticker=ticker,
        quarter=quarter,
        output_file=output_file
    )

    # Return result
    return {
        'insights_file': str(output_file),
        'company': company_name,
        'ticker': ticker,
        'quarter': quarter,
        'year': year,
        'metrics_count': len(insights.financial_metrics) if hasattr(insights, 'financial_metrics') else 0,
        'highlights_count': len(insights.highlights) if hasattr(insights, 'highlights') else 0
    }
