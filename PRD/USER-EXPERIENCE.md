# USER-EXPERIENCE.md

Complete user experience strategy for MarketHawk SaaS platform.

---

## Overview

MarketHawk's UX focuses on:
1. **Show, Don't Tell** - Data visualizations over marketing copy
2. **Progressive Disclosure** - Reveal features as users engage
3. **Frictionless Authentication** - Google One Tap (no explicit sign-in)
4. **Strategic Paywalls** - Free tier with contextual upgrade prompts
5. **Personalization** - Recommendations based on watch history

---

## Landing Page Design ("Show, Don't Tell")

### Design Principles

**❌ What NOT to Do:**
- Long marketing paragraphs
- Generic "Sign Up Now" hero sections
- Wall of text explaining features
- Stock photos of "business people"

**✅ What to Do Instead:**
- Interactive earnings dashboard immediately visible
- Auto-playing video preview (muted)
- Live data visualizations
- Let the product speak for itself

---

### Landing Page Layout

```tsx
// app/page.tsx

export default function HomePage() {
  return (
    <main>
      {/* Hero: Interactive Earnings Grid */}
      <section className="h-screen bg-gradient-to-br from-slate-900 to-slate-800">
        <EarningsGrid companies={featuredCompanies} />
      </section>

      {/* Featured Video (auto-play muted) */}
      <section className="h-screen bg-black">
        <FeaturedVideoPlayer
          videoId="latest"
          autoPlay
          muted
          loop
        />
      </section>

      {/* Live Dashboard */}
      <section className="h-screen bg-slate-900">
        <LiveEarningsDashboard />
      </section>

      {/* Pricing (only after user scrolls) */}
      <section className="min-h-screen bg-gradient-to-br from-blue-900 to-slate-900">
        <PricingSection />
      </section>
    </main>
  );
}
```

---

### Interactive Earnings Grid

**Component:**
```tsx
// components/EarningsGrid.tsx

'use client';

import {useState} from 'react';

export function EarningsGrid({companies}) {
  const [hovered, setHovered] = useState(null);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-8">
      {companies.map(company => (
        <div
          key={company.ticker}
          className="bg-slate-800 rounded-lg p-6 hover:scale-105 transition cursor-pointer"
          onMouseEnter={() => setHovered(company.ticker)}
          onMouseLeave={() => setHovered(null)}
        >
          <div className="flex items-center gap-3 mb-4">
            <img src={company.logo} className="w-12 h-12 rounded" />
            <div>
              <h3 className="font-bold text-white">{company.ticker}</h3>
              <p className="text-sm text-gray-400">{company.name}</p>
            </div>
          </div>

          <div className="space-y-2">
            <Metric label="Revenue" value={company.revenue} change={company.revenueChange} />
            <Metric label="EPS" value={company.eps} change={company.epsChange} />
          </div>

          {hovered === company.ticker && (
            <div className="mt-4 text-sm text-blue-400">
              View earnings call →
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function Metric({label, value, change}) {
  const isPositive = change >= 0;

  return (
    <div className="flex justify-between items-center">
      <span className="text-gray-400 text-sm">{label}</span>
      <div className="text-right">
        <div className="text-white font-semibold">{value}</div>
        <div className={isPositive ? 'text-green-400' : 'text-red-400'}>
          {isPositive ? '↑' : '↓'} {Math.abs(change)}%
        </div>
      </div>
    </div>
  );
}
```

---

## Free Tier Strategy (MVP Simplified)

### Video Access Control - "2 Videos Per Day"

**MVP Approach:** Simple daily limit instead of complex 50% video paywalls.

**✅ Free Tier Access:**
- Watch **2 full videos per day** (resets every 24 hours)
- View **basic company info** and earnings call metadata
- Browse **all videos** (titles, thumbnails, descriptions)
- Access **public videos** without login

**❌ Free Tier Restrictions:**
- Daily limit of 2 videos (tracked per user)
- Must be logged in to watch videos
- Cannot interact with advanced charts (future feature)
- Cannot download transcripts (future feature)
- No email alerts for earnings dates (future feature)

**Database Implementation:**
- `visibility` column on `earnings_calls` table: `'public' | 'freemium' | 'premium'`
- `video_views` table tracks views with timestamps
- Daily limit query: count views in last 24 hours

**UI/UX Principles:**
- **Optimistic UI**: Don't show limit upfront
- **Fail Late**: Let users select video, show limit only when reached
- **Clear feedback**: "You've watched 2/2 videos today. Upgrade for unlimited access."
- **Contextual upgrade**: Show tier comparison when limit hit

---

### Legacy Paywall Strategy (For Reference - Not MVP)

**Note:** The following 50% video progress paywall is documented for future consideration but not implemented in MVP.

### What Free Users Get (Legacy Design)

**✅ Free Tier Access:**
- Watch **50% of video** (first half only)
- View **partial charts** (no zoom, no filter, no interactions)
- Read **summary only** of quarterly reports (not full PDF)
- Browse **all videos** (titles, thumbnails)
- View **basic company info**

