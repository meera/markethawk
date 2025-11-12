#!/usr/bin/env python3
"""
Import NASDAQ screener CSV directly to database.

This script imports the NASDAQ screener CSV file downloaded from:
https://www.nasdaq.com/market-activity/stocks/screener

Usage:
    python import_nasdaq_screener.py [--csv-file PATH]

Environment:
    DATABASE_URL - PostgreSQL connection string
"""

import psycopg2
import csv
import os
import sys
from pathlib import Path
import argparse

# Configuration
DATA_DIR = Path(__file__).parent.parent.parent / "data"
SCREENER_FILE_PATTERN = "nasdaq_screener*.csv"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@192.168.86.250:54322/postgres")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Import NASDAQ screener CSV to database')
    parser.add_argument('--csv-file', type=str, default=None,
                        help='Path to NASDAQ screener CSV file')
    return parser.parse_args()

def find_screener_csv(csv_file=None):
    """Find NASDAQ screener CSV file."""
    if csv_file:
        csv_path = Path(csv_file)
        if not csv_path.exists():
            print(f"❌ File {csv_path} not found")
            sys.exit(1)
        return csv_path

    # Look for nasdaq_screener*.csv in data directory
    csv_files = list(DATA_DIR.glob(SCREENER_FILE_PATTERN))
    if not csv_files:
        print("❌ No nasdaq_screener*.csv found in data/ directory")
        print("\n📥 To download:")
        print("   1. Visit: https://www.nasdaq.com/market-activity/stocks/screener")
        print("   2. Click: 'Download CSV'")
        print("   3. Save to: data/nasdaq_screener.csv")
        sys.exit(1)

    # Use most recent file
    csv_path = max(csv_files, key=lambda p: p.stat().st_mtime)
    return csv_path

def parse_number(value_str):
    """Parse numeric value, handling empty strings."""
    if not value_str or value_str.strip() == '':
        return None
    try:
        # Remove dollar sign and commas
        clean = value_str.replace('$', '').replace(',', '')
        return float(clean)
    except (ValueError, AttributeError):
        return None

def parse_integer(value_str):
    """Parse integer value, handling empty strings."""
    if not value_str or value_str.strip() == '':
        return None
    try:
        return int(float(value_str))
    except (ValueError, AttributeError):
        return None

