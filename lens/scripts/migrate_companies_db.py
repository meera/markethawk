#!/usr/bin/env python3
"""
Migrate companies database schema to use JSONB metadata.

This script:
1. Drops old columns (last_sale, market_cap, sector, etc.)
2. Adds new columns (cik_str, slug, metadata JSONB)
3. Imports data from companies_master.csv

Usage:
    # Local database
    python lens/scripts/migrate_companies_db.py

    # Production database (Neon)
    DATABASE_URL="postgresql://..." python lens/scripts/migrate_companies_db.py
"""

import psycopg2
import csv
import json
import os
import sys
from pathlib import Path

# Configuration
DATA_DIR = Path(__file__).parent.parent.parent / "data"
MASTER_CSV = DATA_DIR / "companies_master.csv"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@192.168.86.250:54322/postgres")

def migrate_schema(conn):
    """Migrate database schema."""
    print("\n🔨 Migrating database schema...")

    cursor = conn.cursor()

    # Drop and recreate table
    print("   🗑️  Dropping existing companies table...")
    cursor.execute("DROP TABLE IF EXISTS markethawkeye.companies CASCADE;")

    # Create new table with clean schema
    print("   🏗️  Creating new companies table...")
    cursor.execute("""
        CREATE TABLE markethawkeye.companies (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            cik_str VARCHAR(20) UNIQUE NOT NULL,
            slug VARCHAR(255) UNIQUE NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # Create indexes
    print("   🔍 Creating indexes...")
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_companies_cik ON markethawkeye.companies(cik_str);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_companies_slug ON markethawkeye.companies(slug);
        CREATE INDEX IF NOT EXISTS idx_companies_metadata ON markethawkeye.companies USING GIN (metadata);
    """)

    # Enable fuzzy search extension
    print("   🔍 Enabling fuzzy search (pg_trgm)...")
    cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_companies_name_trgm
        ON markethawkeye.companies USING GIN (name gin_trgm_ops);
    """)

    conn.commit()
    print("   ✅ Schema migration complete")

def import_data(conn):
    """Import data from master CSV."""
    print("\n💾 Importing data from master CSV...")

    if not MASTER_CSV.exists():
        print(f"❌ Master CSV not found: {MASTER_CSV}")
        print("💡 Run: python lens/scripts/create_master_companies.py")
        sys.exit(1)

    cursor = conn.cursor()

    # Load CSV
    companies = []
    with MASTER_CSV.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append(row)

    print(f"   📖 Loaded {len(companies):,} companies from CSV")

    # Insert in batches
    print("   💾 Inserting companies...")
    batch_size = 1000
    inserted = 0

    for i in range(0, len(companies), batch_size):
        batch = companies[i:i + batch_size]

        values = []
        for company in batch:
            values.append((
                company['symbol'],
                company['name'],
                company['cik_str'],
                company['slug'],
                company['metadata_json'],
            ))

        insert_query = """
            INSERT INTO markethawkeye.companies
                (symbol, name, cik_str, slug, metadata)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (symbol) DO UPDATE SET
                name = EXCLUDED.name,
                cik_str = EXCLUDED.cik_str,
                slug = EXCLUDED.slug,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
        """

        cursor.executemany(insert_query, values)
        inserted += len(batch)

        if inserted % 5000 == 0 or inserted == len(companies):
            print(f"      Progress: {inserted:,} / {len(companies):,}")

    conn.commit()
    print(f"   ✅ Imported {inserted:,} companies")

def verify_data(conn):
    """Verify imported data."""
    print("\n📊 Verification:")

    cursor = conn.cursor()

    # Total count
    cursor.execute("SELECT COUNT(*) FROM markethawkeye.companies")
    total = cursor.fetchone()[0]
    print(f"   Total companies: {total:,}")

    # Companies with slugs
    cursor.execute("SELECT COUNT(*) FROM markethawkeye.companies WHERE slug IS NOT NULL")
    with_slug = cursor.fetchone()[0]
    print(f"   With slug: {with_slug:,}")

    # Companies with CIK
    cursor.execute("SELECT COUNT(*) FROM markethawkeye.companies WHERE cik_str IS NOT NULL")
    with_cik = cursor.fetchone()[0]
    print(f"   With CIK: {with_cik:,}")

    # Companies with metadata
    cursor.execute("SELECT COUNT(*) FROM markethawkeye.companies WHERE metadata != '{}'::jsonb")
    with_metadata = cursor.fetchone()[0]
    print(f"   With metadata: {with_metadata:,}")

    # Sample entries
    cursor.execute("""
        SELECT symbol, name, slug, cik_str, metadata
        FROM markethawkeye.companies
        WHERE metadata != '{}'::jsonb
        ORDER BY (metadata->>'market_cap')::bigint DESC NULLS LAST
        LIMIT 5
    """)

    print("\n   Top 5 by market cap:")
    for row in cursor.fetchall():
        symbol, name, slug, cik_str, metadata = row
        market_cap = metadata.get('market_cap', 0) if metadata else 0
        market_cap_b = market_cap / 1_000_000_000 if market_cap else 0
        sector = metadata.get('sector', 'N/A') if metadata else 'N/A'
        print(f"      {symbol:6} - {slug:30} - ${market_cap_b:,.1f}B ({sector})")

def main():
    print("\n" + "🦅" * 35)
    print("MIGRATE COMPANIES DATABASE")
    print("🦅" * 35 + "\n")

    db_host = DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'localhost'
    print(f"🗄️  Database: {db_host}\n")

    # Connect
    print("🔌 Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        print("   ✅ Connected")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        sys.exit(1)

    try:
        # Migrate schema
        migrate_schema(conn)

        # Import data
        import_data(conn)

        # Verify
        verify_data(conn)

        print("\n" + "=" * 70)
        print("🎉 MIGRATION COMPLETE!")
        print("=" * 70)
        print("\n✅ Database schema updated")
        print("✅ Data imported successfully")
        print("\n📊 New schema:")
        print("   • id, symbol, name (unchanged)")
        print("   • cik_str (NEW - SEC identifier)")
        print("   • slug (NEW - URL-friendly)")
        print("   • metadata JSONB (NEW - flexible data)")
        print("   • created_at, updated_at (unchanged)\n")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
