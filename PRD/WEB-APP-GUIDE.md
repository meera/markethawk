# WEB-APP-GUIDE.md

Complete guide for building the MarketHawk SaaS web application.

---

## Overview

MarketHawk web app is a Next.js-based SaaS platform that provides:
- Interactive earnings call videos
- Financial data visualizations (charts rendered from data, not static images)
- User authentication with Google One Tap
- Subscription management via Stripe
- SEO-optimized video pages with ISR

---

## Technology Stack

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** TailwindCSS
- **UI Components:** shadcn/ui
- **State Management:** React Context / Zustand
- **Forms:** React Hook Form + Zod validation

### Backend
- **Database:** PostgreSQL with Drizzle ORM
  - Avoid Neon-specific packages
  - Use standard PostgreSQL connection
  - Cost-effective serverless deployment
- **Authentication:** Better Auth
  - **Google One Tap** (automatic, no explicit sign-in page)
  - Organization/team structure support
  - Stripe plugin for payments
  - Seamless authentication (users sign in as they browse)
- **Payments:** Stripe
  - Integrated via Better Auth plugin
  - Subscription management
  - Usage-based billing (future)
- **Storage:** Cloudflare R2
  - **Bucket:** `markethawk`
  - Video files, thumbnails, transcripts
  - Public CDN access

### Infrastructure
- **Hosting:** Vercel (Next.js)
- **CDN:** Cloudflare (R2 + caching)
- **Monitoring:** Custom admin dashboard
- **Email:** Resend or SendGrid (transactional)

---

## Authentication: Google One Tap (No Explicit Sign-in)

### What is Google One Tap?

**Traditional OAuth (❌):**
```
User clicks "Sign in with Google"
  → Redirects to google.com
  → User logs in
  → Redirects back to app
  → User is logged in
```

**Google One Tap (✅):**
```
User visits site
  → Small popup appears automatically
  → User clicks once
  → Instantly signed in (no redirect)
```

### Implementation with Better Auth

#### 1. Configure Google OAuth

```typescript
// lib/auth.ts

import {betterAuth} from 'better-auth';
import {google} from 'better-auth/providers';

export const auth = betterAuth({
  database: {
    provider: 'postgres',
    url: process.env.DATABASE_URL,
  },
  providers: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      // Enable One Tap
      oneTap: true,
    },
  },
  // Organization plugin for team structure
  plugins: [
    organizationPlugin(),
    stripePlugin({
      stripeSecretKey: process.env.STRIPE_SECRET_KEY!,
    }),
  ],
});
```

#### 2. Frontend: Auto-display One Tap Prompt

```tsx
// components/auth/GoogleOneTap.tsx

'use client';

import {useEffect} from 'react';
import Script from 'next/script';

export function GoogleOneTap() {
  useEffect(() => {
    // Initialize Google One Tap
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
        auto_select: true, // Auto-select if user previously signed in
        cancel_on_tap_outside: false,
      });

      // Display the One Tap prompt
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed()) {
          console.log('One Tap not displayed:', notification.getNotDisplayedReason());
        }
      });
    }
  }, []);

  async function handleCredentialResponse(response) {
    // Send credential to backend
    const res = await fetch('/api/auth/google-one-tap', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({credential: response.credential}),
    });

    if (res.ok) {
      // User is now signed in
      window.location.reload();
    }
  }

  return (
    <>
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
      />
      <div id="g_id_onload" />
    </>
  );
}
```

#### 3. Add to Layout (Shows on Every Page)

```tsx
// app/layout.tsx

import {GoogleOneTap} from '@/components/auth/GoogleOneTap';
import {auth} from '@/lib/auth-client';

export default async function RootLayout({children}) {
  const session = await auth.getSession();

  return (
    <html>
      <body>
        {/* Only show One Tap if user is NOT logged in */}
        {!session && <GoogleOneTap />}

        {children}
      </body>
    </html>
  );
}
```

#### 4. Backend: Handle One Tap Credential

