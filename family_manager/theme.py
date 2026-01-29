"""
Modern Theme System for Family Household Manager
Provides unified colors, typography, spacing, and component styling
"""

from typing import Dict, Any

class AppTheme:
    """Unified design system for the application"""

    # === COLOR PALETTE ===
    # Primary Brand Colors
    PRIMARY = "#6366F1"          # Indigo-500
    PRIMARY_LIGHT = "#818CF8"    # Indigo-400
    PRIMARY_DARK = "#4F46E5"     # Indigo-600
    PRIMARY_VARIANT = "#312E81"  # Indigo-900

    # Secondary Colors
    SECONDARY = "#EC4899"        # Pink-500
    SECONDARY_LIGHT = "#F472B6"  # Pink-400
    SECONDARY_DARK = "#DB2777"   # Pink-600

    # Semantic Colors
    SUCCESS = "#10B981"          # Emerald-500
    SUCCESS_LIGHT = "#34D399"    # Emerald-400
    SUCCESS_DARK = "#059669"     # Emerald-600

    WARNING = "#F59E0B"          # Amber-500
    WARNING_LIGHT = "#FCD34D"    # Amber-300
    WARNING_DARK = "#D97706"     # Amber-600

    ERROR = "#EF4444"            # Red-500
    ERROR_LIGHT = "#F87171"      # Red-400
    ERROR_DARK = "#DC2626"       # Red-600

    INFO = "#3B82F6"             # Blue-500
    INFO_LIGHT = "#60A5FA"       # Blue-400
    INFO_DARK = "#2563EB"        # Blue-600

    # === NEUTRAL COLORS ===
    # Background Layers
    BACKGROUND = "#0F172A"       # Slate-900 (Darkest)
    SURFACE = "#1E293B"          # Slate-800 (Cards, surfaces)
    CARD = "#334155"             # Slate-700 (Elevated surfaces)
    ELEVATED = "#475569"         # Slate-600 (Dialogs, popups)
    OVERLAY = "#64748B"          # Slate-500 (Active states)

    # Text Colors
    TEXT_PRIMARY = "#F8FAFC"     # Slate-50 (Main text)
    TEXT_SECONDARY = "#CBD5E1"   # Slate-300 (Secondary text)
    TEXT_DISABLED = "#94A3B8"    # Slate-400 (Disabled text)
    TEXT_HINT = "#64748B"        # Slate-500 (Hints, placeholders)

    # Border & Dividers
    BORDER = "#475569"           # Slate-600
    BORDER_LIGHT = "#64748B"     # Slate-500
    DIVIDER = "#334155"          # Slate-700

    # === TYPOGRAPHY ===
    FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    FONT_FAMILY_MONO = "'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, 'Cascadia Code', monospace"

    FONT_SIZES = {
        'xs': '12px',
        'sm': '14px',
        'base': '16px',
        'lg': '18px',
        'xl': '20px',
        '2xl': '24px',
        '3xl': '30px',
        '4xl': '36px',
        '5xl': '48px'
    }

    FONT_WEIGHTS = {
        'normal': '400',
        'medium': '500',
        'semibold': '600',
        'bold': '700',
        'extrabold': '800'
    }

    LINE_HEIGHTS = {
        'tight': '1.25',
        'normal': '1.5',
        'relaxed': '1.625',
        'loose': '2'
    }

    # === SPACING SYSTEM ===
    SPACING = {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px'
    }

    # === BORDER RADIUS ===
    RADIUS = {
        'none': '0px',
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '24px',
        'full': '9999px'
    }

    # === SHADOWS ===
    SHADOWS = {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
    }

    # === Z-INDEX LAYERS ===
    Z_INDEX = {
        'base': '0',
        'dropdown': '1000',
        'sticky': '1020',
        'fixed': '1030',
        'modal': '1040',
        'popover': '1050',
        'tooltip': '1060',
        'toast': '1070'
    }

    @classmethod
    def get_color(cls, color_name: str, variant: str = None) -> str:
        """Get color with optional variant (light/dark)"""
        if variant:
            attr_name = f"{color_name.upper()}_{variant.upper()}"
        else:
            attr_name = color_name.upper()

        return getattr(cls, attr_name, cls.TEXT_PRIMARY)

    @classmethod
    def get_spacing(cls, size: str) -> str:
        """Get spacing value"""
        return cls.SPACING.get(size, cls.SPACING['md'])

    @classmethod
    def get_font_size(cls, size: str) -> str:
        """Get font size value"""
        return cls.FONT_SIZES.get(size, cls.FONT_SIZES['base'])

    @classmethod
    def get_radius(cls, size: str) -> str:
        """Get border radius value"""
        return cls.RADIUS.get(size, cls.RADIUS['md'])

