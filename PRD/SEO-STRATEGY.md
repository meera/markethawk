# SEO-STRATEGY.md

Complete SEO strategy for MarketHawk YouTube videos and website.

---

## Overview

MarketHawk's SEO strategy focuses on:
1. **YouTube SEO** - Maximize video discoverability
2. **Website SEO** - Optimize video landing pages for search engines
3. **Structured Data** - Rich snippets in Google search results

---

## YouTube SEO

### Title Format

**Template:**
```
[Company Name] ([TICKER]) [Quarter] [Year] Earnings Call - Visual Summary | MarketHawk
```

**Examples:**
- `Apple (AAPL) Q4 2024 Earnings Call - Visual Summary | MarketHawk`
- `Brookfield Infrastructure (BIP) Q3 2025 Earnings Call - Visual Summary | MarketHawk`
- `Palantir (PLTR) Q3 2025 Earnings Call - Visual Summary | MarketHawk`

**Best Practices:**
- Keep under 60 characters (visible in search)
- Include ticker symbol (investors search by ticker)
- Include quarter/year (helps with recency)
- Add "Visual Summary" (differentiates from raw earnings calls)
- End with "| MarketHawk" (brand recognition)

---

### Description Template

```
[Company] ([TICKER]) [Quarter] [Year] earnings call with visual charts, transcripts, and financial analysis.

📊 Key Metrics:
- Revenue: $X.XX billion (±X%)
- EPS: $X.XX (±X%)
- Guidance: [Summary]

🔗 Full interactive analysis: https://markethawkeye.com/[ticker]/[quarter]-[year]

Timestamps:
0:00 Intro
0:30 Revenue Overview
1:15 EPS Analysis
2:00 Guidance
3:00 Q&A Highlights

Subscribe for more earnings call visualizations!

#[ticker] #earnings #investing #stocks #finance #[CompanyName]
```

**Example (Apple Q4 2024):**
```
Apple (AAPL) Q4 2024 earnings call with visual charts, transcripts, and financial analysis.

📊 Key Metrics:
- Revenue: $94.9 billion (+6% YoY)
- EPS: $1.64 (beat estimates of $1.58)
- Guidance: Strong iPhone 16 demand, Services growth accelerating

🔗 Full interactive analysis: https://markethawkeye.com/aapl/q4-2024

Timestamps:
0:00 Intro & Opening Remarks
0:30 Revenue Overview by Segment
2:15 iPhone Revenue Deep Dive
4:30 Services Revenue Growth
6:00 Margin Analysis
8:15 Forward Guidance
10:30 Q&A Highlights

Subscribe for more earnings call visualizations!

#AAPL #earnings #investing #stocks #finance #Apple #tech #iPhone
```

**Best Practices:**
- Include actual numbers from earnings (improves relevance)
- Add chapter timestamps (YouTube promotes videos with chapters)
- Link to website (drives traffic, improves SEO)
- Use emojis sparingly (📊, 🔗 for visual separation)
- Add relevant hashtags (max 3-5, placed at end)

---

### Tags

**Primary Tags (Always Include):**
- Ticker symbol (e.g., "AAPL", "BIP", "PLTR")
- Company name (e.g., "Apple", "Brookfield Infrastructure")
- "earnings call"
- "earnings"

**Secondary Tags:**
- Quarter (e.g., "Q4", "Q3")
- Year (e.g., "2024", "2025")
- "investing"
- "stocks"
- "finance"

**Long-Tail Tags:**
- "earnings analysis"
- "quarterly earnings"
- "stock market"
- "financial results"
- "[Company] earnings"
- "[Company] stock"

**Industry-Specific Tags:**
- Tech: "tech stocks", "technology earnings"
- Finance: "bank earnings", "financial services"
- Infrastructure: "infrastructure stocks", "utilities"

**Example Tag Set (15 tags max):**
```
AAPL
Apple
earnings call
earnings
Q4
2024
investing
stocks
finance
earnings analysis
quarterly earnings
stock market
tech stocks
technology earnings
Apple stock
```

---

### Chapter Markers (Timestamps)

**Why Chapter Markers Matter:**
- YouTube promotes videos with chapters
- Improves viewer retention (easier navigation)
- Shows up in YouTube search results
- Better user experience

**How to Add:**
1. Include timestamps in video description (YouTube auto-detects)
2. Start with `0:00 Intro` (required)
3. Add chapters every 30-90 seconds for key moments