```typescript
// app/api/auth/google-one-tap/route.ts

import {OAuth2Client} from 'google-auth-library';

const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);

export async function POST(req: Request) {
  const {credential} = await req.json();

  // Verify the Google credential
  const ticket = await client.verifyIdToken({
    idToken: credential,
    audience: process.env.GOOGLE_CLIENT_ID,
  });

  const payload = ticket.getPayload();

  if (!payload) {
    return Response.json({error: 'Invalid credential'}, {status: 400});
  }

  // Find or create user
  let user = await db.users.findUnique({
    where: {email: payload.email},
  });

  if (!user) {
    user = await db.users.create({
      data: {
        email: payload.email!,
        name: payload.name!,
        avatar_url: payload.picture,
      },
    });
  }

  // Create session with Better Auth
  const session = await auth.createSession({userId: user.id});

  return Response.json({
    success: true,
    session,
  });
}
```

### User Experience Flow

**First Visit (Not Logged In):**
```
1. User lands on market-hawk.com
2. Google One Tap popup appears in corner
   ┌──────────────────────────────┐
   │ Sign in with Google          │
   │                              │
   │ [john@gmail.com]       [→]  │
   │                              │
   │ Continue as John             │
   └──────────────────────────────┘
3. User clicks "Continue as John"
4. Instantly signed in (no redirect)
5. Popup disappears
```

**Subsequent Visits:**
```
1. User returns to market-hawk.com
2. If auto_select: true, automatically signed in
3. No popup shown (seamless)
```

**When User Hits Paywall:**
```
User at 50% video progress → Login required

If already signed in via One Tap:
  → Show upgrade to Pro prompt

If NOT signed in:
  → Show One Tap popup again (contextual)
  → "Sign in to continue watching"
```

### Configuration Options

```typescript
window.google.accounts.id.initialize({
  client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,

  // Auto-select user if they previously signed in
  auto_select: true,

  // Don't close on outside click (less annoying)
  cancel_on_tap_outside: false,

  // Show on specific pages only
  context: 'signin', // or 'signup', 'use'

  // Customize prompt
  prompt_parent_id: 'g_id_onload',

  // Styling
  theme: 'outline', // or 'filled_blue', 'filled_black'
  size: 'large', // or 'medium', 'small'
});
```

### Best Practices

**1. Don't Show Too Early**
```typescript
// Wait until user scrolls or interacts
useEffect(() => {
  const showOneTap = () => {
    window.google.accounts.id.prompt();
  };

  // Show after 3 seconds OR on scroll
  const timer = setTimeout(showOneTap, 3000);
  const handleScroll = () => {
    showOneTap();
    window.removeEventListener('scroll', handleScroll);
  };

  window.addEventListener('scroll', handleScroll, {once: true});

  return () => {
    clearTimeout(timer);
    window.removeEventListener('scroll', handleScroll);
  };
}, []);
```

**2. Contextual Prompts**
```typescript
// Show at strategic moments
// - Before 50% video progress
// - Before clicking external link
// - Before downloading content

if (videoProgress > 0.4 && !user) {
  showGoogleOneTap();
}
```

**3. Respect User Dismissal**
```typescript
// Don't show again if user closes it
const dismissed = localStorage.getItem('oneTapDismissed');

if (!dismissed) {
  window.google.accounts.id.prompt((notification) => {
    if (notification.getDismissedReason() === 'credential_returned') {
      // User signed in
    } else {
      // User dismissed
      localStorage.setItem('oneTapDismissed', 'true');
    }
  });
}
```

---

## Stripe Integration

### Setup

```bash
npm install stripe @stripe/stripe-js
```

### Better Auth Stripe Plugin

```typescript
// lib/auth.ts

import {stripePlugin} from 'better-auth/plugins';

export const auth = betterAuth({
  // ... other config
  plugins: [
    stripePlugin({
      stripeSecretKey: process.env.STRIPE_SECRET_KEY!,
      // Automatically sync users to Stripe customers
      syncUsers: true,
      // Handle subscription events
      webhookEndpoint: '/api/webhooks/stripe',
    }),
  ],
});
```

