# MarketHawk - Testing Infrastructure

## Problem Statement

**You need to know:**
- Did my code change break any of the 100+ video pages?
- Are all charts still rendering correctly?
- Are cross-links between companies working?
- Did database schema changes corrupt data?
- Are Remotion videos still generating correctly?
- Did YouTube API integration break?

**Without testing, you're deploying blind.**

---

## Testing Strategy Overview

```
Testing Pyramid for MarketHawk:

        ┌─────────────────┐
        │   E2E Tests     │  ← Test critical user flows
        │   (10 tests)    │     (video playback, navigation)
        └─────────────────┘
              ▲
             ╱ ╲
            ╱   ╲
      ┌───────────────┐
      │ Integration   │      ← Test API routes, DB queries
      │   (50 tests)  │         (YouTube API, chart data)
      └───────────────┘
            ▲
           ╱ ╲
          ╱   ╲
    ┌─────────────────┐
    │  Unit Tests     │      ← Test utilities, functions
    │  (200+ tests)   │         (data transforms, helpers)
    └─────────────────┘
```

**Plus:**
- Visual Regression Testing (charts, video pages)
- Performance Testing (page load times)
- Data Integrity Testing (earnings data accuracy)
- Remotion Rendering Tests (video output validation)

---

## Tech Stack for Testing

```json
{
  "unit": "Vitest (fast, works with Next.js)",
  "integration": "Vitest + Playwright",
  "e2e": "Playwright (browser automation)",
  "visual_regression": "Percy or Chromatic",
  "performance": "Lighthouse CI",
  "data_validation": "Custom scripts + Zod",
  "ci_cd": "GitHub Actions or Vercel"
}
```

---

## 1. Unit Tests

### What to Test

```typescript
// lib/earnings.test.ts

import {describe, it, expect} from 'vitest';
import {calculateYoYGrowth, formatCurrency, parseTranscript} from './earnings';

describe('Earnings Calculations', () => {
  it('calculates YoY growth correctly', () => {
    const result = calculateYoYGrowth(100e9, 90e9);
    expect(result).toBe(11.11);
  });

  it('handles negative growth', () => {
    const result = calculateYoYGrowth(80e9, 90e9);
    expect(result).toBe(-11.11);
  });

  it('formats currency correctly', () => {
    expect(formatCurrency(89500000000)).toBe('$89.5B');
    expect(formatCurrency(1234567890)).toBe('$1.23B');
    expect(formatCurrency(123456789)).toBe('$123.46M');
  });
});

describe('Transcript Parsing', () => {
  it('extracts financial metrics from transcript', () => {
    const transcript = `
      Revenue came in at $89.5 billion, up 5.3% year over year.
      EPS was $1.64, beating estimates of $1.58.
    `;

    const result = parseTranscript(transcript);

    expect(result.revenue).toBe(89.5e9);
    expect(result.revenueGrowth).toBe(5.3);
    expect(result.eps).toBe(1.64);
  });
});
```

### Test Coverage Goals

```bash
# Run unit tests with coverage
npm run test:unit -- --coverage

# Target coverage:
Statements   : 80%+
Branches     : 75%+
Functions    : 80%+
Lines        : 80%+
```

---

## 2. Integration Tests

### Database Queries

```typescript
// lib/db.test.ts

import {describe, it, expect, beforeEach, afterEach} from 'vitest';
import {db} from './db';
import {createTestDatabase, cleanupTestDatabase} from './test-utils';

describe('Database Queries', () => {
  beforeEach(async () => {
    await createTestDatabase();
  });

  afterEach(async () => {
    await cleanupTestDatabase();
  });

  it('fetches video with related companies', async () => {
    // Seed test data
    const apple = await db.companies.create({
      data: {ticker: 'AAPL', name: 'Apple Inc.'},
    });

    const video = await db.videos.create({
      data: {
        company_id: apple.id,
        slug: 'aapl-q4-2024',
        title: 'Apple Q4 2024 Earnings',
        quarter: 'Q4',
        year: 2024,
        youtube_id: 'test123',
      },
    });

    // Test query
    const result = await getVideoWithRelated(video.slug);

    expect(result.company.ticker).toBe('AAPL');
    expect(result.slug).toBe('aapl-q4-2024');
  });

  it('gets competitor recommendations', async () => {
    // Seed Apple, Microsoft, Google
    const apple = await db.companies.create({...});
    const msft = await db.companies.create({...});

    await db.company_relationships.create({
      data: {
        company_id: apple.id,
        related_company_id: msft.id,
        relationship_type: 'competitor',
      },
    });

    const competitors = await getCompetitors('AAPL');

    expect(competitors).toHaveLength(1);
    expect(competitors[0].ticker).toBe('MSFT');
  });
});
```

