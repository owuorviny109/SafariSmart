# SafariSmart Kenya - File Naming Conventions

## Overview
This document outlines the standardized file naming conventions used throughout the SafariSmart Kenya project. All files now follow consistent, descriptive naming patterns for better maintainability and developer experience.

## Naming Convention Rules

### 1. **kebab-case** for all files
- Use lowercase letters
- Separate words with hyphens (-)
- No underscores or spaces
- Be descriptive and clear

### 2. **File Extensions**
- `.html` for templates
- `.css` for stylesheets  
- `.scss` for Sass files
- `.js` for JavaScript files
- `.py` for Python files
- `.md` for documentation

## File Structure & Naming

### Templates (`templates/`)
```
templates/
├── accounts/
│   ├── login.html
│   ├── register.html
│   ├── password-reset.html
│   ├── password-reset-confirm.html
│   ├── password-reset-complete.html
│   └── password-reset-done.html
├── components/
│   ├── auth-nav.html
│   ├── cookie-consent.html
│   ├── destination-card.html
│   └── forms/
│       ├── contact-form.html
│       ├── progress-bar.html
│       └── wizard-navigation.html
├── core/
│   ├── budget-selection.html
│   ├── dashboard.html
│   ├── destination-selection.html
│   ├── duration-selection.html
│   ├── interests-selection.html
│   ├── itinerary-detail.html
│   ├── itinerary-detail-new.html
│   ├── itinerary-generation.html
│   ├── landing.html
│   ├── landing-v2.html
│   ├── static-page.html
│   └── travel-group-selection.html
├── destinations/
│   ├── browse.html
│   ├── detail.html
│   └── list.html
└── base.html
```

### Static Assets (`static/`)
```
static/
├── css/
│   ├── components/
│   │   ├── cta-section.css
│   │   ├── destination-cards.css
│   │   ├── faq.css
│   │   ├── hero.css
│   │   ├── how-it-works.css
│   │   ├── marquee.css
│   │   └── value-cards.css
│   ├── pages/
│   │   ├── auth.css
│   │   ├── dashboard.css
│   │   ├── destination-detail.css
│   │   ├── destination-selection.css
│   │   ├── destinations-browse.css
│   │   ├── destinations-list.css
│   │   ├── itinerary.css
│   │   ├── landing.css
│   │   ├── password-reset.css
│   │   ├── static-pages.css
│   │   └── wizard.css
│   ├── chat-widget.css
│   ├── components.css
│   ├── hero-backgrounds.css
│   ├── itinerary-detail.css          # ✅ Renamed from itinerary_detail.css
│   ├── main-theme.css                # ✅ Renamed from safarismart-main.css
│   ├── modern-theme.css
│   ├── safari-design-system.css
│   └── unified-design-system.css
├── js/
│   ├── animation-controller.js        # ✅ New centralized animation system
│   ├── chat-widget.js
│   └── itinerary-detail.js           # ✅ Renamed from itinerary_detail.js
├── images/
│   ├── destinations/
│   └── heroes/
└── design-system-demo.html           # ✅ Renamed from color-palette-demo.html
```

### SCSS Architecture (`assets/scss/`)
```
assets/scss/
├── abstracts/
│   └── _tokens.scss
├── animations/
│   └── _keyframes.scss
├── base/
│   ├── _accessibility.scss           # ✅ New accessibility utilities
│   ├── _animation-mixins.scss        # ✅ New animation mixins
│   ├── _mixins.scss
│   └── _reset.scss
├── components/
│   ├── _buttons.scss
│   ├── _card.scss
│   ├── _destination-card.scss
│   ├── _footer.scss                  # ✅ New footer component
│   ├── _marquee.scss
│   ├── _navbar.scss                  # ✅ New navbar component
│   └── _value-cards.scss             # ✅ New value cards component
├── utilities/
│   ├── _display.scss
│   ├── _spacing.scss
│   └── _typography.scss
└── main.scss
```

## Naming Patterns by File Type

