/**
 * Company Theme System
 *
 * Defines brand colors, fonts, and styling for each company's videos.
 * LLM-friendly: Simple JSON structure for easy generation.
 */

export interface CompanyTheme {
  // Company info
  company: string;
  ticker: string;

  // Brand colors
  colors: {
    primary: string;      // Main brand color (e.g., Robinhood green)
    secondary: string;    // Accent color
    background: string;   // Background color
    text: string;         // Primary text color
    textSecondary: string; // Secondary text color
    success: string;      // For positive metrics (green)
    danger: string;       // For negative metrics (red)
    neutral: string;      // For neutral elements
  };

  // Gradients
  gradients?: {
    primary: string[];    // [start, end] colors
    background: string[]; // Background gradient
  };

  // Typography
  typography?: {
    headingFont?: string;
    bodyFont?: string;
    monoFont?: string;
  };

  // Logo
  logo?: {
    url: string;
    backgroundColor?: string; // For logo background
  };

  // Animation preferences
  animation?: {
    style: 'bold' | 'minimal' | 'playful' | 'corporate';
    speed: 'fast' | 'medium' | 'slow';
  };
}

// Default theme (fallback)
export const DEFAULT_THEME: CompanyTheme = {
  company: 'Default',
  ticker: 'DEFAULT',
  colors: {
    primary: '#2563eb',
    secondary: '#3b82f6',
    background: '#000000',
    text: '#ffffff',
    textSecondary: '#9ca3af',
    success: '#10b981',
    danger: '#ef4444',
    neutral: '#6b7280',
  },
  animation: {
    style: 'corporate',
    speed: 'medium',
  },
};