### API Routes

```typescript
// app/api/videos/[slug]/route.test.ts

import {describe, it, expect} from 'vitest';
import {GET} from './route';

describe('GET /api/videos/:slug', () => {
  it('returns video data', async () => {
    const req = new Request('http://localhost/api/videos/aapl-q4-2024');
    const response = await GET(req, {params: {slug: 'aapl-q4-2024'}});

    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.slug).toBe('aapl-q4-2024');
    expect(data.company.ticker).toBe('AAPL');
  });

  it('returns 404 for non-existent video', async () => {
    const req = new Request('http://localhost/api/videos/invalid-slug');
    const response = await GET(req, {params: {slug: 'invalid-slug'}});

    expect(response.status).toBe(404);
  });
});
```

### YouTube API Integration

```typescript
// lib/youtube.test.ts

import {describe, it, expect, vi} from 'vitest';
import {uploadToYouTube, getVideoAnalytics} from './youtube';

describe('YouTube API', () => {
  it('uploads video with correct metadata', async () => {
    const mockYouTube = vi.fn().mockResolvedValue({
      data: {id: 'new-video-id'},
    });

    const result = await uploadToYouTube({
      filePath: '/tmp/test-video.mp4',
      title: 'Apple Q4 2024 Earnings',
      description: 'Test description',
      tags: ['AAPL', 'earnings'],
    });

    expect(result.videoId).toBe('new-video-id');
  });

  it('fetches video analytics', async () => {
    const analytics = await getVideoAnalytics('test-video-id');

    expect(analytics).toHaveProperty('views');
    expect(analytics).toHaveProperty('watchTime');
    expect(analytics.views).toBeGreaterThanOrEqual(0);
  });
});
```

---

## 3. End-to-End Tests (Critical User Flows)

### Test Setup

```typescript
// e2e/setup.ts

import {test as base, expect} from '@playwright/test';
import {db} from '../lib/db';

export const test = base.extend({
  // Seed database before each test
  async seedDatabase({}, use) {
    await db.companies.createMany({
      data: [
        {ticker: 'AAPL', name: 'Apple Inc.', industry: 'Technology'},
        {ticker: 'MSFT', name: 'Microsoft', industry: 'Technology'},
        {ticker: 'GOOGL', name: 'Alphabet', industry: 'Technology'},
      ],
    });

    await use();

    // Cleanup
    await db.videos.deleteMany();
    await db.companies.deleteMany();
  },
});
```

### Critical Flows

