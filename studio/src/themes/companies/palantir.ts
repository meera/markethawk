import { CompanyTheme } from '../types';

/**
 * Palantir Theme
 *
 * Brand colors: Black, Blue (#2E5BFF)
 * Style: Professional, data-driven, high-tech
 */
export const palantirTheme: CompanyTheme = {
  company: 'Palantir Technologies',
  ticker: 'PLTR',

  colors: {
    primary: '#2563eb',      // Blue (currently used in banner)
    secondary: '#3b82f6',    // Lighter blue
    background: '#000000',   // Black
    text: '#ffffff',         // White
    textSecondary: '#9ca3af', // Gray
    success: '#10b981',      // Green for positive metrics
    danger: '#ef4444',       // Red for negative metrics
    neutral: '#6b7280',      // Neutral gray
  },

  gradients: {
    primary: ['#2563eb', '#3b82f6'],
    background: ['#000000', '#1a1a2e'],
  },

  typography: {
    headingFont: 'Inter, system-ui, sans-serif',
    bodyFont: 'Inter, system-ui, sans-serif',
    monoFont: 'JetBrains Mono, monospace',
  },

  logo: {
    url: 'https://logo.clearbit.com/palantir.com',
  },

  animation: {
    style: 'corporate',
    speed: 'medium',
  },
};
