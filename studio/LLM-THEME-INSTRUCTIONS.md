# LLM Instructions: Creating Company Themes

## Overview

This system allows you to create branded video components for each company using their brand colors automatically.

**Structure:** Each company has a theme file that defines colors, typography, and styling preferences.

---

## How to Instruct an LLM to Create Themes

### **Simple Prompt Template:**

```
Create a theme file for [COMPANY] ([TICKER]) with these brand colors:
- Primary: [COLOR]
- Secondary: [COLOR]
- Style: [bold/minimal/playful/corporate]

Save to: src/themes/companies/[company-name].ts
```

### **Example Prompts:**

#### **Example 1: Robinhood**
```
Create a theme for Robinhood (HOOD):
- Primary color: #00C805 (green)
- Black background
- Bold, modern style
- Fast animations
```

**Result:** `src/themes/companies/robinhood.ts` ✅

---

#### **Example 2: Apple**
```
Create a theme for Apple (AAPL):
- Primary color: #000000 (black)
- Secondary: #555555 (gray)
- White background for cards
- Minimal, clean style
- Smooth animations
```

---

#### **Example 3: Tesla**
```
Create a theme for Tesla (TSLA):
- Primary: #E31937 (red)
- Secondary: #000000 (black)
- Style: Bold, futuristic
- Fast animations
```

---

## Theme File Template

**Location:** `src/themes/companies/[company-name].ts`

```typescript
import { CompanyTheme } from '../types';

export const [companyName]Theme: CompanyTheme = {
  company: '[Full Company Name]',
  ticker: '[TICKER]',

  colors: {
    primary: '#XXXXXX',      // Main brand color
    secondary: '#XXXXXX',    // Accent color
    background: '#XXXXXX',   // Background
    text: '#XXXXXX',         // Text color
    textSecondary: '#XXXXXX', // Secondary text
    success: '#10b981',      // Green for gains
    danger: '#ef4444',       // Red for losses
    neutral: '#6b7280',      // Gray
  },

  gradients: {
    primary: ['#START', '#END'],
    background: ['#START', '#END'],
  },

  typography: {
    headingFont: 'Font Name, fallback',
    bodyFont: 'Font Name, fallback',
    monoFont: 'JetBrains Mono, monospace',
  },

  logo: {
    url: 'https://logo.clearbit.com/company.com',
  },

  animation: {
    style: 'bold', // bold | minimal | playful | corporate
    speed: 'medium', // fast | medium | slow
  },
};
```

---

## After Creating Theme

### **Step 1: Register in Theme Registry**

Edit `src/themes/index.ts`:

```typescript
import { [companyName]Theme } from './companies/[company-name]';

const THEME_REGISTRY: Record<string, CompanyTheme> = {
  PLTR: palantirTheme,
  HOOD: robinhoodTheme,
  AAPL: appleTheme,  // <-- Add here
  // ...
};

export { appleTheme }; // <-- Export here
```

---

### **Step 2: Use in Video Compositions**

```typescript
import { getTheme } from '@/themes';

export const AAPL_Q4_2024: React.FC = () => {
  const theme = getTheme('AAPL'); // Automatically loads Apple theme

  return (
    <AbsoluteFill>
      {/* All components use theme colors */}
      <SimpleBanner theme={theme} />
      <SubscribeLowerThird theme={theme} />
      <MetricCard theme={theme} />
    </AbsoluteFill>
  );
};
```

---

## Common Brand Colors (Reference)

| Company | Ticker | Primary | Secondary | Style |
|---------|--------|---------|-----------|-------|
| **Apple** | AAPL | #000000 | #555555 | Minimal |
| **Google** | GOOGL | #4285F4 | #EA4335 | Playful |
| **Microsoft** | MSFT | #00A4EF | #7FBA00 | Corporate |
| **Amazon** | AMZN | #FF9900 | #232F3E | Bold |
| **Meta** | META | #0668E1 | #0A7CFF | Modern |
| **Tesla** | TSLA | #E31937 | #000000 | Bold |
| **Netflix** | NFLX | #E50914 | #000000 | Bold |
| **Spotify** | SPOT | #1DB954 | #191414 | Playful |
| **Stripe** | STRIPE | #635BFF | #0A2540 | Modern |
| **Coinbase** | COIN | #0052FF | #000000 | Bold |

---

## LLM Prompt for Batch Generation

```
Generate theme files for these 10 companies:

1. Apple (AAPL) - Black/Gray, minimal
2. Google (GOOGL) - Blue/Red, playful
3. Microsoft (MSFT) - Blue/Green, corporate
4. Amazon (AMZN) - Orange/Black, bold
5. Meta (META) - Blue, modern
6. Tesla (TSLA) - Red/Black, bold
7. Netflix (NFLX) - Red/Black, bold
8. Spotify (SPOT) - Green/Black, playful
9. Nvidia (NVDA) - Green/Black, tech
10. AMD (AMD) - Red/Black, tech

For each company:
- Create theme file in src/themes/companies/[name].ts
- Use the template structure
- Add to theme registry
- Export from index.ts
```

---

## How Components Use Themes

### **Before (Hardcoded Colors):**
```typescript
<div style={{ background: '#2563eb' }}> {/* Fixed blue */}
  Subscribe
</div>
```

### **After (Theme-based):**
```typescript
<div style={{ background: theme.colors.primary }}> {/* Auto uses company color */}
  Subscribe
</div>
```

### **For Robinhood:**
```typescript
const theme = getTheme('HOOD');
// theme.colors.primary = '#00C805' (green)
```

### **For Apple:**
```typescript
const theme = getTheme('AAPL');
// theme.colors.primary = '#000000' (black)
```

---

## Extracting Brand Colors

### **Method 1: Official Brand Guidelines**
- Search "[Company] brand guidelines PDF"
- Download official color palette

### **Method 2: Logo Extraction**
```bash
# Use clearbit logo API
https://logo.clearbit.com/robinhood.com
https://logo.clearbit.com/apple.com
https://logo.clearbit.com/[company].com
```

### **Method 3: Website Inspection**
- Visit company website
- Inspect primary buttons/nav
- Use browser DevTools color picker

### **Method 4: Ask LLM**
```
What are the official brand colors for Robinhood?
Include hex codes for primary and secondary colors.
```

---

## Testing Themes

### **Preview in Remotion Studio:**
```bash
npm start
# Open http://localhost:8082
# Select composition (e.g., "HOOD-Q3-2025")
# Verify colors match brand
```

### **Quick Test:**
```typescript
import { getTheme } from '@/themes';

const theme = getTheme('HOOD');
console.log(theme.colors.primary); // Should be '#00C805'
```

---

## Benefits of This System

✅ **Consistent branding** across all videos
✅ **Easy to add new companies** (just one file)
✅ **LLM-friendly** (simple JSON structure)
✅ **Type-safe** (TypeScript validation)
✅ **DRY** (no hardcoded colors in components)
✅ **Scalable** (works for 1000+ companies)

---

## Quick Start Checklist

For each new company:

- [ ] Research brand colors
- [ ] Create theme file: `src/themes/companies/[name].ts`
- [ ] Add to registry: `src/themes/index.ts`
- [ ] Test: `getTheme('[TICKER]')`
- [ ] Use in composition: `const theme = getTheme('TICKER')`
- [ ] Verify colors in Remotion Studio

---

**Ready to scale!** Now you can create branded videos for any company by just adding a theme file.
