#!/usr/bin/env tsx

/**
 * Seed database from CSV files
 *
 * Usage:
 *   Local:      npm run db:seed-csv
 *   Production: NODE_ENV=production npm run db:seed-csv
 *   Override:   DATABASE_URL="..." npm run db:seed-csv
 */

import * as dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

// Load environment variables based on NODE_ENV
const envFile = process.env.NODE_ENV === 'production'
  ? '.env.production'
  : '.env.local';

// Try primary env file, fallback to .env
const result = dotenv.config({ path: envFile });
if (result.error) {
  dotenv.config({ path: '.env' });
}

console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
console.log(`📄 Loaded env from: ${envFile}\n`);

import { db } from '../lib/db';
import { companies, earningsCalls } from '../lib/db/schema';

const COMPANIES_CSV = path.join(process.cwd(), '../data/companies_master.csv');
const EARNINGS_CSV = path.join(process.cwd(), '../data/earning-calls.csv');

async function seedCompanies() {
  console.log('\n📦 Seeding companies from CSV...');

  const csvContent = fs.readFileSync(COMPANIES_CSV, 'utf-8');
  const records = parse(csvContent, {
    columns: true,
    skip_empty_lines: true,
  });

  console.log(`   Found ${records.length} companies`);

  let inserted = 0;
  let skipped = 0;

  for (const record of records) {
    try {
      // Parse metadata JSON from CSV
      const csvMetadata = JSON.parse(record.metadata_json || '{}');

      await db.insert(companies).values({
        id: `company_${record.symbol.toLowerCase()}`,
        ticker: record.symbol,
        cikStr: record.cik_str,
        slug: record.slug,
        name: record.name,
        data: {
          industry: csvMetadata.industry || 'Unknown',
        },
        metadata: {
          sector: csvMetadata.sector,
          exchange: csvMetadata.exchange,
          market_cap: csvMetadata.market_cap,
          ipo_year: csvMetadata.ipo_year,
          country: csvMetadata.country,
        },
      }).onConflictDoNothing();

      inserted++;

      if (inserted % 1000 === 0) {
        console.log(`   Progress: ${inserted} companies inserted...`);
      }
    } catch (error) {
      console.error(`   ⚠️  Skipped ${record.symbol}: ${error}`);
      skipped++;
    }
  }

  console.log(`   ✅ Companies: ${inserted} inserted, ${skipped} skipped\n`);
}

async function seedEarningsCalls() {
  console.log('📦 Seeding earnings calls from CSV...');

  const csvContent = fs.readFileSync(EARNINGS_CSV, 'utf-8');
  const records = parse(csvContent, {
    columns: true,
    skip_empty_lines: true,
    bom: true, // Handle BOM (byte order mark)
    quote: '"',
    escape: '"',
    relax_quotes: true,
    relax_column_count: true,
  });

  console.log(`   Found ${records.length} earnings calls`);

  let inserted = 0;
  let skipped = 0;

  for (const record of records) {
    try {
      // Parse JSON fields - strip outer quotes if present
      const stripQuotes = (str: string) => {
        if (!str) return '{}';
        const trimmed = str.trim();
        if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
          return trimmed.slice(1, -1);
        }
        return trimmed;
      };

      const metadata = JSON.parse(stripQuotes(record.metadata));
      const artifacts = JSON.parse(stripQuotes(record.artifacts));

      await db.insert(earningsCalls).values({
        id: record.id,
        cikStr: record.cik_str,
        symbol: record.symbol,
        quarter: record.quarter,
        year: parseInt(record.year),
        mediaUrl: record.media_url || null,
        youtubeId: metadata.youtube_id || null,
        metadata,
        artifacts,
        isLatest: record.is_latest === 'true' || record.is_latest === '1',
      }).onConflictDoNothing();

      inserted++;

      if (inserted % 100 === 0) {
        console.log(`   Progress: ${inserted} earnings calls inserted...`);
      }
    } catch (error) {
      console.error(`   ⚠️  Skipped ${record.id}: ${error}`);
      console.error(`      metadata field: ${record.metadata?.substring(0, 100)}`);
      skipped++;
    }
  }

  console.log(`   ✅ Earnings Calls: ${inserted} inserted, ${skipped} skipped\n`);
}

async function main() {
  console.log('\n🌱 Starting CSV seed process...');
  console.log(`   Database: ${process.env.DATABASE_URL?.split('@')[1]?.split('/')[0] || 'unknown'}\n`);

  // Check if CSV files exist
  if (!fs.existsSync(COMPANIES_CSV)) {
    console.error(`❌ Companies CSV not found: ${COMPANIES_CSV}`);
    process.exit(1);
  }

  if (!fs.existsSync(EARNINGS_CSV)) {
    console.error(`❌ Earnings calls CSV not found: ${EARNINGS_CSV}`);
    process.exit(1);
  }

  try {
    await seedCompanies();
    await seedEarningsCalls();

    console.log('✅ Seed complete!\n');
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Seed failed:', error);
    process.exit(1);
  }
}

main();
