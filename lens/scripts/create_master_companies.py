#!/usr/bin/env python3
"""
Create master companies CSV with slugs.

Merges SEC company data (clean names, CIK) with NASDAQ screener data (financial info),
generates URL-friendly slugs, and outputs master CSV for database import.

Usage:
    python lens/scripts/create_master_companies.py
"""

import json
import csv
import re
from pathlib import Path
from collections import Counter
import sys

# Configuration
DATA_DIR = Path(__file__).parent.parent.parent / "data"
SEC_FILE = DATA_DIR / "sec_company_tickers.json"
NASDAQ_FILE = DATA_DIR / "nasdaq_screener_cleaned.csv"
OUTPUT_FILE = DATA_DIR / "companies_master.csv"

def generate_slug(company_name):
    """Generate URL-friendly slug from company name."""
    # Convert to lowercase
    slug = company_name.lower()

    # Remove common suffixes
    slug = re.sub(r'\s+(inc\.?|corp\.?|corporation|company|co\.?|ltd\.?|llc|lp|plc)$', '', slug, flags=re.IGNORECASE)

    # Replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)

    return slug

def is_derivative_security(ticker):
    """Check if ticker is a warrant, unit, preferred share, or other derivative."""
    ticker = ticker.upper()

    # Patterns that indicate derivative securities
    derivative_patterns = [
        '-WT', '-WS', 'W', '.WS',  # Warrants
        '-UN', '-U', '.U',  # Units
        '-P', '.P',  # Preferred shares (e.g., ACR-PC, ACR-PD)
        '-R', '.R',  # Rights
        '/', '=', '+',  # Special characters
    ]

    for pattern in derivative_patterns:
        if pattern in ticker:
            return True

    return False

