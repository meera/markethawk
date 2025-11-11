# Market Hawk Eye Brand Guidelines

**Last Updated:** November 10, 2025

## Brand Identity

**Brand Name:** Market Hawk Eye
**Domain:** markethawkeye.com
**Tagline:** Transform earnings calls into visual insights
**Visual Identity:** Ultra-modern, premium, data-focused with laser precision

---

## Color Palette

### Dark Theme (Primary)

**Background (Ultra-Dark)**
- Hex: `#030712`
- RGB: `rgb(3, 7, 18)`
- Usage: Main background - ultra-dark, premium, stealthy
- Effect: Makes highlights pop, creates depth

**Primary / Brand Color (Emerald Green)**
- Hex: `#10B981`
- RGB: `rgb(16, 185, 129)`
- HSL: `hsl(160, 84%, 39%)`
- Usage: Brand color, CTAs, interactive elements, graphs, hover states, headers, logos
- Mood: Growth, success, precision, professional actionability

**Accent / Alerts (Amber Glint)**
- Hex: `#FFBF00`
- RGB: `rgb(255, 191, 0)`
- HSL: `hsl(45, 100%, 50%)`
- Usage: Small accent bursts only - hawk's eye glint, pulsing dots, numbered badges, attention markers (10-15% usage)
- Mood: Sharp focus, attention, precision highlight

**Text / Labels (Off-White)**
- Hex: `#F9FAFB`
- RGB: `rgb(249, 250, 251)`
- Usage: Primary text, headings, high-readability content
- Effect: Clean, crisp, maximum readability on dark background

**Muted Text / Panels (Slate 800)**
- Hex: `#1E293B`
- RGB: `rgb(30, 41, 59)`
- Usage: Cards, secondary text, background panels within dark UI
- Effect: Subtle depth, layering, hierarchy

### Light Theme (Alternative)

**Background**
- Hex: `#F9FAFB`
- Usage: Clean, readable, report-friendly

**Primary / Brand Color**
- Hex: `#10B981` (same as dark theme)
- Usage: Maintains brand consistency; CTAs, charts, hover states

**Accent / Alerts**
- Hex: `#FFBF00` (same as dark theme)
- Usage: Small accent bursts - key focus points, attention markers (10-15% usage)

**Text / Labels**
- Hex: `#0F172A`
- Usage: Dark text for readability

**Muted Text / Panels**
- Hex: `#E2E8F0`
- Usage: Cards, secondary info

---

## Typography

### Primary Font: Satoshi

**Font Family:** Satoshi
**Weights:**
- Regular (400) - Body text
- Medium (500) - Emphasis, subheadings
- Bold (700) - Headings, strong emphasis

**Usage:** All text — headings, body, numbers, UI, logo

**Style Characteristics:**
- Geometric, modern, highly readable
- Consistent across dark/light themes
- Conveys precision, intelligence, and premium analytics vibe

**Fallback:** `system-ui, sans-serif`

### Monospace Font: JetBrains Mono

**Usage:** Code, data, metrics, technical displays

---

## Color Usage Guidelines

### Dark Theme Application

**Backgrounds:**
```css
/* Ultra-dark primary background */
background: #030712;

/* Gradient variation */
background: linear-gradient(135deg, #030712 0%, #0a0f1e 50%, #030712 100%);

/* Card backgrounds */
background: rgba(30, 41, 59, 0.5); /* Slate 800 @ 50% */
```

**Text Hierarchy:**
```css
/* Primary headings */
color: #F9FAFB;

/* Body text */
color: rgba(249, 250, 251, 0.8); /* 80% opacity */

/* Secondary/muted text */
color: rgba(249, 250, 251, 0.6); /* 60% opacity */

/* Emphasis (green) */
color: #10B981;

/* Alerts/focus (amber - small bursts only) */
color: #FFBF00;
```

**Interactive Elements:**
```css
/* Primary button */
background: #10B981;
hover: #059669;

/* Secondary button */
background: #030712;
hover: #0F172A;

/* Border accent */
border: 1px solid rgba(16, 185, 129, 0.3);

/* Border hover */
border: 1px solid rgba(16, 185, 129, 0.6);

/* Amber hover glow (small bursts) */
border: 1px solid rgba(251, 191, 36, 0.4);
```

