# MailerLite Setup Guide

Complete guide to set up MailerLite for MarketHawk newsletter and welcome emails.

---

## Part 1: MailerLite Dashboard Setup

### Step 1: Create Two Groups

1. Go to **MailerLite Dashboard** → **Subscribers** → **Groups**

2. **Create Group 1: "MarketHawk - New Users"**
   - Click "Create Group"
   - Name: `MarketHawk - New Users`
   - Description: "Users who create accounts (for welcome emails)"
   - Click "Create"
   - **SAVE THE GROUP ID** (you'll see it in the URL: `/groups/123456789`)

3. **Create Group 2: "MarketHawk - Newsletter"**
   - Click "Create Group"
   - Name: `MarketHawk - Newsletter`
   - Description: "Website newsletter subscribers"
   - Click "Create"
   - **SAVE THE GROUP ID**

---

### Step 2: Verify markethawkeye.com Domain

1. Go to **Settings** → **Domains** → **Add Domain**

2. Enter: `markethawkeye.com`

3. MailerLite will show you DNS records. **Copy all of them.**

4. **Add DNS Records in Cloudflare:**
   - Go to your Cloudflare dashboard
   - Select `markethawkeye.com` domain
   - Go to **DNS** → **Records**
   - Add each record MailerLite provided:

**SPF Record:**
```
Type: TXT
Name: @
Content: v=spf1 include:_spf.mlsend.com ~all
TTL: Auto
```

**DKIM Record:**
```
Type: TXT
Name: ml._domainkey
Content: [Long key from MailerLite - copy exactly]
TTL: Auto
```

**DMARC Record:**
```
Type: TXT
Name: _dmarc
Content: v=DMARC1; p=none; rua=mailto:dmarc@markethawkeye.com
TTL: Auto
```

**Return-Path (Optional):**
```
Type: CNAME
Name: bounces
Content: bounces.mlsend.com
TTL: Auto
```

5. **Wait 24-48 hours** for DNS propagation and MailerLite verification

---

### Step 3: Create Welcome Email Automation

**Purpose:** Send welcome email when new users create accounts

1. Go to **Automations** → **Create automation** → **Start from scratch**

2. **Set trigger:**
   - Trigger type: "Subscriber joins a group"
   - Select group: "MarketHawk - New Users"

3. **Add email action:**
   - Click "+ " → "Send email"
   - Create new email or use template

4. **Email content suggestions:**

**Subject:** "Welcome to MarketHawk!"

**Email body:**
```
Hi {{subscriber.name}},

Welcome to MarketHawk! We're excited to have you.

Here's what you can do now:

• Search 7,600+ companies by name or ticker
• Listen to earnings call audio (not just transcripts)
• Spot discrepancies between what executives say and what the data shows
• Hear the hesitation, confidence, and tone that transcripts miss

Get started: https://markethawkeye.com

Questions? Just reply to this email.

Cheers,
The MarketHawk Team

---
Unsubscribe | Update preferences
```

5. **Set sender:**
   - From name: "MarketHawk"
   - From email: `welcome@markethawkeye.com` (once domain is verified)
   - Reply-to: `meera@videotobe.com` (or your preferred email)

6. **Activate the automation**

---

### Step 4: Create Newsletter Confirmation (Optional)

**Purpose:** Confirm subscription for newsletter signups

1. Go to **Automations** → **Create automation**

2. **Set trigger:**
   - Trigger: "Subscriber joins a group"
   - Select group: "MarketHawk - Newsletter"

3. **Add email:**
   - Subject: "You're subscribed to MarketHawk updates"
   - Body: "Thanks for subscribing! We'll send you updates when we launch new features..."
   - Sender: `newsletter@markethawkeye.com`

4. **Activate**

---

## Part 2: Environment Variables

Add these to your `.env.local` file:

```bash
# MailerLite Configuration
MAILERLITE_API_KEY="your-api-key-here"
MAILERLITE_GROUP_NEW_USERS="123456789"      # Group ID from Step 1
MAILERLITE_GROUP_NEWSLETTER="987654321"      # Group ID from Step 1
```

**Where to find:**
- `MAILERLITE_API_KEY`: Settings → Integrations → Developer API
- Group IDs: In the URL when you click a group (`/groups/123456789`)

---

## Part 3: Restart Dev Server

```bash
# Kill current server
# Then restart
cd /Users/Meera/markethawk/web
npm run dev
```

---

## Part 4: Testing

### Test 1: Newsletter Subscription

1. Go to http://localhost:3000/about
2. Scroll to newsletter section
3. Enter your email and click "Subscribe"
4. **Verify:**
   - Success message appears
   - Email appears in MailerLite under "MarketHawk - Newsletter" group
   - You receive confirmation email (if you set up automation)

### Test 2: Welcome Email (Account Signup)

1. Go to http://localhost:3000/sign-up
2. Create a new account
3. Verify email address
4. **Verify:**
   - Account is created
   - Email appears in MailerLite under "MarketHawk - New Users" group
   - You receive welcome email
   - Check server logs for: `Welcome email sent to user@email.com`

---

## Part 5: Production Deployment

### Update Vercel Environment Variables

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables

2. Add these variables:
   ```
   MAILERLITE_API_KEY=your-api-key
   MAILERLITE_GROUP_NEW_USERS=123456789
   MAILERLITE_GROUP_NEWSLETTER=987654321
   ```

3. Redeploy your site

---

## Troubleshooting

### "MailerLite API key not configured"
- Check `.env.local` has `MAILERLITE_API_KEY`
- Restart dev server after adding env variables

### "Welcome email group not configured"
- Check `.env.local` has `MAILERLITE_GROUP_NEW_USERS`
- Make sure the group ID is correct (no quotes in .env)

### Domain not verifying
- Wait 24-48 hours for DNS propagation
- Check DNS records in Cloudflare match MailerLite exactly
- Use `dig TXT ml._domainkey.markethawkeye.com` to verify DKIM record

### Emails going to spam
- Wait for domain verification (24-48 hours)
- Make sure SPF, DKIM, and DMARC records are all added
- Send from verified domain only (`@markethawkeye.com`)

### Not receiving test emails
- Check MailerLite "Unsubscribed" list (you might be unsubscribed)
- Check spam folder
- Verify automation is "Active" not "Draft"

---

## What Happens Now

**When a user creates an account:**
1. Better Auth creates user in database
2. Auth hook triggers → `sendWelcomeEmail()` called
3. User added to MailerLite "New Users" group
4. MailerLite automation sends welcome email

**When a user subscribes to newsletter:**
1. Form submits to `/api/newsletter/subscribe`
2. User added to MailerLite "Newsletter" group
3. Optional: Confirmation email sent
4. PostHog tracks `newsletter_subscribed` event

---

## Next Steps

1. ✅ Code implemented (done)
2. ⏳ Create groups in MailerLite
3. ⏳ Add DNS records in Cloudflare
4. ⏳ Wait for domain verification (24-48 hours)
5. ⏳ Create welcome email automation
6. ⏳ Add environment variables
7. ⏳ Test both flows
8. ⏳ Deploy to production

---

**Questions?** Check MailerLite docs: https://developers.mailerlite.com/docs