def load_sec_data():
    """Load SEC company tickers (common stock only)."""
    print("📖 Loading SEC data...")
    with SEC_FILE.open('r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert to list of dicts, filter out derivatives
    companies = []
    filtered_count = 0

    for key, company in data.items():
        ticker = company.get('ticker', '').strip().upper()
        name = company.get('title', '').strip()
        cik_str = str(company.get('cik_str', company.get('cik', '')))

        # Skip derivative securities
        if is_derivative_security(ticker):
            filtered_count += 1
            continue

        companies.append({
            'cik_str': cik_str,
            'ticker': ticker,
            'name': name,
        })

    print(f"   ✅ Loaded {len(companies):,} companies from SEC")
    print(f"   ℹ️  Filtered out {filtered_count:,} derivative securities (warrants, units, preferred)")
    return companies

def load_nasdaq_data():
    """Load NASDAQ screener data for enrichment."""
    print("📖 Loading NASDAQ screener data...")

    if not NASDAQ_FILE.exists():
        print("   ⚠️  NASDAQ file not found - will use SEC data only")
        return {}

    nasdaq_by_ticker = {}
    with NASDAQ_FILE.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row.get('Symbol', '').strip().upper()
            if ticker:
                nasdaq_by_ticker[ticker] = {
                    'exchange': 'NASDAQ',  # All from NASDAQ screener
                    'market_cap': row.get('Market Cap', ''),
                    'sector': row.get('Sector', ''),
                    'industry': row.get('Industry', ''),
                    'ipo_year': row.get('IPO Year', ''),
                    'country': row.get('Country', ''),
                }

    print(f"   ✅ Loaded {len(nasdaq_by_ticker):,} companies from NASDAQ")
    return nasdaq_by_ticker

def merge_and_generate_slugs():
    """Merge SEC and NASDAQ data, generate slugs."""
    print("\n🔨 Merging data and generating slugs...")

    sec_companies = load_sec_data()
    nasdaq_data = load_nasdaq_data()

    # Deduplicate by CIK (keep ticker that's in NASDAQ, or first one)
    print("   🔍 Deduplicating by CIK...")
    cik_to_company = {}
    for company in sec_companies:
        cik = company['cik_str']
        ticker = company['ticker']

        # If we haven't seen this CIK, or this ticker is in NASDAQ, use it
        if cik not in cik_to_company or ticker in nasdaq_data:
            cik_to_company[cik] = company

    sec_companies = list(cik_to_company.values())
    print(f"   ✅ Kept {len(sec_companies):,} unique companies (by CIK)")

    # First pass: generate base slugs and count duplicates
    slug_counts = Counter()
    for company in sec_companies:
        name = company['name']
        if name:
            base_slug = generate_slug(name)
            slug_counts[base_slug] += 1

    # Second pass: assign slugs with ticker suffix for duplicates
    companies = []
    slug_usage = Counter()

    for company in sec_companies:
        ticker = company['ticker']
        name = company['name']
        cik_str = company['cik_str']

        if not ticker or not name:
            continue

        # Generate base slug
        base_slug = generate_slug(name)

        # If this slug has duplicates, append ticker to make unique
        if slug_counts[base_slug] > 1:
            slug = f"{base_slug}-{ticker.lower()}"
        else:
            slug = base_slug

        slug_usage[slug] += 1

        # Get NASDAQ enrichment data
        nasdaq_info = nasdaq_data.get(ticker, {})

        # Build metadata JSON
        metadata = {}
        if nasdaq_info:
            if nasdaq_info.get('exchange'):
                metadata['exchange'] = nasdaq_info['exchange']
            if nasdaq_info.get('market_cap'):
                try:
                    metadata['market_cap'] = int(float(nasdaq_info['market_cap']))
                except:
                    pass
            if nasdaq_info.get('sector'):
                metadata['sector'] = nasdaq_info['sector']
            if nasdaq_info.get('industry'):
                metadata['industry'] = nasdaq_info['industry']
            if nasdaq_info.get('ipo_year'):
                try:
                    metadata['ipo_year'] = int(nasdaq_info['ipo_year'])
                except:
                    pass
            if nasdaq_info.get('country'):
                metadata['country'] = nasdaq_info['country']

        companies.append({
            'cik_str': cik_str,
            'symbol': ticker,
            'name': name,
            'slug': slug,
            'metadata_json': json.dumps(metadata) if metadata else '{}',
        })

    print(f"   ✅ Generated {len(companies):,} company records")

    # Check for duplicate slugs (should be none after ticker suffix logic)
    duplicates = [slug for slug, count in slug_usage.items() if count > 1]
    if duplicates:
        print(f"\n⚠️  WARNING: Found {len(duplicates)} duplicate slugs:")
        for slug in duplicates[:10]:  # Show first 10
            matching = [c for c in companies if c['slug'] == slug]
            print(f"   '{slug}' →", ', '.join([f"{c['name']} ({c['symbol']})" for c in matching]))

        print("\n❌ ABORTED: Duplicate slugs detected!")
        print("💡 Fix: Adjust slug generation logic or handle conflicts")
        sys.exit(1)

    print("   ✅ All slugs are unique!")
    print(f"   ℹ️  {sum(1 for s in companies if slug_counts[generate_slug(s['name'])] > 1):,} slugs include ticker suffix to resolve conflicts")

    return companies

def save_master_csv(companies):
    """Save master CSV file."""
    print("\n💾 Saving master CSV...")

    with OUTPUT_FILE.open('w', newline='', encoding='utf-8') as f:
        fieldnames = ['cik_str', 'symbol', 'name', 'slug', 'metadata_json']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(companies)

    print(f"   ✅ Saved {len(companies):,} companies to {OUTPUT_FILE}")

    # Show sample with metadata
    print("\n📊 Sample entries:")
    for company in companies[:5]:
        metadata = json.loads(company['metadata_json'])
        exchange = metadata.get('exchange', 'N/A')
        sector = metadata.get('sector', 'N/A')
        print(f"   {company['symbol']:6} - {company['slug']:30} ({exchange}, {sector})")

def main():
    print("\n" + "🦅" * 35)
    print("CREATE MASTER COMPANIES CSV")
    print("🦅" * 35 + "\n")

    # Check inputs
    if not SEC_FILE.exists():
        print(f"❌ SEC file not found: {SEC_FILE}")
        print("💡 Run: python lens/scripts/download_sec_companies.py")
        sys.exit(1)

    # Merge and generate
    companies = merge_and_generate_slugs()

    # Save
    save_master_csv(companies)

    print("\n" + "=" * 70)
    print("🎉 SUCCESS!")
    print("=" * 70)
    print(f"\n✅ Master CSV ready: {OUTPUT_FILE}")
    print(f"✅ {len(companies):,} companies with unique slugs")
    print("\n📊 Next steps:")
    print("   1. Commit to Git: git add data/companies_master.csv")
    print("   2. Update database: python lens/scripts/migrate_companies_db.py\n")

if __name__ == "__main__":
    main()
