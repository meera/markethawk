/**
 * Database Seed Script
 *
 * Populates database with initial companies and placeholder videos
 *
 * Run: npm run db:seed
 */

import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: '.env.local' });

import { db, closeDb } from '../lib/db';
import { companies, videos } from '../lib/db/schema';
import {
  generateCompanyId,
  generateVideoId,
  generateVideoSlug,
} from '../lib/utils/ids';

const SEED_COMPANIES = [
  // Tech Giants
  {
    ticker: 'AAPL',
    name: 'Apple Inc.',
    industry: 'Technology',
    sector: 'Consumer Electronics',
    logoUrl: 'https://logo.clearbit.com/apple.com',
    description: 'Apple designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.',
  },
  {
    ticker: 'MSFT',
    name: 'Microsoft Corporation',
    industry: 'Technology',
    sector: 'Software',
    logoUrl: 'https://logo.clearbit.com/microsoft.com',
    description: 'Microsoft develops, licenses, and supports software, services, devices, and solutions.',
  },
  {
    ticker: 'GOOGL',
    name: 'Alphabet Inc.',
    industry: 'Technology',
    sector: 'Internet Services',
    logoUrl: 'https://logo.clearbit.com/google.com',
    description: 'Alphabet is a collection of companies, the largest of which is Google.',
  },
  {
    ticker: 'AMZN',
    name: 'Amazon.com Inc.',
    industry: 'Technology',
    sector: 'E-commerce',
    logoUrl: 'https://logo.clearbit.com/amazon.com',
    description: 'Amazon is an American multinational technology company focusing on e-commerce, cloud computing, and AI.',
  },
  {
    ticker: 'META',
    name: 'Meta Platforms Inc.',
    industry: 'Technology',
    sector: 'Social Media',
    logoUrl: 'https://logo.clearbit.com/meta.com',
    description: 'Meta builds technologies that help people connect, find communities, and grow businesses.',
  },
  {
    ticker: 'TSLA',
    name: 'Tesla Inc.',
    industry: 'Automotive',
    sector: 'Electric Vehicles',
    logoUrl: 'https://logo.clearbit.com/tesla.com',
    description: 'Tesla designs, develops, manufactures, and sells electric vehicles and energy generation and storage systems.',
  },
  {
    ticker: 'NVDA',
    name: 'NVIDIA Corporation',
    industry: 'Technology',
    sector: 'Semiconductors',
    logoUrl: 'https://logo.clearbit.com/nvidia.com',
    description: 'NVIDIA is a technology company that designs graphics processing units (GPUs) for gaming and professional markets.',
  },

  // Finance
  {
    ticker: 'JPM',
    name: 'JPMorgan Chase & Co.',
    industry: 'Finance',
    sector: 'Banking',
    logoUrl: 'https://logo.clearbit.com/jpmorganchase.com',
    description: 'JPMorgan Chase is a leading global financial services firm.',
  },
  {
    ticker: 'BAC',
    name: 'Bank of America Corporation',
    industry: 'Finance',
    sector: 'Banking',
    logoUrl: 'https://logo.clearbit.com/bankofamerica.com',
    description: 'Bank of America serves individual consumers, small and middle-market businesses, and large corporations.',
  },
  {
    ticker: 'WFC',
    name: 'Wells Fargo & Company',
    industry: 'Finance',
    sector: 'Banking',
    logoUrl: 'https://logo.clearbit.com/wellsfargo.com',
    description: 'Wells Fargo is a diversified, community-based financial services company.',
  },
];

async function seed() {
  console.log('🌱 Starting database seed...\n');

  try {
    // 1. Insert companies
    console.log('📊 Inserting companies...');
    const insertedCompanies = [];

    for (const company of SEED_COMPANIES) {
      const id = generateCompanyId(company.ticker);

      await db.insert(companies).values({
        id,
        ticker: company.ticker,
        data: {
          name: company.name,
          industry: company.industry,
          sector: company.sector,
          logoUrl: company.logoUrl,
          description: company.description,
        },
      });

      insertedCompanies.push({ id, ticker: company.ticker, name: company.name });
      console.log(`  ✓ ${company.ticker} - ${company.name}`);
    }

    console.log(`\n✅ Inserted ${insertedCompanies.length} companies\n`);

    // 2. Insert placeholder videos (for Phase 0: pointing to existing YouTube videos)
    console.log('🎥 Inserting placeholder videos...');

    const quarters = ['Q4'] as const;
    const year = 2024;
    let videoCount = 0;

    for (const company of insertedCompanies.slice(0, 5)) {
      // First 5 companies only
      for (const quarter of quarters) {
        const id = generateVideoId(company.ticker, quarter, year);
        const slug = generateVideoSlug(company.ticker, quarter, year);

        await db.insert(videos).values({
          id,
          companyId: company.id,
          slug,
          status: 'published',
          quarter,
          year,
          youtubeId: null, // Will be filled when we find/upload actual videos
          data: {
            title: `${company.name} (${company.ticker}) ${quarter} ${year} Earnings Call`,
            description: `Visual summary of ${company.name} ${quarter} ${year} earnings call with charts, transcripts, and financial analysis.`,
            duration: 600, // 10 minutes placeholder
            thumbnailUrl: undefined,
            r2VideoPath: `${company.ticker}/videos/${year}-${quarter}-full.mp4`,
            r2VideoUrl: undefined,
            sources: [],
            artifacts: [],
            remotionProps: {},
          },
        });

        console.log(`  ✓ ${company.ticker} ${quarter} ${year}`);
        videoCount++;
      }
    }

    console.log(`\n✅ Inserted ${videoCount} placeholder videos\n`);

    console.log('🎉 Seed completed successfully!\n');
    console.log('Next steps:');
    console.log('  1. Visit http://localhost:3000 to see the landing page');
    console.log('  2. Videos will show "Coming Soon" until YouTube IDs are added');
    console.log('  3. Run seed script again to add more companies/videos\n');
  } catch (error) {
    console.error('❌ Seed failed:', error);
    throw error;
  } finally {
    await closeDb();
  }
}

seed();
