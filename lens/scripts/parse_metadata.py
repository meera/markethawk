#!/usr/bin/env python3
"""
Parse video metadata to infer company ticker and quarter.
Uses multiple signals: title, description, channel name, publish date.
"""

import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple


# Common ticker mappings
TICKER_MAP = {
    "palantir": "PLTR",
    "palantir technologies": "PLTR",
    "apple": "AAPL",
    "microsoft": "MSFT",
    "alphabet": "GOOGL",
    "google": "GOOGL",
    "amazon": "AMZN",
    "tesla": "TSLA",
    "nvidia": "NVDA",
    "meta": "META",
    "facebook": "META",
    "netflix": "NFLX",
    "amd": "AMD",
    "intel": "INTC",
    "oracle": "ORCL",
    "salesforce": "CRM",
    "adobe": "ADBE",
}


class MetadataParser:
    """Parse earnings call metadata to extract company and quarter"""

    def __init__(self, metadata_path: str):
        self.metadata_path = Path(metadata_path)
        with open(self.metadata_path, "r") as f:
            self.metadata = json.load(f)

    def parse(self) -> Dict:
        """Parse metadata and return company/quarter info"""

        title = self.metadata.get("title", "")
        description = self.metadata.get("description", "")
        channel = self.metadata.get("channel", {})
        channel_name = channel.get("name", "") if isinstance(channel, dict) else ""

        # Extract ticker
        ticker = self._extract_ticker(title, description)

        # Extract quarter
        quarter = self._extract_quarter(title, description)

        # Extract company name
        company_name = self._extract_company_name(title, channel_name)

        # If no ticker found, try to look it up
        if not ticker and company_name:
            ticker = self._lookup_ticker(company_name)

        # Calculate confidence
        confidence = self._calculate_confidence(ticker, quarter, company_name)

        return {
            "ticker": ticker,
            "quarter": quarter,
            "company_name": company_name,
            "confidence": confidence,
            "title": title,
            "description": description[:200],  # First 200 chars
        }

    def _extract_ticker(self, title: str, description: str) -> Optional[str]:
        """Extract ticker symbol from text"""

        # Look for patterns like (NYSE: PLTR), (NASDAQ: AAPL), (PLTR)
        patterns = [
            r'\((?:NYSE|NASDAQ|TSX):\s*([A-Z]{1,5})\)',  # (NYSE: PLTR)
            r'\(([A-Z]{2,5})\)',  # (PLTR)
            r'NYSE:\s*([A-Z]{1,5})',  # NYSE: PLTR
            r'NASDAQ:\s*([A-Z]{1,5})',  # NASDAQ: AAPL
        ]

        for pattern in patterns:
            # Try description first (usually has ticker)
            match = re.search(pattern, description)
            if match:
                return match.group(1)

            # Then try title
            match = re.search(pattern, title)
            if match:
                return match.group(1)

        return None

    def _extract_quarter(self, title: str, description: str) -> Optional[str]:
        """Extract quarter from text"""

        # Look for Q1/Q2/Q3/Q4 followed by year
        patterns = [
            r'Q([1-4])\s+(\d{4})',  # Q3 2024
            r'([1-4])Q\s+(\d{4})',  # 3Q 2024
            r'Q([1-4])\s+FY\s*(\d{4})',  # Q3 FY 2024
        ]

        for pattern in patterns:
            # Try title first
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                q_num = match.group(1)
                year = match.group(2)
                return f"Q{q_num}-{year}"

            # Then try description
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                q_num = match.group(1)
                year = match.group(2)
                return f"Q{q_num}-{year}"

        return None

    def _extract_company_name(self, title: str, channel_name: str) -> Optional[str]:
        """Extract company name from title or channel"""

        # Try to extract from title (usually "Company Name | Q3 2024 Earnings")
        if "|" in title:
            parts = title.split("|")
            company = parts[0].strip()
            # Clean up common suffixes
            company = re.sub(r'\s+(Inc\.|Corp\.|Ltd\.|LLC)$', '', company, flags=re.IGNORECASE)
            return company

        # Fallback to channel name
        if channel_name:
            return channel_name

        return None

    def _lookup_ticker(self, company_name: str) -> Optional[str]:
        """Lookup ticker from company name"""

        # Normalize company name
        normalized = company_name.lower().strip()

        # Direct lookup
        if normalized in TICKER_MAP:
            return TICKER_MAP[normalized]

        # Try partial matches
        for key, ticker in TICKER_MAP.items():
            if key in normalized or normalized in key:
                return ticker

        return None

    def _calculate_confidence(self, ticker: Optional[str], quarter: Optional[str],
                            company_name: Optional[str]) -> str:
        """Calculate confidence level"""

        if ticker and quarter:
            return "high"
        elif (ticker or company_name) and quarter:
            return "medium"
        elif ticker or quarter:
            return "low"
        else:
            return "very_low"


def parse_video_metadata(metadata_path: str) -> Dict:
    """
    Parse video metadata to extract company and quarter information.

    Args:
        metadata_path: Path to metadata.json file

    Returns:
        Dictionary with parsed data including ticker, quarter, company_name, and confidence
    """
    parser_obj = MetadataParser(metadata_path)
    result = parser_obj.parse()
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Parse video metadata to infer company and quarter"
    )
    parser.add_argument(
        "metadata_path",
        help="Path to metadata.json (e.g., /var/markethawk/_downloads/jUnV3LiN0_k/input/metadata.json)"
    )

    args = parser.parse_args()

    # Parse metadata
    try:
        result = parse_video_metadata(args.metadata_path)

        # Print results
        print(f"📄 Parsed metadata:")
        print(f"  Company: {result['company_name']}")
        print(f"  Ticker: {result['ticker'] or 'NOT FOUND'}")
        print(f"  Quarter: {result['quarter'] or 'NOT FOUND'}")
        print(f"  Confidence: {result['confidence']}")
        print()
        print(f"  Title: {result['title']}")

        # Output as JSON for scripting
        print()
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