# === GLOBAL STYLESHEET ===
MAIN_STYLESHEET = f"""
    /* ===== BASE APPLICATION STYLES ===== */
    QMainWindow {{
        background-color: {AppTheme.BACKGROUND};
        color: {AppTheme.TEXT_PRIMARY};
        font-family: {AppTheme.FONT_FAMILY};
        font-size: {AppTheme.FONT_SIZES['base']};
        selection-background-color: {AppTheme.PRIMARY};
    }}

    QWidget {{
        color: {AppTheme.TEXT_PRIMARY};
        font-family: {AppTheme.FONT_FAMILY};
    }}

    /* ===== MODERN TAB SYSTEM ===== */
    QTabWidget::pane {{
        border: 1px solid {AppTheme.BORDER};
        background-color: {AppTheme.SURFACE};
        border-radius: {AppTheme.RADIUS['lg']};
        top: -1px;
    }}

    QTabBar::tab {{
        background-color: {AppTheme.CARD};
        color: {AppTheme.TEXT_SECONDARY};
        padding: {AppTheme.SPACING['md']} {AppTheme.SPACING['lg']};
        margin-right: 2px;
        border: 1px solid {AppTheme.BORDER};
        border-bottom: none;
        border-radius: {AppTheme.RADIUS['md']} {AppTheme.RADIUS['md']} 0 0;
        font-weight: {AppTheme.FONT_WEIGHTS['medium']};
        min-width: 120px;
    }}

    QTabBar::tab:selected {{
        background-color: {AppTheme.SURFACE};
        color: {AppTheme.TEXT_PRIMARY};
        font-weight: {AppTheme.FONT_WEIGHTS['semibold']};
        border-bottom: 3px solid {AppTheme.PRIMARY};
    }}

    QTabBar::tab:hover {{
        background-color: {AppTheme.OVERLAY};
        color: {AppTheme.TEXT_PRIMARY};
    }}

    QTabBar::tab:first {{
        margin-left: 0px;
    }}

    /* ===== MODERN BUTTONS ===== */
    QPushButton {{
        background-color: {AppTheme.PRIMARY};
        color: white;
        border: none;
        padding: {AppTheme.SPACING['sm']} {AppTheme.SPACING['lg']};
        border-radius: {AppTheme.RADIUS['md']};
        font-weight: {AppTheme.FONT_WEIGHTS['medium']};
        font-size: {AppTheme.FONT_SIZES['sm']};
        min-height: 36px;
    }}

    QPushButton:hover {{
        background-color: {AppTheme.PRIMARY_LIGHT};
    }}

    QPushButton:pressed {{
        background-color: {AppTheme.PRIMARY_DARK};
    }}

    QPushButton:disabled {{
        background-color: {AppTheme.BORDER};
        color: {AppTheme.TEXT_DISABLED};
    }}

    /* Secondary Buttons */
    QPushButton[class="secondary"] {{
        background-color: {AppTheme.SECONDARY};
    }}

    QPushButton[class="secondary"]:hover {{
        background-color: {AppTheme.SECONDARY_LIGHT};
    }}

    QPushButton[class="secondary"]:pressed {{
        background-color: {AppTheme.SECONDARY_DARK};
    }}

    /* Success Buttons */
    QPushButton[class="success"] {{
        background-color: {AppTheme.SUCCESS};
    }}

    QPushButton[class="success"]:hover {{
        background-color: {AppTheme.SUCCESS_LIGHT};
    }}

    /* ===== MODERN CARDS ===== */
    QWidget[class="card"] {{
        background-color: {AppTheme.CARD};
        border: 1px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['lg']};
        padding: {AppTheme.SPACING['lg']};
        margin: {AppTheme.SPACING['sm']};
    }}

    QLabel[class="card-title"] {{
        color: {AppTheme.TEXT_PRIMARY};
        font-size: {AppTheme.FONT_SIZES['lg']};
        font-weight: {AppTheme.FONT_WEIGHTS['semibold']};
        margin-bottom: {AppTheme.SPACING['md']};
    }}

    QLabel[class="card-subtitle"] {{
        color: {AppTheme.TEXT_SECONDARY};
        font-size: {AppTheme.FONT_SIZES['sm']};
        margin-bottom: {AppTheme.SPACING['sm']};
    }}

    /* ===== FORM ELEMENTS ===== */
    QLineEdit {{
        background-color: {AppTheme.SURFACE};
        color: {AppTheme.TEXT_PRIMARY};
        border: 2px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['md']};
        padding: {AppTheme.SPACING['sm']} {AppTheme.SPACING['md']};
        font-size: {AppTheme.FONT_SIZES['base']};
        min-height: 40px;
    }}

    QLineEdit:focus {{
        border-color: {AppTheme.PRIMARY};
        outline: none;
    }}

    QLineEdit::placeholder {{
        color: {AppTheme.TEXT_HINT};
    }}

    QComboBox {{
        background-color: {AppTheme.SURFACE};
        color: {AppTheme.TEXT_PRIMARY};
        border: 2px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['md']};
        padding: {AppTheme.SPACING['sm']};
        min-height: 40px;
    }}

    QComboBox:focus {{
        border-color: {AppTheme.PRIMARY};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid {AppTheme.TEXT_SECONDARY};
        margin-right: 8px;
    }}

    /* ===== TABLES ===== */
    QTableWidget {{
        background-color: {AppTheme.SURFACE};
        border: 1px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['lg']};
        gridline-color: {AppTheme.DIVIDER};
        selection-background-color: {AppTheme.PRIMARY}33;
        alternate-background-color: {AppTheme.CARD};
    }}

    QTableWidget::item {{
        padding: {AppTheme.SPACING['md']};
        border-bottom: 1px solid {AppTheme.DIVIDER};
        color: {AppTheme.TEXT_PRIMARY};
        font-size: {AppTheme.FONT_SIZES['sm']};
    }}

    QTableWidget::item:selected {{
        background-color: {AppTheme.PRIMARY}33;
    }}

    QHeaderView::section {{
        background-color: {AppTheme.CARD};
        color: {AppTheme.TEXT_PRIMARY};
        padding: {AppTheme.SPACING['md']};
        border: none;
        border-right: 1px solid {AppTheme.DIVIDER};
        font-weight: {AppTheme.FONT_WEIGHTS['semibold']};
        font-size: {AppTheme.FONT_SIZES['sm']};
    }}

    /* ===== TREE WIDGETS ===== */
    QTreeWidget {{
        background-color: {AppTheme.SURFACE};
        border: 1px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['lg']};
        color: {AppTheme.TEXT_PRIMARY};
        font-size: {AppTheme.FONT_SIZES['sm']};
        alternate-background-color: {AppTheme.CARD};
        selection-background-color: {AppTheme.PRIMARY}33;
    }}

    QTreeWidget::item {{
        padding: {AppTheme.SPACING['sm']};
        border-bottom: 1px solid {AppTheme.DIVIDER};
        color: {AppTheme.TEXT_PRIMARY};
    }}

    QTreeWidget::item:selected {{
        background-color: {AppTheme.PRIMARY}33;
    }}

    /* ===== SCROLL BARS ===== */
    QScrollBar:vertical {{
        background-color: {AppTheme.SURFACE};
        width: 12px;
        border-radius: {AppTheme.RADIUS['md']};
        margin: 2px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['sm']};
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {AppTheme.OVERLAY};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}

    /* ===== PROGRESS BARS ===== */
    QProgressBar {{
        border: 2px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['md']};
        text-align: center;
        font-weight: {AppTheme.FONT_WEIGHTS['medium']};
        color: {AppTheme.TEXT_PRIMARY};
    }}

    QProgressBar::chunk {{
        background-color: {AppTheme.PRIMARY};
        border-radius: {AppTheme.RADIUS['sm']};
    }}

    /* ===== STATUS BAR ===== */
    QStatusBar {{
        background-color: {AppTheme.CARD};
        color: {AppTheme.TEXT_SECONDARY};
        border-top: 1px solid {AppTheme.BORDER};
        font-size: {AppTheme.FONT_SIZES['sm']};
    }}

    /* ===== GROUP BOXES ===== */
    QGroupBox {{
        font-weight: {AppTheme.FONT_WEIGHTS['semibold']};
        border: 2px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['lg']};
        margin-top: 1ex;
        padding-top: {AppTheme.SPACING['md']};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: {AppTheme.SPACING['md']};
        padding: 0 {AppTheme.SPACING['md']} 0 {AppTheme.SPACING['md']};
        color: {AppTheme.TEXT_PRIMARY};
        font-size: {AppTheme.FONT_SIZES['lg']};
        font-weight: {AppTheme.FONT_WEIGHTS['semibold']};
    }}

    /* ===== DIALOGS ===== */
    QDialog {{
        background-color: {AppTheme.SURFACE};
        color: {AppTheme.TEXT_PRIMARY};
        border-radius: {AppTheme.RADIUS['xl']};
    }}

    /* ===== MENUS ===== */
    QMenu {{
        background-color: {AppTheme.CARD};
        color: {AppTheme.TEXT_PRIMARY};
        border: 1px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['md']};
        padding: {AppTheme.SPACING['sm']};
    }}

    QMenu::item {{
        padding: {AppTheme.SPACING['sm']} {AppTheme.SPACING['lg']};
        border-radius: {AppTheme.RADIUS['sm']};
        color: {AppTheme.TEXT_PRIMARY};
    }}

    QMenu::item:selected {{
        background-color: {AppTheme.PRIMARY};
        color: white;
    }}

    QMenu::separator {{
        height: 1px;
        background-color: {AppTheme.DIVIDER};
        margin: {AppTheme.SPACING['xs']} 0;
    }}

    /* ===== TOOLTIPS ===== */
    QToolTip {{
        background-color: {AppTheme.ELEVATED};
        color: {AppTheme.TEXT_PRIMARY};
        border: 1px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS['md']};
        padding: {AppTheme.SPACING['sm']};
        font-size: {AppTheme.FONT_SIZES['sm']};
    }}
"""