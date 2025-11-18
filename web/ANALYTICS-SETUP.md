# Analytics Setup Guide for MarketHawk

Complete guide to set up Facebook Pixel, PostHog, and Google Analytics in Next.js 16.

## 1. Environment Variables

Add to `.env.local`:

```bash
# Google Analytics
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX

# Facebook Pixel
NEXT_PUBLIC_FB_PIXEL_ID=123456789012345

# PostHog
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

## 2. Install Packages

```bash
npm install @next/third-parties posthog-js
```

## 3. Implementation

### A. PostHog Provider (`app/providers.tsx`)

```typescript
'use client'

import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import { useEffect } from 'react'

export function PHProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (typeof window !== 'undefined' && process.env.NEXT_PUBLIC_POSTHOG_KEY) {
      posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
        api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
        capture_pageview: true,
        autocapture: true,
      })
    }
  }, [])

  return <PostHogProvider client={posthog}>{children}</PostHogProvider>
}
```

### B. Facebook Pixel (`app/_components/FacebookPixel.tsx`)

```typescript
'use client'

import Script from 'next/script'
import { usePathname, useSearchParams } from 'next/navigation'
import { useEffect } from 'react'

export function FacebookPixel() {
  const pathname = usePathname()
  const searchParams = useSearchParams()

  useEffect(() => {
    if (window.fbq) {
      window.fbq('track', 'PageView')
    }
  }, [pathname, searchParams])

  if (!process.env.NEXT_PUBLIC_FB_PIXEL_ID) return null

  return (
    <>
      <Script
        id="fb-pixel"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            !function(f,b,e,v,n,t,s)
            {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
            n.callMethod.apply(n,arguments):n.queue.push(arguments)};
            if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
            n.queue=[];t=b.createElement(e);t.async=!0;
            t.src=v;s=b.getElementsByTagName(e)[0];
            s.parentNode.insertBefore(t,s)}(window, document,'script',
            'https://connect.facebook.net/en_US/fbevents.js');
            fbq('init', '${process.env.NEXT_PUBLIC_FB_PIXEL_ID}');
          `,
        }}
      />
    </>
  )
}

declare global {
  interface Window {
    fbq: any
  }
}
```

### C. Update Root Layout (`app/layout.tsx`)

```typescript
import { GoogleAnalytics } from '@next/third-parties/google'
import { PHProvider } from './providers'
import { FacebookPixel } from './_components/FacebookPixel'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <PHProvider>
        <body>
          {children}
          <FacebookPixel />
        </body>
      </PHProvider>
      {process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID && (
        <GoogleAnalytics gaId={process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID} />
      )}
    </html>
  )
}
```

## 4. Tracking Events

### Track Search (`app/page.tsx` or search component)

```typescript
'use client'

import { usePostHog } from 'posthog-js/react'
import { sendGAEvent } from '@next/third-parties/google'

export function SearchBar() {
  const posthog = usePostHog()

  const handleSearch = (query: string, results: number) => {
    // Facebook Pixel
    if (window.fbq) {
      window.fbq('track', 'Search', {
        search_string: query,
        num_items: results,
      })
    }

    // PostHog
    posthog?.capture('search_performed', {
      query,
      result_count: results,
    })

    // Google Analytics
    sendGAEvent('event', 'search', {
      search_term: query,
      result_count: results,
    })
  }

  // ... rest of component
}
```

### Track Earnings Call View

```typescript
// In earnings call page
'use client'

import { useEffect } from 'react'
import { usePostHog } from 'posthog-js/react'
import { sendGAEvent } from '@next/third-parties/google'

export function EarningsCallPage({ company, ticker, quarter, year }) {
  const posthog = usePostHog()

  useEffect(() => {
    // Facebook Pixel
    if (window.fbq) {
      window.fbq('track', 'ViewContent', {
        content_name: `${company} ${quarter} ${year}`,
        content_ids: [ticker],
        content_type: 'earnings_call',
      })
    }

    // PostHog
    posthog?.capture('earnings_call_viewed', {
      company,
      ticker,
      quarter,
      year,
    })

    // Google Analytics
    sendGAEvent('event', 'view_earnings_call', {
      company,
      ticker,
      quarter: `${quarter} ${year}`,
    })
  }, [company, ticker, quarter, year, posthog])

  // ... rest of component
}
```

## 5. PostHog Dashboard Setup

### Create Custom Dashboard for Search Analytics

1. Go to PostHog → Insights → New Insight
2. Create insights for:
   - **Search Volume**: Count of `search_performed` events
   - **Top Searches**: Group by `query` property
   - **Search-to-Click Rate**: Funnel from search → earnings_call_viewed
   - **Zero Result Searches**: Filter where `result_count = 0`

### Session Recordings

Enable in PostHog settings to watch user sessions who performed searches.

## 6. Facebook Ads Retargeting

### Create Custom Audiences in Facebook Ads Manager

1. **Searchers Audience**:
   - Event: Search
   - Time: Last 30 days

2. **Earnings Call Viewers**:
   - Event: ViewContent
   - content_type = earnings_call
   - Time: Last 30 days

3. **High-Intent Users** (Lookalike):
   - Users who searched AND viewed 3+ earnings calls
   - Create Lookalike Audience from this segment

### Ad Campaign Structure

1. **Awareness Campaign**: Target all website visitors
2. **Consideration Campaign**: Target searchers
3. **Conversion Campaign**: Target earnings call viewers

## 7. Google Analytics Reports

### Custom Explorations

1. **Search Report**:
   - Dimension: search_term
   - Metrics: Event count, Users
   - Filter: event_name = search

2. **Funnel Analysis**:
   - Steps: page_view → search → view_earnings_call → subscribe

## 8. Verification

Test in browser console:

```javascript
// Check Facebook Pixel
window.fbq('track', 'Search', { search_string: 'test' })

// Check PostHog
window.posthog.capture('test_event')

// Check Google Analytics
gtag('event', 'test_event')
```

Use browser extensions:
- **Meta Pixel Helper** (Chrome)
- **Google Analytics Debugger** (Chrome)
- **PostHog Toolbar** (built-in, press Cmd+K)

## 9. Privacy & GDPR Compliance

Add cookie consent banner before initializing:

```typescript
// Only initialize after consent
if (hasUserConsent) {
  posthog.init(...)
  fbq('init', ...)
}
```

## 10. Next Steps

1. Set up conversion tracking for paid subscriptions
2. Create email sequences for retargeting
3. Set up A/B tests with PostHog feature flags
4. Monitor search queries daily to improve content
