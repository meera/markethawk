#!/usr/bin/env python3
"""
Download SEC company tickers data.

Downloads the official SEC company_tickers.json file containing all publicly
traded US companies with clean names (no "Common Stock" suffixes).

Usage:
    python lens/scripts/download_sec_companies.py
"""

import requests
from pathlib import Path
import sys

# Configuration
SEC_URL = "https://www.sec.gov/files/company_tickers.json"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "sec_company_tickers.json"

# SEC requires User-Agent header
HEADERS = {
    'User-Agent': 'MarketHawkEye info@markethawkeye.com'
}

def download_sec_data():
    """Download SEC company tickers JSON."""
    print("\n" + "🦅" * 35)
    print("DOWNLOAD SEC COMPANY TICKERS")
    print("🦅" * 35 + "\n")

    print(f"📡 Downloading from: {SEC_URL}")

    try:
        response = requests.get(SEC_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()

        # Save to file
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(response.text, encoding='utf-8')

        # Parse and count
        data = response.json()
        company_count = len(data)

        print(f"✅ Downloaded {company_count:,} companies")
        print(f"💾 Saved to: {OUTPUT_FILE}")

        # Show sample
        print("\n📊 Sample entries:")
        for i, (key, company) in enumerate(list(data.items())[:5]):
            cik = company.get('cik_str', company.get('cik', 'N/A'))
            ticker = company.get('ticker', 'N/A')
            title = company.get('title', 'N/A')
            print(f"   {ticker:6} - {title}")

        print(f"\n✅ Complete! Ready to process.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        print("\n💡 Note: SEC may block requests without proper User-Agent header")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = download_sec_data()
    sys.exit(0 if success else 1)
