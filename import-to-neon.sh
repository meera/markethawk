#!/bin/bash
# Import NASDAQ companies data to Neon production database
# 
# This script:
# 1. Cleans the CSV (removes $ and % symbols)
# 2. Creates schema and table in Neon
# 3. Imports data using psql \COPY

set -e

NEON_URL="postgresql://neondb_owner:npg_e1uBMOdh5QUy@ep-twilight-leaf-a4dgbd70-pooler.us-east-1.aws.neon.tech:5432/neondb?sslmode=require&channel_binding=require"

echo "🦅 MARKEY HAWKEYE - Import to Neon"
echo "================================="

# Step 1: Clean CSV
echo ""
echo "📝 Cleaning CSV..."
python3 << 'PYTHON_EOF'
import csv
from pathlib import Path

input_file = Path('data/nasdaq_screener_1762899599168.csv')
output_file = Path('data/nasdaq_screener_cleaned.csv')

def parse_number(value):
    if not value or value.strip() == '':
        return ''
    try:
        clean = value.replace('$', '').replace(',', '').replace('%', '')
        return clean
    except:
        return ''

def parse_integer(value):
    if not value or value.strip() == '':
        return ''
    try:
        clean = value.replace(',', '')
        num = float(clean)
        return str(int(num))
    except:
        return ''

with input_file.open('r', encoding='utf-8') as f_in:
    reader = csv.DictReader(f_in)
    with output_file.open('w', encoding='utf-8', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
        writer.writeheader()
        count = 0
        for row in reader:
            cleaned_row = {}
            for key, value in row.items():
                if key in ['Market Cap', 'Volume', 'IPO Year']:
                    cleaned_row[key] = parse_integer(value)
                elif key in ['Last Sale', 'Net Change']:
                    cleaned_row[key] = parse_number(value)
                else:
                    cleaned_row[key] = value.replace('$', '').replace('%', '') if value else ''
            writer.writerow(cleaned_row)
            count += 1
print(f"✅ Cleaned {count} rows")
PYTHON_EOF

# Step 2: Create schema and table
echo ""
echo "🔨 Creating schema and table..."
psql "$NEON_URL" -c "
CREATE SCHEMA IF NOT EXISTS markethawkeye;
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
CREATE INDEX IF NOT EXISTS idx_companies_symbol ON markethawkeye.companies(symbol);
CREATE INDEX IF NOT EXISTS idx_companies_name ON markethawkeye.companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON markethawkeye.companies(sector);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON markethawkeye.companies(industry);
CREATE INDEX IF NOT EXISTS idx_companies_market_cap ON markethawkeye.companies(market_cap);
"

# Step 3: Import data
echo ""
echo "💾 Importing data..."
psql "$NEON_URL" -c "\COPY markethawkeye.companies (symbol, name, last_sale, net_change, pct_change, market_cap, country, ipo_year, volume, sector, industry) FROM 'data/nasdaq_screener_cleaned.csv' DELIMITER ',' CSV HEADER"

# Step 4: Verify
echo ""
echo "📊 Verification:"
psql "$NEON_URL" -c "
SELECT COUNT(*) as total FROM markethawkeye.companies;
SELECT symbol, name, market_cap FROM markethawkeye.companies ORDER BY market_cap DESC LIMIT 5;
"

echo ""
echo "✅ Import complete!"
