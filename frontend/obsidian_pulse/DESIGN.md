---
name: Obsidian Pulse
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#cbc3d7'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#958ea0'
  outline-variant: '#494454'
  surface-tint: '#d0bcff'
  primary: '#d0bcff'
  on-primary: '#3c0091'
  primary-container: '#a078ff'
  on-primary-container: '#340080'
  inverse-primary: '#6d3bd7'
  secondary: '#c0c1ff'
  on-secondary: '#1000a9'
  secondary-container: '#3131c0'
  on-secondary-container: '#b0b2ff'
  tertiary: '#dbb8ff'
  on-tertiary: '#3f2160'
  tertiary-container: '#a482c8'
  on-tertiary-container: '#381959'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e9ddff'
  primary-fixed-dim: '#d0bcff'
  on-primary-fixed: '#23005c'
  on-primary-fixed-variant: '#5516be'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#efdbff'
  tertiary-fixed-dim: '#dbb8ff'
  on-tertiary-fixed: '#29074a'
  on-tertiary-fixed-variant: '#573878'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-lg:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  display-lg-mobile:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.02em
  body-base:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: 0em
  label-caps:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  2xl: 64px
  container-max: 1280px
  gutter: 24px
---

## Brand & Style

The brand personality is high-performance, analytical, and visionary. It targets product leaders and developers who value data density balanced with aesthetic clarity. The design system leverages a **Glassmorphic** style layered over a **Minimalist** dark foundation, creating a "command center" atmosphere.

The emotional response should be one of "effortless intelligence." By utilizing deep space-like backgrounds and vibrant, neon-flecked accents, the UI evokes a sense of cutting-edge technology and premium exclusivity. Surfaces feel like physical sheets of dark glass floating in a structured vacuum, punctuated by precise, high-contrast typography.

## Colors

The palette is anchored in a deep navy neutral (`#0F172A`), providing a low-light environment where vibrant purples and indigos can thrive. 

- **Primary & Secondary:** A duo of Electric Purple and Indigo used primarily for calls-to-action, active states, and data visualizations.
- **Surface Strategy:** Backgrounds utilize a solid deep navy. Interactive surfaces use a translucent navy with a 70% opacity, allowing background gradients or content to subtly bleed through.
- **Accents:** Use the tertiary lavender for subtle highlights and "hover glow" effects to guide the eye toward interactive nodes.

## Typography

This design system uses a dual-sans-serif approach to balance technical precision with extreme legibility. 

- **Geist** is reserved for headlines, labels, and UI elements requiring a "developer-centric" and geometric feel. Large displays use tight letter-spacing to appear impactful and architectural.
- **Inter** handles all body copy and prose-heavy reports. Its humanist qualities ensure long-form insights remain readable and approachable.
- **Hierarchy:** Use `label-caps` for secondary metadata and category tags to create a clear structural distinction from body text.

## Layout & Spacing

The layout follows a **Fluid Grid** model with a maximum container width of 1280px for desktop. It utilizes a 12-column system where content typically occupies centered 8-column or 10-column "report" containers to maintain focus.

- **Mobile:** Margins shrink to 16px. Typography scales down specifically for the Display-LG role.
- **Rhythm:** An 8px linear scale drives all padding and margins. Use `xl` (40px) for section vertical spacing and `md` (16px) for internal component padding.
- **Safe Areas:** Cards and glass containers must maintain internal padding of at least `lg` (24px) to ensure content does not feel cramped against the frosted borders.

## Elevation & Depth

Depth is achieved through **Glassmorphism** and selective illumination rather than traditional shadows.

1.  **The Floor (Level 0):** Solid `#0F172A`.
2.  **Surface (Level 1):** `glass_surface` with a 1px `glass_border` (top/left tinted slightly brighter than bottom/right to simulate a top-down light source).
3.  **Backdrop Blur:** All glass surfaces must apply a `backdrop-filter: blur(12px)`.
4.  **The Glow:** Active components do not use shadows; instead, they use an outer glow (box-shadow) with a high blur radius (20px+) and low opacity (20%) using the primary color to simulate a neon light emission.

## Shapes

The design system uses a **Rounded** (0.5rem) baseline to soften the technical nature of the typography and dark colors. 

- **Cards/Containers:** Use `rounded-lg` (1rem) to create a distinct frame for insights.
- **Interactive Elements:** Buttons and input fields use the base 0.5rem.
- **Status Pills:** Use the `rounded-xl` (1.5rem) or full pill-shape to distinguish them from functional buttons.

## Components

### Buttons
Primary buttons use the `accent_gradient` with white text. On hover, apply a `primary_color` glow. Secondary buttons use a transparent background with a 1px `glass_border` and white text.

### Glassmorphic Inputs
Fields should have a `glass_surface` background and a subtle `glass_border`. On focus, the border transitions to the primary purple, and the backdrop blur increases slightly.

### Premium Metric Cards
Cards feature a large `headline-md` value. The background is a translucent navy. Top-right corners may feature a subtle, low-opacity radial gradient of the primary color to add visual interest.

### Document Report Container
The central "Pulse" report is a large glass sheet with 24px padding. It uses `source-serif` (if available) or `inter` with increased line height (1.8) for maximum readability.

### Chips & Tags
Small, pill-shaped elements with a low-opacity background of the primary or secondary color (e.g., 10% opacity) and high-contrast text. Borders should be omitted for tags to keep the UI clean.