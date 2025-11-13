# Stripe Subscription Setup Guide

## Pricing Strategy

### Free Tier
- 3 video views per month
- Access to top 100 companies
- 480p video quality
- **Goal:** Viral growth, SEO

### Pro Tier: $19/month or $190/year
- Unlimited video views
- All 7,372 companies
- 1080p HD video quality
- Download transcripts
- Email alerts
- **Target:** Active retail investors

### Team Tier: $49/month or $490/year
- Everything in Pro
- 5 team members
- API access
- Priority support
- **Target:** Small investment firms

---

## Setup Steps

### 1. Create Stripe Account

1. Sign up at https://stripe.com
2. Complete business verification
3. Enable test mode for development

### 2. Create Products in Stripe Dashboard

#### Product 1: Markey HawkEye Pro

1. Go to **Products** → **Add Product**
2. Name: `Markey HawkEye Pro`
3. Description: `Unlimited access to earnings call videos for all 7,372 companies`
4. Create two prices:

**Monthly Price:**
- Amount: `$19.00 USD`
- Billing period: `Monthly`
- Copy the Price ID (starts with `price_...`)

**Yearly Price:**
- Amount: `$190.00 USD`
- Billing period: `Yearly`
- Copy the Price ID

#### Product 2: Markey HawkEye Team

1. Go to **Products** → **Add Product**
2. Name: `Markey HawkEye Team`
3. Description: `Pro features + team collaboration for up to 5 members`
4. Create two prices:

**Monthly Price:**
- Amount: `$49.00 USD`
- Billing period: `Monthly`
- Copy the Price ID

**Yearly Price:**
- Amount: `$490.00 USD`
- Billing period: `Yearly`
- Copy the Price ID

### 3. Enable Customer Portal

1. Go to **Settings** → **Billing** → **Customer Portal**
2. Enable portal
3. Configure allowed actions:
   - Update payment method
   - Update billing information
   - Cancel subscription
   - Switch plans
4. Save settings

### 4. Set Up Webhooks

1. Go to **Developers** → **Webhooks**
2. Add endpoint: `https://markethawkeye.com/api/auth/webhook/stripe`
3. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy **Webhook Signing Secret** (starts with `whsec_...`)

### 5. Get API Keys

1. Go to **Developers** → **API Keys**
2. Copy **Publishable Key** (starts with `pk_...`)
3. Copy **Secret Key** (starts with `sk_...`)

### 6. Configure Environment Variables

Add to `.env.local` (development):

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Stripe Price IDs
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_YEARLY_PRICE_ID=price_...
STRIPE_TEAM_MONTHLY_PRICE_ID=price_...
STRIPE_TEAM_YEARLY_PRICE_ID=price_...

# App URL
NEXT_PUBLIC_APP_URL=http://localhost:3001
```

Add to `.env.prod` (production):

```bash
# Stripe Configuration (LIVE keys)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Stripe Price IDs (production)
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_YEARLY_PRICE_ID=price_...
STRIPE_TEAM_MONTHLY_PRICE_ID=price_...
STRIPE_TEAM_YEARLY_PRICE_ID=price_...

# App URL
NEXT_PUBLIC_APP_URL=https://markethawkeye.com
```

### 7. Set Vercel Environment Variables

```bash
vercel env add STRIPE_SECRET_KEY
vercel env add STRIPE_PUBLISHABLE_KEY
vercel env add STRIPE_WEBHOOK_SECRET
vercel env add STRIPE_PRO_MONTHLY_PRICE_ID
vercel env add STRIPE_PRO_YEARLY_PRICE_ID
vercel env add STRIPE_TEAM_MONTHLY_PRICE_ID
vercel env add STRIPE_TEAM_YEARLY_PRICE_ID
vercel env add NEXT_PUBLIC_APP_URL
```

### 8. Enable Tax Calculation (Optional but Recommended)

1. Go to **Settings** → **Tax**
2. Enable **Stripe Tax**
3. Configure tax settings for your jurisdiction
4. This automatically handles sales tax/VAT globally

---

## Testing

### Test Credit Cards

Use Stripe test cards in development:

- **Success:** `4242 4242 4242 4242`
- **Decline:** `4000 0000 0000 0002`
- **Requires 3D Secure:** `4000 0027 6000 3184`

Any future expiry date and any 3-digit CVC.

### Test Webhooks Locally

1. Install Stripe CLI:
   ```bash
   brew install stripe/stripe-cli/stripe
   ```

2. Login:
   ```bash
   stripe login
   ```

3. Forward webhooks:
   ```bash
   stripe listen --forward-to localhost:3001/api/auth/webhook/stripe
   ```

4. Trigger test events:
   ```bash
   stripe trigger customer.subscription.created
   ```

---

## Database Schema

Better Auth Stripe plugin automatically adds these fields to the `user` table:

```sql
ALTER TABLE user ADD COLUMN stripe_customer_id TEXT;
ALTER TABLE user ADD COLUMN stripe_subscription_id TEXT;
ALTER TABLE user ADD COLUMN stripe_subscription_status TEXT;
ALTER TABLE user ADD COLUMN stripe_current_period_end TIMESTAMP;
ALTER TABLE user ADD COLUMN stripe_plan_id TEXT;
```

Run Better Auth migration to apply:

```bash
npx better-auth migrate
```

---

## User Flow

### Subscribe to Pro

1. User visits `/pricing`
2. Clicks "Start Pro Trial"
3. Redirects to `/api/billing/checkout?plan=pro`
4. Creates Stripe Checkout session
5. User enters payment info
6. Stripe webhook fires `customer.subscription.created`
7. Better Auth updates user record with subscription data
8. Redirects to `/billing?success=true`

### Manage Subscription

1. User visits `/billing`
2. Clicks "Manage Subscription"
3. Redirects to `/api/billing/portal`
4. Opens Stripe Customer Portal
5. User can:
   - Update payment method
   - Change plan
   - Cancel subscription
   - View invoices
6. Returns to `/billing`

### Cancel Subscription

1. User opens Customer Portal
2. Clicks "Cancel Subscription"
3. Stripe webhook fires `customer.subscription.deleted`
4. Better Auth marks subscription as canceled
5. User retains access until period end

---

## Go Live Checklist

- [ ] Switch to live Stripe keys in production
- [ ] Update webhook endpoint to production URL
- [ ] Test complete payment flow
- [ ] Test webhook delivery
- [ ] Enable Stripe Tax
- [ ] Set up billing alerts in Stripe dashboard
- [ ] Configure payout schedule
- [ ] Add Terms of Service link to checkout
- [ ] Add Privacy Policy link to checkout
- [ ] Test subscription cancellation flow
- [ ] Monitor first real transaction

---

## Support

- Stripe Dashboard: https://dashboard.stripe.com
- Stripe Docs: https://stripe.com/docs
- Better Auth Stripe Plugin: https://better-auth.com/docs/plugins/stripe
