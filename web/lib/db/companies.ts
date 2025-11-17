import { sql } from 'drizzle-orm';
import { db } from './index';

export interface Company {
  id: number;
  cik_str: string;
  ticker: string;
  name: string;
  slug: string;
  metadata: {
    exchange?: string;
    market_cap?: number;
    sector?: string;
    industry?: string;
    ipo_year?: number;
    country?: string;
    website?: string;
    description?: string;
    [key: string]: any;  // Flexible for future additions
  };
  created_at: Date;
  updated_at: Date;
}

/**
 * Get all companies with optional filtering
 */
export async function getCompanies(options?: {
  sector?: string;
  limit?: number;
  offset?: number;
  search?: string;
}): Promise<Company[]> {
  const { sector, limit = 100, offset = 0, search } = options || {};

  let query = sql`
    SELECT *
    FROM markethawkeye.companies
    WHERE 1=1
  `;

  if (sector) {
    query = sql`${query} AND metadata->>'sector' = ${sector}`;
  }

  if (search) {
    query = sql`${query} AND (
      name ILIKE ${`%${search}%`} OR
      ticker ILIKE ${`%${search}%`}
    )`;
  }

  query = sql`${query}
    ORDER BY (metadata->>'market_cap')::bigint DESC NULLS LAST
    LIMIT ${limit}
    OFFSET ${offset}
  `;

  const result = await db.execute(query);
  return result as unknown as Company[];
}

/**
 * Get a single company by ticker symbol
 */
export async function getCompanyByTicker(ticker: string): Promise<Company | null> {
  const result = await db.execute(sql`
    SELECT *
    FROM markethawkeye.companies
    WHERE UPPER(ticker) = UPPER(${ticker})
    LIMIT 1
  `);

  return (result[0] as unknown as Company) || null;
}

/**
 * Get a single company by slug
 */
export async function getCompanyBySlug(slug: string): Promise<Company | null> {
  const result = await db.execute(sql`
    SELECT *
    FROM markethawkeye.companies
    WHERE slug = ${slug}
    LIMIT 1
  `);

  return (result[0] as unknown as Company) || null;
}

/**
 * Get all unique sectors
 */
export async function getSectors(): Promise<{ sector: string; count: number }[]> {
  const result = await db.execute(sql`
    SELECT metadata->>'sector' as sector, COUNT(*) as count
    FROM markethawkeye.companies
    WHERE metadata->>'sector' IS NOT NULL
    GROUP BY metadata->>'sector'
    ORDER BY count DESC
  `);

  return result as unknown as { sector: string; count: number }[];
}

/**
 * Get total company count
 */
export async function getCompanyCount(options?: {
  sector?: string;
  search?: string;
}): Promise<number> {
  const { sector, search } = options || {};

  let query = sql`
    SELECT COUNT(*) as count
    FROM markethawkeye.companies
    WHERE 1=1
  `;

  if (sector) {
    query = sql`${query} AND metadata->>'sector' = ${sector}`;
  }

  if (search) {
    query = sql`${query} AND (
      name ILIKE ${`%${search}%`} OR
      ticker ILIKE ${`%${search}%`}
    )`;
  }

  const result = await db.execute(query);
  return Number((result[0] as any).count) || 0;
}

/**
 * Get top companies by market cap
 */
export async function getTopCompaniesByMarketCap(limit: number = 10): Promise<Company[]> {
  const result = await db.execute(sql`
    SELECT *
    FROM markethawkeye.companies
    WHERE metadata->>'market_cap' IS NOT NULL
      AND (metadata->>'market_cap')::bigint > 0
    ORDER BY (metadata->>'market_cap')::bigint DESC
    LIMIT ${limit}
  `);

  return result as unknown as Company[];
}

/**
 * Get companies by sector
 */
export async function getCompaniesBySector(sector: string, limit: number = 50): Promise<Company[]> {
  const result = await db.execute(sql`
    SELECT *
    FROM markethawkeye.companies
    WHERE metadata->>'sector' = ${sector}
    ORDER BY (metadata->>'market_cap')::bigint DESC NULLS LAST
    LIMIT ${limit}
  `);

  return result as unknown as Company[];
}