**Template:**
```
0:00 Intro & Opening Remarks
[TIME] Revenue Overview
[TIME] Segment Performance
[TIME] Operating Expenses
[TIME] Net Income & EPS
[TIME] Forward Guidance
[TIME] Q&A Highlights
[TIME] Conclusion
```

**Example (Brookfield Infrastructure Q3 2025):**
```
0:00 Intro Music & Title Card
0:30 Opening Remarks
1:15 Revenue: $4.7B (+12% YoY)
2:30 FFO Growth: $550M
4:00 Segment Performance Overview
5:30 Data & Digital Infrastructure
7:00 Transport & Energy
8:30 Utilities
10:00 Forward Guidance: Strong Pipeline
11:30 Q&A Highlights
13:00 Conclusion & Subscribe
```

---

### Thumbnail Optimization

**Best Practices:**
- **Resolution:** 1280x720 (16:9 aspect ratio)
- **File size:** Under 2MB
- **Format:** JPG or PNG
- **Text:** Large, bold, readable on mobile
- **Colors:** High contrast (company brand colors)
- **Face:** Include CEO/CFO if available (increases CTR)

**Text Elements to Include:**
- Ticker symbol (large, prominent)
- Key metric (e.g., "Revenue +12%", "Beat Estimates")
- Quarter/Year
- Company logo

**See:** `PRD/recipes/THUMBNAIL-OPTIONS.md` for detailed thumbnail generation guide.

---

## Website SEO

### Dynamic Meta Tags

```tsx
// app/[company]/[slug]/page.tsx

export async function generateMetadata({params}) {
  const video = await getVideo(params.slug);

  return {
    title: `${video.company} (${video.ticker}) ${video.quarter} ${video.year} Earnings | MarketHawk`,
    description: `Watch ${video.company} earnings call with interactive charts and financial data analysis. Revenue: ${video.revenue}, EPS: ${video.eps}.`,
    keywords: [
      video.ticker,
      video.company,
      'earnings call',
      'earnings analysis',
      'quarterly earnings',
      video.quarter,
      video.year.toString(),
    ],
    openGraph: {
      title: video.title,
      description: video.description,
      images: [video.thumbnail_url],
      type: 'video.other',
      url: `https://markethawkeye.com/${video.ticker.toLowerCase()}/${video.slug}`,
    },
    twitter: {
      card: 'player',
      title: video.title,
      description: video.description,
      images: [video.thumbnail_url],
      players: {
        playerUrl: `https://www.youtube.com/embed/${video.youtube_id}`,
        streamUrl: `https://www.youtube.com/watch?v=${video.youtube_id}`,
        width: 1280,
        height: 720,
      },
    },
  };
}
```

---

### Structured Data (JSON-LD)

**Video Object Schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Apple (AAPL) Q4 2024 Earnings Call - Visual Summary",
  "description": "Apple Q4 2024 earnings call with visual charts, transcripts, and financial analysis.",
  "thumbnailUrl": "https://markethawkeye.com/thumbnails/aapl-q4-2024.jpg",
  "uploadDate": "2024-11-01T10:00:00Z",
  "duration": "PT13M42S",
  "contentUrl": "https://youtube.com/watch?v=abc123",
  "embedUrl": "https://youtube.com/embed/abc123",
  "interactionStatistic": {
    "@type": "InteractionCounter",
    "interactionType": "http://schema.org/WatchAction",
    "userInteractionCount": 15234
  },
  "publisher": {
    "@type": "Organization",
    "name": "MarketHawk",
    "logo": {
      "@type": "ImageObject",
      "url": "https://markethawkeye.com/logo.png"
    }
  }
}
```

**Breadcrumb Schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://markethawkeye.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Apple (AAPL)",
      "item": "https://markethawkeye.com/aapl"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Q4 2024 Earnings",
      "item": "https://markethawkeye.com/aapl/q4-2024"
    }
  ]
}
```

**Organization Schema (Homepage):**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "MarketHawk",
  "url": "https://markethawkeye.com",
  "logo": "https://markethawkeye.com/logo.png",
  "description": "Visual earnings call analysis with interactive charts and financial data.",
  "sameAs": [
    "https://youtube.com/@markethawk",
    "https://twitter.com/markethawk"
  ]
}
```

---

### Content Strategy