---

## Gradients

**Green Gradient (Primary):**
```css
background: linear-gradient(135deg, #10B981 0%, #059669 100%);
```

**Green to Lighter Green (Growth):**
```css
background: linear-gradient(90deg, #10B981 0%, #34D399 100%);
```

**Text Gradient (Hero):**
```css
background: linear-gradient(90deg, #10B981 0%, #34D399 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
```

**Amber Accent (Small Bursts):**
```css
background: linear-gradient(135deg, #FFBF00 0%, #EA580C 100%);
```

---

## Component Examples

### Header
```tsx
<header className="border-b border-[#10B981]/30 bg-[#030712]/80 backdrop-blur-sm">
  <div className="w-10 h-10 bg-gradient-to-br from-[#10B981] to-[#059669] shadow-lg shadow-[#10B981]/20">
    <span className="text-white font-bold">M</span>
    {/* Amber accent burst */}
    <span className="absolute -top-1 -right-1 w-2 h-2 bg-[#FFBF00] rounded-full animate-pulse"></span>
  </div>
  <h1 className="text-[#F9FAFB] font-bold">Market Hawk Eye</h1>
</header>
```

### Card
```tsx
<div className="bg-[#1E293B]/50 border border-[#10B981]/30 rounded-2xl hover:bg-[#1E293B]/70 hover:border-[#10B981]/50 transition-all">
  <h3 className="text-[#F9FAFB]">Title</h3>
  <p className="text-[#F9FAFB]/70">Body text</p>
</div>
```

### Feature Card
```tsx
<div className="bg-[#1E293B]/40 border border-[#10B981]/20 rounded-xl hover:bg-[#1E293B]/60 hover:border-[#FFBF00]/40">
  {/* Amber numbered badge (small burst) */}
  <div className="absolute -top-3 -right-3 w-8 h-8 bg-gradient-to-br from-[#FFBF00] to-[#EA580C] rounded-full">1</div>
  <div className="bg-[#10B981]/10 rounded-lg">
    <span>Icon</span>
  </div>
  <h4 className="text-[#10B981] group-hover:text-[#34D399] font-semibold">Feature Title</h4>
  <p className="text-[#F9FAFB]/60">Description</p>
</div>
```

### Button - Primary
```tsx
<button className="bg-[#10B981] hover:bg-[#059669] text-white font-semibold shadow-lg">
  Call to Action
</button>
```

### Button - Secondary
```tsx
<button className="bg-[#030712] hover:bg-[#0F172A] text-white font-semibold shadow-lg">
  Secondary Action
</button>
```

---

## Logo Specifications

### Logo Mark
- Simple "M" lettermark
- Background: Green gradient (`#10B981` to `#059669`)
- Text: White (`#FFFFFF`)
- Accent: Amber glint (`#FFBF00`) - small pulsing dot (optional)
- Shape: Rounded rectangle (8px border radius)
- Shadow: `shadow-lg shadow-[#10B981]/20`

### Logo Sizes
- Header: 40px × 40px
- Footer: 32px × 32px
- Favicon: 16px × 16px, 32px × 32px

### Logo Variations
- **Primary:** Green gradient background with white "M" + amber glint
- **Minimal:** Solid green background
- **Monochrome:** All white or all green (for specific contexts)

---

## Design Principles

### Visual Style
- **Ultra-Modern & Premium:** Extremely dark background with laser-precision highlights
- **Data-Focused:** Emphasis on charts, metrics, visualizations
- **Technical Sophistication:** Hawk's eye precision - sharp, focused, intelligent
- **Financial Authority:** Trustworthy, stable, professional analytics platform

