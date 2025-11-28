# Finnhub vs NASDAQ Earnings Calendar Data Comparison

## Date: November 27, 2025

## Finnhub Data Summary

**API Endpoint:** `https://finnhub.io/api/v1/calendar/earnings`
**Date Range:** Nov 27 - Dec 26, 2025 (30 days)
**Total Earnings:** 433 companies

### Sample Finnhub Data (First 10):
1. FWDI - 2025-12-26 - Q4 2025 - hour: N/A
2. CHN - 2025-12-26 - Q4 2025 - hour: N/A
3. SHMD - 2025-12-26 - Q2 2025 - hour: N/A
4. PMO - 2025-12-26 - Q2 2026 - hour: N/A
5. NGTF - 2025-12-26 - Q4 2025 - hour: N/A
6. CSQ - 2025-12-26 - Q4 2025 - hour: N/A
7. CTXR - 2025-12-26 - Q4 2025 - hour: amc
8. IH - 2025-12-26 - Q3 2025 - hour: N/A
9. BDL - 2025-12-26 - Q4 2025 - hour: N/A
10. CCD - 2025-12-26 - Q4 2026 - hour: N/A

### Finnhub Data Characteristics:
- **Free tier limitations:** 60 API calls/minute
- **Data quality issues observed:**
  - Many entries have empty `hour` field (no BMO/AMC/DMH timing)
  - Mix of different fiscal years for same calendar date
  - Includes small-cap and penny stocks
  - Some questionable quality entries

## NASDAQ Earnings Calendar

**URL:** https://www.nasdaq.com/market-activity/earnings
**Access:** Requires browser/JavaScript (dynamic loading)
**Data Extraction:** Challenging - appears to use client-side rendering

### Expected NASDAQ Data (based on URL inspection):
- Shows major companies first
- Better quality filtering
- More reliable timing information (BMO/AMC)
- Typically focuses on companies investors care about

## Key Differences Observed:

1. **Company Quality:**
   - Finnhub: Includes ALL companies (including micro-caps, penny stocks)
   - NASDAQ: Likely filters for market cap / investor relevance

2. **Data Timing:**
   - Finnhub: Many entries missing `hour` field
   - NASDAQ: Generally has reliable BMO/AMC timing

3. **User Experience:**
   - Finnhub: API-first, programmatic access
   - NASDAQ: UI-first, human-readable

## Recommendation:

**Issue:** Finnhub free tier may not provide the quality of data users expect when comparing to NASDAQ.

**Options:**
1. Filter Finnhub data by market cap (only show companies >$1B or >$100M)
2. Use alternative free API (if available)
3. Supplement with web scraping (legal/ethical considerations)
4. Upgrade to paid Finnhub tier for better data quality
5. Build our own aggregation from SEC filings + company IR pages

**Current Status:**
- Using Finnhub free tier
- Showing ALL 433 companies from API
- Users comparing to NASDAQ see very different lists
- May need to add quality filters
