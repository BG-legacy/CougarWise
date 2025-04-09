# CougarWise UI Theme Guide

## Brand Colors

### Primary Colors
- **CSU Maroon**: `#800000`
  - Use for primary buttons, headers, and important UI elements
  - Dark variant: `#600000`
  - Light variant: `#A05050`

- **Gold**: `#FFD700`
  - Use for accents, highlights, and call-to-action elements
  - Dark variant: `#DAA520`
  - Light variant: `#FFEB99`

### Neutral Colors
- **Dark Gray**: `#333333`
  - Use for text and icons
- **Medium Gray**: `#757575`
  - Use for secondary text and disabled states
- **Light Gray**: `#E0E0E0`
  - Use for borders and dividers
- **Off White**: `#F5F5F5`
  - Use for backgrounds
- **White**: `#FFFFFF`
  - Use for card backgrounds and content areas

### Semantic Colors
- **Success**: `#4CAF50`
  - Use for positive feedback, completed actions
- **Warning**: `#FFC107`
  - Use for alerts, warnings, and caution states
- **Error**: `#F44336`
  - Use for errors and critical actions
- **Info**: `#2196F3`
  - Use for informational messages and notifications

## Typography

### Font Family
- Primary font: `'Roboto', 'Helvetica', 'Arial', sans-serif`

### Font Weights
- Light: 300
- Regular: 400
- Medium: 500
- Bold: 700

### Type Scale
- **H1**: 32px / 40px line height / Bold
  - Use for page titles
- **H2**: 24px / 32px line height / Bold
  - Use for section headers
- **H3**: 20px / 28px line height / Medium
  - Use for card titles and subsections
- **Subtitle**: 16px / 24px line height / Medium
  - Use for subtitles and emphasized text
- **Body**: 14px / 20px line height / Regular
  - Use for general content
- **Small**: 12px / 16px line height / Regular
  - Use for captions, labels, and helper text
- **Button**: 14px / 16px line height / Medium
  - Use for button text (ALL CAPS for primary buttons)

## Component Styles

### Buttons

#### Primary Button
- Background: CSU Maroon (`#800000`)
- Text: White (`#FFFFFF`)
- Padding: 12px 24px
- Border Radius: 4px
- Text Transform: Uppercase
- Font Weight: Medium
- Hover state: Darken background by 10%
- Active state: Darken background by 15%
- Disabled state: 50% opacity

#### Secondary Button
- Background: Transparent
- Text: CSU Maroon (`#800000`)
- Border: 1px solid CSU Maroon (`#800000`)
- Padding: 12px 24px
- Border Radius: 4px
- Text Transform: Uppercase
- Font Weight: Medium
- Hover state: Background 10% CSU Maroon
- Active state: Background 15% CSU Maroon
- Disabled state: 50% opacity

#### Text Button
- Background: Transparent
- Text: CSU Maroon (`#800000`)
- Padding: 8px 16px
- Border Radius: 4px
- Font Weight: Medium
- Hover state: Background 5% CSU Maroon
- Active state: Background 10% CSU Maroon
- Disabled state: 50% opacity

### Cards
- Background: White (`#FFFFFF`)
- Border Radius: 8px
- Padding: 16px
- Box Shadow: 0px 2px 8px rgba(0, 0, 0, 0.1)
- Header Padding: 16px
- Content Padding: 16px
- Footer Padding: 12px 16px
- Divider: 1px solid Light Gray (`#E0E0E0`)

### Form Elements

#### Text Fields
- Height: 40px
- Border: 1px solid Light Gray (`#E0E0E0`)
- Border Radius: 4px
- Background: White (`#FFFFFF`)
- Text: Dark Gray (`#333333`)
- Padding: 8px 12px
- Label: Medium Gray (`#757575`), 12px, above field
- Focus state: Border CSU Maroon (`#800000`), no background change
- Error state: Border Error (`#F44336`)
- Placeholder: Medium Gray (`#757575`), italic

#### Checkboxes & Radio Buttons
- Size: 18px × 18px
- Border: 1px solid Light Gray (`#E0E0E0`)
- Selected state: CSU Maroon (`#800000`) fill
- Focus state: Gold (`#FFD700`) outline

#### Dropdowns
- Same styling as text fields
- Dropdown icon: Medium Gray (`#757575`)
- Options: White background, hover state 5% Gray

### Data Visualization

#### Charts
- Primary data: CSU Maroon (`#800000`)
- Secondary data: Gold (`#FFD700`)
- Tertiary data: Use a complementary color palette:
  - `#1E88E5` (Blue)
  - `#43A047` (Green)
  - `#7E57C2` (Purple)
  - `#E53935` (Red)
  - `#FFA000` (Amber)
- Axis lines: Light Gray (`#E0E0E0`)
- Labels: Medium Gray (`#757575`)
- Tooltips: Dark Gray background (`#333333`), White text

#### Progress Bars
- Track: Light Gray (`#E0E0E0`)
- Indicator: CSU Maroon (`#800000`)
- Low progress indicator (< 30%): Error (`#F44336`)
- Success indicator (100%): Success (`#4CAF50`)

### Navigation

#### Top Navigation Bar
- Background: White (`#FFFFFF`)
- Text: Dark Gray (`#333333`)
- Active item: CSU Maroon (`#800000`)
- Hover state: 5% Gray
- Box Shadow: 0px 2px 4px rgba(0, 0, 0, 0.1)

#### Side Navigation
- Background: CSU Maroon (`#800000`)
- Text: White (`#FFFFFF`)
- Active item: Gold (`#FFD700`) left border and tint
- Hover state: 10% lighter background
- Icon: 20px, centered with text

### Spacing System
- 4px base unit
- Extra Small: 4px
- Small: 8px
- Medium: 16px
- Large: 24px
- Extra Large: 32px
- 2X Large: 48px
- 3X Large: 64px

## Responsive Breakpoints
- Small: 0-599px (mobile)
- Medium: 600-959px (tablet)
- Large: 960-1279px (desktop)
- Extra Large: 1280px+ (large desktop)

## Accessibility

### Contrast Ratios
- Regular text: Maintain at least 4.5:1 contrast ratio
- Large text: Maintain at least 3:1 contrast ratio
- UI components: Maintain at least 3:1 contrast ratio

### Focus States
- All interactive elements must have a visible focus state
- Focus outline: 2px solid Gold (`#FFD700`)
- Ensure focus order follows a logical sequence

### Text Sizing
- Allow text to be resized up to 200% without loss of content
- Avoid using absolute units for text (use rem or em)

## Animation and Transitions

### Timing
- Fast (UI feedback): 100-150ms
- Medium (UI transitions): 200-300ms
- Slow (emphasis): 400-500ms

### Easing
- Standard: cubic-bezier(0.4, 0.0, 0.2, 1)
- Deceleration: cubic-bezier(0.0, 0.0, 0.2, 1)
- Acceleration: cubic-bezier(0.4, 0.0, 1, 1)

### Hover/Active States
- Scale: Transform scale 1.02-1.05 for clickable items
- Color: Lighten/darken by 10-15%
- Shadow: Increase elevation slightly

## Icons
- Use Material Icons for consistency
- Primary size: 24px × 24px
- Small size: 18px × 18px
- Large size: 36px × 36px
- Color should match text color of context
- Active/selected icons: CSU Maroon (`#800000`) or Gold (`#FFD700`) 