### Color Psychology
- **Emerald Green (#10B981):** Brand color, growth, success, professional actionability, precision
- **Amber (#FFBF00):** Hawk's eye glint (small bursts only) - sharp focus, attention, key highlights
- **Ultra-Dark (#030712):** Premium, stealthy, makes green & amber "pop"

### Effect
Extremely modern, premium, and data-focused; makes green "pop" like laser precision against ultra-dark background, with amber providing strategic highlight bursts.

---

## Accessibility

### Contrast Ratios (WCAG Compliance)

**Off-White (#F9FAFB) on Ultra-Dark (#030712):**
- Ratio: 19.2:1 ✅ (Passes AAA)

**Emerald Green (#10B981) on Ultra-Dark (#030712):**
- Ratio: 6.9:1 ✅ (Passes AA)

**Amber (#FBBF24) on Ultra-Dark (#030712):**
- Ratio: 9.2:1 ✅ (Passes AA)

**Emerald Green (#10B981) on Slate (#1E293B):**
- Ratio: 4.5:1 ✅ (Passes AA)

### Best Practices
- Use off-white (`#F9FAFB`) for primary text on dark backgrounds
- Use emerald green (`#10B981`) for interactive elements, CTAs, and highlights
- Use amber (`#FBBF24`) ONLY for small accent bursts (10-15% usage) - glints, badges, hover glows
- Maintain 60-80% opacity for secondary text to create hierarchy
- Always test color combinations before production use

---

## Semantic Color Usage

### Data Visualization

**Primary / Brand Metrics:**
```css
color: #10B981; /* Emerald Green */
```

**Positive Metrics (Growth, Gains):**
```css
color: #34D399; /* Lighter Green */
```

**Alerts / Focus Points (Small Bursts):**
```css
color: #FFBF00; /* Amber */
```

**Chart Color Palette (Multi-metric):**
```typescript
const chartColors = [
  '#10B981',  // Primary - Green
  '#34D399',  // Positive - Lighter Green
  '#FFBF00',  // Accent - Amber (small bursts)
  '#8B5CF6',  // Additional - Purple (if needed)
  '#EC4899',  // Additional - Pink (if needed)
];
```

---

## Usage in Video Pipeline

### Company Brand Profiles

When creating videos for specific companies (AAPL, HOOD, PLTR), use **their** brand colors for video overlays.

Use Market Hawk Eye colors for:
- Market Hawk Eye watermark/logo
- Website elements
- Marketing materials
- Landing pages
- Admin dashboard

### Market Hawk Eye Brand Profile JSON
```json
{
  "ticker": "HAWKEYE",
  "name": "Market Hawk Eye",
  "brandColors": {
    "primary": "#10B981",
    "accent": "#FFBF00",
    "background": "#030712",
    "backgroundGradient": ["#030712", "#0a0f1e"],
    "text": "#F9FAFB",
    "textSecondary": "#F9FAFB99",
    "muted": "#1E293B"
  },
  "typography": {
    "heading": "Satoshi, system-ui, sans-serif",
    "body": "Satoshi, system-ui, sans-serif",
    "mono": "JetBrains Mono, monospace",
    "headingWeight": "700",
    "bodyWeight": "400"
  }
}
```

---

## File References

- **Landing Page:** `web/app/page.tsx` (uses Hawk Theme dark colors)
- **Company Profiles:** `lens/companies/*.json` (company-specific colors)
- **Theme System:** `studio/src/types/brand.ts` (type definitions)
- **Complementary Colors Brief:** `BRIEF-COMPLEMENTARY-COLORS.md` (technical implementation)

---

## Implementation Checklist

**Approved By:** Meera
**Approval Date:** November 10, 2025
**Status:** ✅ Approved and Implemented

- [x] Landing page updated with Hawk Theme colors
- [x] Brand guidelines documented
- [ ] Add Satoshi font to web app
- [ ] Update marketing materials
- [ ] Update email templates
- [ ] Update social media graphics
- [ ] Create logo variations (SVG)

---

## Quick Color Reference

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Background | Ultra-Dark | `#030712` | Main background |
| Primary | Emerald Green | `#10B981` | Brand, CTAs, highlights, logos |
| Accent | Amber | `#FFBF00` | Small bursts only (10-15%) - glints, badges, hover glows |
| Text | Off-White | `#F9FAFB` | Primary text |
| Muted | Slate 800 | `#1E293B` | Cards, secondary panels |

---

**For questions or updates, contact:** hello@markethawkeye.com
