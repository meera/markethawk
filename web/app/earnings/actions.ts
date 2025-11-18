'use server';

import { db } from '@/lib/db';
import { earningsCalls } from '@/lib/db/schema';
import { desc, eq, and } from 'drizzle-orm';

/**
 * Get all earnings calls with pagination
 */
export async function getEarningsCalls(limit: number = 50, offset: number = 0) {
  try {
    const calls = await db
      .select()
      .from(earningsCalls)
      .orderBy(desc(earningsCalls.createdAt))
      .limit(limit)
      .offset(offset);

    return { success: true, data: calls };
  } catch (error) {
    console.error('Error fetching earnings calls:', error);
    return { success: false, error: 'Failed to fetch earnings calls' };
  }
}

/**
 * Get single earnings call by ID
 */
export async function getEarningsCall(id: string) {
  try {
    const call = await db.query.earningsCalls.findFirst({
      where: eq(earningsCalls.id, id),
    });

    if (!call) {
      return { success: false, error: 'Earnings call not found' };
    }

    return { success: true, data: call };
  } catch (error) {
    console.error('Error fetching earnings call:', error);
    return { success: false, error: 'Failed to fetch earnings call' };
  }
}

/**
 * Get earnings calls by symbol (latest versions only)
 */
export async function getEarningsCallsBySymbol(symbol: string) {
  try {
    const calls = await db
      .select()
      .from(earningsCalls)
      .where(
        and(
          eq(earningsCalls.symbol, symbol.toUpperCase()),
          eq(earningsCalls.isLatest, true)
        )
      )
      .orderBy(desc(earningsCalls.year), desc(earningsCalls.quarter));

    return { success: true, data: calls };
  } catch (error) {
    console.error('Error fetching earnings calls by symbol:', error);
    return { success: false, error: 'Failed to fetch earnings calls' };
  }
}

/**
 * Get earnings calls by CIK
 */
export async function getEarningsCallsByCik(cikStr: string) {
  try {
    const calls = await db
      .select()
      .from(earningsCalls)
      .where(eq(earningsCalls.cikStr, cikStr))
      .orderBy(desc(earningsCalls.year), desc(earningsCalls.quarter));

    return { success: true, data: calls };
  } catch (error) {
    console.error('Error fetching earnings calls by CIK:', error);
    return { success: false, error: 'Failed to fetch earnings calls' };
  }
}

/**
 * Get earnings call by symbol, quarter, and year
 */
export async function getEarningsCallBySlug(symbol: string, quarter: string, year: number) {
  try {
    const call = await db.query.earningsCalls.findFirst({
      where: and(
        eq(earningsCalls.symbol, symbol.toUpperCase()),
        eq(earningsCalls.quarter, quarter.toUpperCase()),
        eq(earningsCalls.year, year)
      ),
    });

    if (!call) {
      return { success: false, error: 'Earnings call not found' };
    }

    return { success: true, data: call };
  } catch (error) {
    console.error('Error fetching earnings call by slug:', error);
    return { success: false, error: 'Failed to fetch earnings call' };
  }
}
