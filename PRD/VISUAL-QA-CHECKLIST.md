# Visual QA Checklist

**Purpose:** Catch visual bugs that code review cannot detect. This checklist MUST be completed with actual screenshots and browser testing.

---

## Prerequisites (MANDATORY)

Before starting QA, you MUST:

1. **Take screenshots** in BOTH light and dark mode
2. **Test at 3 viewport sizes:**
   - Mobile: 375px width
   - Tablet: 768px width
   - Desktop: 1440px width
3. **Open browser DevTools** and keep Color Picker ready
4. **Test actual page** - do NOT rely on code analysis alone

---

## Color Contrast (WCAG AA: 4.5:1 minimum)

Use DevTools Color Picker to verify actual contrast ratios:

### Light Mode
- [ ] Page title/headline visible and high contrast (>7:1 ideal)
- [ ] Body text meets minimum 4.5:1 contrast
- [ ] Button text readable on button background (4.5:1)
- [ ] Link text distinguishable from body text
- [ ] Placeholder text in inputs (minimum 3:1)
- [ ] Disabled elements clearly different from enabled (but still readable)

### Dark Mode
- [ ] Page title/headline visible (white or near-white on dark)
- [ ] Body text meets minimum contrast
- [ ] Button text readable on dark button backgrounds
- [ ] Links visible and distinguishable
- [ ] Form inputs have visible borders
- [ ] No "invisible" text anywhere

### Interactive States
- [ ] **Hover states** change appearance BUT remain visible
- [ ] **Focus states** have visible outline/ring
- [ ] **Active states** provide visual feedback
- [ ] **Disabled states** clearly non-interactive but readable

---

## Layout Proportions

### Viewport Usage
- [ ] No single element exceeds 50% of viewport height (except modals)
- [ ] Video/media players limited to reasonable size (max 400px height recommended)
- [ ] Sticky elements don't obscure main content
- [ ] Primary content visible "above the fold" without scrolling

### Spacing
- [ ] Adequate whitespace between sections (minimum 2rem)
- [ ] Buttons/interactive elements not cramped (minimum 44x44px touch target)
- [ ] Text not running edge-to-edge (proper padding/margins)

### Responsive Behavior
- [ ] Mobile: Single column, readable text size (16px minimum)
- [ ] Tablet: Comfortable layout, no awkward wrapping
- [ ] Desktop: Content doesn't stretch too wide (max-width respected)

---

## Typography

### Readability
- [ ] Body text minimum 16px (1rem)
- [ ] Line height adequate for reading (1.5-1.75 for body text)
- [ ] Headings clearly differentiated by size and weight
- [ ] No text truncation without reason

### Hierarchy
- [ ] Clear visual distinction between heading levels
- [ ] Consistent font weights (don't mix too many)
- [ ] Proper semantic HTML (h1 for page title, etc.)

---

## Dark Mode Parity

Test every section in dark mode:

- [ ] All text visible (no black-on-black or white-on-white)
- [ ] Cards/containers have visible borders or backgrounds
- [ ] Images/icons render appropriately
- [ ] Form elements (inputs, selects) clearly visible
- [ ] Breadcrumbs, navigation links visible in all states
- [ ] Shadows/borders adjusted for dark backgrounds

---

## Common Visual Bugs to Check

### Text Visibility
- [ ] White text on white background
- [ ] Black text on black background
- [ ] Gray text on gray background (low contrast)
- [ ] Hover states that make text invisible

### Button Issues
- [ ] Button text same color as button background
- [ ] Buttons with no visible border/background
- [ ] Hover states remove visibility
- [ ] Icon-only buttons missing tooltips

### Media Elements
- [ ] Video players taking up 90%+ of viewport
- [ ] Images without proper sizing constraints
- [ ] Sticky media covering content when scrolling

### Navigation
- [ ] Breadcrumbs invisible on hover
- [ ] Links indistinguishable from body text
- [ ] Back links hidden or low contrast
- [ ] Menu items disappear on interaction

---

## Testing Process

### Step 1: Light Mode Desktop (1440px)
1. Open page in Chrome/Firefox
2. Take full-page screenshot
3. Check each item in checklist
4. Use DevTools Color Picker on suspected issues

### Step 2: Dark Mode Desktop (1440px)
1. Toggle dark mode (system preference or dev tools)
2. Take full-page screenshot
3. Check each item again
4. Compare with light mode for parity

### Step 3: Mobile (375px)
1. Open DevTools responsive mode
2. Set viewport to 375px width
3. Test both light and dark mode
4. Check touch target sizes (minimum 44x44px)

### Step 4: Interactive States
1. Hover over every interactive element
2. Tab through page with keyboard
3. Click buttons and verify feedback
4. Test form inputs if present

---

## Automated Tools (Supplement, Not Replace)

These tools help but DON'T replace manual testing:

- **Chrome DevTools Lighthouse:** Accessibility audit
- **WAVE Browser Extension:** Contrast checker
- **axe DevTools:** Accessibility scanner

---

## When to Use This Checklist

Use this checklist:

1. **Before deploying new pages** to production
2. **After major UI changes** (layout, colors, components)
3. **When UX reviewer agent** completes code review (verify visually)
4. **After dark mode implementation** (parity check)
5. **When user reports** "I can't see X" bugs

---

## Reporting Issues

When filing visual bugs, include:

1. **Screenshot** showing the issue
2. **Browser and mode** (Chrome dark mode, Safari light mode, etc.)
3. **Viewport size** (mobile 375px, desktop 1440px, etc.)
4. **Expected behavior** (should be visible, should contrast, etc.)
5. **Actual contrast ratio** (from DevTools if applicable)

---

## Example Bug Report

```
BUG: Breadcrumb links invisible on hover

- Screenshot: [attached]
- Browser: Chrome 131, Dark Mode
- Viewport: 1440px desktop
- Issue: Breadcrumb links turn from gray-600 to gray-900 on hover,
  but page is in dark mode, making them invisible on dark background
- Fix: Add dark:hover:text-gray-100 to maintain visibility
```

---

**Remember:** Code review catches logic bugs. Visual QA catches rendering bugs. Both are essential.

**Last Updated:** 2025-11-24
