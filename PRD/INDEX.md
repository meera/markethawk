# PRD Documentation Index

Complete documentation for **Markey HawkEye** project.

🌐 **Website:** [markethawkeye.com](https://markethawkeye.com)

---

## Core Documentation

📋 **[README.md](./README.md)** - Complete Product Requirements Document
- Full product vision, features, roadmap
- Business model and monetization strategy
- Technical architecture overview


## Guidelines
Never output coming soon or waitlist. Never ship implement features. Okay to ship fewer features - but UI should always look complete. 
---

## SaaS Platform Guides

Build the Markey HawkEye web application:

🌐 **[WEB-APP-GUIDE.md](./WEB-APP-GUIDE.md)** - Next.js Web Application
- Next.js 14+ setup with App Router
- Better Auth + Google One Tap implementation
- Stripe subscription integration
- ISR optimization for video pages
- Interactive charts (data-driven, not images)

🔍 **[SEO-STRATEGY.md](./SEO-STRATEGY.md)** - SEO Optimization
- YouTube SEO (titles, descriptions, tags, chapters)
- Website SEO (meta tags, structured data)
- Keyword research and content strategy
- Analytics tracking

👤 **[USER-EXPERIENCE.md](./USER-EXPERIENCE.md)** - User Experience Design
- "Show, Don't Tell" landing page design
- Free tier restrictions and paywalls
- Subscription tiers (Free, Pro, Team)
- Personalization engine and recommendations
- Content gating strategy

📊 **[ADMIN-DASHBOARD.md](./ADMIN-DASHBOARD.md)** - Admin Monitoring
- Real-time dashboard (mobile-first)
- Video performance tracking
- Click-through correlation (YouTube → Website)
- Revenue breakdown (YouTube ads + subscriptions)
- Quick actions (edit, hide, re-upload videos)

🗄️ **[DATABASE-SCHEMA.md](./DATABASE-SCHEMA.md)** - Database Design
- Complete schema with Drizzle ORM
- Tables: users, videos, companies, earnings_data, analytics
- Example queries and migrations
- Indexes for performance

🌱 **[DATABASE-SEEDING.md](./DATABASE-SEEDING.md)** - Database Seeding Guide
- Populating the `markethawkeye.companies` table
- Automated scripts for SEC, NASDAQ, exchange data
- Production deployment procedures
- Data refresh schedules and verification

🚀 **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production Deployment
- Vercel deployment guide
- Environment variables
- Database setup (Neon, Supabase, self-hosted)
- Cloudflare R2 configuration
- Stripe + YouTube API setup
- Monitoring and backups

---

## Video Pipeline Recipes

Step-by-step guides for video production:

🎵 **[recipes/AUDIO-ONLY-EARNINGS-RECIPE.md](./recipes/AUDIO-ONLY-EARNINGS-RECIPE.md)** - Audio-Only Videos
- Complete workflow for audio-only earnings calls
- Using `<Audio>` component in Remotion
- FadedAudio transitions
- Branded static backgrounds
- Common issues and solutions

🖼️ **[recipes/THUMBNAIL-OPTIONS.md](./recipes/THUMBNAIL-OPTIONS.md)** - Thumbnail Generation
- 4 thumbnail variations with different text effects
- Using `smart_thumbnail_generator.py`
- Best practices for YouTube thumbnails
- Text placement and color schemes

📁 **[recipes/COLLOCATION-STRUCTURE.md](./recipes/COLLOCATION-STRUCTURE.md)** - Job Directory Structure
- `/var/markethawk/jobs/{JOB_ID}/` organization
- `job.yaml` as single source of truth
- Input, transcripts, renders, thumbnails structure
- State tracking and resumable processing

---

## Quick Navigation

**Starting a new video project?**
1. Read: [recipes/AUDIO-ONLY-EARNINGS-RECIPE.md](./recipes/AUDIO-ONLY-EARNINGS-RECIPE.md)
2. Follow: Job-based workflow in `CLAUDE.md`
3. Reference: [recipes/COLLOCATION-STRUCTURE.md](./recipes/COLLOCATION-STRUCTURE.md)

**Building the web app?**
1. Start: [WEB-APP-GUIDE.md](./WEB-APP-GUIDE.md)
2. Setup: [DATABASE-SCHEMA.md](./DATABASE-SCHEMA.md)
3. Seed: [DATABASE-SEEDING.md](./DATABASE-SEEDING.md)
4. Deploy: [DEPLOYMENT.md](./DEPLOYMENT.md)
5. Monitor: [ADMIN-DASHBOARD.md](./ADMIN-DASHBOARD.md)

**Optimizing for growth?**
1. SEO: [SEO-STRATEGY.md](./SEO-STRATEGY.md)
2. UX: [USER-EXPERIENCE.md](./USER-EXPERIENCE.md)
3. Analytics: [ADMIN-DASHBOARD.md](./ADMIN-DASHBOARD.md)

---

**Last Updated:** 2025-11-11