### 1. Template Files
- **Pattern**: `{feature}-{action}.html`
- **Examples**:
  - `destination-selection.html` (feature: destination, action: selection)
  - `budget-selection.html` (feature: budget, action: selection)
  - `itinerary-detail.html` (feature: itinerary, action: detail)
  - `password-reset.html` (feature: password, action: reset)

### 2. CSS/SCSS Files
- **Pattern**: `{component-name}.css` or `_{component-name}.scss`
- **Examples**:
  - `itinerary-detail.css` (component: itinerary detail page)
  - `_navbar.scss` (component: navigation bar)
  - `_value-cards.scss` (component: value cards)
  - `chat-widget.css` (component: chat widget)

### 3. JavaScript Files
- **Pattern**: `{feature-name}.js`
- **Examples**:
  - `animation-controller.js` (feature: animation control)
  - `itinerary-detail.js` (feature: itinerary detail functionality)
  - `chat-widget.js` (feature: chat widget)

### 4. Image Files
- **Pattern**: `{descriptive-name}.{ext}`
- **Examples**:
  - `maasai-mara-hero.jpg`
  - `diani-beach-hero.jpg`
  - `amboseli-elephants-hero.jpg`

## Migration Summary

### Files Renamed ✅
1. **Templates**:
   - `budget_selection.html` → `budget-selection.html`
   - `destination_selection.html` → `destination-selection.html`
   - `duration_selection.html` → `duration-selection.html`
   - `interests_selection.html` → `interests-selection.html`
   - `itinerary_detail.html` → `itinerary-detail.html`
   - `itinerary_detail_new.html` → `itinerary-detail-new.html`
   - `itinerary_generation.html` → `itinerary-generation.html`
   - `landing_v2.html` → `landing-v2.html`
   - `static_page.html` → `static-page.html`
   - `travel_group_selection.html` → `travel-group-selection.html`
   - `auth_nav.html` → `auth-nav.html`
   - `cookie_consent.html` → `cookie-consent.html`
   - `destination_card.html` → `destination-card.html`

2. **CSS Files**:
   - `itinerary_detail.css` → `itinerary-detail.css`
   - `safarismart-main.css` → `main-theme.css`

3. **JavaScript Files**:
   - `itinerary_detail.js` → `itinerary-detail.js`

4. **Demo Files**:
   - `color-palette-demo.html` → `design-system-demo.html`

### References Updated ✅
- All Django view template references
- CSS and JavaScript file references in templates
- Import statements in SCSS files

## Benefits of New Naming Convention

1. **Consistency**: All files follow the same kebab-case pattern
2. **Readability**: Descriptive names make purpose clear
3. **SEO Friendly**: Kebab-case is URL-friendly
4. **Industry Standard**: Follows modern web development conventions
5. **Maintainability**: Easier to find and organize files
6. **Cross-Platform**: Works consistently across all operating systems

## Development Guidelines

### When Creating New Files:
1. Use kebab-case for all file names
2. Be descriptive but concise
3. Include the feature/component name
4. Use appropriate file extensions
5. Follow the established directory structure

### When Referencing Files:
1. Always use the full, correct file name
2. Update all references when renaming files
3. Test that all links and imports work after changes
4. Update documentation when adding new files

## Build Process Integration

The naming conventions work seamlessly with our build process:

```bash
# SCSS compilation
npm run sass:build    # Compiles assets/scss → static/dist/css
npm run sass:watch    # Watches for changes during development

# Quick build scripts
build-css.bat         # Windows batch file for CSS compilation
watch-css.bat         # Windows batch file for development watching
```

## Validation Checklist

When adding or renaming files, ensure:
- [ ] File name uses kebab-case
- [ ] File name is descriptive and clear
- [ ] All references are updated
- [ ] Build process still works
- [ ] No broken links or imports
- [ ] Documentation is updated

---

**Last Updated**: 2025-01-27  
**Version**: 2.0.0  
**Maintainer**: SafariSmart Kenya Development Team