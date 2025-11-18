# MarketHawk Monetization Strategy & User Journey

**Status:** Draft for Review
**Last Updated:** 2025-11-17
**Owner:** Product Team

---

## Overview

MarketHawk operates on a freemium model with two tiers:
- **Free Tier:** Limited daily access to encourage habit formation
- **Premium Tier:** Unlimited access for power users and professionals

**Pricing:**
- Free: $0 (10 earnings calls per day)
- Premium: $39/month (unlimited access)
- **No free trial** - immediate paid conversion
- Black Friday Promotion: Seasonal discount coupon (timing TBD)

---

## User Journey Flow

### 1. Anonymous Visitor (Not Logged In)

**Landing Experience:**
```
Home Page (/)
  ↓
Browse 7,600+ Companies
  ↓
Click Company (e.g., /companies/nvidia)
  ↓
See Latest Earnings Calls
  ↓
Click "Watch Q3 2025 Earnings Call"
  ↓
PAYWALL APPEARS (50% through content)
```


**What They Can See (No Login):**
- Browse all companies
- View company pages
- See earnings call metadata (date, quarter, duration)
- **Watch first 50% of any earnings call** (video/audio stops at 50%)
- **Read first 50% of transcript**

**Exception - Public Calls (Admin Override):**C
- Admin can mark specific earnings calls as "public"
- Public calls are fully accessible without login
- Use case: Featured content, viral marketing, partnerships

**What Triggers Auth Requirement:**
- Trying to watch beyond 50% of video
- Trying to read beyond 50% of transcript
- Trying to access AI insights/charts

**Paywall Message (Not Logged In):**
```
┌─────────────────────────────────────────┐
│  Sign in to continue watching           │
│                                          │
│  Free Account:                          │
│  • Watch 10 full earnings calls/day    │
│  • Full transcripts & AI insights      │
│  • Browse all 7,600+ companies         │
│                                          │
│  [Sign In with Google]  [Sign Up]      │
│                                          │
│  Premium: Unlimited access for $39/mo   │
└─────────────────────────────────────────┘
```

---

### 2. Free User (Logged In, 0-9 Views Today)

**Daily Quota: 10 earnings calls per day**

**What They Can Do:**
- ✅ Watch **full** earnings calls (up to 10/day)
- ✅ Read **full** transcripts
- ✅ Access **AI-generated insights**
- ✅ View **financial charts**
- ✅ Browse all companies
- ✅ Create watchlists (future feature)

**What Counts as a "View":**
- Opening any `/earnings/[id]` page
- Each unique earnings call ID counts once per day
- Counter resets at midnight UTC

**View Counter Display:**
```
┌────────────────────────────────┐
│ Daily Views: 7/10              │
│ Resets in: 6h 23m              │
│                                 │
│ Upgrade to Premium for         │
│ unlimited access                │
└────────────────────────────────┘
```

**Where Counter Appears:**
- Settings page (prominent)
- Subtle indicator in header (when 7+ views)
- Warning banner (at view 8-9)

---

### 3. Free User (Logged In, Hit 10 View Limit)

**When They Open 11th Earnings Call:**

**Soft Paywall Overlay:**
```
┌─────────────────────────────────────────┐
│  Daily Limit Reached (10/10)            │
│                                          │
│  You've used all your free views today  │
│  Resets in: 6h 23m                      │
│                                          │
│  Upgrade to Premium                     │
│  • Unlimited earnings calls             │
│  • Advanced analytics                   │
│  • Export data (coming soon)            │
│                                          │
│  $39/month                              │
│  [Upgrade Now]                          │
│                                          │
│  [Maybe Later - Close]                  │
└─────────────────────────────────────────┘
```

**Behavior:**
- Overlay covers 50% of content (blurred background)
- User can dismiss ("Maybe Later")
- Overlay reappears on next page load
- After 3 dismissals, show full-page interstitial

