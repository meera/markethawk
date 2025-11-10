# Brief: Add Complementary Colors to Theme System

## Executive Summary

Add two complementary colors (#008B8B and #001F3F) to the MarketHawk brand and theme system to enhance visual variety and depth in earnings call videos and the web platform.

**Colors:**
- **Teal/Cyan**: `#008B8B` (Dark cyan - sophisticated, calm, data-oriented)
- **Navy Blue**: `#001F3F` (Deep navy - professional, trustworthy, stable)

---

## Current State Analysis

### Existing Color Architecture

**1. Brand Profile System** (`lens/companies/*.json`):
```json
{
  "brandColors": {
    "primary": "#...",
    "secondary": "#...",
    "accent": "#...",
    "background": "#...",
    "backgroundGradient": ["#...", "#..."],
    "text": "#...",
    "textSecondary": "#..."
  }
}
```

**2. Theme System** (`studio/src/themes/types.ts`):
```typescript
colors: {
  primary, secondary, background,
  text, textSecondary,
  success, danger, neutral
}
```

**3. Web App** (`web/app/globals.css`):
- Uses CSS variables: `--text-tertiary: #717171`
- Limited color palette currently

### Gap Analysis

**Missing:**
- ❌ No complementary/tertiary brand colors for visual variety
- ❌ No intermediate color options between primary and secondary
- ❌ Limited palette for data visualization (charts, metrics)
- ❌ No depth in color hierarchy for UI layering

---

## Proposed Solution

### 1. Add Complementary Colors to Type System

**Location**: `studio/src/types/brand.ts`

**Before:**
```typescript
export interface BrandColors {
  primary: string;
  secondary: string;
  accent: string;
  // ... other colors
}
```

**After:**
```typescript
export interface BrandColors {
  primary: string;
  secondary: string;
  accent: string;
  complementary?: string[];  // NEW: Array of complementary colors
  // ... other colors
}
```

### 2. Update Theme Types

**Location**: `studio/src/themes/types.ts`

**Add to CompanyTheme interface:**
```typescript
colors: {
  primary: string;
  secondary: string;
  background: string;
  text: string;
  textSecondary: string;
  success: string;
  danger: string;
  neutral: string;
  // NEW:
  complementary1?: string;  // Teal #008B8B
  complementary2?: string;  // Navy #001F3F
  tertiary?: string;        // Alias for complementary1
}
```

### 3. Update All Brand Profiles

**Update these files:**
- `lens/companies/_default.json`
- `lens/companies/HOOD.json`
- `lens/companies/PLTR.json`
- `studio/src/themes/companies/robinhood.ts`
- `studio/src/themes/companies/palantir.ts`

**Example for _default.json:**
```json
{
  "brandColors": {
    "primary": "#3b82f6",
    "secondary": "#60a5fa",
    "accent": "#f59e0b",
    "complementary": ["#008B8B", "#001F3F"],
    "background": "#0f172a",
    "backgroundGradient": ["#0f172a", "#1e293b"],
    "text": "#ffffff",
    "textSecondary": "#94a3b8"
  }
}
```

### 4. Update Web App CSS Variables

**Location**: `web/app/globals.css`

**Add:**
```css
:root {
  /* Existing */
  --text-tertiary: #717171;

  /* NEW: Complementary colors */
  --complementary-teal: #008B8B;
  --complementary-navy: #001F3F;

  /* Color references */
  --color-complementary-1: var(--complementary-teal);
  --color-complementary-2: var(--complementary-navy);
}
```

---

## Use Cases

### 1. Video Enhancements

**Metric Display Variations**:
```typescript
// Current: Only uses primary/secondary
<MetricDisplay
  metric="Revenue"
  value="$1.3B"
  brandColors={theme.colors}
/>

// Enhanced: Use complementary for variety
<MetricDisplay
  metric="EPS"
  value="$2.45"
  accentColor={theme.colors.complementary1} // Teal
/>

<MetricDisplay
  metric="Guidance"
  value="↑ 15%"
  accentColor={theme.colors.complementary2} // Navy
/>
```

**Background Gradients**:
```typescript
// Create depth with complementary colors
gradients: {
  primary: ['#2563eb', '#3b82f6'],
  background: ['#000000', '#1a1a2e'],
  // NEW:
  accent: ['#008B8B', '#001F3F'],  // Teal to Navy
  overlay: ['#001F3F80', '#008B8B40'] // Semi-transparent
}
```

### 2. Data Visualization

**Chart Color Palettes**:
```typescript
// Revenue breakdown by segment
const chartColors = [
  theme.colors.primary,      // iPhone sales
  theme.colors.secondary,    // Services
  theme.colors.complementary1, // Mac
  theme.colors.complementary2, // iPad
  theme.colors.accent        // Wearables
];
```

**Metric Cards**:
```typescript
// Different metric types use different colors
- Revenue card: Primary blue
- EPS card: Complementary teal
- Guidance card: Complementary navy
- Growth rate: Accent orange
```

### 3. Web App UI

**Visual Hierarchy**:
```tsx
<div className="border-l-4 border-complementary-teal">
  <h3 className="text-complementary-navy">Q3 2025 Highlights</h3>
  <p className="text-text-tertiary">Revenue up 100% YoY</p>
</div>
```

**Interactive States**:
```tsx
// Hover states, active states
<button className="
  bg-primary hover:bg-complementary-teal
  active:bg-complementary-navy
">
  Watch Video
</button>
```

### 4. Speaker Labels

**Alternate Speaker Colors**:
```typescript
// CEO: Primary color
// CFO: Complementary teal
// COO: Complementary navy
// Analysts: Secondary color

<SpeakerLabel
  name="CFO"
  accentColor={theme.colors.complementary1}
/>
```

---

## Color Theory Rationale

### Why These Colors?

**#008B8B (Dark Cyan/Teal)**:
- **Psychology**: Trust, sophistication, technology, stability
- **Contrast**: Works well with both dark and light backgrounds
- **Use**: Financial data, tech metrics, calm emphasis
- **Accessibility**: Good contrast ratio (WCAG AA compliant)

**#001F3F (Navy Blue)**:
- **Psychology**: Professional, authoritative, corporate, depth
- **Contrast**: Excellent for layering and depth
- **Use**: Backgrounds, overlays, corporate branding
- **Accessibility**: Works as background with white text

**Together**:
- Complementary relationship creates visual harmony
- Teal brings energy, navy brings stability
- Both align with financial/tech industry aesthetic
- Expands palette without overwhelming brand identity

### Accessibility Considerations

**Contrast Ratios** (white text on colored background):

| Color | Hex | Contrast Ratio | WCAG Level |
|-------|-----|----------------|------------|
| Teal | #008B8B | 4.86:1 | AA ✓ |
| Navy | #001F3F | 16.78:1 | AAA ✓ |

Both colors pass WCAG AA standards for text contrast.

---

## Implementation Plan

### Phase 1: Type System & Schemas (1 hour)
1. Update `studio/src/types/brand.ts`
2. Update `studio/src/themes/types.ts`
3. Update TypeScript interfaces
4. Ensure backward compatibility (optional fields)

### Phase 2: Brand Profiles (30 min)
1. Update `lens/companies/_default.json`
2. Update `lens/companies/HOOD.json`
3. Update `lens/companies/PLTR.json`
4. Update `studio/src/themes/companies/*.ts`

### Phase 3: Web App Styles (30 min)
1. Update `web/app/globals.css`
2. Update Tailwind config (if needed)
3. Add color utility classes

### Phase 4: Component Updates (2 hours)
1. Update enhancement components to accept complementary colors
2. Add color variation props to MetricDisplay, SpeakerLabel, etc.
3. Update CallToAction, AnimatedTitle for color options

### Phase 5: Documentation (30 min)
1. Update CLAUDE.md with complementary color usage
2. Add examples to component documentation
3. Create color usage guidelines

**Total Estimated Time**: ~4.5 hours

---

## Testing Strategy

### Visual Testing
- [ ] Preview all existing compositions with new colors
- [ ] Verify color contrast ratios
- [ ] Test on dark/light backgrounds
- [ ] Check gradient combinations

### Component Testing
- [ ] MetricDisplay with complementary colors
- [ ] SpeakerLabel variations
- [ ] CallToAction with different accents
- [ ] Charts with expanded palette

### Cross-Platform Testing
- [ ] Remotion Studio preview
- [ ] Rendered video output
- [ ] Web app displays
- [ ] Mobile responsiveness

---

## Examples

### Before (Limited Palette)
```typescript
// Only primary and secondary available
<MetricDisplay
  metric="Revenue"
  brandColors={{ primary: "#00C805", secondary: "#00E805" }}
/>
```

### After (Enhanced Palette)
```typescript
// Rich color options
<MetricDisplay
  metric="Revenue"
  color={theme.colors.primary}           // Green
/>
<MetricDisplay
  metric="EPS"
  color={theme.colors.complementary1}    // Teal
/>
<MetricDisplay
  metric="Guidance"
  color={theme.colors.complementary2}    // Navy
/>
<MetricDisplay
  metric="Growth"
  color={theme.colors.accent}            // Orange
/>
```

### Data Visualization
```typescript
const segmentColors = {
  'iPhone': theme.colors.primary,        // #00C805 (green)
  'Services': theme.colors.complementary1, // #008B8B (teal)
  'Mac': theme.colors.complementary2,    // #001F3F (navy)
  'iPad': theme.colors.secondary,        // #00E805 (bright green)
  'Wearables': theme.colors.accent       // #FF6154 (red)
};
```

---

## Risks & Mitigation

### Risk 1: Visual Overload
**Problem**: Too many colors can look chaotic
**Mitigation**:
- Establish clear usage guidelines
- Primary color remains dominant
- Complementary colors used sparingly for accents

### Risk 2: Brand Confusion
**Problem**: Straying from company brand identity
**Mitigation**:
- Keep complementary colors optional
- Use only when primary/secondary not distinctive enough
- Maintain brand guidelines per company

### Risk 3: Accessibility
**Problem**: Poor contrast combinations
**Mitigation**:
- Test all color combinations for WCAG compliance
- Provide high-contrast fallbacks
- Never use complementary colors for critical text

---

## Success Metrics

**Qualitative:**
- [ ] Enhanced visual appeal of videos
- [ ] Clearer metric differentiation
- [ ] More professional, polished look
- [ ] Better data visualization

**Quantitative:**
- [ ] All color combinations meet WCAG AA
- [ ] Zero regressions in existing compositions
- [ ] All 3 brand profiles updated
- [ ] Documentation complete

---

## Future Enhancements

### Post-MVP Ideas:
1. **Dynamic color generation**: Auto-generate complementary colors from primary
2. **Industry-specific palettes**: Finance (blues), Tech (teals), Healthcare (greens)
3. **Seasonal themes**: Quarterly color variations
4. **User customization**: Let users choose accent colors in web app
5. **AI-powered palette**: LLM generates optimal color combinations per company

---

## Appendix: Color Specifications

### Teal (#008B8B)
- **RGB**: `rgb(0, 139, 139)`
- **HSL**: `hsl(180, 100%, 27%)`
- **CMYK**: `cmyk(100%, 0%, 0%, 45%)`
- **Name**: Dark Cyan / Teal
- **Mood**: Sophisticated, technical, trustworthy

### Navy (#001F3F)
- **RGB**: `rgb(0, 31, 63)`
- **HSL**: `hsl(210, 100%, 12%)`
- **CMYK**: `cmyk(100%, 51%, 0%, 75%)`
- **Name**: Navy Blue / Midnight Blue
- **Mood**: Professional, stable, corporate

### Color Harmony
```
Primary (varies by company)
  ↓
Secondary (lighter variant)
  ↓
Complementary 1 (Teal) ← Adds sophistication
  ↓
Complementary 2 (Navy) ← Adds depth
  ↓
Accent (varies by company)
```

---

## Questions for Review

1. Should complementary colors be **required** or **optional** in brand profiles?
   - **Recommendation**: Optional (backward compatible)

2. Should we support **more than 2** complementary colors?
   - **Recommendation**: Start with 2, expand if needed

3. Should the **web app theme** automatically sync with video themes?
   - **Recommendation**: Yes, use same JSON source

4. Should we create a **color picker UI** for admins to customize?
   - **Recommendation**: Phase 2 feature

---

## Approval & Next Steps

**Owner**: Meera
**Estimated Time**: 4.5 hours
**Priority**: Medium (enhances visuals, not critical path)
**Dependencies**: None

**Approval Checklist**:
- [ ] Color choices approved
- [ ] Type system changes approved
- [ ] Implementation plan approved
- [ ] Testing strategy approved

**Once approved, proceed with**:
1. Create feature branch: `claude/add-complementary-colors-*`
2. Implement Phase 1 (Type System)
3. Implement Phase 2 (Brand Profiles)
4. Test and iterate
5. Commit and push
6. Create pull request

---

**Document Version**: 1.0
**Created**: 2025-11-09
**Status**: Ready for Review
