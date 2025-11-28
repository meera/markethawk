# MarketHawk TODO

## Earnings Calendar Feature - Data Quality Investigation (Nov 27, 2025)

### Summary
Implemented earnings calendar using Finnhub API (free tier), but discovered significant data discrepancies when comparing to NASDAQ.com's earnings calendar.

### What We Built
1. **Database Schema**
   - Added `earnings_date` and `earnings_time` fields to `earningsCalls` table
   - Stores BMO (before market open), AMC (after market close), DMH (during market hours)

2. **Finnhub API Integration**
   - Created `lib/finnhub.ts` API client
   - Fetches 30-day earnings calendar
   - Rate limit: 60 calls/min (free tier)
   - Auto-sync via Vercel Cron Job (daily at 2 AM UTC)

3. **UI Implementation**
   - `/earnings-calendar` page with weekly/monthly views
   - Filters by companies in our database
   - Filters by major US exchanges (NASDAQ, NYSE, AMEX)
   - Shows: Symbol, Company, Market Cap, Quarter, Date

4. **Test Results**
   - Successfully synced 433 earnings (30 days)
   - 324 updated/created in database
   - 109 skipped (not in our companies table)
   - Sync duration: 3.6 seconds

### Critical Issue Discovered

**Problem:** Finnhub free tier data does NOT match NASDAQ.com earnings calendar

**Example - November 28, 2025:**
- **NASDAQ.com shows:** CHA, USBC, FGMC, NAMM, GLBS, CLRO, GWAV, SCNI (8 companies)
- **Finnhub shows:** GOGL, FTW, AFJK, CNXX, WHEN, PSHG, IMII, ATMV, PBPB, WINT, TRX, RIME, TBMC (13 companies)
- **Overlap:** Only 1 company (GLBS), but on WRONG DATE (Finnhub: Nov 27, NASDAQ: Nov 28)

**Root Cause Analysis:**
1. **Different Data Sources**
   - NASDAQ.com = Official exchange data (high quality, curated)
   - Finnhub free tier = Aggregated from multiple sources (incomplete, delayed)

2. **Coverage Differences**
   - NASDAQ.com focuses on NASDAQ-listed companies + major NYSE
   - Finnhub aggregates 60+ exchanges globally (OTC, Pink Sheets, international)
   - Different update schedules and lag times

3. **Data Quality**
   - Many Finnhub entries missing `hour` field (timing unknown)
   - Some companies on wrong dates
   - Missing newly listed companies (e.g., CHA - Chagee Holdings, $1.68B cap)

### Saved Data for Analysis
- `.cache/earnings-data/finnhub_earnings_30days.json` (66KB, 433 companies)
- `.cache/earnings-data/nasdaq_earnings.html` (291KB, NASDAQ page)
- `.cache/earnings-data/data_comparison_analysis.md` (Detailed comparison)

### Current Status
- **Feature:** Implemented and functional
- **Data Quality:** Questionable - does not match industry standard (NASDAQ.com)
- **User Impact:** Users comparing to NASDAQ will see completely different companies

### Options Going Forward

#### Option 1: Accept Finnhub Limitations ⚠️
- **Pros:** Free, already implemented
- **Cons:** Inaccurate data, poor user trust
- **Action:** Add disclaimer "Data may be incomplete or delayed"

#### Option 2: Scrape NASDAQ.com 🚫
- **Pros:** Accurate, matches user expectations
- **Cons:** Legal gray area, brittle (breaks if they change HTML), may violate ToS
- **Action:** Research legal implications, implement parser

#### Option 3: Paid Finnhub Tier 💰
- **Pros:** Better data quality, more reliable
- **Cons:** $79-299/month, unknown if it fixes the issues
- **Action:** Trial paid tier, validate data quality improvement

#### Option 4: Alternative Free API 🔍
- **Pros:** Free, potentially better quality
- **Cons:** Unknown if exists, integration time
- **Action:** Research: Yahoo Finance API, Alpha Vantage, IEX Cloud, Polygon.io

#### Option 5: Build Our Own Data Pipeline 🏗️
- **Pros:** Complete control, authoritative sources (SEC 8-K filings)
- **Cons:** Time-intensive, maintenance burden
- **Sources:**
  - SEC EDGAR 8-K filings (earnings announcements)
  - Company investor relations pages
  - Press releases
- **Action:** Build scraper for SEC 8-K forms, parse filing dates

#### Option 6: Hybrid Approach (Recommended) ✅
- Use Finnhub as baseline
- Supplement with SEC 8-K filings for companies we track
- Add manual overrides for major companies
- **Pros:** Best of both worlds, scalable
- **Cons:** More complex implementation

### Recommendation
**Pause earnings calendar feature** until we:
1. Decide on acceptable data quality threshold
2. Evaluate paid Finnhub tier OR find better free alternative
3. Consider hybrid approach (Finnhub + SEC filings)

**Do NOT launch publicly** with current Finnhub free tier data - it will damage trust.

### Technical Details
- **Database:** 5,437 companies (5,435 NASDAQ, 2 NYSE)
- **Finnhub sync:** Working, but unreliable data
- **UI:** Functional, weekly/monthly views implemented
- **Cron job:** Configured but should be disabled until data source resolved

### Next Steps (On Hold)
1. [ ] Research alternative APIs (Yahoo Finance, Alpha Vantage, IEX Cloud)
2. [ ] Trial Finnhub paid tier to validate data quality
3. [ ] Evaluate SEC 8-K filing parser feasibility
4. [ ] Make decision on data source
5. [ ] Update sync logic based on chosen source
6. [ ] Add data quality validation tests
7. [ ] Consider adding "Last updated" timestamp to UI
8. [ ] Add data source attribution ("Powered by...")

---

**Last Updated:** November 27, 2025
**Status:** On Hold - Awaiting data source decision
**Created By:** Claude Code investigation session

---

## ❌ DISCARDED - Earnings Calendar Feature (Nov 27, 2025)

### Status: ABANDONED - Data quality issues with Finnhub free tier

**What was attempted:**
- Implemented earnings calendar using Finnhub API (free tier)
- Added database schema for earnings dates
- Created Vercel cron job for daily sync
- Built UI with weekly/monthly views

**Why it was discarded:**
- Finnhub free tier data does NOT match NASDAQ.com (industry standard)
- Only 1/8 companies matched on same date (very poor accuracy)
- Missing newly listed companies (e.g., CHA - $1.68B cap company)
- Would damage user trust if launched with inaccurate data

**Detailed Analysis:**
- See: `.cache/earnings-data/` for saved comparison data
- Documentation: Previous TODO section (now moved below)

**Files removed:**
- `app/earnings-calendar/` - UI pages
- `app/api/cron/sync-earnings/` - Cron endpoint
- `lib/finnhub.ts` - API client
- `scripts/test-earnings-sync.ts` - Test script
- `vercel.json` - Cron configuration
- Database migrations reverted

**If reconsidering in future:**
1. Research paid Finnhub tier for data quality
2. Consider SEC 8-K filing parser (authoritative but reactive)
3. Evaluate alternative APIs (Yahoo Finance, Alpha Vantage, IEX Cloud)
4. Hybrid approach: Multiple sources + manual overrides

**Decision:** Focus on core video platform instead of unreliable earnings calendar

---
