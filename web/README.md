# MarketHawk Web App

Next.js web application - Transform earnings calls into visually-enhanced videos.

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS 4
- **Database**: PostgreSQL + Drizzle ORM
- **Authentication**: Better Auth (Google One Tap, Organization, Stripe plugins)
- **Storage**: Cloudflare R2

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your DATABASE_URL and credentials

# Push database schema
npm run db:push

# Run development server
npm run dev
```

Open http://localhost:3000

## Database Schema

### Better Auth Tables (Auto-Created)
- `user`, `session`, `organization`, `member`, `invitation`, `subscription`

### Custom Tables
- **companies** - Public companies (AAPL, MSFT)
- **sources** - Raw materials (audio, video, documents) - prefix: `avd_`
- **artifacts** - Generated outputs (charts, thumbnails) - prefix: `art_`
- **videos** - Final rendered videos - prefix: `vid_`
- **video_views** - Analytics tracking
- **video_engagement** - User interactions
- **click_throughs** - YouTube → Website conversion

### ID Convention
Stripe-like IDs: `<prefix>_<humanreadable>_<4chars>`
- `comp_aapl_a1b2` - Company
- `vid_aapl_q4_2024_x9z3` - Video
- `avd_audio_yt_k8m2` - Audio/Video/Document source

### JSONB Heavy Usage
All metadata stored in JSONB columns for flexibility:
- `companies.data` - Company metadata
- `sources.data` - Source details (varies by type)
- `artifacts.data` - Chart data, thumbnails, etc.
- `videos.data` - Video metadata, Remotion props, analytics

## Database Commands

```bash
npm run db:generate    # Generate migrations from schema
npm run db:migrate     # Run migrations
npm run db:push        # Push schema directly (dev)
npm run db:studio      # Open Drizzle Studio GUI
npm run db:drop        # Drop all migrations
```

## ISR (Incremental Static Regeneration)

Pages revalidate every hour for optimal performance:
- Landing page: Pre-renders with latest 12 videos
- Video pages: Pre-generated at build time via `generateStaticParams`
- Result: <500ms page loads (static HTML)

## Authentication Setup

### Google One Tap
1. Get credentials from [Google Cloud Console](https://console.cloud.google.com/)
2. Add to `.env.local`:
   ```
   GOOGLE_CLIENT_ID="your-id.apps.googleusercontent.com"
   GOOGLE_CLIENT_SECRET="your-secret"
   NEXT_PUBLIC_GOOGLE_CLIENT_ID="your-id.apps.googleusercontent.com"
   ```
3. Google One Tap appears automatically for non-logged-in users

## Project Structure

```
web/
├── app/
│   ├── page.tsx                 # Landing page (ISR)
│   ├── api/auth/                # Better Auth endpoints
│   └── [company]/[slug]/        # Video pages (ISR)
├── components/auth/
│   └── GoogleOneTap.tsx         # Google One Tap component
├── lib/
│   ├── auth.ts                  # Better Auth server config
│   ├── auth-client.ts           # Client-side hooks
│   └── db/
│       ├── schema.ts            # Drizzle schema (JSONB-heavy)
│       └── index.ts             # Database client
└── drizzle/                     # Migrations folder
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - Google OAuth
- `BETTER_AUTH_SECRET` - Random secret for sessions

Optional (for full features):
- Stripe, YouTube API, Cloudflare R2, Resend (see `.env.example`)

## Deployment

```bash
# Deploy to Vercel
vercel deploy
```

Add environment variables in Vercel dashboard.

## Resources

- [PRD](../PRD.md) - Product requirements
- [CLAUDE.md](../CLAUDE.md) - Development guidelines
- [Better Auth](https://www.better-auth.com)
- [Drizzle ORM](https://orm.drizzle.team)
