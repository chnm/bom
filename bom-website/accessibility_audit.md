# WCAG 2.1 Level AA Audit — Death by Numbers
**URL:** https://deathbynumbers.org  
**Date:** 2026-03-20  
**Standard:** WCAG 2.1 Level AA  
**Status:** ❌ Does Not Meet Level AA

---

## Overall Summary

The Death by Numbers site is a relatively simple academic/research website with modest complexity. Based on markup analysis, there are several failures and areas of concern across multiple WCAG 2.1 criteria. The site does not currently meet Level AA standards and requires remediation in several high-priority areas before it can be considered conformant.

---

## Identified Issues & Recommendations

### 1. Images Missing Meaningful Alt Text
**WCAG Criterion:** 1.1.1 – Non-text Content  
**Severity:** 🔴 High  
**Status:** ❌ FAIL

Several images have empty or missing `alt` attributes, including:
- `/images/bodleian-1642-09-recto.png` — no alt text
- `/images/preview_viz.png` — no alt text
- `/images/IMG_4187.jpeg` — no alt text
- `/images/004179.jpg` — `alt="Death by Numbers"` (same as the logo alt text — ambiguous and duplicative)

These images are used as section illustrations and carry contextual meaning, so they require descriptive alt text explaining what is depicted.

**Recommendation:** Add meaningful, descriptive `alt` attributes to all informational images. For purely decorative images, use `alt=""` explicitly so screen readers skip them.

---

### 2. Navigation Lacks ARIA Landmark Roles or Semantic HTML
**WCAG Criterion:** 1.3.1 – Info and Relationships / 4.1.2 – Name, Role, Value  
**Severity:** 🟢 Low  
**Status:** ⚠️ LIKELY FAIL

The navigation menu uses dropdown-style links but it is unclear from the markup whether proper `<nav>` elements, `aria-label` attributes, and list semantics (`<ul>/<li>`) are in place. Without these, screen reader users may struggle to identify and skip navigation.

**Recommendation:** Wrap primary navigation in a `<nav aria-label="Main navigation">` element. Use `<ul>/<li>` structure for navigation items. Add a "Skip to main content" link at the top of the page.

---

### 3. No Visible Skip Navigation Link
**WCAG Criterion:** 2.4.1 – Bypass Blocks  
**Severity:** 🔴 High  
**Status:** ❌ FAIL

There is no "Skip to main content" link present in the markup. Keyboard-only users must tab through the entire navigation on every page load before reaching content.

**Recommendation:** Add a visually hidden (but focus-visible) skip link as the very first focusable element:

```html
<a href="#main-content" class="skip-link">Skip to main content</a>
```

Add `id="main-content"` to the `<main>` element. The skip link should become visible on focus.

---

### 4. Page Title Adequacy
**WCAG Criterion:** 2.4.2 – Page Titled  
**Severity:** N/A  
**Status:** ✅ PASS

The page title "Welcome to the Bills of Mortality Project - Death by Numbers" is descriptive and unique. This criterion appears to be met on the homepage.

---

### 5. Ambiguous and Duplicate Link Text
**WCAG Criterion:** 2.4.4 – Link Purpose (In Context)  
**Severity:** 🟡 Medium  
**Status:** ⚠️ PARTIAL FAIL

The word "Overview" is used as link text multiple times across different navigation sections (Context, Data, Analysis, Pedagogy, About) without differentiation. For screen reader users navigating a list of links out of context, multiple identical "Overview" links are confusing and indistinguishable.

**Recommendation:** Use `aria-label` to differentiate repeated links, for example:

```html
<a href="/context/overview/" aria-label="Context Overview">Overview</a>
<a href="/data/" aria-label="Data Overview">Overview</a>
```

Alternatively, use visually hidden `<span>` text to provide context while preserving the visual design.

---

### 6. Color Contrast
**WCAG Criterion:** 1.4.3 – Contrast (Minimum)  
**Severity:** 🟡 Medium  
**Status:** ⚠️ REQUIRES LIVE VERIFICATION

Color contrast ratios cannot be confirmed without rendering the page. Academic and historical sites sometimes use muted or sepia-toned palettes that risk falling below the required ratios: **4.5:1** for normal text and **3:1** for large text (18pt+ or 14pt bold).

