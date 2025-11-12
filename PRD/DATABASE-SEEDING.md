# Database Seeding Guide

Complete guide for populating the `markethawkeye.companies` table with company data from SEC and NASDAQ sources.

---

## Overview

The company database is populated using a **simple 3-step process**:

1. **Download files manually** - SEC JSON + NASDAQ screener CSV
2. **Generate combined CSV** - One script merges both sources
3. **Import to database** - One script imports the combined CSV

### Data Sources

1. **SEC EDGAR JSON** - Ticker, name, CIK (~10,000+ companies)
   - https://www.sec.gov/files/company_tickers.json
2. **NASDAQ Screener CSV** - Sector, industry, market cap (~7,000 companies)
   - https://www.nasdaq.com/market-activity/stocks/screener

**Why this approach?**
- ✅ Simple manual downloads (no automated scripts)
- ✅ Generate CSV once on development machine
- ✅ Upload single file to production (1.2 MB)
- ✅ Easy to review/verify data before import
- ✅ No need to download from SEC/NASDAQ on production

**Data Directory:** All downloaded files are saved to `/Users/Meera/markethawk/data/` (or `/var/markethawk/data/` on production)

**Schema:** `markethawkeye.companies`

---

## Prerequisites

### 1. PostgreSQL Database
- Local development: `postgresql://postgres:postgres@192.168.86.250:54322/postgres`
- Production: Set `DATABASE_URL` environment variable

### 2. Python Environment
```bash
cd ~/markethawk
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Data Directory
```bash
# Create data directory if not exists
mkdir -p ~/markethawk/data
```

---

## Database Management

### Drop Existing Database (Fresh Start)

**Development:**
```bash
psql "postgresql://postgres:postgres@192.168.86.250:54322/postgres" \
  -c "DROP SCHEMA IF EXISTS markethawkeye CASCADE;"
```

**Production (use with caution):**
```bash
# Set production DATABASE_URL first
export DATABASE_URL="your_production_database_url"

psql "$DATABASE_URL" -c "DROP SCHEMA IF EXISTS markethawkeye CASCADE;"
```

**What this does:**
- Drops the entire `markethawkeye` schema
- Removes all tables, indexes, and data
- Use `CASCADE` to drop dependent objects
- Safe to run - will skip if schema doesn't exist

### Verify Database is Clean
```bash
psql "postgresql://postgres:postgres@192.168.86.250:54322/postgres" \
  -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'markethawkeye';"
```

Expected output: Empty result (0 rows)

---

## Quick Start

### Development (Generate CSV)

```bash
# 1. Download SEC company tickers JSON
curl -o ~/markethawk/data/company_tickers.json \
  https://www.sec.gov/files/company_tickers.json

# 2. Download NASDAQ screener CSV (manual)
# Visit: https://www.nasdaq.com/market-activity/stocks/screener
# Click: "Download CSV"
# Save to: ~/markethawk/data/nasdaq_screener.csv

# 3. Generate combined CSV
cd ~/markethawk
source .venv/bin/activate
python lens/scripts/generate_combined_csv.py

# Output: ~/markethawk/data/companies_combined.csv
```

### Production (Import CSV)

```bash
# 1. Upload CSV to production
scp ~/markethawk/data/companies_combined.csv user@production:/var/markethawk/data/

# 2. Import into database
ssh user@production
cd /var/markethawk/markethawk
source .venv/bin/activate
export DATABASE_URL="your_production_database_url"
python lens/scripts/import_companies_csv.py
```

---

## Detailed Process

### Step 1: Download Required Files (Manual)

**File 1: SEC EDGAR Company Tickers**

```bash
# Download SEC company tickers JSON
curl -o ~/markethawk/data/company_tickers.json \
  https://www.sec.gov/files/company_tickers.json
```

**File 2: NASDAQ Stock Screener CSV**

1. Visit https://www.nasdaq.com/market-activity/stocks/screener
2. Click "Download CSV" button
3. Save to `~/markethawk/data/` directory
4. Any filename starting with `nasdaq_screener` works

---

### Step 2: Generate Combined CSV

**Script:** `lens/scripts/generate_combined_csv.py`

**What it does:**
1. Reads SEC company JSON (ticker, name, CIK)
2. Reads NASDAQ screener CSV (sector, industry, market cap)
3. Merges both sources into single CSV file

**Prerequisites:**
- `data/company_tickers.json` (from SEC)
- `data/nasdaq_screener*.csv` (from NASDAQ)

**Run:**
```bash
cd ~/markethawk
source .venv/bin/activate
python lens/scripts/generate_combined_csv.py
```

**Expected output:**
```
🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅
MARKEY HAWKEYE - GENERATE COMBINED CSV
🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅

