# DATABASE-SCHEMA.md

Complete database schema for MarketHawk using Drizzle ORM.

---

## Overview

MarketHawk uses PostgreSQL with Drizzle ORM for type-safe database access.

**Key Tables:**
- `users` - User accounts (managed by Better Auth)
- `organizations` - Organization/team structure
- `companies` - Public companies (AAPL, MSFT, etc.)
- `videos` - YouTube videos + metadata
- `video_views` - View tracking
- `video_engagement` - User interactions
- `click_throughs` - YouTube → website traffic
- `subscriptions` - Stripe subscriptions
- `earnings_data` - Financial metrics (JSON)

---

## Setup Drizzle ORM

```bash
npm install drizzle-orm postgres
npm install -D drizzle-kit
```

```typescript
// drizzle.config.ts

import type {Config} from 'drizzle-kit';

export default {
  schema: './lib/db/schema.ts',
  out: './lib/db/migrations',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.DATABASE_URL!,
  },
} satisfies Config;
```

---

## Schema Definitions

### Users & Auth

```typescript
// lib/db/schema/users.ts

import {pgTable, uuid, text, timestamp, boolean} from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  name: text('name'),
  avatar_url: text('avatar_url'),
  tier: text('tier').notNull().default('free'), // 'free', 'pro', 'team'
  role: text('role').notNull().default('user'), // 'user', 'admin'
  created_at: timestamp('created_at').notNull().defaultNow(),
  updated_at: timestamp('updated_at').notNull().defaultNow(),
});

export const sessions = pgTable('sessions', {
  id: uuid('id').primaryKey().defaultRandom(),
  user_id: uuid('user_id').notNull().references(() => users.id, {onDelete: 'cascade'}),
  token: text('token').notNull().unique(),
  expires_at: timestamp('expires_at').notNull(),
  created_at: timestamp('created_at').notNull().defaultNow(),
});
```

### Organizations

```typescript
// lib/db/schema/organizations.ts

export const organizations = pgTable('organizations', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: text('name').notNull(),
  slug: text('slug').notNull().unique(),
  tier: text('tier').notNull().default('team'), // 'team'
  max_members: integer('max_members').notNull().default(10),
  created_at: timestamp('created_at').notNull().defaultNow(),
});

export const organization_members = pgTable('organization_members', {
  id: uuid('id').primaryKey().defaultRandom(),
  organization_id: uuid('organization_id').notNull().references(() => organizations.id, {onDelete: 'cascade'}),
  user_id: uuid('user_id').notNull().references(() => users.id, {onDelete: 'cascade'}),
  role: text('role').notNull().default('member'), // 'owner', 'admin', 'member'
  joined_at: timestamp('joined_at').notNull().defaultNow(),
});
```

### Companies

```typescript
// lib/db/schema/companies.ts

export const companies = pgTable('companies', {
  id: uuid('id').primaryKey().defaultRandom(),
  ticker: text('ticker').notNull().unique(),
  name: text('name').notNull(),
  industry: text('industry'),
  sector: text('sector'),
  logo_url: text('logo_url'),
  brand_color: text('brand_color'),
  website: text('website'),
  created_at: timestamp('created_at').notNull().defaultNow(),
});
```

### Videos

```typescript
// lib/db/schema/videos.ts

export const videos = pgTable('videos', {
  id: uuid('id').primaryKey().defaultRandom(),
  company_id: uuid('company_id').notNull().references(() => companies.id),

  // YouTube metadata
  youtube_id: text('youtube_id').unique(),
  youtube_url: text('youtube_url'),
  title: text('title').notNull(),
  description: text('description'),
  thumbnail_url: text('thumbnail_url'),
  duration: integer('duration'), // seconds

  // MarketHawk metadata
  ticker: text('ticker').notNull(),
  quarter: text('quarter').notNull(), // 'Q1', 'Q2', 'Q3', 'Q4'
  year: integer('year').notNull(),
  earnings_date: timestamp('earnings_date'),

  // Files
  job_id: text('job_id'), // Links to /var/markethawk/jobs/{JOB_ID}
  r2_video_url: text('r2_video_url'),
  r2_audio_url: text('r2_audio_url'),
  r2_transcript_url: text('r2_transcript_url'),

  // Status
  status: text('status').notNull().default('draft'), // 'draft', 'published', 'hidden'
  published_at: timestamp('published_at'),

  // SEO
  slug: text('slug').notNull().unique(),
  meta_description: text('meta_description'),

  created_at: timestamp('created_at').notNull().defaultNow(),
  updated_at: timestamp('updated_at').notNull().defaultNow(),
});
```

### Earnings Data

```typescript
// lib/db/schema/earnings.ts

import {jsonb} from 'drizzle-orm/pg-core';

export const earnings_data = pgTable('earnings_data', {
  id: uuid('id').primaryKey().defaultRandom(),
  video_id: uuid('video_id').notNull().references(() => videos.id, {onDelete: 'cascade'}),

  // All financial data as JSON
  financial_data: jsonb('financial_data').notNull(),
  /*
  Example:
  {
    "revenue": {
      "current": 94900000000,
      "previous": 89500000000,
      "change_percent": 6.0,
      "segments": [
        {"name": "iPhone", "value": 43800000000},
        {"name": "Services", "value": 22300000000}
      ]
    },
    "eps": {
      "current": 1.64,
      "estimate": 1.58,
      "beat": true
    },
    "guidance": {
      "q1_revenue_low": 100000000000,
      "q1_revenue_high": 105000000000
    }
  }
  */

  created_at: timestamp('created_at').notNull().defaultNow(),
});
```

### Analytics