**❌ Free Tier Restrictions:**
- Cannot watch full video (paused at 50%)
- Cannot interact with charts
- Cannot download transcripts
- Cannot access full quarterly reports
- No email alerts for earnings dates

---

### Paywall Trigger Points (Legacy - Not MVP)

**1. 50% Video Progress**
```tsx
// components/VideoPlayer.tsx

'use client';

import {useEffect, useState} from 'react';

export function VideoPlayer({videoId, user}) {
  const [progress, setProgress] = useState(0);
  const isFreeUser = !user || user.tier === 'free';

  useEffect(() => {
    if (isFreeUser && progress >= 0.5) {
      pauseVideo();
      showUpgradeModal({
        title: 'Enjoying the earnings call?',
        message: 'Upgrade to Pro to watch the full video and access interactive charts.',
        cta: 'Upgrade to Pro - $29/month',
      });
    }
  }, [progress, isFreeUser]);

  return (
    <div className="relative">
      <YouTubeEmbed
        videoId={videoId}
        onProgressUpdate={setProgress}
      />

      {isFreeUser && progress >= 0.5 && (
        <div className="absolute inset-0 bg-black/80 flex items-center justify-center">
          <UpgradePrompt />
        </div>
      )}
    </div>
  );
}
```

**2. Chart Interaction**
```tsx
// components/InteractiveChart.tsx

export function InteractiveChart({data, user}) {
  const isFreeUser = !user || user.tier === 'free';

  function handleChartClick() {
    if (isFreeUser) {
      showUpgradeModal({
        title: 'Interactive charts are a Pro feature',
        message: 'Upgrade to zoom, filter, and explore financial data.',
        cta: 'Upgrade to Pro - $29/month',
      });
      return;
    }

    // Enable full chart interactions
    enableChartZoom();
    enableChartFilters();
  }

  return (
    <div className={isFreeUser ? 'cursor-not-allowed opacity-75' : ''}>
      <Chart
        data={data}
        onClick={handleChartClick}
        interactive={!isFreeUser}
      />

      {isFreeUser && (
        <div className="text-center mt-2 text-sm text-gray-500">
          🔒 Upgrade to interact with charts
        </div>
      )}
    </div>
  );
}
```

**3. Quarterly Report Download**
```tsx
// components/QuarterlyReportLink.tsx

export function QuarterlyReportLink({reportUrl, user}) {
  const isFreeUser = !user || user.tier === 'free';

  async function handleDownload() {
    if (isFreeUser) {
      showUpgradeModal({
        title: 'Full reports are a Pro feature',
        message: 'Access full SEC filings and quarterly reports.',
        cta: 'Upgrade to Pro - $29/month',
      });
      return;
    }

    // Download full report
    window.open(reportUrl, '_blank');
  }

  return (
    <button
      onClick={handleDownload}
      className={isFreeUser ? 'opacity-75' : ''}
    >
      📄 {isFreeUser ? 'View Summary (Free)' : 'Download Full Report'}
    </button>
  );
}
```

---

## Upgrade Prompts (Contextual)

### Upgrade Modal Component

```tsx
// components/UpgradeModal.tsx

'use client';

import {Dialog} from '@/components/ui/dialog';

export function UpgradeModal({
  isOpen,
  onClose,
  title,
  message,
  cta,
  features,
}) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <div className="p-8 max-w-md">
        <h2 className="text-2xl font-bold mb-4">{title}</h2>
        <p className="text-gray-600 mb-6">{message}</p>

        <div className="space-y-3 mb-6">
          {features.map(feature => (
            <div key={feature} className="flex items-center gap-2">
              <CheckIcon className="text-green-500" />
              <span>{feature}</span>
            </div>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-gray-200 hover:bg-gray-300 px-6 py-3 rounded"
          >
            Maybe Later
          </button>
          <button
            onClick={() => window.location.href = '/pricing'}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded"
          >
            {cta}
          </button>
        </div>
      </div>
    </Dialog>
  );
}
```

---

## Subscription Tiers

### Free Tier (Default)

**Features:**
- Watch 50% of videos
- View partial charts (no interactions)
- Read summaries of quarterly reports
- Browse all videos

**Limitations:**
- No full video access
- No chart interactions
- No downloads
- No email alerts

**Goal:** Get users hooked, then convert to paid

---

### Pro Tier ($29/month)

**Features:**
- ✅ **Unlimited video access** - Watch full earnings calls
- ✅ **Full interactive charts** - Zoom, filter, explore
- ✅ **Download transcripts** - PDF, JSON, VTT formats
- ✅ **Email alerts** - Notified 1 day before earnings dates
- ✅ **Priority support** - Faster response times

**Target Users:**
- Individual investors
- Day traders
- Finance enthusiasts
- Analysts (personal use)

---

### Team Tier ($99/month)

**Features:**
- ✅ **All Pro features**
- ✅ **Up to 10 team members** - Shared organization account
- ✅ **Shared watchlists** - Collaborate on companies to track
- ✅ **Custom alerts** - Set thresholds for metrics
- ✅ **API access** - Programmatic access to transcripts/data