📖 Reading company_tickers.json...
✅ Loaded 10,142 companies

📊 Looking for NASDAQ screener CSV...
📄 Found nasdaq_screener_1762899599168.csv
✅ Loaded screener data for 7,048 tickers

🔗 Merging data and generating combined CSV...
✅ Generated companies_combined.csv

📊 Statistics:
  Total companies: 10,142
  With screener data (exchange/sector/industry): 7,048

📦 File size: 1.23 MB
📁 Location: /Users/Meera/markethawk/data/companies_combined.csv

======================================================================
🎉 DONE!
======================================================================

📁 Combined CSV: /Users/Meera/markethawk/data/companies_combined.csv

📤 Upload to production:
   scp /Users/Meera/markethawk/data/companies_combined.csv user@production:/var/markethawk/data/

💾 Import on production:
   python lens/scripts/import_companies_csv.py
```

**Output file:**
- `data/companies_combined.csv` - **Final combined CSV (this is what you upload)**

**CSV format:**
```csv
ticker,name,cik,exchange,sector,industry,market_cap,country
AAPL,Apple Inc.,0000320193,,Technology,Computer Manufacturing,2800000000000,United States
MSFT,Microsoft Corporation,0000789019,,Technology,Computer Software: Prepackaged Software,2820000000000,United States
```

**Note:** Exchange column will be NULL (not available in current data sources)

---

### Step 3: Import CSV into Database

**Script:** `lens/scripts/import_companies_csv.py`

**What it does:**
1. Reads `companies_combined.csv`
2. Creates `markethawkeye` schema and `companies` table
3. Imports all data in batches
4. Creates indexes for performance
5. Shows verification statistics

**Prerequisites:**
- CSV file uploaded to production
- PostgreSQL database accessible
- DATABASE_URL environment variable set

**Run:**
```bash
# Default: reads data/companies_combined.csv
python lens/scripts/import_companies_csv.py

# Custom CSV location
python lens/scripts/import_companies_csv.py --csv-file /path/to/companies.csv
```

**Expected output:**
```
🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅
MARKEY HAWKEYE - IMPORT COMPANIES CSV
🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅🦅

📁 CSV file: /var/markethawk/data/companies_combined.csv
🗄️  Database: production-db-host:5432

📖 Reading companies_combined.csv...
✅ Loaded 10,142 companies from CSV

🔌 Connecting to database...
✅ Connected
🔨 Creating schema and companies table...
✅ Table ready
🗑️  Clearing existing data...
💾 Inserting 10,142 companies...
  Progress: 5,000 / 10,142
  Progress: 10,000 / 10,142
  Progress: 10,142 / 10,142
✅ Imported 10,142 companies

📊 Verification:
  Total companies: 10,142
  With exchange: 7,500
  With sector: 7,048
  With industry: 7,048
  With market cap: 7,048

  By exchange:
    NASDAQ          - 3,500 companies
    NYSE            - 2,800 companies
    NYSE MKT        - 500 companies
    NYSE ARCA       - 400 companies
    BATS            - 100 companies

  Top 10 sectors:
    Technology                     - 1,500 companies
    Healthcare                     - 1,200 companies
    Financial Services             - 1,000 companies
    Consumer Cyclical              - 800 companies
    Industrials                    - 700 companies

  Sample entries (by market cap):
    AAPL   - NASDAQ     - Technology          - Apple Inc.
    MSFT   - NASDAQ     - Technology          - Microsoft Corporation
    GOOGL  - NASDAQ     - Communication Services - Alphabet Inc.
    AMZN   - NASDAQ     - Consumer Cyclical   - Amazon.com, Inc.
    NVDA   - NASDAQ     - Technology          - NVIDIA Corporation

======================================================================
🎉 DONE!
======================================================================

Database is now populated with company data!
```

**Database schema created:**
```sql
CREATE SCHEMA markethawkeye;

CREATE TABLE markethawkeye.companies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    cik VARCHAR(20),
    exchange VARCHAR(20),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_companies_ticker ON markethawkeye.companies(ticker);
