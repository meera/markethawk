import { CompanyTheme, DEFAULT_THEME } from './types';
import { palantirTheme } from './companies/palantir';
import { robinhoodTheme } from './companies/robinhood';

/**
 * Theme Registry
 *
 * Central registry of all company themes.
 * Add new themes here as you create them.
 */
const THEME_REGISTRY: Record<string, CompanyTheme> = {
  PLTR: palantirTheme,
  HOOD: robinhoodTheme,
  // Add more companies here
  // AAPL: appleTheme,
  // GOOGL: googleTheme,
  // MSFT: microsoftTheme,
};

/**
 * Get theme by company ticker
 */
export function getTheme(ticker: string): CompanyTheme {
  return THEME_REGISTRY[ticker.toUpperCase()] || DEFAULT_THEME;
}

/**
 * Get all available themes
 */
export function getAllThemes(): CompanyTheme[] {
  return Object.values(THEME_REGISTRY);
}

/**
 * Check if theme exists for ticker
 */
export function hasTheme(ticker: string): boolean {
  return ticker.toUpperCase() in THEME_REGISTRY;
}

// Export types and themes
export type { CompanyTheme } from './types';
export { DEFAULT_THEME } from './types';
export { palantirTheme, robinhoodTheme };