```typescript
// e2e/video-playback.spec.ts

import {test, expect} from './setup';

test.describe('Video Playback', () => {
  test('plays video and shows related videos', async ({page}) => {
    await page.goto('/aapl/q4-2024');

    // Video player loads
    await expect(page.locator('iframe[src*="youtube.com"]')).toBeVisible();

    // Related videos sidebar exists
    await expect(page.locator('[data-testid="related-videos"]')).toBeVisible();

    // Competitor links are present
    const competitors = page.locator('[data-testid="competitor-link"]');
    await expect(competitors).toHaveCount(3); // MSFT, GOOGL, META
  });

  test('navigates to competitor video', async ({page}) => {
    await page.goto('/aapl/q4-2024');

    // Click Microsoft competitor link
    await page.click('text=Microsoft Q4 2024');

    // Should navigate to MSFT page
    await expect(page).toHaveURL(/\/msft\/q4-2024/);

    // Sidebar now shows Apple as competitor
    await expect(page.locator('text=Apple Q4 2024')).toBeVisible();
  });
});

// e2e/charts.spec.ts

test.describe('Chart Rendering', () => {
  test('renders revenue chart with correct data', async ({page}) => {
    await page.goto('/aapl/q4-2024');

    // Wait for chart to load
    await page.waitForSelector('[data-testid="revenue-chart"]');

    // Check canvas element exists (Chart.js renders to canvas)
    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible();

    // Check data labels are present
    await expect(page.locator('text=iPhone')).toBeVisible();
    await expect(page.locator('text=Services')).toBeVisible();
  });

  test('chart is interactive (hover shows tooltip)', async ({page}) => {
    await page.goto('/aapl/q4-2024');

    const chart = page.locator('[data-testid="revenue-chart"]');
    await chart.hover();

    // Tooltip should appear
    await expect(page.locator('[role="tooltip"]')).toBeVisible();
  });
});

// e2e/auth.spec.ts

test.describe('Free Tier Restrictions', () => {
  test('shows login prompt at 50% video progress', async ({page}) => {
    await page.goto('/aapl/q4-2024');

    // Simulate video progress (mock YouTube API)
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('video-progress', {
        detail: {progress: 0.5},
      }));
    });

    // Login modal should appear
    await expect(page.locator('[data-testid="login-modal"]')).toBeVisible();
    await expect(page.locator('text=Login to watch full video')).toBeVisible();
  });

  test('logged-in user can watch full video', async ({page}) => {
    // Login first
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to video
    await page.goto('/aapl/q4-2024');

    // Simulate 100% progress
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('video-progress', {
        detail: {progress: 1.0},
      }));
    });

    // No login modal
    await expect(page.locator('[data-testid="login-modal"]')).not.toBeVisible();
  });
});
```

---

## 4. Visual Regression Testing

**Problem:** Charts and pages look different after code changes

**Solution:** Percy or Chromatic (screenshot comparison)

### Setup Percy

```bash
npm install --save-dev @percy/cli @percy/playwright
```

```typescript
// e2e/visual-regression.spec.ts

import {test} from '@playwright/test';
import percySnapshot from '@percy/playwright';

test.describe('Visual Regression', () => {
  test('AAPL Q4 2024 page looks correct', async ({page}) => {
    await page.goto('/aapl/q4-2024');

    // Wait for charts to render
    await page.waitForSelector('[data-testid="revenue-chart"]');

    // Take screenshot
    await percySnapshot(page, 'AAPL Q4 2024 - Full Page');
  });

  test('Revenue chart looks correct', async ({page}) => {
    await page.goto('/aapl/q4-2024');

    const chart = page.locator('[data-testid="revenue-chart"]');
    await chart.waitFor();

    // Screenshot just the chart
    await percySnapshot(page, 'Revenue Chart - AAPL Q4 2024', {
      scope: '[data-testid="revenue-chart"]',
    });
  });

  test('Mobile view looks correct', async ({page}) => {
    await page.setViewportSize({width: 375, height: 667}); // iPhone size

    await page.goto('/aapl/q4-2024');

    await percySnapshot(page, 'AAPL Q4 2024 - Mobile');
  });
});
```

**Result:** Percy shows side-by-side comparison of old vs new screenshots

```
Before Deploy:
┌────────────────┐
│ Old Screenshot │
│ [Chart image]  │
└────────────────┘

After Deploy:
┌────────────────┐
│ New Screenshot │
│ [Chart image]  │ ← Looks different? Percy highlights changes
└────────────────┘
```

---

## 5. Data Integrity Tests

**Problem:** Database changes might corrupt earnings data

### Schema Validation