CREATE INDEX idx_companies_name ON markethawkeye.companies(name);
CREATE INDEX idx_companies_cik ON markethawkeye.companies(cik);
CREATE INDEX idx_companies_exchange ON markethawkeye.companies(exchange);
CREATE INDEX idx_companies_sector ON markethawkeye.companies(sector);
```


---

## Verification Queries

### 1. Total Company Count
```sql
SELECT COUNT(*) FROM markethawkeye.companies;
-- Expected: ~10,142
```

### 2. Companies by Exchange
```sql
SELECT exchange, COUNT(*)
FROM markethawkeye.companies
WHERE exchange IS NOT NULL
GROUP BY exchange
ORDER BY COUNT(*) DESC;
```

### 3. Companies with Enrichment Data
```sql
SELECT
    COUNT(*) as total,
    COUNT(exchange) as with_exchange,
    COUNT(sector) as with_sector,
    COUNT(industry) as with_industry,
    COUNT(market_cap) as with_market_cap
FROM markethawkeye.companies;
```

### 4. Top 10 Companies by Market Cap
```sql
SELECT ticker, name, sector, market_cap
FROM markethawkeye.companies
WHERE market_cap IS NOT NULL
ORDER BY market_cap DESC
LIMIT 10;
```

### 5. Sample Technology Companies
```sql
SELECT ticker, name, industry, market_cap
FROM markethawkeye.companies
WHERE sector = 'Technology'
ORDER BY market_cap DESC NULLS LAST
LIMIT 10;
```

---

## Production Deployment

### Complete Workflow

**On Development Machine:**
```bash
# 1. Download required files
curl -o ~/markethawk/data/company_tickers.json \
  https://www.sec.gov/files/company_tickers.json

# 2. Download NASDAQ screener CSV manually
# Visit: https://www.nasdaq.com/market-activity/stocks/screener
# Save to: ~/markethawk/data/nasdaq_screener.csv

# 3. Generate combined CSV
cd ~/markethawk
source .venv/bin/activate
python lens/scripts/generate_combined_csv.py

# Output: ~/markethawk/data/companies_combined.csv (1.2 MB)
```

**Upload to Production:**
```bash
# 2. Upload CSV file
scp ~/markethawk/data/companies_combined.csv user@production:/var/markethawk/data/

# 3. Upload import script (if not in git repo)
scp ~/markethawk/lens/scripts/import_companies_csv.py user@production:/var/markethawk/markethawk/lens/scripts/
```

**On Production Server:**
```bash
# 4. Set environment
ssh user@production
export DATABASE_URL="postgresql://user:password@host:port/database"

# 5. Verify CSV uploaded
ls -lh /var/markethawk/data/companies_combined.csv

# 6. Import into database
cd /var/markethawk/markethawk
source .venv/bin/activate
python lens/scripts/import_companies_csv.py

# 7. Verify
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM markethawkeye.companies;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM markethawkeye.companies WHERE sector IS NOT NULL;"
```

---

## Data Refresh Schedule

### Recommended Refresh Intervals

**Complete Refresh (All Data):**
- Refresh: Quarterly
- Reason: New IPOs, delistings, sector reclassifications
- Process:
  1. Download new SEC JSON: `curl -o data/company_tickers.json https://www.sec.gov/files/company_tickers.json`
  2. Download new NASDAQ screener CSV from website
  3. Run `python lens/scripts/generate_combined_csv.py` on development
  4. Upload new `companies_combined.csv` to production
  5. Run `python lens/scripts/import_companies_csv.py` on production

**Market Cap Only:**
- Refresh: Weekly
- Reason: Market cap changes daily
- Process: Same as complete refresh (CSV includes latest market cap)

### Automated Refresh (Development)

**Note:** Automated refresh requires manually downloading both files first. Consider a script to download SEC JSON automatically:

```bash
# Add to crontab on development machine (crontab -e)

# Download SEC data and generate CSV quarterly (1st of Jan/Apr/Jul/Oct, 2am)
0 2 1 1,4,7,10 * cd ~/markethawk && curl -o data/company_tickers.json https://www.sec.gov/files/company_tickers.json

# Then manually download NASDAQ screener CSV and run generate script
```

### Manual Production Update (Recommended)

```bash
# On development
# 1. Download files
curl -o ~/markethawk/data/company_tickers.json \
  https://www.sec.gov/files/company_tickers.json
# (Also download NASDAQ screener CSV manually)

# 2. Generate CSV
cd ~/markethawk
source .venv/bin/activate
python lens/scripts/generate_combined_csv.py

# 3. Upload to production
scp ~/markethawk/data/companies_combined.csv user@production:/var/markethawk/data/

# 4. Import on production
ssh user@production
export DATABASE_URL="..."
cd /var/markethawk/markethawk
source .venv/bin/activate
python lens/scripts/import_companies_csv.py
```