**Full-Page Interstitial (After 3 Dismissals):**
```
You've reached your daily limit

Free Plan: 10 earnings calls/day
Resets in: 5h 42m

┌─────────────────────────────────┐
│          Premium                 │
│         $39/month                │
│                                  │
│  ✓ Unlimited earnings calls     │
│  ✓ AI-powered insights          │
│  ✓ Advanced charts & metrics    │
│  ✓ Export data & reports        │
│  ✓ Priority support             │
│                                  │
│  [Start 7-Day Free Trial]       │
└─────────────────────────────────┘

[View Pricing Details]
```

---

### 4. Premium User (Paid Subscription)

**Monthly Price: $39**

**What They Get:**
- ✅ **Unlimited earnings call access**
- ✅ Full transcripts & AI insights
- ✅ Advanced financial charts
- ✅ Historical data (all quarters)
- ✅ Export transcripts (coming soon)
- ✅ Priority support
- ✅ Early access to new features

**No View Limits:**
- Watch as many earnings calls as needed
- No daily reset
- No paywall overlays

**Badge in Header:**
```
[Avatar] [Premium ⭐]
```

---

## Conversion Funnels

### Primary Conversion Path
```
Anonymous → Free Account → Premium
   ↓            ↓              ↓
50% wall    10/day limit   Unlimited
```

### Key Conversion Triggers

**Trigger 1: Anonymous 50% Wall**
- **When:** Halfway through first earnings call
- **CTA:** "Sign in free to watch the rest"
- **Goal:** Capture email, demonstrate value

**Trigger 2: View #8-9 Warning**
- **When:** Approaching daily limit
- **Message:** "Only 2 views left today. Upgrade for unlimited access."
- **Goal:** Convert while they're actively using