```typescript
// scripts/validate-data.ts

import {z} from 'zod';
import {db} from '../lib/db';

const EarningsDataSchema = z.object({
  revenue: z.object({
    current: z.number().positive(),
    previous: z.number().positive(),
    yoy: z.number().positive(),
  }),
  eps: z.object({
    current: z.number(),
    estimate: z.number(),
  }),
  margins: z.object({
    gross: z.number().min(0).max(100),
    operating: z.number().min(0).max(100),
    net: z.number().min(0).max(100),
  }),
});

async function validateAllEarningsData() {
  const allData = await db.earnings_data.findMany();

  const errors = [];

  for (const data of allData) {
    try {
      EarningsDataSchema.parse(data.financial_data);
    } catch (error) {
      errors.push({
        video_id: data.video_id,
        error: error.message,
      });
    }
  }

  if (errors.length > 0) {
    console.error('❌ Data validation failed:');
    console.error(errors);
    process.exit(1);
  }

  console.log('✅ All earnings data is valid');
}

validateAllEarningsData();
```

### Run Before Deploy

```bash
# In CI/CD pipeline
npm run validate:data

# If validation fails, deployment stops
```

---

## 6. Remotion Video Tests

**Problem:** Remotion rendering might break, producing corrupted videos

### Test Video Rendering

```typescript
// remotion/test-render.test.ts

import {describe, it, expect} from 'vitest';
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';
import fs from 'fs';
import path from 'path';

describe('Remotion Video Rendering', () => {
  it('renders AAPL Q4 2024 video successfully', async () => {
    // Bundle Remotion code
    const bundleLocation = await bundle({
      entryPoint: path.join(__dirname, 'index.ts'),
      webpackOverride: (config) => config,
    });

    // Select composition
    const composition = await selectComposition({
      serveUrl: bundleLocation,
      id: 'EarningsVideo',
      inputProps: {
        ticker: 'AAPL',
        company: 'Apple Inc.',
        quarter: 'Q4',
        year: 2024,
      },
    });

    // Render video
    const outputPath = '/tmp/test-render-aapl-q4-2024.mp4';

    await renderMedia({
      composition,
      serveUrl: bundleLocation,
      codec: 'h264',
      outputLocation: outputPath,
      inputProps: composition.defaultProps,
    });

    // Verify video file exists
    expect(fs.existsSync(outputPath)).toBe(true);

    // Verify file size is reasonable (>1MB)
    const stats = fs.statSync(outputPath);
    expect(stats.size).toBeGreaterThan(1_000_000);

    // Cleanup
    fs.unlinkSync(outputPath);
  }, 60000); // 60s timeout

  it('renders with correct duration', async () => {
    // ... similar setup ...

    expect(composition.durationInFrames).toBe(1800); // 60s at 30fps
    expect(composition.fps).toBe(30);
    expect(composition.width).toBe(1920);
    expect(composition.height).toBe(1080);
  });
});
```

### Video Quality Checks

```typescript
// scripts/validate-videos.ts

import {exec} from 'child_process';
import {promisify} from 'util';

const execAsync = promisify(exec);

async function validateVideo(filePath: string) {
  // Use ffprobe to check video metadata
  const {stdout} = await execAsync(`ffprobe -v quiet -print_format json -show_format -show_streams "${filePath}"`);

  const metadata = JSON.parse(stdout);

  // Validate video stream exists
  const videoStream = metadata.streams.find(s => s.codec_type === 'video');
  expect(videoStream).toBeDefined();
  expect(videoStream.codec_name).toBe('h264');
  expect(videoStream.width).toBe(1920);
  expect(videoStream.height).toBe(1080);

  // Validate audio stream exists
  const audioStream = metadata.streams.find(s => s.codec_type === 'audio');
  expect(audioStream).toBeDefined();

  // Validate duration (should be ~60 seconds)
  const duration = parseFloat(metadata.format.duration);
  expect(duration).toBeGreaterThan(55);
  expect(duration).toBeLessThan(65);

  console.log('✅ Video validation passed:', filePath);
}
```

---

## 7. Performance Testing

**Problem:** Page load times slow down as you add features

### Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml

name: Lighthouse CI
on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Install dependencies
        run: npm ci

      - name: Build Next.js
        run: npm run build

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

