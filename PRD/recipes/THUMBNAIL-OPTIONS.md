# Thumbnail Options for Earnings Call Videos

## Current State (Phase 1)

**Problem:** We don't have a database of CEO/executive images yet.

**Solution:** Use text-focused thumbnails with strong branding and key metrics.

---

## Phase 1: Text-Only Thumbnails (Current)

### Option 1A: Metric-Focused

```
┌─────────────────────────────────────┐
│                                     │
│         REVENUE UP 100%             │
│            $1.3B                    │
│                                     │
│    Robinhood (HOOD) Q3 2025        │
│                                     │
└─────────────────────────────────────┘
```

**Elements:**
- Large metric (REVENUE UP 100%)
- Large value ($1.3B)
- Company + ticker + quarter at bottom
- Brand colors (green for Robinhood, blue for BIP)

**Pros:**
- Eye-catching numbers
- Clear value proposition
- Works without CEO photos

**Cons:**
- Less personal
- Generic corporate feel

---

### Option 1B: Company-Focused

```
┌─────────────────────────────────────┐
│   ╔═══╗                             │
│   ║ M ║  MarketHawk                 │
│   ╚═══╝                             │
│                                     │
│   Brookfield Infrastructure         │
│   Q3 2025 Earnings Call             │
│                                     │
│   FFO: $654M (+9% YoY)              │
└─────────────────────────────────────┘
```

**Elements:**
- MarketHawk branding
- Company name prominent
- Quarter + year
- 1-2 key metrics

**Pros:**
- Builds MarketHawk brand
- Professional look
- Clean hierarchy

**Cons:**
- Less clickable (no faces)
- Doesn't stand out

---

### Option 1C: Question/Teaser Format

```
┌─────────────────────────────────────┐
│                                     │
│   Why did Brookfield stock          │
│   surge after Q3 earnings?          │
│                                     │
│   BIP • Q3 2025                     │
│   Watch the full call →             │
│                                     │
└─────────────────────────────────────┘
```

**Elements:**
- Provocative question
- Ticker + quarter
- CTA ("Watch the full call")

**Pros:**
- High click-through rate
- Curiosity-driven
- Engaging

**Cons:**
- Can feel clickbait-y
- Doesn't work for all companies

---

## Phase 2: Executive Photos (Future)

Once we have CEO/CFO image database, much more compelling options:

### Option 2A: Split Screen (CEO + Metrics)

```
┌─────────────┬───────────────────────┐
│             │                       │
│   [CEO      │  REVENUE: $654M       │
│    Photo]   │  +9% YoY              │
│             │                       │
│             │  Brookfield (BIP)     │
│             │  Q3 2025              │
└─────────────┴───────────────────────┘
```

**Layout:**
- Left 40%: CEO headshot (circular crop)
- Right 60%: Key metric + company info

**Pros:**
- Personal connection (face)
- Professional look
- High CTR (faces = clicks)

**Cons:**
- Need executive photo database

---

### Option 2B: Full-Width CEO (Overlay Text)

```
┌─────────────────────────────────────┐
│                                     │
│        [CEO Photo Full Width]       │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Sam Pollock, CEO            │   │
│  │ "Record quarter for BIP"    │   │
│  │ Q3 2025 Earnings            │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Layout:**
- Full-width CEO photo (slightly blurred background)
- Bottom third: Text overlay with quote + info

**Pros:**
- Very personal (large face)
- Quote adds context
- Premium feel

**Cons:**
- Need high-res photos
- Text readability on mobile

---

### Option 2C: Dual Executive (CEO + CFO)

```
┌──────────────┬──────────────────────┐
│ [CEO Photo]  │  [CFO Photo]         │
│              │                      │
│ Sam Pollock  │  David Krantz        │
│ CEO          │  CFO                 │
│              │                      │
│  Brookfield Infrastructure          │
│  Q3 2025 • FFO: $654M (+9%)        │
└──────────────┴──────────────────────┘
```

**Layout:**
- Top: CEO + CFO photos side-by-side
- Bottom: Company + key metric

**Pros:**
- Shows leadership team
- Professional credibility
- Unique (not common on YouTube)

**Cons:**
- Need photos of both executives
- More complex layout

---

## How to Build CEO/Executive Database

### Option A: Manual Collection (Start Small)

**Process:**
1. Create directory structure:
   ```
   /var/markethawk/executives/
   ├── AAPL/
   │   ├── tim_cook_ceo.jpg
   │   └── luca_maestri_cfo.jpg
   ├── HOOD/
   │   ├── vlad_tenev_ceo.jpg
   │   └── jason_warnick_cfo.jpg
   └── BIP/
       ├── sam_pollock_ceo.jpg
       └── david_krantz_cfo.jpg
   ```

2. Manually download from:
   - Company investor relations pages
   - LinkedIn (screenshot profile photos)
   - Press releases
   - News articles

3. Naming convention:
   - `{first_name}_{last_name}_{role}.jpg`
   - Lowercase, underscores
   - Role: ceo, cfo, coo, etc.

**Pros:**
- High quality images
- Full control
- Start immediately

**Cons:**
- Time-consuming
- Doesn't scale to 1000+ companies

---

### Option B: Automated Scraping

**Sources:**
1. **Company Investor Relations Pages**
   ```python
   # Scrape IR page for executive team section
   url = f"https://{company_domain}/investors/leadership"
   # Extract headshots from page
   ```

2. **LinkedIn (via API)**
   ```python
   # Requires LinkedIn API access
   # Search for: "{Company Name} CEO"
   # Extract profile photo
   ```

3. **Google Images (Fallback)**
   ```python
   # Search: "{CEO Name} {Company} headshot"
   # Filter: Faces, high-res
   # Download top result
   ```

**Pros:**
- Scales to 1000+ companies
- Automated updates
- No manual work

**Cons:**
- Image quality varies
- Copyright concerns
- API rate limits

---

### Option C: Third-Party APIs

**1. Clearbit Logo API**
- URL: https://clearbit.com/logo
- Has executive photos for some companies
- Free tier available
- Example: `https://logo.clearbit.com/robinhood.com`

