/**
 * FRANKLIN OS DESIGN SYSTEM
 * 
 * A cohesive visual language inspired by:
 * - Benjamin Franklin's 18th-century aesthetics (order, clarity, enlightenment)
 * - Glassmorphism (frosted glass, transparency, depth)
 * - Cyberpunk/Galactic (neon accents, dark backgrounds, electric energy)
 * - VS Code IDE structure (compartmentalized, stackable, resizable)
 */

// ============================================================================
//                         COLOR PALETTE
// ============================================================================

export const COLORS = {
  // PRIMARY COLORS (Electric Blue - Intelligence, Trust)
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c3d66',
  },

  // SECONDARY COLORS (Purple - Creativity, Mystique)
  secondary: {
    50: '#faf5ff',
    100: '#f3e8ff',
    200: '#e9d5ff',
    300: '#d8b4fe',
    400: '#c084fc',
    500: '#a855f7',
    600: '#9333ea',
    700: '#7e22ce',
    800: '#6b21a8',
    900: '#581c87',
  },

  // ACCENT COLORS (Neon Cyan - Energy, Activation)
  accent: {
    50: '#f0fdfa',
    100: '#ccfbf1',
    200: '#99f6e4',
    300: '#5eead4',
    400: '#2dd4bf',
    500: '#14b8a6',
    600: '#0d9488',
    700: '#0f766e',
    800: '#134e4a',
    900: '#0d3331',
  },

  // NEUTRALS (Slate - Depth, Background)
  neutral: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',    // Surface
    900: '#0f172a',    // Background
    950: '#020617',    // Deepest dark
  },

  // SEMANTIC COLORS
  success: '#10b981',   // Green
  warning: '#f59e0b',   // Amber
  error: '#ef4444',     // Red
  info: '#3b82f6',      // Blue

  // GLASS COLORS (with transparency for glassmorphism)
  glass: {
    light: 'rgba(241, 245, 249, 0.1)',      // Slight light
    medium: 'rgba(30, 41, 59, 0.6)',        // Medium dark glass
    dark: 'rgba(15, 23, 42, 0.8)',          // Deep dark glass
    translucent: 'rgba(15, 23, 42, 0.5)',   // Highly transparent
  },

  // GLOW COLORS (for perimeter lighting)
  glow: {
    blue: 'rgba(59, 130, 246, 0.3)',        // Blue glow
    purple: 'rgba(168, 85, 247, 0.3)',      // Purple glow
    cyan: 'rgba(45, 212, 191, 0.3)',        // Cyan glow
  },
};

// ============================================================================
//                       SPACING SYSTEM
// ============================================================================

export const SPACING = {
  xs: '0.25rem',  // 4px
  sm: '0.5rem',   // 8px
  md: '1rem',     // 16px
  lg: '1.5rem',   // 24px
  xl: '2rem',     // 32px
  xxl: '3rem',    // 48px
};

// ============================================================================
//                       TYPOGRAPHY
// ============================================================================

export const TYPOGRAPHY = {
  fontFamily: {
    mono: '"JetBrains Mono", "Courier New", monospace',
    sans: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    serif: '"Georgetown", Georgia, serif',
  },
  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px
    lg: '1.125rem',     // 18px
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px
    '3xl': '1.875rem',  // 30px
  },
  fontWeight: {
    light: 300,
    normal: 400,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  },
};

// ============================================================================
//                    GLASSMORPHISM EFFECTS
// ============================================================================