```typescript
// lib/db/schema/analytics.ts

export const video_views = pgTable('video_views', {
  id: uuid('id').primaryKey().defaultRandom(),
  video_id: uuid('video_id').notNull().references(() => videos.id, {onDelete: 'cascade'}),
  user_id: uuid('user_id').references(() => users.id, {onDelete: 'set null'}),

  // View metadata
  source: text('source'), // 'youtube', 'website', 'embed'
  referrer: text('referrer'),
  device: text('device'), // 'mobile', 'desktop', 'tablet'

  timestamp: timestamp('timestamp').notNull().defaultNow(),
});

export const video_engagement = pgTable('video_engagement', {
  id: uuid('id').primaryKey().defaultRandom(),
  video_id: uuid('video_id').notNull().references(() => videos.id, {onDelete: 'cascade'}),
  user_id: uuid('user_id').references(() => users.id, {onDelete: 'cascade'}),

  // Engagement type
  action: text('action').notNull(), // 'like', 'save', 'share', 'chart_interact'
  metadata: jsonb('metadata'), // Additional data (chart type, share destination, etc.)

  timestamp: timestamp('timestamp').notNull().defaultNow(),
});

export const click_throughs = pgTable('click_throughs', {
  id: uuid('id').primaryKey().defaultRandom(),
  video_id: uuid('video_id').notNull().references(() => videos.id, {onDelete: 'cascade'}),
  user_id: uuid('user_id').references(() => users.id, {onDelete: 'set null'}),

  // Click metadata
  source: text('source').notNull(), // 'youtube_description', 'youtube_end_screen', 'youtube_card'
  destination: text('destination').notNull(), // URL clicked

  timestamp: timestamp('timestamp').notNull().defaultNow(),
});
```

### Subscriptions

```typescript
// lib/db/schema/subscriptions.ts

export const subscriptions = pgTable('subscriptions', {
  id: uuid('id').primaryKey().defaultRandom(),
  user_id: uuid('user_id').notNull().references(() => users.id, {onDelete: 'cascade'}),
  organization_id: uuid('organization_id').references(() => organizations.id, {onDelete: 'cascade'}),

  // Stripe metadata
  stripe_subscription_id: text('stripe_subscription_id').unique(),
  stripe_customer_id: text('stripe_customer_id'),

  // Subscription details
  plan: text('plan').notNull(), // 'pro', 'team'
  status: text('status').notNull(), // 'active', 'canceled', 'past_due'
  current_period_start: timestamp('current_period_start').notNull(),
  current_period_end: timestamp('current_period_end').notNull(),

  // Billing
  amount: integer('amount').notNull(), // cents
  currency: text('currency').notNull().default('usd'),

  created_at: timestamp('created_at').notNull().defaultNow(),
  updated_at: timestamp('updated_at').notNull().defaultNow(),
});
```

---

## Indexes

```typescript
// lib/db/schema/indexes.ts

import {index} from 'drizzle-orm/pg-core';

// Video lookups
export const videoYoutubeIdIdx = index('video_youtube_id_idx').on(videos.youtube_id);
export const videoTickerQuarterIdx = index('video_ticker_quarter_idx').on(videos.ticker, videos.quarter, videos.year);

// Analytics queries
export const videoViewsTimestampIdx = index('video_views_timestamp_idx').on(video_views.timestamp);
export const videoViewsVideoIdIdx = index('video_views_video_id_idx').on(video_views.video_id);

// User queries
export const userEmailIdx = index('user_email_idx').on(users.email);
export const subscriptionUserIdIdx = index('subscription_user_id_idx').on(subscriptions.user_id);
```

---

## Database Client

```typescript
// lib/db/client.ts

import {drizzle} from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

const connectionString = process.env.DATABASE_URL!;

// Query client
const queryClient = postgres(connectionString);

export const db = drizzle(queryClient, {schema});
```

---

## Migrations

### Generate Migration

```bash
npx drizzle-kit generate:pg
```

### Run Migration

```bash
npx drizzle-kit push:pg
```

---

## Example Queries

### Fetch Video with Company

```typescript
import {db} from '@/lib/db/client';
import {videos, companies} from '@/lib/db/schema';
import {eq} from 'drizzle-orm';

export async function getVideo(slug: string) {
  const result = await db
    .select()
    .from(videos)
    .leftJoin(companies, eq(videos.company_id, companies.id))
    .where(eq(videos.slug, slug))
    .limit(1);

  return result[0];
}
```

### Track Video View

```typescript
import {db} from '@/lib/db/client';
import {video_views} from '@/lib/db/schema';

export async function trackVideoView({
  videoId,
  userId,
  source,
  referrer,
}: {
  videoId: string;
  userId?: string;
  source: string;
  referrer?: string;
}) {
  await db.insert(video_views).values({
    video_id: videoId,
    user_id: userId,
    source,
    referrer,
  });
}
```

### Get Top Videos (24h)

```typescript
import {db} from '@/lib/db/client';
import {videos, video_views} from '@/lib/db/schema';
import {eq, gte, sql} from 'drizzle-orm';

export async function getTopVideos() {
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);

  const result = await db
    .select({
      video: videos,
      viewCount: sql<number>`count(${video_views.id})`,
    })
    .from(videos)
    .leftJoin(video_views, eq(videos.id, video_views.video_id))
    .where(gte(video_views.timestamp, oneDayAgo))
    .groupBy(videos.id)
    .orderBy(sql`count(${video_views.id}) DESC`)
    .limit(10);

  return result;
}
```

---

## Related Documentation

- **WEB-APP-GUIDE.md** - Better Auth integration with database
- **ADMIN-DASHBOARD.md** - Analytics queries for dashboard
- **USER-EXPERIENCE.md** - User tier and subscription logic

---

**Last Updated:** 2025-11-10
