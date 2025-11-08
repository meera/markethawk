import { CompanyTheme } from '../types';

/**
 * Robinhood Theme
 *
 * Brand colors: Green (#00C805), Black (#000000)
 * Style: Bold, modern, approachable
 */
export const robinhoodTheme: CompanyTheme = {
  company: 'Robinhood',
  ticker: 'HOOD',

  colors: {
    primary: '#00C805',      // Robinhood signature green
    secondary: '#00E805',    // Lighter green accent
    background: '#000000',   // Black background
    text: '#ffffff',         // White text
    textSecondary: '#a0a0a0', // Gray text
    success: '#00C805',      // Same as primary
    danger: '#FF6154',       // Robinhood red
    neutral: '#6b7280',      // Neutral gray
  },

  gradients: {
    primary: ['#00C805', '#00E805'],
    background: ['#000000', '#1a1a1a'],
  },

  typography: {
    headingFont: 'Inter, system-ui, sans-serif',
    bodyFont: 'Inter, system-ui, sans-serif',
    monoFont: 'JetBrains Mono, monospace',
  },

  logo: {
    url: 'https://logo.clearbit.com/robinhood.com',
    backgroundColor: '#00C805',
  },

  animation: {
    style: 'bold',
    speed: 'fast',
  },
};