**Trigger 3: Hit Limit (View #11)**
- **When:** User tries to exceed 10 views
- **Message:** "Daily limit reached. Upgrade now or wait 6 hours."
- **Goal:** Impulse conversion during peak usage

**Trigger 4: Habit Formation (Day 7)**
- **When:** User has logged in 7 days in a row
- **Message:** "You're a power user! Get 20% off Premium this week."
- **Goal:** Reward engaged users

---

## Implementation Details

### Database Schema

**User Table Fields:**
```typescript
{
  // Subscription
  subscriptionTier: 'free' | 'premium'
  stripeCustomerId: string | null
  stripeSubscriptionId: string | null
  subscriptionStatus: 'active' | 'canceled' | 'past_due' | null
  subscriptionEndsAt: timestamp | null

  // Usage Tracking
  dailyViewCount: number (default: 0)
  lastViewDate: date | null  // For daily reset
}
```

**Earnings Call Views Table (Analytics):**
```typescript
{
  id: serial
  userId: string
  earningsCallId: string
  viewedAt: timestamp
  completed: boolean  // Did they watch to end?
}
```

**Public Calls Configuration (Hardcoded):**
```typescript
// /lib/public-earnings-calls.ts
// Simple array of earnings call IDs that are fully public
export const PUBLIC_EARNINGS_CALLS = [
  'PLBY-Q3-2025-wvcx',  // Featured call
  'NVDA-Q2-2024-xyz',   // Viral marketing
  // Add more as needed
];

// Helper function
export function isPublicCall(earningsCallId: string): boolean {
  return PUBLIC_EARNINGS_CALLS.includes(earningsCallId);
}
```

**Why Hardcoded (MVP):**
- ✅ Zero database changes needed
- ✅ No admin UI required
- ✅ Easy to add/remove (just edit array)
- ✅ Can move to database in V2 if needed

### View Tracking Logic

**When user opens `/earnings/[id]`:**
```typescript
1. Check if earnings call is public (hardcoded list)
   - if (isPublicCall(id)) → Allow full access (skip all checks)
   - NO → Continue to step 2

2. Check if user is logged in
   - NO → Show 50% content + hard stop at 50% playback
   - YES → Continue to step 3

3. Check subscription tier
   - premium → Allow full access
   - free → Continue to step 4

4. Check daily view count
   a. If lastViewDate < today:
      - Reset dailyViewCount = 0
      - Update lastViewDate = today

   b. If dailyViewCount < 10:
      - Increment dailyViewCount
      - Log view in analytics table
      - Allow full access

   c. If dailyViewCount >= 10:
      - Show soft paywall overlay
      - Allow dismissal (log dismissal count)
      - After 3 dismissals → full interstitial
```

### Reset Schedule
- Daily reset at **00:00 UTC**
- Backend cron job (or check on first request of day)
- Display countdown timer: "Resets in: 5h 42m"

---

## Media Delivery & Security

### R2 Private Bucket Strategy

**Current Setup:**
- Media files stored in private R2 bucket (not public)
- Server generates signed URLs with expiration
- Client receives time-limited access to media

**Security Model:**

**50% Limit = Client-Side Enforcement Only**
- Audio/video playback stopped at 50% in UI
- Tech-savvy users CAN bypass (acceptable for MVP)
- 95%+ of users won't attempt bypass
- Signed URLs expire quickly to limit sharing

**Rationale:**
- Faster time to market (2-3 hours vs 3-5 days for proxy)
- Acceptable risk for MVP (most users don't bypass)
- Can add stricter controls in V2 if needed
- Industry standard: Even major platforms use client-side DRM that's bypassable

### Signed URL Configuration

**Expiry Time: 1 hour**
- Balances security and user experience
- Covers typical earnings call length (30-60 minutes)
- Short enough to limit URL sharing
- Long enough for uninterrupted playback

**Generation:**
```typescript
// Server-side only
const signedUrl = await getSignedUrlForR2Media(r2Key, 3600); // 1 hour
```

### Handling URL Expiry

**What Happens:**
- User opens page → Fresh signed URL generated
- User plays audio → Works perfectly (buffered in browser)
- URL expires after 1 hour → New requests fail with 403

**Edge Cases:**
1. **User pauses for 1+ hours** → Audio won't resume
   - Solution: Show error + "Refresh Page" button

2. **User seeks after expiry** → Request fails
   - Solution: Auto page refresh with error message

3. **User stays on page 1+ hours** → Signed URL expires
   - MVP: Accept this limitation (rare case)
   - V2: Auto-refresh signed URL at 50-minute mark

**Error Handling (MVP):**
```typescript
// Detect playback errors
audio.onError = () => {
  if (signedUrlExpired) {
    showMessage("Session expired. Please refresh the page.");
    showRefreshButton();
  }
}
```

**Future Enhancement (V2):**
- Auto-refresh signed URLs before expiry
- Maintain playback position during refresh
- Seamless continuation without user action

### HLS Playlist Considerations

**Format:** `.m3u8` manifest + multiple `.ts` segments

**Challenge:**
- Manifest references multiple segment files
- Each segment needs its own signed URL

**MVP Approach:**
- Generate signed URLs for ALL segments in manifest
- Client-side 50% limit stops playback mid-stream
- User CAN download remaining segments if determined (acceptable)

**V2 Approach (if needed):**
- Sign only first 50% of segments in manifest
- Remaining segments return 403
- Requires custom manifest generation

---

## Stripe Integration

### Products

**Product 1: MarketHawk Premium**
- **Price:** $39/month (recurring)
- **Stripe Price ID:** `price_premium_monthly`
- **Features:**
  - Unlimited earnings call access
  - AI insights & analytics
  - Export capabilities
  - Priority support

**Coupon: Black Friday Discount**
- **Code:** `BLACKFRIDAY` (or `BFCM2025`)
- **Type:** Percentage off
- **Amount:** 30% off (TBD - could be 20-40%)
- **Duration:** Forever (applies to all future payments)
- **Valid:** Black Friday weekend only (Nov 29 - Dec 2, 2025)
- **Usage:** Unlimited during promo period
- **Result:** $39 → $27.30/month (if 30% off)

### Checkout Flow

**From Paywall → Stripe Checkout:**
```
1. User clicks "Upgrade to Premium"
2. Redirect to /api/billing/checkout
3. Backend creates Stripe Checkout Session:
   - price_id: price_premium_monthly
   - customer_email: user.email
   - success_url: /billing/success
   - cancel_url: /pricing
4. User completes payment on Stripe
5. Webhook updates user.subscriptionTier = 'premium'
6. Redirect to success page
```

---

## Pricing Page

**URL:** `/pricing`

**Layout:**
```
┌─────────────────────────────────────────┐
│     Choose Your Plan                    │
└─────────────────────────────────────────┘

┌──────────────┐  ┌────────────────────┐
│     FREE     │  │     PREMIUM ⭐     │
│   $0/month   │  │    $39/month       │
│              │  │                    │
│ ✓ 10 calls/  │  │ ✓ Unlimited calls │
│   day        │  │ ✓ AI insights     │
│ ✓ Transcripts│  │ ✓ Export data     │
│ ✓ Charts     │  │ ✓ Priority support│
│              │  │                    │
│ [Current]    │  │ [Upgrade Now]     │
└──────────────┘  └────────────────────┘

Enter coupon: [LAUNCH10]  [Apply]
```

---

## Success Metrics

### Free Tier Goals
- **Activation:** 70% of signups view at least 1 full earnings call
- **Retention:** 40% return within 7 days
- **Habit Formation:** 20% hit daily limit within first week

### Premium Conversion Goals
- **Overall Conversion:** 5% of free users upgrade within 30 days
- **Limit-Hit Conversion:** 15% of users who hit limit upgrade same day
- **Trial-to-Paid:** 60% of trial users convert to paid

### Revenue Targets
- **Month 1:** $1,000 MRR (26 paying users)
- **Month 3:** $5,000 MRR (128 paying users)
- **Month 6:** $15,000 MRR (385 paying users)

---

## Decisions Made

✅ **No Free Trial** - Direct paid conversion only
✅ **No Launch Coupon** - Save promotional pricing for Black Friday
✅ **Hard Stop at 50%** - Video/audio playback stops at 50% completion for non-logged-in users
✅ **Admin Public Override** - Admin can mark specific calls as fully public (no login required)

## Open Questions (For Future Versions)

1. **Annual Plan:** Add $390/year option (save $78 = 2 months free)?
   - Pro: Better cash flow, higher LTV
   - Con: More complexity for MVP
   - **Decision:** Defer to V2

2. **Team Plans:** Add team tier ($99/month for 5 users)?
   - Pro: Higher ACV, targets institutions
   - Con: Need collaboration features first
   - **Decision:** Defer to V2

3. **Content Gate:** What if they hit limit mid-earnings call?
   - Option A: Let them finish current call, block next one
   - Option B: Hard stop at 50% of 11th call
   - **Decision:** Option A (better UX)

4. **Black Friday Discount Amount:** 20%, 30%, or 40% off?
   - Need to model revenue impact
   - Consider competitor pricing
   - **Decision:** Test 30% off, adjust based on conversion data

---

## Implementation Plan

### Phase 1: Database & Schema (Day 1)

**Priority: HIGH - Foundation for everything else**

- [ ] Update user table schema
  - Add subscriptionTier, stripeCustomerId, stripeSubscriptionId
  - Add subscriptionStatus, subscriptionEndsAt
  - Add dailyViewCount, lastViewDate
- [ ] Create earnings_call_views analytics table
- [ ] Generate and run migrations
- [ ] Push to production database
- [ ] Create /lib/public-earnings-calls.ts (hardcoded public IDs)

**Time Estimate:** 2 hours (reduced - no isPublic field needed)

---

### Phase 2: Stripe Setup (Day 1-2)

**Priority: HIGH - Needed for payments**

- [ ] Create Stripe Premium product
  - Product name: "MarketHawk Premium"
  - Price: $39/month recurring
  - Save price ID to environment variables
- [ ] Create Black Friday coupon
  - Code: BLACKFRIDAY
  - Type: Percentage off (30%)
  - Duration: Forever
  - Valid: Nov 29 - Dec 2, 2025
- [ ] Set up Stripe webhooks
  - checkout.session.completed
  - customer.subscription.updated
  - customer.subscription.deleted
- [ ] Test payment flow in Stripe test mode

**Time Estimate:** 2-3 hours

**Stripe Link (Production):** https://buy.stripe.com/9B65kCbaj0vc0CJbUu6AM00

---

### Phase 3: Audio/Video Player with 50% Limit (Day 2)

**Priority: HIGH - Core feature**

- [ ] Create AudioPlayer component
  - Track playback time with timeupdate event
  - Stop playback at 50% of total duration
  - Prevent seeking beyond 50%
  - Show paywall overlay when limit reached
- [ ] Add error handling for signed URL expiry
  - Detect 403 errors
  - Show "Session expired" message
  - Provide "Refresh Page" button
- [ ] Update signed URL expiry to 1 hour (3600s)
- [ ] Test with various audio lengths
- [ ] Test with HLS playlists

**Time Estimate:** 3-4 hours

---

### Phase 4: User Authentication & Access Control (Day 3)

**Priority: HIGH - Gates content**

- [ ] Create access control middleware
  - Check if earnings call is public (isPublic flag)
  - Check if user is logged in
  - Check subscription tier (free vs premium)
  - Check daily view count for free users
- [ ] Implement daily view tracking
  - Increment dailyViewCount on page load
  - Reset counter if lastViewDate < today
  - Log to earnings_call_views table
- [ ] Add view counter UI
  - Show "Daily Views: X/10" in settings
  - Show warning at views 8-9
  - Show countdown timer for reset

**Time Estimate:** 4-5 hours

---

### Phase 5: Paywall Components (Day 3-4)

**Priority: HIGH - Conversion mechanism**

- [ ] Create AnonymousPaywall component (50% wall)
  - Shows at 50% for non-logged-in users
  - "Sign in free to continue" message
  - Links to /auth/signin
- [ ] Create FreeTierPaywall component (daily limit)
  - Shows when dailyViewCount >= 10
  - Soft overlay (dismissible)
  - Track dismissal count
  - Full interstitial after 3 dismissals
- [ ] Create ViewCounter component
  - Shows current usage: "7/10 views today"
  - Countdown timer: "Resets in: 5h 42m"
  - Upgrade CTA
- [ ] Style all paywalls to match dark theme
- [ ] Test dismissal and re-appearance logic

**Time Estimate:** 4-5 hours

---

### Phase 6: Pricing Page (Day 4)

**Priority: MEDIUM - Needed for conversions**

- [ ] Create /pricing page
  - Two-column layout: Free vs Premium
  - Feature comparison table
  - Clear $39/month pricing
  - Coupon code input field
  - "Upgrade Now" CTA button
- [ ] Link pricing page from:
  - Paywall overlays
  - User settings
  - Navigation (subtle)
- [ ] Test Stripe checkout flow
  - Click "Upgrade" → Stripe Checkout
  - Complete payment → Redirect to success
  - Verify subscription in database

**Time Estimate:** 3-4 hours

---

### Phase 7: Admin Features (Day 5)

**Priority: LOW - Nice to have**

- [ ] Add admin UI to toggle isPublic flag
  - Admin page: /admin/earnings-calls
  - List all earnings calls
  - Toggle switch for isPublic
  - Save to database
- [ ] Protect admin routes
  - Check if user.email matches admin list
  - Or check if user has admin role
- [ ] Test public call bypass
  - Mark call as public
  - Access without login
  - Verify full playback

**Time Estimate:** 2-3 hours

---

### Phase 8: Stripe Webhooks & Subscription Management (Day 5-6)

**Priority: HIGH - Critical for production**

- [ ] Create /api/webhooks/stripe route
  - Verify webhook signature
  - Handle checkout.session.completed
    - Update user.subscriptionTier = 'premium'
    - Save stripeCustomerId, stripeSubscriptionId
  - Handle customer.subscription.updated
    - Update subscriptionStatus
  - Handle customer.subscription.deleted
    - Downgrade to free tier
- [ ] Test webhooks with Stripe CLI
  - stripe listen --forward-to localhost:3000/api/webhooks/stripe
  - Trigger test events
  - Verify database updates
- [ ] Deploy webhook endpoint to production
- [ ] Configure webhook in Stripe dashboard

**Time Estimate:** 3-4 hours

---

### Phase 9: Testing & Polish (Day 6-7)

**Priority: HIGH - Quality assurance**

- [ ] End-to-end user flow testing
  - Anonymous → Free → Premium journey
  - Test paywall triggers
  - Test view counting and reset
  - Test Stripe payment flow
- [ ] Cross-browser testing
  - Chrome, Safari, Firefox
  - Mobile Safari, Chrome Mobile
- [ ] Error handling
  - Network failures
  - Payment failures
  - Signed URL expiry
- [ ] Performance optimization
  - Lazy load components
  - Optimize signed URL generation
- [ ] Analytics setup
  - Track paywall impressions
  - Track upgrade button clicks
  - Track conversion events

**Time Estimate:** 4-6 hours

---

## Total Time Estimate

**Minimum:** 27 hours (3-4 days full-time)
**Maximum:** 37 hours (5-6 days full-time)

**Realistic MVP Timeline:** 1 week (5 business days)

---

## Dependencies & Blockers

**External Dependencies:**
- Stripe account approval (if new account)
- Production database access
- R2 bucket permissions

**Technical Blockers:**
- Need Better Auth Stripe plugin configuration
- Need production Stripe keys
- Need to test webhook signature verification

**Nice-to-Haves (Defer to V2):**
- Auto-refresh signed URLs
- Advanced analytics dashboard
- A/B testing framework
- Email notifications for limit reached
- Annual pricing plan
- Team/organization plans

---

## Appendix: User Flows (Detailed)

### Flow 1: Anonymous to Free User
```
1. Visitor lands on markethawkeye.com
2. Clicks "Browse Companies"
3. Selects "NVIDIA"
4. Sees "Q3 2025 Earnings Call"
5. Clicks "Watch Now"
6. Video starts playing
7. At 50% mark → HARD STOP
8. Paywall overlay appears:
   "Sign in free to continue watching"
9. User clicks "Sign In with Google"
10. OAuth flow completes
11. Redirected back to earnings call
12. Video resumes from 50% mark
13. User can now watch full video
14. dailyViewCount = 1
```

### Flow 2: Free User Approaching Limit
```
1. User has viewed 8 earnings calls today
2. Opens 9th earnings call
3. Banner appears at top:
   "⚠️ 1 view remaining today. Upgrade for unlimited."
4. User watches full earnings call
5. Opens 10th earnings call (last free view)
6. Banner: "🚨 Last free view today. Resets in 7h."
7. User watches full earnings call
8. Tries to open 11th earnings call
9. Soft paywall overlay appears (can dismiss)
10. User dismisses → video plays at 50% quality
11. Overlay reappears on next page load
```

### Flow 3: Conversion to Premium
```
1. Free user hits daily limit (10/10)
2. Clicks "Upgrade to Premium"
3. Redirected to /pricing
4. Reviews plan details
5. Enters coupon: LAUNCH10
6. Sees price: $39 → $29 (first month)
7. Clicks "Subscribe Now"
8. Redirected to Stripe Checkout
9. Enters payment details
10. Completes purchase
11. Webhook fires → user.subscriptionTier = 'premium'
12. Redirected to /billing/success
13. Success page: "Welcome to Premium!"
14. User can now access unlimited earnings calls
15. Premium badge appears in header
```

---

**End of PRD**