**Above the Fold (Visible Without Scrolling):**
1. **Headline:** `[Company] ([TICKER]) [Quarter] [Year] Earnings Call`
2. **Intro Paragraph:** Brief summary of key metrics (100-150 words)
3. **Video Embed:** YouTube video player
4. **Meta Description Preview:** First 160 characters of intro paragraph

**Example Intro Paragraph:**
```
Apple (AAPL) reported Q4 2024 earnings on November 1st, 2024, beating analyst
estimates with revenue of $94.9 billion (+6% YoY) and EPS of $1.64 (vs. $1.58
estimate). iPhone revenue remained strong at $43.8 billion, while Services
revenue grew 12% to $22.3 billion. The company provided optimistic guidance for
Q1 2025, citing strong iPhone 16 demand and accelerating Services growth.
```

**Below the Fold (Scrollable Content):**
1. **Key Metrics Table** (Revenue, EPS, Margins, Guidance)
2. **Interactive Charts** (Revenue by segment, YoY growth)
3. **Transcript** (Full earnings call transcript with timestamps)
4. **Related Videos** (Same company previous quarters, same industry)
5. **Sign-in Gate** (Blur content at 50% scroll for free users)

---

## SEO Best Practices

### On-Page SEO
- Use H1 for video title
- Use H2 for section headings (Key Metrics, Transcript, etc.)
- Include internal links to related videos
- Add alt text to all images (thumbnails, charts)
- Use semantic HTML (article, section, aside)

### Technical SEO
- Fast page load (<2 seconds)
- Mobile-responsive design
- HTTPS enabled
- XML sitemap updated after new video
- Canonical URLs to avoid duplicate content

### Link Building
- Link from YouTube description to website
- Add video to company investor relations pages (if possible)
- Share on financial forums (Reddit r/investing, r/stocks)
- Submit to finance aggregators (Seeking Alpha, Yahoo Finance)

---

## Keyword Research

**Primary Keywords (High Volume):**
- "[Ticker] earnings"
- "[Company] earnings call"
- "[Company] Q[X] earnings"

**Long-Tail Keywords (Lower Volume, Higher Intent):**
- "[Company] earnings call transcript"
- "[Company] [Quarter] [Year] earnings analysis"
- "[Company] earnings beat estimates"
- "[Company] revenue breakdown"

**Tools:**
- Google Keyword Planner
- Ahrefs
- SEMrush
- YouTube search autocomplete

---

## Analytics & Tracking

**YouTube Analytics (Track Weekly):**
- Impressions
- Click-through rate (CTR)
- Average view duration
- Traffic sources (search, suggested, external)

**Google Search Console (Track Monthly):**
- Search impressions
- Click-through rate
- Average position
- Top queries

**Website Analytics (Track Daily):**
- Organic traffic from Google
- Referral traffic from YouTube
- Bounce rate on video pages
- Conversion rate (free → paid)

---

## Automation

**Auto-generate SEO Metadata from job.yaml:**

```python
# lens/scripts/generate_seo_metadata.py

def generate_youtube_metadata(job_data):
    ticker = job_data['ticker']
    company = job_data['company']
    quarter = job_data['quarter']
    year = job_data['year']

    title = f"{company} ({ticker}) {quarter} {year} Earnings Call - Visual Summary | MarketHawk"

    description = f"""
{company} ({ticker}) {quarter} {year} earnings call with visual charts, transcripts, and financial analysis.

📊 Key Metrics:
- Revenue: {job_data['insights']['revenue']}
- EPS: {job_data['insights']['eps']}
- Guidance: {job_data['insights']['guidance']}

🔗 Full interactive analysis: https://markethawkeye.com/{ticker.lower()}/{quarter.lower()}-{year}

Subscribe for more earnings call visualizations!

#{ticker} #earnings #investing #stocks #finance #{company.replace(' ', '')}
    """.strip()

    tags = [
        ticker,
        company,
        'earnings call',
        'earnings',
        quarter,
        str(year),
        'investing',
        'stocks',
        'finance',
        'earnings analysis',
        'quarterly earnings',
        'stock market',
    ]

    return {
        'title': title,
        'description': description,
        'tags': tags[:15],  # YouTube limit
    }
```

---

## Related Documentation

- **THUMBNAIL-OPTIONS.md** - Thumbnail generation guide
- **USER-EXPERIENCE.md** - Content gating strategy
- **WEB-APP-GUIDE.md** - ISR configuration for SEO
- **ADMIN-DASHBOARD.md** - SEO performance tracking

---

**Last Updated:** 2025-11-10