### Subscription Tiers

```typescript
// lib/stripe/plans.ts

export const PLANS = {
  free: {
    name: 'Free',
    price: 0,
    features: [
      'Watch 50% of videos',
      'View partial charts',
      'Limited quarterly reports',
    ],
  },
  pro: {
    name: 'Pro',
    price: 29,
    priceId: process.env.STRIPE_PRICE_ID_PRO,
    features: [
      'Unlimited video access',
      'Full interactive charts',
      'Download transcripts',
      'Email alerts for earnings dates',
      'Priority support',
    ],
  },
  team: {
    name: 'Team',
    price: 99,
    priceId: process.env.STRIPE_PRICE_ID_TEAM,
    features: [
      'All Pro features',
      'Up to 10 team members',
      'Shared watchlists',
      'Custom alerts',
      'API access',
    ],
  },
};
```

### Checkout Flow

```tsx
// components/UpgradeButton.tsx

'use client';

import {useState} from 'react';
import {loadStripe} from '@stripe/stripe-js';

export function UpgradeButton({plan}) {
  const [loading, setLoading] = useState(false);

  async function handleUpgrade() {
    setLoading(true);

    const res = await fetch('/api/checkout', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({priceId: plan.priceId}),
    });

    const {sessionId} = await res.json();

    const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);
    await stripe.redirectToCheckout({sessionId});
  }

  return (
    <button onClick={handleUpgrade} disabled={loading}>
      {loading ? 'Processing...' : `Upgrade to ${plan.name} - $${plan.price}/mo`}
    </button>
  );
}
```

### Webhook Handler

```typescript
// app/api/webhooks/stripe/route.ts

import {headers} from 'next/headers';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(req: Request) {
  const body = await req.text();
  const signature = headers().get('stripe-signature')!;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err) {
    return Response.json({error: 'Invalid signature'}, {status: 400});
  }

  // Handle events
  switch (event.type) {
    case 'customer.subscription.created':
    case 'customer.subscription.updated':
      const subscription = event.data.object as Stripe.Subscription;
      await db.subscriptions.upsert({
        where: {stripe_subscription_id: subscription.id},
        update: {
          status: subscription.status,
          current_period_end: new Date(subscription.current_period_end * 1000),
        },
        create: {
          user_id: subscription.metadata.userId,
          stripe_subscription_id: subscription.id,
          status: subscription.status,
          plan: subscription.metadata.plan,
          current_period_end: new Date(subscription.current_period_end * 1000),
        },
      });
      break;

    case 'customer.subscription.deleted':
      const deletedSub = event.data.object as Stripe.Subscription;
      await db.subscriptions.update({
        where: {stripe_subscription_id: deletedSub.id},
        data: {status: 'canceled'},
      });
      break;
  }

  return Response.json({received: true});
}
```

---

## ISR Optimization (Blog-Like Performance)

**MarketHawk is a content site with 100+ video pages** → Use Next.js ISR for static performance

### Pre-render All Video Pages

```typescript
// app/[company]/[slug]/page.tsx

// Revalidate every hour
export const revalidate = 3600;

// Pre-render all video pages at build time
export async function generateStaticParams() {
  const videos = await db.videos.findMany({
    where: {status: 'published'},
    include: {company: true},
  });

  return videos.map((video) => ({
    company: video.company.ticker.toLowerCase(),
    slug: video.slug,
  }));
}

// This page is pre-rendered as static HTML
export default async function VideoPage({params}) {
  const video = await getVideo(params.slug);

  return (
    <div>
      <VideoEmbed youtubeId={video.youtube_id} />
      <ChartSection data={video.earnings_data} />
      <RelatedVideos videos={video.recommendations} />
    </div>
  );
}
```