def import_csv(csv_path):
    """Import CSV file into database."""

    print(f"📖 Reading {csv_path.name}...")
    companies = []

    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row.get('Symbol', '').strip()
            if not symbol:
                continue

            companies.append({
                'symbol': symbol,
                'name': row.get('Name', '').strip(),
                'last_sale': parse_number(row.get('Last Sale', '')),
                'net_change': parse_number(row.get('Net Change', '')),
                'pct_change': row.get('% Change', '').strip() or None,
                'market_cap': parse_integer(row.get('Market Cap', '')),
                'country': row.get('Country', '').strip() or None,
                'ipo_year': parse_integer(row.get('IPO Year', '')),
                'volume': parse_integer(row.get('Volume', '')),
                'sector': row.get('Sector', '').strip() or None,
                'industry': row.get('Industry', '').strip() or None,
            })

    print(f"✅ Loaded {len(companies):,} companies from CSV")

    # Connect to database
    print(f"\n🔌 Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

    try:
        cursor = conn.cursor()

        # Create schema and table
        print("🔨 Creating schema and companies table...")
        cursor.execute("""
            -- Create schema
            CREATE SCHEMA IF NOT EXISTS markethawkeye;

            -- Create table in schema
            CREATE TABLE IF NOT EXISTS markethawkeye.companies (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                last_sale NUMERIC(10, 2),
                net_change NUMERIC(10, 2),
                pct_change VARCHAR(20),
                market_cap BIGINT,
                country VARCHAR(100),
                ipo_year INTEGER,
                volume BIGINT,
                sector VARCHAR(100),
                industry VARCHAR(150),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );

            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_companies_symbol ON markethawkeye.companies(symbol);
            CREATE INDEX IF NOT EXISTS idx_companies_name ON markethawkeye.companies(name);
            CREATE INDEX IF NOT EXISTS idx_companies_sector ON markethawkeye.companies(sector);
            CREATE INDEX IF NOT EXISTS idx_companies_industry ON markethawkeye.companies(industry);
            CREATE INDEX IF NOT EXISTS idx_companies_market_cap ON markethawkeye.companies(market_cap);
        """)
        conn.commit()
        print("✅ Table ready")

        # Clear existing data
        print("🗑️  Clearing existing data...")
        cursor.execute("DELETE FROM markethawkeye.companies")
        conn.commit()

        # Insert in batches
        print(f"💾 Inserting {len(companies):,} companies...")
        batch_size = 1000
        inserted = 0

        for i in range(0, len(companies), batch_size):
            batch = companies[i:i + batch_size]

            values = []
            for company in batch:
                values.append((
                    company['symbol'],
                    company['name'],
                    company['last_sale'],
                    company['net_change'],
                    company['pct_change'],
                    company['market_cap'],
                    company['country'],
                    company['ipo_year'],
                    company['volume'],
                    company['sector'],
                    company['industry'],
                ))

            insert_query = """
                INSERT INTO markethawkeye.companies
                    (symbol, name, last_sale, net_change, pct_change, market_cap,
                     country, ipo_year, volume, sector, industry)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE SET
                    name = EXCLUDED.name,
                    last_sale = EXCLUDED.last_sale,
                    net_change = EXCLUDED.net_change,
                    pct_change = EXCLUDED.pct_change,
                    market_cap = EXCLUDED.market_cap,
                    country = EXCLUDED.country,
                    ipo_year = EXCLUDED.ipo_year,
                    volume = EXCLUDED.volume,
                    sector = EXCLUDED.sector,
                    industry = EXCLUDED.industry,
                    updated_at = NOW()
            """

            cursor.executemany(insert_query, values)
            inserted += len(batch)

            if inserted % 5000 == 0 or inserted == len(companies):
                print(f"  Progress: {inserted:,} / {len(companies):,}")

        conn.commit()
        print(f"✅ Imported {inserted:,} companies")

        # Verify data
        print("\n📊 Verification:")

        cursor.execute("SELECT COUNT(*) FROM markethawkeye.companies")
        total = cursor.fetchone()[0]
        print(f"  Total companies: {total:,}")

        cursor.execute("SELECT COUNT(*) FROM markethawkeye.companies WHERE sector IS NOT NULL")
        with_sector = cursor.fetchone()[0]
        print(f"  With sector: {with_sector:,}")

        cursor.execute("SELECT COUNT(*) FROM markethawkeye.companies WHERE industry IS NOT NULL")
        with_industry = cursor.fetchone()[0]
        print(f"  With industry: {with_industry:,}")

        cursor.execute("SELECT COUNT(*) FROM markethawkeye.companies WHERE market_cap IS NOT NULL AND market_cap > 0")
        with_market_cap = cursor.fetchone()[0]
        print(f"  With market cap: {with_market_cap:,}")

        # Show sector distribution
        cursor.execute("""
            SELECT sector, COUNT(*)
            FROM markethawkeye.companies
            WHERE sector IS NOT NULL
            GROUP BY sector
            ORDER BY COUNT(*) DESC
        """)

        print("\n  By sector:")
        for row in cursor.fetchall():
            print(f"    {row[0]:30} - {row[1]:,} companies")

        # Sample entries
        cursor.execute("""
            SELECT symbol, name, sector, market_cap
            FROM markethawkeye.companies
            WHERE sector IS NOT NULL AND market_cap IS NOT NULL
            ORDER BY market_cap DESC
            LIMIT 5
        """)

        print("\n  Top 5 by market cap:")
        for row in cursor.fetchall():
            market_cap_b = row[3] / 1_000_000_000 if row[3] else 0
            print(f"    {row[0]:6} - {row[2]:20} - ${market_cap_b:,.1f}B - {row[1]}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

def main():
    print("\n" + "🦅" * 35)
    print("MARKEY HAWKEYE - IMPORT NASDAQ SCREENER")
    print("🦅" * 35 + "\n")

    args = parse_args()
    csv_path = find_screener_csv(args.csv_file)

    print(f"📁 CSV file: {csv_path.name}")
    print(f"🗄️  Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}\n")

    import_csv(csv_path)

    print("\n" + "=" * 70)
    print("🎉 DONE!")
    print("=" * 70)
    print("\nDatabase is now populated with NASDAQ screener data!")
    print("\n📊 Example queries:")
    print("   SELECT * FROM markethawkeye.companies WHERE sector = 'Technology';")
    print("   SELECT * FROM markethawkeye.companies ORDER BY market_cap DESC LIMIT 10;")
    print("   SELECT sector, COUNT(*) FROM markethawkeye.companies GROUP BY sector;\n")

if __name__ == "__main__":
    main()