**Target Users:**
- Investment firms
- Hedge funds
- Corporate finance teams
- Financial advisors

---

## Personalization Engine

### Recommendation Algorithm

**Inputs:**
- Watch history (companies, industries)
- Engagement (likes, saves, shares)
- Watch time per video
- Chart interactions
- Industry preferences (explicit + inferred)

**Recommendation Types:**

#### 1. Related Earnings (Same Industry)

```sql
SELECT v.* FROM videos v
JOIN companies c ON v.company_id = c.id
WHERE c.industry = $user_preferred_industry
AND v.id NOT IN (SELECT video_id FROM user_watch_history WHERE user_id = $user_id)
ORDER BY v.published_at DESC
LIMIT 10
```

**Example:**
- User watches AAPL → Recommend MSFT, GOOGL (tech industry)

#### 2. Trending Now (High Engagement)

```sql
SELECT v.*, COUNT(ve.id) as engagement_score
FROM videos v
JOIN video_engagement ve ON v.id = ve.video_id
WHERE ve.timestamp > NOW() - INTERVAL '24 hours'
GROUP BY v.id
ORDER BY engagement_score DESC
LIMIT 10
```

**Example:**
- TSLA earnings just released → High engagement → Show to everyone

#### 3. Companies You Might Like (Collaborative Filtering)

```sql
-- Find users with similar watch history
WITH similar_users AS (
  SELECT DISTINCT wh2.user_id
  FROM user_watch_history wh1
  JOIN user_watch_history wh2 ON wh1.video_id = wh2.video_id
  WHERE wh1.user_id = $current_user_id
  AND wh2.user_id != $current_user_id
)
SELECT v.*
FROM videos v
JOIN user_watch_history wh ON v.id = wh.video_id
WHERE wh.user_id IN (SELECT user_id FROM similar_users)
AND v.id NOT IN (SELECT video_id FROM user_watch_history WHERE user_id = $current_user_id)
GROUP BY v.id
ORDER BY COUNT(*) DESC
LIMIT 10
```

**Example:**
- Users who watched AAPL also watched NVDA → Recommend NVDA

#### 4. Upcoming Earnings (Calendar-Based)

```sql
SELECT c.*, ec.earnings_date
FROM companies c
JOIN earnings_calendar ec ON c.id = ec.company_id
WHERE ec.earnings_date BETWEEN NOW() AND NOW() + INTERVAL '7 days'
AND c.id IN (SELECT company_id FROM user_watchlist WHERE user_id = $user_id)
ORDER BY ec.earnings_date ASC
```

**Example:**
- AAPL earnings in 2 days → Send email alert
- Show banner on homepage

---

## Content Gating Strategy

### Progressive Content Reveal

**Page Scroll Behavior (Free Users):**

```tsx
// components/ContentGate.tsx

'use client';

import {useEffect, useState} from 'react';

export function ContentGate({children, user}) {
  const [scrollPercent, setScrollPercent] = useState(0);
  const isFreeUser = !user || user.tier === 'free';

  useEffect(() => {
    function handleScroll() {
      const scrolled = (window.scrollY / document.body.scrollHeight) * 100;
      setScrollPercent(scrolled);
    }

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="relative">
      {children}

      {/* Blur content at 50% scroll for free users */}
      {isFreeUser && scrollPercent >= 50 && (
        <div className="fixed inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent backdrop-blur-sm">
          <div className="absolute bottom-20 inset-x-0 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Want to see more?
            </h2>
            <p className="text-gray-300 mb-6">
              Upgrade to Pro for unlimited access to earnings calls and interactive charts.
            </p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg">
              Upgrade to Pro - $29/month
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## A/B Testing Ideas

### Test 1: Paywall Timing
- **Variant A:** Paywall at 50% video
- **Variant B:** Paywall at 75% video
- **Metric:** Conversion rate (free → paid)

### Test 2: Upgrade CTA
- **Variant A:** "Upgrade to Pro"
- **Variant B:** "Unlock Full Video"
- **Metric:** Click-through rate

### Test 3: Free Tier Chart Access
- **Variant A:** No chart interactions (current)
- **Variant B:** Limited chart interactions (3 per day)
- **Metric:** Conversion rate + engagement

---

## User Onboarding Flow

**First Visit:**
1. Land on homepage → See interactive earnings grid
2. Scroll → Auto-playing video preview (muted)
3. Click video → Google One Tap appears
4. Sign in with one click
5. Watch video → Paused at 50%
6. Upgrade prompt → "Unlock full video"

**Goal:** Minimize friction, maximize value demonstration

---

## Related Documentation

- **WEB-APP-GUIDE.md** - Google One Tap implementation
- **SEO-STRATEGY.md** - Content optimization for organic traffic
- **ADMIN-DASHBOARD.md** - Track conversion metrics
- **DATABASE-SCHEMA.md** - User tier and subscription tables

---

**Last Updated:** 2025-11-10