**Result:**
- User visits `/aapl/q4-2024` → **instant load** (pre-rendered HTML)
- Page updates hourly (revalidates from database)
- Build time: ~5-10 minutes for 100 pages
- Page load: <500ms (served from CDN)

---

## Charts: Data-Driven, Not Static Images

### Philosophy

**Store chart DATA in database, render charts dynamically on frontend**

```
Traditional (❌):                   MarketHawk (✅):
─────────────────                   ─────────────────
1. Generate chart PNG               1. Store data in database (JSON)
2. Upload to R2                     2. Render chart client-side (Chart.js)
3. Display <img> tag                3. Charts are interactive (zoom, hover)
4. Static, not interactive          4. Can re-style without re-uploading
```

### Database Schema

```sql
CREATE TABLE earnings_data (
  id UUID PRIMARY KEY,
  video_id UUID REFERENCES videos(id),

  -- All chart data as JSON
  financial_data JSONB NOT NULL

  -- Example:
  -- {
  --   "revenue": {
  --     "current": 89500000000,
  --     "segments": [
  --       {"name": "iPhone", "value": 43800000000},
  --       {"name": "Services", "value": 22300000000}
  --     ]
  --   },
  --   "eps": {"current": 1.64, "estimate": 1.58}
  -- }
);
```

### Chart Component

```tsx
'use client';

import {Bar} from 'react-chartjs-2';

export function RevenueChart({data}) {
  const chartData = {
    labels: data.revenue.segments.map(s => s.name),
    datasets: [{
      data: data.revenue.segments.map(s => s.value / 1e9),
      backgroundColor: ['#007AFF', '#5AC8FA', '#34C759'],
    }],
  };

  return <Bar data={chartData} options={chartOptions} />;
}
```

**Benefits:**
- ✅ Interactive charts (zoom, filter, hover tooltips)
- ✅ No image storage costs
- ✅ Re-style charts without re-uploading
- ✅ Export to PNG on-demand (for social sharing)

---

## Environment Variables

```bash
# Database
DATABASE_URL="postgresql://user:password@host:5432/markethawk"

# Better Auth
AUTH_SECRET="your-secret-key"
AUTH_GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
AUTH_GOOGLE_CLIENT_SECRET="xxx"

# Stripe
STRIPE_SECRET_KEY="sk_live_..."
STRIPE_PUBLISHABLE_KEY="pk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
STRIPE_PRICE_ID_PRO="price_xxx"
STRIPE_PRICE_ID_TEAM="price_xxx"

# YouTube
YOUTUBE_API_KEY="..."
YOUTUBE_CLIENT_ID="..."
YOUTUBE_CLIENT_SECRET="..."
YOUTUBE_REFRESH_TOKEN="..."

# Cloudflare R2
R2_ACCOUNT_ID="..."
R2_ACCESS_KEY_ID="..."
R2_SECRET_ACCESS_KEY="..."
R2_BUCKET_NAME="markethawk"
R2_PUBLIC_URL="https://pub-{hash}.r2.dev"

# Email
RESEND_API_KEY="..."

# Analytics (optional)
NEXT_PUBLIC_GA_ID="..."
```

---

## Testing Google One Tap

**Chrome DevTools:**
```
1. Open DevTools → Application → Cookies
2. Delete all cookies for localhost:3000
3. Refresh page
4. One Tap should appear
```

**Test Auto-Select:**
```
1. Sign in once via One Tap
2. Sign out
3. Refresh page
4. Should auto-sign in (if auto_select: true)
```

---

## Related Documentation

- **DATABASE-SCHEMA.md** - Complete database schema with Drizzle examples
- **USER-EXPERIENCE.md** - Free tier restrictions, paywalls, personalization
- **SEO-STRATEGY.md** - YouTube + website SEO templates
- **ADMIN-DASHBOARD.md** - Monitoring, analytics, real-time metrics
- **DEPLOYMENT.md** - Vercel deployment, environment variables

---

**Last Updated:** 2025-11-10