---

## Troubleshooting

### Error: "psycopg2 not installed"
```bash
pip install psycopg2-binary
# or update requirements.txt and run:
pip install -r requirements.txt
```

### Error: "Database connection failed"
```bash
# Test connection manually
psql "postgresql://postgres:postgres@192.168.86.250:54322/postgres"

# Check DATABASE_URL environment variable
echo $DATABASE_URL

# Verify PostgreSQL is running
pg_isready -h 192.168.86.250 -p 54322
```

### Error: "No nasdaq_screener*.csv file found"
1. Visit https://www.nasdaq.com/market-activity/stocks/screener
2. Click "Download CSV"
3. Save to `~/markethawk/data/` directory
4. File must start with `nasdaq_screener`

### Error: "Permission denied" on data directory
```bash
# Fix permissions (run from machine with write access)
chmod 755 ~/markethawk/data
chmod 644 ~/markethawk/data/*.csv
chmod 644 ~/markethawk/data/*.txt
```

### Issue: Some companies missing enrichment data
- **Expected:** ~3,000 companies won't have sector/industry
- **Reason:** NASDAQ screener only includes actively traded major exchanges (7,000 companies)
- **SEC data** includes all registered companies including OTC, Pink Sheets, delisted (10,000+ companies)
- This is normal and expected behavior

---

## File Locations

### Development (Mac)
```
~/markethawk/
├── data/                           # Downloaded data files
│   ├── companies_sec.csv           # SEC company data
│   ├── companies_nasdaq.txt        # NASDAQ exchange mappings
│   ├── companies_otherlisted.txt   # NYSE/AMEX mappings
│   └── nasdaq_screener_*.csv       # Manual download
├── lens/scripts/
│   ├── seed_companies.py                    # Basic seeding (no exchange)
│   ├── seed_companies_with_exchange.py      # Full seeding with exchange
│   └── enrich_from_nasdaq_csv.py            # Sector/industry enrichment
└── requirements.txt
```

### Production (Linux)
```
/var/markethawk/
├── data/                           # Downloaded data files
│   ├── companies_sec.csv
│   ├── companies_nasdaq.txt
│   ├── companies_otherlisted.txt
│   └── nasdaq_screener_*.csv
└── markethawk/                     # Git repo
    ├── lens/scripts/
    │   ├── seed_companies.py
    │   ├── seed_companies_with_exchange.py
    │   └── enrich_from_nasdaq_csv.py
    └── requirements.txt
```

---

## Summary

**Complete Workflow:**

**Development (Generate CSV):**
```bash
# 1. Download SEC company tickers
curl -o ~/markethawk/data/company_tickers.json \
  https://www.sec.gov/files/company_tickers.json

# 2. Download NASDAQ screener CSV
# Visit: https://www.nasdaq.com/market-activity/stocks/screener
# Click: "Download CSV"
# Save to: ~/markethawk/data/nasdaq_screener.csv

# 3. Generate combined CSV
cd ~/markethawk
source .venv/bin/activate
python lens/scripts/generate_combined_csv.py

# Output: ~/markethawk/data/companies_combined.csv (1.2 MB)
```

**Production (Import CSV):**
```bash
# 1. Upload CSV to production
scp ~/markethawk/data/companies_combined.csv user@production:/var/markethawk/data/

# 2. Import into database
ssh user@production
export DATABASE_URL="your_production_database_url"
cd /var/markethawk/markethawk
source .venv/bin/activate
python lens/scripts/import_companies_csv.py

# 3. Verify
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM markethawkeye.companies;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM markethawkeye.companies WHERE sector IS NOT NULL;"
```

**Benefits of this approach:**
- ✅ Simple manual downloads (no automated scripts breaking)
- ✅ Generate CSV once, use everywhere
- ✅ No need to download from SEC/NASDAQ on production
- ✅ Easy to review/verify data before import
- ✅ Single file upload (1.2 MB)
- ✅ Fast production deployment
- ✅ Can version control the CSV if needed

**Scripts:**
- `lens/scripts/generate_combined_csv.py` - Merges SEC JSON + NASDAQ CSV
- `lens/scripts/import_companies_csv.py` - Imports combined CSV to database

---

**Last Updated:** 2025-11-11
**Related Documentation:** `DATABASE-SCHEMA.md`, `data/README.md`
