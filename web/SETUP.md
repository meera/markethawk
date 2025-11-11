# Market Hawk Eye Website Setup

Simple landing page with newsletter subscription.

## Quick Start

```bash
cd ~/markethawk/web

# Install dependencies
npm install

# Set up database URL (if not already set)
echo "DATABASE_URL=postgresql://..." > .env

# Run development server
npm run dev
```

Visit: http://localhost:3000

## Landing Page Features

✅ **Complete Look** - No "Coming Soon" or "Waitlist" language
✅ **Vision Statement** - Clear explanation of what Market Hawk Eye does
✅ **Newsletter Subscription** - Collects emails for updates
✅ **Mobile Responsive** - Works on all devices
✅ **Professional Design** - Gradient background, modern UI

## Newsletter Subscribers

Emails are stored in the `newsletterSubscribers` table in the database.

**View subscribers:**
```bash
# Using Drizzle Studio
npx drizzle-kit studio

# Or query directly
psql $DATABASE_URL -c "SELECT * FROM markethawk.newsletter_subscribers;"
```

## Deployment

**Deploy to Vercel:**
```bash
cd ~/markethawk/web
vercel --prod
```

**Environment Variables (Vercel):**
- `DATABASE_URL` - PostgreSQL connection string

## Future Enhancements

When ready to add:
- [ ] Send confirmation emails (Resend integration)
- [ ] Add video grid when first videos are published
- [ ] Add Google One Tap authentication
- [ ] Add SEO meta tags
- [ ] Add analytics tracking

---

**Website:** [markethawkeye.com](https://markethawkeye.com)

**Current Status:** Simple landing page ready for deployment ✅