export const GLASSMORPHISM = {
  // Base glass panel - frosted background with blur
  basePanel: {
    backdropFilter: 'blur(10px)',
    backgroundColor: COLORS.glass.medium,
    border: `1px solid ${COLORS.glass.light}`,
    boxShadow: `
      inset 0 1px 2px rgba(255, 255, 255, 0.05),
      0 8px 32px rgba(0, 0, 0, 0.3)
    `,
  },

  // Panel with blue perimeter glow
  glowPanelBlue: {
    backdropFilter: 'blur(10px)',
    backgroundColor: COLORS.glass.medium,
    border: `1px solid ${COLORS.glow.blue}`,
    boxShadow: `
      inset 0 1px 2px rgba(255, 255, 255, 0.05),
      0 0 20px ${COLORS.glow.blue},
      inset -1px -1px 0 rgba(0, 0, 0, 0.2)
    `,
  },

  // Panel with purple perimeter glow
  glowPanelPurple: {
    backdropFilter: 'blur(10px)',
    backgroundColor: COLORS.glass.medium,
    border: `1px solid ${COLORS.glow.purple}`,
    boxShadow: `
      inset 0 1px 2px rgba(255, 255, 255, 0.05),
      0 0 20px ${COLORS.glow.purple},
      inset -1px -1px 0 rgba(0, 0, 0, 0.2)
    `,
  },

  // Panel with cyan perimeter glow
  glowPanelCyan: {
    backdropFilter: 'blur(10px)',
    backgroundColor: COLORS.glass.medium,
    border: `1px solid ${COLORS.glow.cyan}`,
    boxShadow: `
      inset 0 1px 2px rgba(255, 255, 255, 0.05),
      0 0 20px ${COLORS.glow.cyan},
      inset -1px -1px 0 rgba(0, 0, 0, 0.2)
    `,
  },

  // Active button state - glowing
  buttonActive: {
    backgroundColor: 'rgba(59, 130, 246, 0.15)',
    boxShadow: `
      inset 0 1px 3px rgba(255, 255, 255, 0.1),
      0 0 15px rgba(59, 130, 246, 0.4)
    `,
  },

  // Hover state
  buttonHover: {
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Floating element (Ghost Franklin)
  floating: {
    backdropFilter: 'blur(20px)',
    backgroundColor: COLORS.glass.dark,
    border: `1px solid ${COLORS.primary[500]}`,
    boxShadow: `
      0 0 40px rgba(59, 130, 246, 0.2),
      0 8px 32px rgba(0, 0, 0, 0.4),
      inset 0 1px 2px rgba(255, 255, 255, 0.1)
    `,
  },
};

// ============================================================================
//                       ANIMATIONS
// ============================================================================

export const ANIMATIONS = {
  // Smooth panel expansion/collapse
  collapse: {
    duration: '300ms',
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Glow pulse (for active states)
  glowPulse: `
    @keyframes glow-pulse {
      0%, 100% {
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
      }
      50% {
        box-shadow: 0 0 40px rgba(59, 130, 246, 0.6);
      }
    }
  `,

  // Fade in
  fadeIn: {
    duration: '200ms',
    easing: 'ease-in',
  },

  // Slide in
  slideIn: {
    duration: '300ms',
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
};

// ============================================================================
//                    CONTEXT WINDOW PANEL STYLES
// ============================================================================

/**
 * The IDE mirrors Franklin's cognitive model:
 * - Context windows are horizontal "boxes" (like how I organize info)
 * - Each box is collapsible to hide/show detail
 * - Related boxes can be stacked vertically
 * - Color indicates box type (connector, code, output, etc.)
 */

export const CONTEXT_WINDOW_TYPES = {
  // Input/Agent Connector (Purple - Creativity)
  connector: {
    accentColor: COLORS.secondary[500],
    backgroundColor: COLORS.glass.medium,
    borderColor: COLORS.secondary[600],
    glowColor: 'rgba(168, 85, 247, 0.3)',
  },

  // Code/Editor (Blue - Intelligence)
  code: {
    accentColor: COLORS.primary[500],
    backgroundColor: COLORS.glass.medium,
    borderColor: COLORS.primary[600],
    glowColor: 'rgba(59, 130, 246, 0.3)',
  },

  // Output/Terminal (Cyan - Energy)
  output: {
    accentColor: COLORS.accent[500],
    backgroundColor: COLORS.glass.medium,
    borderColor: COLORS.accent[600],
    glowColor: 'rgba(45, 212, 191, 0.3)',
  },

  // Information/Context (Neutral - Clarity)
  info: {
    accentColor: COLORS.neutral[400],
    backgroundColor: COLORS.glass.medium,
    borderColor: COLORS.neutral[600],
    glowColor: 'rgba(148, 163, 184, 0.2)',
  },

  // Status/Quality Gate (Green/Amber - Validation)
  status: {
    accentColor: COLORS.success,
    backgroundColor: COLORS.glass.medium,
    borderColor: COLORS.success,
    glowColor: 'rgba(16, 185, 129, 0.2)',
  },
};

// ============================================================================
//                          BREAKPOINTS
// ============================================================================

export const BREAKPOINTS = {
  xs: '320px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

// ============================================================================
//                        Z-INDEX LAYERS
// ============================================================================

export const Z_INDEX = {
  background: 0,
  panels: 10,
  modal: 40,
  popover: 50,
  tooltip: 60,
  ghostFranklin: 100,  // Always on top, can be interacted with
};

// ============================================================================
//                      COMPONENT DEFAULTS
// ============================================================================

export const COMPONENT_DEFAULTS = {
  // Panel border radius
  borderRadius: {
    sm: '0.375rem',   // 6px
    md: '0.5rem',     // 8px
    lg: '0.75rem',    // 12px
  },

  // Panel sizing
  panelMinSize: 15,   // 15% of viewport
  panelDefaultSize: 50,
  panelMaxSize: 80,

  // Sidebar
  sidebarWidth: 280,
  sidebarCollapsedWidth: 60,

  // Bottom panel
  bottomPanelHeight: 280,
  bottomPanelMinHeight: 100,

  // Right panel
  rightPanelWidth: 320,
  rightPanelMinWidth: 250,
};

export default {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  GLASSMORPHISM,
  ANIMATIONS,
  CONTEXT_WINDOW_TYPES,
  BREAKPOINTS,
  Z_INDEX,
  COMPONENT_DEFAULTS,
};
