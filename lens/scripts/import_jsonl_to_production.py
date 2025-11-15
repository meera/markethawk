#!/usr/bin/env python3
"""
JSONL Import Script for Production Database

Imports earnings call records from JSONL export files into production database.
Handles is_latest flag updates atomically to prevent race conditions.

Usage:
    # Import single batch export
    python lens/scripts/import_jsonl_to_production.py \\
        /var/markethawk/batch_runs/nov-13-2025-test/exports/earnings_calls.jsonl \\
        --db-url "postgresql://user:pass@host:port/dbname"

    # Import from multiple batches
    python lens/scripts/import_jsonl_to_production.py \\
        /var/markethawk/batch_runs/*/exports/earnings_calls.jsonl \\
        --db-url "postgresql://user:pass@host:port/dbname"

    # Dry run (no database changes)
    python lens/scripts/import_jsonl_to_production.py \\
        /path/to/earnings_calls.jsonl \\
        --db-url "postgresql://..." \\
        --dry-run
"""

import argparse
import json
import psycopg2
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def load_jsonl(file_path: Path) -> List[Dict]:
    """
    Load JSONL file into list of dictionaries

    Args:
        file_path: Path to JSONL file

    Returns:
        List of record dictionaries
    """
    records = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                records.append(json.loads(line))
    return records


def import_records(records: List[Dict], db_url: str, dry_run: bool = False):
    """
    Import earnings call records into production database

    Args:
        records: List of record dictionaries from JSONL
        db_url: PostgreSQL connection URL
        dry_run: If True, don't commit changes
    """
    print(f"\n📊 Import Summary:")
    print(f"   Records to import: {len(records)}")
    print(f"   Dry run: {dry_run}")
    print(f"   Database: {db_url.split('@')[1] if '@' in db_url else db_url}\n")

    if dry_run:
        print("🔍 DRY RUN MODE - No database changes will be made\n")

    # Connect to database
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    imported = 0
    updated = 0
    skipped = 0
    errors = []

    try:
        for record in records:
            try:
                # Extract fields
                record_id = record['id']
                cik_str = record['cik_str']
                symbol = record['symbol']
                quarter = record['quarter']
                year = record['year']
                audio_url = record.get('audio_url')
                youtube_id = record.get('youtube_id')
                is_latest = record.get('is_latest', True)
                metadata = json.dumps(record.get('metadata', {}))

                # Atomic transaction for each record
                cursor.execute("BEGIN;")

                # Mark existing records as NOT latest
                cursor.execute("""
                    UPDATE markethawkeye.earnings_calls
                    SET is_latest = false
                    WHERE cik_str = %s
                      AND quarter = %s
                      AND year = %s
                      AND is_latest = true;
                """, (cik_str, quarter, year))

                rows_updated = cursor.rowcount

                # Insert new record
                cursor.execute("""
                    INSERT INTO markethawkeye.earnings_calls
                      (id, cik_str, symbol, quarter, year, audio_url, youtube_id, is_latest, metadata, created_at, updated_at)
                    VALUES
                      (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (
                    record_id,
                    cik_str,
                    symbol,
                    quarter,
                    year,
                    audio_url,
                    youtube_id,
                    is_latest,
                    metadata,
                    record.get('created_at', datetime.now().isoformat()),
                    record.get('updated_at', datetime.now().isoformat())
                ))

                rows_inserted = cursor.rowcount

                if dry_run:
                    cursor.execute("ROLLBACK;")
                    print(f"   [DRY RUN] Would import: {record_id} ({symbol} {quarter} {year})")
                    if rows_updated > 0:
                        print(f"             Would mark {rows_updated} existing record(s) as NOT latest")
                    imported += 1
                else:
                    cursor.execute("COMMIT;")
                    if rows_inserted > 0:
                        print(f"   ✓ Imported: {record_id} ({symbol} {quarter} {year})")
                        if rows_updated > 0:
                            print(f"     Marked {rows_updated} existing record(s) as NOT latest")
                        imported += 1
                    else:
                        print(f"   ⊘ Skipped: {record_id} (already exists)")
                        skipped += 1

            except Exception as e:
                cursor.execute("ROLLBACK;")
                error_msg = f"Error importing {record.get('id', 'unknown')}: {e}"
                errors.append(error_msg)
                print(f"   ✗ {error_msg}")

    finally:
        cursor.close()
        conn.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"Import Complete!")
    print(f"{'='*60}")
    print(f"   Imported: {imported}")
    print(f"   Skipped: {skipped}")
    print(f"   Errors: {len(errors)}")

    if errors:
        print(f"\n❌ Errors:")
        for error in errors:
            print(f"   - {error}")

    if dry_run:
        print(f"\n⚠️  This was a DRY RUN - no changes were committed to the database")


def main():
    parser = argparse.ArgumentParser(
        description='Import JSONL earnings call exports to production database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import single batch
  python lens/scripts/import_jsonl_to_production.py \\
    /var/markethawk/batch_runs/nov-13-2025-test/exports/earnings_calls.jsonl \\
    --db-url "postgresql://postgres:password@host:port/postgres"

  # Dry run (preview)
  python lens/scripts/import_jsonl_to_production.py \\
    /path/to/earnings_calls.jsonl \\
    --db-url "postgresql://..." \\
    --dry-run

  # Use environment variable for connection string
  export PRODUCTION_DB_URL="postgresql://..."
  python lens/scripts/import_jsonl_to_production.py /path/to/earnings_calls.jsonl
        """
    )

    parser.add_argument(
        'jsonl_file',
        type=Path,
        help='Path to JSONL export file'
    )
    parser.add_argument(
        '--db-url',
        help='PostgreSQL connection URL (or set PRODUCTION_DB_URL env var)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without committing to database'
    )

    args = parser.parse_args()

    # Validate file exists
    if not args.jsonl_file.exists():
        print(f"❌ Error: File not found: {args.jsonl_file}")
        return 1

    # Get database URL
    import os
    db_url = args.db_url or os.getenv('PRODUCTION_DB_URL')
    if not db_url:
        print("❌ Error: Database URL required (--db-url or PRODUCTION_DB_URL env var)")
        return 1

    # Load records
    print(f"\n📖 Loading records from: {args.jsonl_file}")
    records = load_jsonl(args.jsonl_file)
    print(f"✓ Loaded {len(records)} records\n")

    if not records:
        print("⚠️  No records found in file")
        return 0

    # Import records
    import_records(records, db_url, dry_run=args.dry_run)

    return 0


if __name__ == '__main__':
    exit(main())