```javascript
// lighthouserc.js

module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/aapl/q4-2024',
        'http://localhost:3000/msft/q4-2024',
      ],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', {minScore: 0.9}],
        'categories:accessibility': ['error', {minScore: 0.9}],
        'categories:seo': ['error', {minScore: 0.9}],

        // Page load metrics
        'first-contentful-paint': ['error', {maxNumericValue: 2000}],
        'largest-contentful-paint': ['error', {maxNumericValue: 3000}],
        'cumulative-layout-shift': ['error', {maxNumericValue: 0.1}],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

**Result:** CI fails if performance drops below thresholds

---

## 8. Change Detection System

**The Critical Part: What Changed?**

### Automated Change Report

```typescript
// scripts/generate-change-report.ts

import {execSync} from 'child_process';
import {db} from '../lib/db';

async function generateChangeReport() {
  console.log('🔍 Generating change report...\n');

  // 1. Git changes
  const gitDiff = execSync('git diff --name-only main').toString();
  const changedFiles = gitDiff.split('\n').filter(Boolean);

  console.log('📝 Files changed:');
  changedFiles.forEach(file => console.log(`  - ${file}`));

  // 2. Database schema changes
  const schemaDiff = execSync('npx prisma migrate diff \
    --from-schema-datamodel prisma/schema.prisma \
    --to-schema-datasource postgresql://...').toString();

  if (schemaDiff) {
    console.log('\n🗄️ Database schema changes detected:');
    console.log(schemaDiff);
  }

  // 3. Affected video pages
  const affectedPages = await detectAffectedPages(changedFiles);

  console.log('\n📄 Affected video pages:');
  if (affectedPages.length === 0) {
    console.log('  ✅ No video pages affected');
  } else {
    affectedPages.forEach(page => console.log(`  - ${page}`));
  }

  // 4. Test results summary
  console.log('\n🧪 Test Results:');
  const testResults = execSync('npm run test:all -- --reporter=json').toString();
  const {numPassedTests, numFailedTests} = JSON.parse(testResults);

  console.log(`  ✅ Passed: ${numPassedTests}`);
  console.log(`  ❌ Failed: ${numFailedTests}`);

  // 5. Visual changes (Percy)
  console.log('\n👁️ Visual Changes:');
  console.log('  View Percy report: https://percy.io/...');

  return {
    changedFiles,
    schemaDiff,
    affectedPages,
    testResults,
  };
}

async function detectAffectedPages(changedFiles: string[]) {
  const affected = new Set<string>();

  // If chart rendering logic changed, all pages affected
  if (changedFiles.some(f => f.includes('components/charts/'))) {
    const allVideos = await db.videos.findMany();
    allVideos.forEach(v => affected.add(`/${v.company.ticker.toLowerCase()}/${v.slug}`));
  }

  // If specific video data changed
  if (changedFiles.some(f => f.includes('scripts/seed-'))) {
    // Parse which companies were seeded
    // Add their pages to affected set
  }

  return Array.from(affected);
}

generateChangeReport();
```

### Example Output

```bash
🔍 Generating change report...

📝 Files changed:
  - components/charts/RevenueChart.tsx
  - lib/earnings.ts
  - app/[company]/[slug]/page.tsx

🗄️ Database schema changes detected:
  + ALTER TABLE earnings_data ADD COLUMN fiscal_year INTEGER;

📄 Affected video pages:
  - /aapl/q4-2024
  - /msft/q4-2024
  - /googl/q4-2024
  - ... (97 more)

🧪 Test Results:
  ✅ Passed: 247
  ❌ Failed: 3

👁️ Visual Changes:
  View Percy report: https://percy.io/markethawk/pr/123

  Changes detected:
  - Revenue chart layout shifted 2px
  - Mobile sidebar width increased
```

---

## 9. CI/CD Pipeline (GitHub Actions)

### Complete Workflow

```yaml
# .github/workflows/test-and-deploy.yml

