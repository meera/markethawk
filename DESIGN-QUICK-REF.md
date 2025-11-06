# Design Quick Reference

Quick copy-paste reference for EarningLens design system.

## Colors

```css
/* Primary */
--primary: #2563EB;
--primary-hover: #1D4ED8;

/* Accent */
--accent: #667EEA;
--accent-dark: #764BA2;

/* Data Viz */
--positive: #48BB78;  /* Green - up trends */
--negative: #F56565;  /* Red - down trends */
--neutral: #718096;   /* Gray - no change */
--warning: #F59E0B;   /* Amber - alerts */

/* Text */
--text-primary: #111827;
--text-secondary: #6B7280;
--text-tertiary: #9CA3AF;

/* Background */
--bg-page: #F9FAFB;
--bg-card: #FFFFFF;
```

## Typography

```css
/* Fonts */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Consolas', monospace;

/* Sizes */
--text-xs: 12px;
--text-sm: 14px;
--text-base: 16px;
--text-lg: 18px;
--text-xl: 20px;
--text-2xl: 24px;
--text-3xl: 30px;
--text-4xl: 36px;

/* Headings */
H1: 36px / font-weight: 700
H2: 30px / font-weight: 600
H3: 24px / font-weight: 600
Body: 16px / font-weight: 400
Caption: 14px / font-weight: 400
```

## Spacing

```css
/* 8px grid */
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
--space-12: 48px;
--space-16: 64px;
```

## Common Patterns

### Button
```css
padding: 12px 24px;
border-radius: 8px;
font-size: 16px;
font-weight: 600;
background: #2563EB;
color: white;
```

### Card
```css
background: white;
border-radius: 12px;
padding: 24px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
```

### Input
```css
padding: 12px 16px;
border-radius: 8px;
border: 1px solid #D1D5DB;
font-size: 16px;
```

### Metric Card (Video)
```css
background: white;
border-radius: 20px;
padding: 32px;
box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
min-width: 280px;
```

## Video Overlays

### Lower Third
```
Background: rgba(0, 0, 0, 0.85)
Accent Bar: 8px wide, #667EEA
Text: 28px, font-weight: 700, white
```

### Metric Display
```
Label: 14px, uppercase, #718096
Value: 48px, font-weight: 700
Trend: 20px, colored (#48BB78 or #F56565)
```

## Tailwind Classes

```html
<!-- Primary Button -->
<button class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg">

<!-- Card -->
<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">

<!-- Heading -->
<h1 class="text-4xl font-bold text-gray-900">

<!-- Body Text -->
<p class="text-base text-gray-600 leading-relaxed">

<!-- Metric Card -->
<div class="bg-white rounded-2xl p-8 shadow-lg min-w-[280px]">
  <div class="text-sm uppercase text-gray-500 tracking-wide font-semibold">Revenue</div>
  <div class="text-5xl font-bold text-gray-900">$725M</div>
  <div class="text-xl font-bold text-green-500">↑ +30%</div>
</div>
```

## Chart Colors (in order)

```
1. #2563EB (Primary Blue)
2. #48BB78 (Green)
3. #667EEA (Purple)
4. #F59E0B (Amber)
5. #EC4899 (Pink)
6. #14B8A6 (Teal)
```