**Recommendation:** Run the site through the [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) or axe DevTools. Pay particular attention to:
- Body text against background colors
- Navigation link text
- Any text overlaid on images or decorative backgrounds

---

### 7. Focus Visibility
**WCAG Criterion:** 2.4.7 – Focus Visible  
**Severity:** 🟡 Medium  
**Status:** ⚠️ REQUIRES LIVE VERIFICATION

Many sites suppress the browser's default focus outline via CSS (`outline: none` or `outline: 0`). This is a common failure that makes keyboard navigation extremely difficult for sighted keyboard users.

**Recommendation:** Ensure all interactive elements (links, buttons, form fields) have a clearly visible focus indicator. Do not remove default browser outlines without providing a custom, high-contrast replacement that meets the WCAG 2.4.7 requirement.

---

### 8. Scanned Historical Document Images Without Text Alternatives
**WCAG Criterion:** 1.1.1 – Non-text Content / 1.4.5 – Images of Text  
**Severity:** 🔴 High  
**Status:** ❌ LIKELY FAIL

The site's core purpose involves displaying scanned historical documents (e.g., `bodleian-1642-09-recto.png`). Images of text cannot be read by screen readers and fail WCAG 1.4.5 unless the same information is provided as a text alternative.

**Recommendation:** Provide transcriptions or captions alongside all scanned bill images. The database feature may partially address this, but any page displaying image-based documents should offer an accessible text equivalent alongside or linked from the image.

---

### 9. Language of Page
**WCAG Criterion:** 3.1.1 – Language of Page  
**Severity:** 🟢 Low  
**Status:** ⚠️ UNVERIFIED

The HTML `lang` attribute must be present on the `<html>` element so that screen readers apply the correct voice and pronunciation profile.

**Recommendation:** Confirm `<html lang="en">` is set on every page template across the site.

---

### 10. Keyboard Accessibility of Dropdown Navigation
**WCAG Criterion:** 2.1.1 – Keyboard  
**Severity:** 🟡 Medium  
**Status:** ⚠️ LIKELY ISSUE

The multi-level dropdown navigation (Context, Data, Analysis, Pedagogy, About) must be fully keyboard operable. Hover-only dropdowns are a common and significant keyboard accessibility failure.

**Recommendation:** Ensure dropdown submenus are accessible via keyboard:
- **Enter** or **Space** to open a submenu
- **Escape** to close and return focus to the parent item
- **Arrow keys** to navigate within an open submenu

Follow the [ARIA Disclosure Navigation pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/) or the ARIA Menu Button pattern.

---

## Priority Action Summary

| Priority | Issue | WCAG Criterion |
|---|---|---|
| 🔴 High | Missing/empty alt text on content images | 1.1.1 |
| 🔴 High | No skip navigation link | 2.4.1 |
| 🔴 High | Scanned images without text alternatives | 1.1.1 / 1.4.5 |
| 🟡 Medium | Duplicate "Overview" link text | 2.4.4 |
| 🟡 Medium | Keyboard accessibility of dropdowns | 2.1.1 |
| 🟡 Medium | Color contrast (needs live verification) | 1.4.3 |
| 🟡 Medium | Focus visibility (needs live verification) | 2.4.7 |
| 🟢 Low | ARIA landmarks / semantic nav structure | 1.3.1 / 4.1.2 |
| 🟢 Low | Confirm `lang` attribute | 3.1.1 |

---

## Recommended Next Steps

For a thorough automated and manual audit, run the site through the following tools:

- **[axe DevTools](https://www.deque.com/axe/devtools/)** — Free browser extension for automated accessibility testing
- **[WAVE](https://wave.webaim.org/)** — Web accessibility evaluation tool by WebAIM
- **[Lighthouse](https://developer.chrome.com/docs/lighthouse/)** — Built into Chrome DevTools under the Audits tab

These tools will surface additional issues on subpages, the database, and the visualizations section — which are likely more complex and may introduce further failures such as:
- Data tables missing proper header associations (`<th scope="...">`)
- Chart and visualization content requiring text alternatives
- Form inputs on the search page missing associated labels

---

*Report generated: 2026-03-20 | Auditor: Claude (Anthropic) | Method: Markup & structural analysis*
