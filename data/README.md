# Company Data Directory

This directory stores manually downloaded company data used to seed the database.

## Required Download

### NASDAQ Stock Screener

**URL:** https://www.nasdaq.com/market-activity/stocks/screener

**What it provides:**
- ✅ Ticker symbol
- ✅ Company name
- ✅ Sector
- ✅ Industry
- ✅ Market cap
- ✅ Country
- ~7,000 companies (major exchanges only)

**How to download:**

1. Visit https://www.nasdaq.com/market-activity/stocks/screener
2. Click "Download CSV" button (exports all ~7,000 stocks)
3. Save to this directory (any filename starting with `nasdaq_screener` works)

**CSV Format:**
```csv
Symbol,Name,Last Sale,Net Change,% Change,Market Cap,Country,IPO Year,Volume,Sector,Industry
AAPL,Apple Inc.,182.52,1.23,0.68%,2800000000000,United States,1980,50000000,Technology,Computer Manufacturing
MSFT,Microsoft Corporation,378.91,2.45,0.65%,2820000000000,United States,1986,25000000,Technology,Computer Software: Prepackaged Software
```

## Data Files

```
data/
├── README.md                      # This file
├── .gitignore                     # Ignore downloaded files
└── nasdaq_screener.csv            # Manual download from NASDAQ
```

## Database Schema

```sql
markethawkeye.companies (
  id          SERIAL PRIMARY KEY
  symbol      VARCHAR(10)   -- Ticker symbol
  name        VARCHAR(255)  -- Company name
  last_sale   NUMERIC(10,2) -- Last sale price
  net_change  NUMERIC(10,2) -- Net change
  pct_change  VARCHAR(20)   -- Percentage change
  market_cap  BIGINT        -- Market capitalization
  country     VARCHAR(100)  -- Country
  ipo_year    INTEGER       -- IPO year
  volume      BIGINT        -- Trading volume
  sector      VARCHAR(100)  -- Sector
  industry    VARCHAR(150)  -- Industry
  created_at  TIMESTAMP     -- Created timestamp
  updated_at  TIMESTAMP     -- Updated timestamp
)
```

## Usage

### Step 1: Download NASDAQ Screener CSV

```bash
# Download NASDAQ screener CSV manually
# Visit: https://www.nasdaq.com/market-activity/stocks/screener
# Click: "Download CSV"
# Save to: data/nasdaq_screener.csv
```

### Step 2: Import to Database

```bash
# Local/Development
cd ~/markethawk
source .venv/bin/activate
python lens/scripts/import_nasdaq_screener.py

# Production
scp data/nasdaq_screener.csv user@production:/var/markethawk/data/
ssh user@production
export DATABASE_URL="..."
cd /var/markethawk
python lens/scripts/import_nasdaq_screener.py
```

## Notes

- Downloaded CSV files are gitignored (not committed to repo)
- NASDAQ screener provides ~7,600+ companies with complete data
- Includes ticker, name, sector, industry, market cap, country, IPO year, volume, price data
- Database will have indexes on symbol, name, sector, industry, and market cap for fast queries