name: Test and Deploy

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test

      - name: Validate data schemas
        run: npm run validate:data

      - name: Build Next.js
        run: npm run build

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Run Lighthouse
        run: npm run lighthouse

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Install dependencies
        run: npm ci

      - name: Run Percy visual tests
        run: npm run test:visual
        env:
          PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}

  remotion-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Test Remotion rendering
        run: npm run test:remotion

      - name: Validate output videos
        run: npm run validate:videos

  deploy:
    needs: [test, visual-tests, remotion-tests]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

      - name: Generate change report
        run: npm run change-report

      - name: Notify deployment
        run: |
          echo "✅ Deployed to production"
          echo "📊 View change report: ..."
```

---

## 10. Pre-Deployment Checklist

```bash
# scripts/pre-deploy.sh

#!/bin/bash

echo "🚀 Pre-deployment checks..."

# 1. Run all tests
echo "\n1️⃣ Running tests..."
npm run test:all || exit 1

# 2. Validate data integrity
echo "\n2️⃣ Validating data..."
npm run validate:data || exit 1

# 3. Check database migrations
echo "\n3️⃣ Checking migrations..."
npx prisma migrate diff || echo "⚠️ Migrations pending"

# 4. Build production bundle
echo "\n4️⃣ Building production..."
npm run build || exit 1

# 5. Test production build locally
echo "\n5️⃣ Testing production build..."
npm run start &
SERVER_PID=$!
sleep 5

# Hit critical pages
curl -f http://localhost:3000/ || exit 1
curl -f http://localhost:3000/aapl/q4-2024 || exit 1
curl -f http://localhost:3000/api/videos/aapl-q4-2024 || exit 1

kill $SERVER_PID

# 6. Generate change report
echo "\n6️⃣ Generating change report..."
npm run change-report

echo "\n✅ All pre-deployment checks passed!"
echo "Ready to deploy 🚀"
```

---

## 11. Monitoring After Deployment

### Vercel Analytics

```typescript
// app/layout.tsx

import {Analytics} from '@vercel/analytics/react';

export default function RootLayout({children}) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

### Error Tracking (Sentry)

```typescript
// sentry.client.config.ts

import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  tracesSampleRate: 0.1,

  beforeSend(event) {
    // Filter out non-critical errors
    if (event.message?.includes('ResizeObserver')) {
      return null;
    }
    return event;
  },
});
```

### Custom Health Checks

```typescript
// app/api/health/route.ts

export async function GET() {
  const checks = {
    database: await checkDatabase(),
    youtube: await checkYouTubeAPI(),
    r2: await checkR2Bucket(),
  };

  const allHealthy = Object.values(checks).every(c => c.status === 'ok');

  return Response.json({
    status: allHealthy ? 'ok' : 'degraded',
    checks,
    timestamp: new Date().toISOString(),
  }, {
    status: allHealthy ? 200 : 503,
  });
}

async function checkDatabase() {
  try {
    await db.$queryRaw`SELECT 1`;
    return {status: 'ok'};
  } catch (error) {
    return {status: 'error', message: error.message};
  }
}
```

---

## 12. Rollback Strategy

### Vercel Instant Rollback

```bash
# If deployment breaks, instantly rollback
vercel rollback

# Or via UI: Vercel Dashboard → Deployments → Click previous deployment → Promote
```

### Database Rollback

```bash
# If migration breaks production
npx prisma migrate resolve --rolled-back <migration-name>

# Then rollback to previous migration
npx prisma migrate deploy
```

---

## Summary: Test Before Every Deploy

### Run This Before Deploying

```bash
# Full test suite
npm run test:all

# Change report
npm run change-report

# Pre-deploy checks
npm run pre-deploy

# If all pass → deploy
npm run deploy
```

### What You'll Know

✅ **Code changes:** Which files changed
✅ **Affected pages:** Which video pages are impacted
✅ **Test coverage:** Unit, integration, E2E results
✅ **Visual changes:** Screenshots of UI changes
✅ **Performance:** Page load metrics
✅ **Data integrity:** Earnings data is valid
✅ **Video rendering:** Remotion still works

**Never deploy blind again!**