**2. PeopleDataLabs**
- URL: https://www.peopledatalabs.com/
- Professional database
- Includes headshots
- Paid API ($99/mo+)

**3. Hunter.io (Email + Photos)**
- URL: https://hunter.io/
- Finds email + LinkedIn profiles
- Can extract photos from LinkedIn
- Paid ($49/mo+)

**4. Crunchbase API**
- URL: https://www.crunchbase.com/
- Executive team info
- Some photos available
- Paid ($29/mo+)

**Pros:**
- High-quality data
- Maintained by third party
- Scales well

**Cons:**
- Monthly cost
- API limits
- Not 100% coverage

---

## Recommendation

### Phase 1 (Now - Next 30 days)
**Use Option 1A: Metric-Focused Thumbnails**
- Fast to implement
- Works with current pipeline
- No dependency on executive photos

```bash
# Current workflow
python lens/smart_thumbnail_generator.py \
  --video /var/markethawk/jobs/BIP_Q3_2025/renders/take1.mp4 \
  --data /var/markethawk/jobs/BIP_Q3_2025/job.yaml \
  --output /var/markethawk/jobs/BIP_Q3_2025/thumbnails/
```

### Phase 2 (After 10-20 videos)
**Start Manual Collection for Top Companies**
- Top 50 most-watched companies (AAPL, MSFT, GOOGL, etc.)
- Manually download CEO/CFO photos
- Use Option 2A: Split Screen (CEO + Metrics)
- Build database incrementally

### Phase 3 (Scale to 1000+ companies)
**Automate with Scraping + APIs**
- Scrape company IR pages (free)
- Use Clearbit API for logos + some photos (free tier)
- LinkedIn scraping for missing executives
- Fallback to Google Images search

---

## Thumbnail Best Practices

### YouTube CTR Optimization

**What works:**
- ✅ Faces (especially looking at camera)
- ✅ Large text (readable on mobile)
- ✅ High contrast colors
- ✅ Numbers (metrics, percentages)
- ✅ Emotion (surprised, serious)

**What doesn't work:**
- ❌ Too much text
- ❌ Low contrast
- ❌ Complex graphics
- ❌ Generic stock photos
- ❌ Busy backgrounds

### Text Guidelines

- **Font size:** Minimum 48px (readable on mobile)
- **Font:** Bold, sans-serif (Arial, Helvetica, Roboto)
- **Colors:** High contrast (white text on dark bg, or vice versa)
- **Outline:** Add text stroke/shadow for readability
- **Line limit:** Maximum 3 lines of text

### Image Quality

- **Resolution:** 1920x1080 (1080p)
- **Format:** JPG (smaller file size than PNG)
- **Compression:** 80-90% quality
- **File size:** Under 2MB

---

## Database Schema (Future)

```sql
-- executives table
CREATE TABLE executives (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  first_name TEXT,
  last_name TEXT,
  role TEXT, -- CEO, CFO, COO, etc.
  photo_url TEXT, -- URL to headshot
  photo_source TEXT, -- linkedin, company_ir, google, manual
  linkedin_url TEXT,
  bio TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Index for fast lookups
CREATE INDEX idx_executives_company ON executives(company_id);
CREATE INDEX idx_executives_role ON executives(role);
```

---

**Last Updated:** 2025-11-09
**Next Steps:** Render BIP take1, generate text-only thumbnails, plan Phase 2 executive database
