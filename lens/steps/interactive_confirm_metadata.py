"""
Interactive Metadata Confirmation

Shows extracted metadata to user and allows confirmation or editing
"""

from pathlib import Path
from typing import Dict, Any


def interactive_confirm_metadata(job_dir: Path, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Show extracted metadata to user for confirmation or editing

    Args:
        job_dir: Job directory path
        job_data: Job data dict (must contain processing.extract_metadata.extracted)

    Returns:
        Result dict with confirmed metadata
    """
    # Get extracted metadata from previous step
    extract_metadata_result = job_data.get('processing', {}).get('extract_metadata', {})
    if not extract_metadata_result:
        raise ValueError(
            "No metadata extraction results found. Run 'extract_metadata' step first"
        )

    extracted = extract_metadata_result.get('extracted', {})
    ticker = extracted.get('ticker')
    company = extracted.get('company')
    quarter = extracted.get('quarter')
    year = extracted.get('year')

    print(f"\n{'='*60}")
    print("Extracted Metadata (confirm or edit):")
    print(f"{'='*60}")
    print(f"Ticker: {ticker or '(not found)'}")
    print(f"Company: {company or '(not found)'}")
    print(f"Quarter: {quarter or '(not found)'}")
    print(f"Year: {year or '(not found)'}")
    print(f"{'='*60}\n")

    # Prompt user for confirmation
    while True:
        response = input("Confirm? (y/n/edit): ").strip().lower()

        if response == 'y':
            # User confirmed - use extracted values
            print("✅ Metadata confirmed")
            confirmed_ticker = ticker
            confirmed_company = company
            confirmed_quarter = quarter
            confirmed_year = year
            break

        elif response == 'n':
            # User rejected - prompt for all fields
            print("\n📝 Enter metadata manually:\n")
            confirmed_ticker = input(f"Ticker: ").strip() or None
            confirmed_company = input(f"Company: ").strip() or None
            confirmed_quarter = input(f"Quarter (e.g., Q3): ").strip() or None
            year_input = input(f"Year (e.g., 2024): ").strip()
            confirmed_year = int(year_input) if year_input else None
            break

        elif response == 'edit':
            # User wants to edit - show defaults and allow overrides
            print("\n📝 Edit metadata (press Enter to keep current value):\n")
            confirmed_ticker = input(f"Ticker [{ticker}]: ").strip() or ticker
            confirmed_company = input(f"Company [{company}]: ").strip() or company
            confirmed_quarter = input(f"Quarter [{quarter}]: ").strip() or quarter
            year_input = input(f"Year [{year}]: ").strip()
            confirmed_year = int(year_input) if year_input else year
            break

        else:
            print("Invalid response. Please enter 'y', 'n', or 'edit'")

    # Validate required fields
    if not all([confirmed_ticker, confirmed_company, confirmed_quarter, confirmed_year]):
        raise ValueError(
            f"Missing required metadata fields:\n"
            f"  Ticker: {confirmed_ticker}\n"
            f"  Company: {confirmed_company}\n"
            f"  Quarter: {confirmed_quarter}\n"
            f"  Year: {confirmed_year}\n"
            "All fields are required. Please run again and provide complete metadata."
        )

    print(f"\n✅ Final Metadata:")
    print(f"   Ticker: {confirmed_ticker}")
    print(f"   Company: {confirmed_company}")
    print(f"   Quarter: {confirmed_quarter}")
    print(f"   Year: {confirmed_year}\n")

    # IMPORTANT: Update top-level company section in job_data
    # This ensures upload_youtube and other steps use correct company info
    if 'company' not in job_data:
        job_data['company'] = {}

    job_data['company']['ticker'] = confirmed_ticker
    job_data['company']['name'] = confirmed_company
    job_data['company']['quarter'] = confirmed_quarter
    job_data['company']['year'] = confirmed_year

    return {
        'confirmed': {
            'ticker': confirmed_ticker,
            'company': confirmed_company,
            'quarter': confirmed_quarter,
            'year': confirmed_year,
        },
        'method': 'interactive',
        'updated_job_company': True  # Flag that we updated top-level company
    }
