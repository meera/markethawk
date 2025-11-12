import { sql } from 'drizzle-orm';
import { db } from './index';

export interface Company {
  id: number;
  symbol: string;
  name: string;
  last_sale: number | null;
  net_change: number | null;
  pct_change: string | null;
  market_cap: number | null;
  country: string | null;
  ipo_year: number | null;
  volume: number | null;
  sector: string | null;
  industry: string | null;
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
    query = sql`${query} AND sector = ${sector}`;
  }

  if (search) {
    query = sql`${query} AND (
      name ILIKE ${`%${search}%`} OR
      symbol ILIKE ${`%${search}%`}
    )`;
  }

  query = sql`${query}
    ORDER BY market_cap DESC NULLS LAST
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
    WHERE UPPER(symbol) = UPPER(${ticker})
    LIMIT 1
  `);

  return (result[0] as unknown as Company) || null;
}

/**
 * Get all unique sectors
 */
export async function getSectors(): Promise<{ sector: string; count: number }[]> {
  const result = await db.execute(sql`
    SELECT sector, COUNT(*) as count
    FROM markethawkeye.companies
    WHERE sector IS NOT NULL
    GROUP BY sector
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
    query = sql`${query} AND sector = ${sector}`;
  }

  if (search) {
    query = sql`${query} AND (
      name ILIKE ${`%${search}%`} OR
      symbol ILIKE ${`%${search}%`}
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
    WHERE market_cap IS NOT NULL AND market_cap > 0
    ORDER BY market_cap DESC
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
    WHERE sector = ${sector}
    ORDER BY market_cap DESC NULLS LAST
    LIMIT ${limit}
  `);

  return result as unknown as Company[];
}
