"""
Modern UI Components for Family Household Manager
Provides reusable, themed UI components with consistent styling
"""

from PyQt6.QtWidgets import (
    QPushButton, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QGroupBox, QScrollArea, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

try:
    from .theme import AppTheme
except ImportError:
    from theme import AppTheme
except ImportError:
    from theme import AppTheme

class ModernButton(QPushButton):
    """Modern button with hover effects and multiple variants"""

    def __init__(self, text="", variant="primary", size="md", icon=None):
        super().__init__(text)
        self.variant = variant
        self.size = size
        self.icon = icon
        self.setup_button()

    def setup_button(self):
        """Configure button appearance and behavior"""

        # Set size
        size_map = {
            "sm": (32, "12px", AppTheme.SPACING['sm']),
            "md": (40, "14px", AppTheme.SPACING['md']),
            "lg": (48, "16px", AppTheme.SPACING['lg'])
        }
        height, font_size, padding = size_map.get(self.size, size_map["md"])
        self.setMinimumHeight(height)

        # Set colors based on variant
        color_map = {
            "primary": (AppTheme.PRIMARY, AppTheme.PRIMARY_LIGHT, AppTheme.PRIMARY_DARK),
            "secondary": (AppTheme.SECONDARY, AppTheme.SECONDARY_LIGHT, AppTheme.SECONDARY_DARK),
            "success": (AppTheme.SUCCESS, AppTheme.SUCCESS_LIGHT, AppTheme.SUCCESS_DARK),
            "warning": (AppTheme.WARNING, AppTheme.WARNING_LIGHT, AppTheme.WARNING_DARK),
            "error": (AppTheme.ERROR, AppTheme.ERROR_LIGHT, AppTheme.ERROR_DARK),
            "info": (AppTheme.INFO, AppTheme.INFO_LIGHT, AppTheme.INFO_DARK)
        }

        base_color, hover_color, pressed_color = color_map.get(self.variant, color_map["primary"])

        # Set icon if provided
        if self.icon:
            self.setIcon(QIcon(self.icon))
            self.setIconSize(QSize(16, 16))

        # Apply stylesheet
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {base_color};
                color: white;
                border: none;
                padding: {AppTheme.SPACING['xs']} {padding};
                border-radius: {AppTheme.RADIUS['md']};
                font-weight: {AppTheme.FONT_WEIGHTS['medium']};
                font-size: {font_size};
                font-family: {AppTheme.FONT_FAMILY};
                text-align: center;
            }}

            QPushButton:hover {{
                background-color: {hover_color};
                transform: translateY(-1px);
            }}

            QPushButton:pressed {{
                background-color: {pressed_color};
                transform: translateY(0px);
            }}

            QPushButton:disabled {{
                background-color: {AppTheme.BORDER};
                color: {AppTheme.TEXT_DISABLED};
            }}
        """)

        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class ModernCard(QWidget):
    """Modern card component with shadow and rounded corners"""

    def __init__(self, title=None, subtitle=None, content=None, icon=None):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.content = content
        self.icon = icon
        self.setup_card()

    def setup_card(self):
        """Configure card layout and styling"""

        # Set object name for CSS targeting
        self.setObjectName("modern-card")

        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header section (icon + title/subtitle)
        if self.title or self.icon:
            header_layout = QHBoxLayout()
            header_layout.setSpacing(12)

            # Icon
            if self.icon:
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(self.icon).pixmap(24, 24))
                header_layout.addWidget(icon_label)

            # Title and subtitle
            text_layout = QVBoxLayout()
            text_layout.setSpacing(4)

            if self.title:
                title_label = QLabel(self.title)
                title_label.setObjectName("card-title")
                title_font = QFont(AppTheme.FONT_FAMILY)
                title_font.setPixelSize(18)
                title_font.setWeight(QFont.Weight.DemiBold)
                title_label.setFont(title_font)
                title_label.setStyleSheet(f"color: {AppTheme.TEXT_PRIMARY};")
                text_layout.addWidget(title_label)

            if self.subtitle:
                subtitle_label = QLabel(self.subtitle)
                subtitle_label.setObjectName("card-subtitle")
                subtitle_font = QFont(AppTheme.FONT_FAMILY)
                subtitle_font.setPixelSize(14)
                subtitle_label.setFont(subtitle_font)
                subtitle_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY};")
                text_layout.addWidget(subtitle_label)

            header_layout.addLayout(text_layout)
            header_layout.addStretch()
            layout.addLayout(header_layout)

        # Content section
        if self.content:
            if isinstance(self.content, str):
                content_label = QLabel(self.content)
                content_font = QFont(AppTheme.FONT_FAMILY)
                content_font.setPixelSize(14)
                content_label.setFont(content_font)
                content_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY};")
                content_label.setWordWrap(True)
                layout.addWidget(content_label)
            else:
                layout.addWidget(self.content)

        self.setLayout(layout)

        # Apply card styling
        self.setStyleSheet(f"""
            QWidget#modern-card {{
                background-color: {AppTheme.CARD};
                border: 1px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS['lg']};
                padding: 0px;
            }}

            QWidget#modern-card:hover {{
                border-color: {AppTheme.PRIMARY};
                box-shadow: {AppTheme.SHADOWS['md']};
            }}
        """)

class DashboardCard(ModernCard):
    """Specialized card for dashboard metrics"""

    def __init__(self, title, value, subtitle=None, trend=None, icon=None):
        # Store initial value
        self._value = str(value)

        # Create value display
        value_layout = QVBoxLayout()
        value_layout.setSpacing(4)

        # Main value
        self.value_label = QLabel(str(value))
        value_font = QFont(AppTheme.FONT_FAMILY)
        value_font.setPixelSize(32)
        value_font.setWeight(QFont.Weight.Bold)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {AppTheme.TEXT_PRIMARY};")
        value_layout.addWidget(self.value_label)

        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_font = QFont(AppTheme.FONT_FAMILY)
            subtitle_font.setPixelSize(12)
            subtitle_label.setFont(subtitle_font)
            subtitle_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY};")
            value_layout.addWidget(subtitle_label)

        # Trend indicator
        if trend:
            trend_text = f"{trend.get('direction', '')} {trend.get('value', '')}"
            trend_color = AppTheme.SUCCESS if trend.get('direction') == '↑' else AppTheme.ERROR
            trend_label = QLabel(trend_text)
            trend_font = QFont(AppTheme.FONT_FAMILY)
            trend_font.setPixelSize(11)
            trend_label.setFont(trend_font)
            trend_label.setStyleSheet(f"color: {trend_color}; font-weight: bold;")
            value_layout.addWidget(trend_label)

        # Create a container widget for the layout
        container = QWidget()
        container.setLayout(value_layout)
        super().__init__(title=title, content=container, icon=icon)

    @property
    def value(self):
        """Get the current value"""
        return self._value

    @value.setter
    def value(self, new_value):
        """Update the displayed value"""
        self._value = str(new_value)
        self.value_label.setText(str(new_value))

class ModernTable(QTableWidget):
    """Enhanced table with modern styling and features"""

    def __init__(self, headers=None, data=None):
        super().__init__()

        # Set basic properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.setShowGrid(False)

        # Set headers if provided
        if headers:
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)

            # Configure header
            header = self.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Set data if provided
        if data:
            self.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.setItem(row_idx, col_idx, item)

        self.setup_modern_styling()

    def setup_modern_styling(self):
        """Apply modern styling to the table"""

        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {AppTheme.SURFACE};
                border: 1px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS['lg']};
                gridline-color: {AppTheme.DIVIDER};
                selection-background-color: {AppTheme.PRIMARY}33;
                alternate-background-color: {AppTheme.CARD};
                font-family: {AppTheme.FONT_FAMILY};
                font-size: {AppTheme.FONT_SIZES['sm']};
            }}

            QTableWidget::item {{
                padding: {AppTheme.SPACING['md']};
                border-bottom: 1px solid {AppTheme.DIVIDER};
                color: {AppTheme.TEXT_PRIMARY};
                font-size: {AppTheme.FONT_SIZES['sm']};
            }}

            QTableWidget::item:selected {{
                background-color: {AppTheme.PRIMARY}33;
                color: {AppTheme.TEXT_PRIMARY};
            }}

            QTableWidget::item:hover {{
                background-color: {AppTheme.OVERLAY};
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

            QHeaderView::section:first {{
                border-top-left-radius: {AppTheme.RADIUS['lg']};
            }}

            QHeaderView::section:last {{
                border-top-right-radius: {AppTheme.RADIUS['lg']};
                border-right: none;
            }}
        """)

    def add_row(self, row_data):
        """Add a new row to the table"""
        row_count = self.rowCount()
        self.setRowCount(row_count + 1)

        for col_idx, cell_data in enumerate(row_data):
            item = QTableWidgetItem(str(cell_data))
            self.setItem(row_count, col_idx, item)

    def clear_table(self):
        """Clear all data from the table"""
        self.setRowCount(0)

class ModernProgressBar(QProgressBar):
    """Modern progress bar with enhanced styling"""

    def __init__(self, text_visible=True):
        super().__init__()
        self.setTextVisible(text_visible)
        self.setup_modern_styling()

    def setup_modern_styling(self):
        """Apply modern styling"""

        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS['md']};
                text-align: center;
                font-weight: {AppTheme.FONT_WEIGHTS['medium']};
                color: {AppTheme.TEXT_PRIMARY};
                font-family: {AppTheme.FONT_FAMILY};
                font-size: {AppTheme.FONT_SIZES['sm']};
                background-color: {AppTheme.SURFACE};
                min-height: 24px;
            }}

            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {AppTheme.PRIMARY},
                    stop:1 {AppTheme.PRIMARY_LIGHT});
                border-radius: {AppTheme.RADIUS['sm']};
            }}
        """)

class ModernGroupBox(QGroupBox):
    """Enhanced group box with modern styling"""

    def __init__(self, title="", collapsible=False):
        super().__init__(title)
        self.collapsible = collapsible
        self.collapsed = False
        self.setup_modern_styling()

        if collapsible:
            self.setup_collapsible()

    def setup_modern_styling(self):
        """Apply modern styling"""

        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: {AppTheme.FONT_WEIGHTS['semibold']};
                border: 2px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS['lg']};
                margin-top: 1ex;
                padding-top: {AppTheme.SPACING['md']};
                background-color: {AppTheme.CARD};
                font-family: {AppTheme.FONT_FAMILY};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {AppTheme.SPACING['md']};
                padding: 0 {AppTheme.SPACING['md']} 0 {AppTheme.SPACING['md']};
                color: {AppTheme.TEXT_PRIMARY};
                font-size: {AppTheme.FONT_SIZES['lg']};
                font-weight: {AppTheme.FONT_WEIGHTS['semibold']};
                background-color: transparent;
            }}
        """)

    def setup_collapsible(self):
        """Make the group box collapsible"""
        self.setCheckable(True)
        self.toggled.connect(self.toggle_content)

    def toggle_content(self, checked):
        """Toggle visibility of content when collapsed"""
        # This would require additional implementation to hide/show content
        pass

class AnimatedButton(ModernButton):
    """Button with smooth hover animations"""

    def __init__(self, text="", variant="primary", size="md", icon=None):
        super().__init__(text, variant, size, icon)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.setDuration(150)

        # Connect hover events
        self.enterEvent = self.start_hover_animation
        self.leaveEvent = self.end_hover_animation

    def start_hover_animation(self, event):
        """Start hover animation"""
        # Subtle scale effect
        pass

    def end_hover_animation(self, event):
        """End hover animation"""
        # Return to normal size
        pass

# Utility functions for consistent styling
def apply_theme_to_widget(widget):
    """Apply theme colors to any widget"""
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(AppTheme.SURFACE))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(AppTheme.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(AppTheme.SURFACE))
    palette.setColor(QPalette.ColorRole.Text, QColor(AppTheme.TEXT_PRIMARY))
    widget.setPalette(palette)

def create_spacer(size="md"):
    """Create a consistent spacer widget"""
    spacer = QWidget()
    spacer.setFixedSize(int(AppTheme.SPACING[size].replace('px', '')), 1)
    return spacer

class ModernCheckBox(QCheckBox):
    """Enhanced checkbox with better styling and larger touch targets"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setup_modern_styling()

    def setup_modern_styling(self):
        """Apply modern styling with better accessibility"""
        self.setStyleSheet(f"""
            QCheckBox {{
                font-size: {AppTheme.FONT_SIZES['base']};
                font-weight: 500;
                color: {AppTheme.TEXT_PRIMARY};
                spacing: 12px;
                padding: 4px;
                min-height: 24px;
            }}

            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS['sm']};
                background-color: {AppTheme.SURFACE};
                margin-right: 8px;
            }}

            QCheckBox::indicator:checked {{
                background-color: {AppTheme.PRIMARY};
                border-color: {AppTheme.PRIMARY};
            }}

            QCheckBox::indicator:checked::hover {{
                background-color: {AppTheme.PRIMARY_LIGHT};
                border-color: {AppTheme.PRIMARY_LIGHT};
            }}

            QCheckBox::indicator:hover {{
                border-color: {AppTheme.PRIMARY_LIGHT};
            }}

            QCheckBox::indicator:pressed {{
                background-color: {AppTheme.PRIMARY_DARK};
            }}
        """)

class DietaryPreferenceItem(QWidget):
    """Individual dietary preference item with checkbox and description"""

    def __init__(self, name, description, parent=None):
        super().__init__(parent)
        self.name = name
        self.description = description
        self.checkbox = None
        self.setup_preference_item()

    def setup_preference_item(self):
        """Create the preference item layout"""
        self.setObjectName("preference-item")
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Checkbox
        self.checkbox = ModernCheckBox(self.name)
        self.checkbox.setToolTip(self.description)
        self.checkbox.setMinimumWidth(140)
        layout.addWidget(self.checkbox)

        # Description
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            color: {AppTheme.TEXT_SECONDARY};
            font-size: {AppTheme.FONT_SIZES['sm']};
            line-height: {AppTheme.LINE_HEIGHTS['relaxed']};
            padding-right: {AppTheme.SPACING['md']};
        """)
        layout.addWidget(desc_label, 1)  # Stretch factor 1

        self.setLayout(layout)

        # Item styling
        self.setStyleSheet(f"""
            QWidget#preference-item {{
                border: 1px solid {AppTheme.BORDER_LIGHT};
                border-radius: {AppTheme.RADIUS['lg']};
                background-color: {AppTheme.CARD};
                margin: {AppTheme.SPACING['xs']} 0px;
            }}

            QWidget#preference-item:hover {{
                border-color: {AppTheme.PRIMARY_LIGHT};
                background-color: {AppTheme.SURFACE};
            }}
        """)

    def is_checked(self):
        """Get checkbox state"""
        return self.checkbox.isChecked() if self.checkbox else False

    def set_checked(self, checked):
        """Set checkbox state"""
        if self.checkbox:
            self.checkbox.setChecked(checked)

class DietaryPreferencesPanel(QWidget):
    """Panel for managing dietary preferences with spacious layout"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.preference_items = {}
        self.setup_panel()

    def setup_panel(self):
        """Create the dietary preferences panel"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable area for preferences
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(250)
        scroll_area.setMaximumHeight(350)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS['lg']};
                background-color: {AppTheme.SURFACE};
            }}

            QScrollBar:vertical {{
                width: 12px;
                background-color: {AppTheme.SURFACE};
            }}

            QScrollBar::handle:vertical {{
                background-color: {AppTheme.BORDER};
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {AppTheme.OVERLAY};
            }}
        """)

        # Container widget for preferences
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(4)
        container_layout.setContentsMargins(8, 8, 8, 8)

        # Add preference items
        dietary_options = self.get_dietary_options()
        for name, description in dietary_options:
            pref_item = DietaryPreferenceItem(name, description)
            self.preference_items[name.lower().replace('-', '_')] = pref_item
            container_layout.addWidget(pref_item)

        container.setLayout(container_layout)
        scroll_area.setWidget(container)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def get_dietary_options(self):
        """Get the list of dietary options with descriptions"""
        return [
            ("Vegetarian", "Excludes meat, poultry, and fish. Focuses on plant-based proteins like beans, tofu, and dairy."),
            ("Vegan", "Excludes all animal products including meat, dairy, eggs, and honey. 100% plant-based."),
            ("Pork-Free", "Excludes all pork products and pork-derived ingredients. Suitable for religious or cultural preferences."),
            ("Gluten-Free", "Excludes wheat and all gluten-containing foods. Essential for celiac disease or gluten sensitivity."),
            ("Dairy-Free", "Excludes milk and all dairy products. Includes alternatives like almond, soy, or oat milk."),
            ("Nut-Free", "Excludes all nuts and nut products. Critical for nut allergies and school environments."),
            ("Low-Carb", "Minimizes carbohydrate-rich foods. Focuses on proteins, healthy fats, and vegetables."),
            ("Keto", "High-fat, low-carb ketogenic diet. Typically under 50g carbs per day for ketosis."),
            ("Paleo", "Focuses on whole foods that our ancestors ate: meats, fish, vegetables, fruits, and nuts.")
        ]

    def get_selected_preferences(self):
        """Get dictionary of selected dietary preferences"""
        return {
            name: item.is_checked()
            for name, item in self.preference_items.items()
        }

    def set_preferences(self, preferences_dict):
        """Set dietary preferences from dictionary"""
        for name, checked in preferences_dict.items():
            if name in self.preference_items:
                self.preference_items[name].set_checked(checked)

class AutoGenerationPanel(QWidget):
    """Panel for auto-generation settings integrated with dietary preferences"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_panel()

    def setup_panel(self):
        """Create the auto-generation settings panel"""
        layout = QHBoxLayout()
        layout.setSpacing(24)
        layout.setContentsMargins(16, 16, 16, 16)

        # Left side: Basic settings
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(12)

        # Enable/disable auto-generation
        self.enable_auto_gen = ModernCheckBox("Enable automatic meal generation")
        self.enable_auto_gen.setChecked(True)
        self.enable_auto_gen.setToolTip("Automatically generate meals based on your dietary preferences and available inventory")
        settings_layout.addWidget(self.enable_auto_gen)

        # Generation frequency
        freq_layout = QHBoxLayout()
        freq_layout.setSpacing(8)

        freq_label = QLabel("Generation Frequency:")
        freq_label.setStyleSheet(f"""
            color: {AppTheme.TEXT_PRIMARY};
            font-weight: 500;
            font-size: {AppTheme.FONT_SIZES['sm']};
        """)
        freq_layout.addWidget(freq_label)

        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems([
            "Manual Only",
            "Daily (Fill Gaps)",
            "Daily (Replace All)",
            "Weekly",
            "On App Start"
        ])
        self.frequency_combo.setCurrentText("Daily (Fill Gaps)")
        self.frequency_combo.setMinimumWidth(140)
        self.frequency_combo.setStyleSheet(f"""
            QComboBox {{
                padding: {AppTheme.SPACING['sm']};
                border: 2px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS['md']};
                background-color: {AppTheme.SURFACE};
                color: {AppTheme.TEXT_PRIMARY};
                min-height: 32px;
            }}

            QComboBox:hover {{
                border-color: {AppTheme.PRIMARY_LIGHT};
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
            }}
        """)
        freq_layout.addWidget(self.frequency_combo)
        freq_layout.addStretch()

        settings_layout.addLayout(freq_layout)
        settings_layout.addStretch()

        # Right side: Action buttons
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)

        # Regenerate label
        regen_label = QLabel("Quick Regenerate:")
        regen_label.setStyleSheet(f"""
            color: {AppTheme.TEXT_PRIMARY};
            font-weight: 600;
            font-size: {AppTheme.FONT_SIZES['sm']};
            margin-bottom: {AppTheme.SPACING['xs']};
        """)
        actions_layout.addWidget(regen_label)

        # Regenerate buttons
        self.regen_today_btn = ModernButton("📅 Today", variant="info", size="sm")
        self.regen_today_btn.setToolTip("Regenerate meals for today only")
        actions_layout.addWidget(self.regen_today_btn)

        self.regen_week_btn = ModernButton("📆 This Week", variant="warning", size="sm")
        self.regen_week_btn.setToolTip("Regenerate meals for this week")
        actions_layout.addWidget(self.regen_week_btn)

        self.regen_all_btn = ModernButton("🔄 All Meals", variant="error", size="sm")
        self.regen_all_btn.setToolTip("Regenerate ALL meals (overwrites existing meals)")
        actions_layout.addWidget(self.regen_all_btn)

        # Add stretch to push buttons to top
        actions_layout.addStretch()

        layout.addLayout(settings_layout, 1)  # Stretch factor 1
        layout.addLayout(actions_layout, 0)  # No stretch

        self.setLayout(layout)

        # Panel styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {AppTheme.CARD};
                border: 1px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS['lg']};
            }}
        """)

class MealsActionBar(QWidget):
    """Organized action bar for meals tab with grouped functionality"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_action_bar()

    def setup_action_bar(self):
        """Create organized action bar with functional groups and improved spacing"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(32)  # Increased spacing between groups
        main_layout.setContentsMargins(20, 20, 20, 20)  # More padding

        # Group 1: Meal CRUD Operations
        crud_group = self.create_action_group(
            "Meal Management",
            [
                ("➕ Add Meal", "add_meal", "success", "Add a new meal to the selected date and type"),
                ("✏️ Edit Meal", "edit_meal", "primary", "Edit the currently selected meal"),
                ("🗑️ Delete Meal", "delete_meal", "error", "Delete the currently selected meal")
            ]
        )

        # Group 2: AI Features
        ai_group = self.create_action_group(
            "AI Features",
            [
                ("🤖 AI Suggestions", "show_ai_suggestion_dialog", "secondary", "Get AI-powered meal suggestions"),
                ("🍽️ Daily Plan", "generate_daily_meal_plan", "success", "Generate a complete daily meal plan"),
                ("⚡ Quick Match", "quick_inventory_match", "info", "Quick match meals to available inventory")
            ]
        )

        # Group 3: Import/Export
        io_group = self.create_action_group(
            "Import/Export",
            [
                ("📥 Import CSV", "import_meals_csv", "info", "Import meals from CSV file"),
                ("📤 Export CSV", "export_meals_csv", "info", "Export meals to CSV file")
            ]
        )

        main_layout.addWidget(crud_group)
        main_layout.addWidget(ai_group)
        main_layout.addWidget(io_group)
        main_layout.addStretch()  # Push groups to the left

        self.setLayout(main_layout)

    def create_action_group(self, title, actions):
        """Create a group of related action buttons with improved spacing"""
        group_widget = QWidget()
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)  # Increased spacing between buttons
        group_layout.setContentsMargins(0, 0, 0, 0)

        # Group title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {AppTheme.TEXT_SECONDARY};
            font-weight: 600;
            font-size: {AppTheme.FONT_SIZES['sm']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: {AppTheme.SPACING['sm']};
            padding: 4px 0;
        """)
        group_layout.addWidget(title_label)

        # Action buttons with better spacing
        for icon_text, method_name, variant, tooltip in actions:
            btn = ModernButton(icon_text, variant=variant, size="md")  # Changed from sm to md
            btn.setToolTip(tooltip)
            btn.setMinimumWidth(140)  # Ensure consistent button width
            # Store method name for later connection
            btn.setProperty("method_name", method_name)
            group_layout.addWidget(btn)

        group_widget.setLayout(group_layout)
        return group_widget

    def connect_actions(self, parent_widget):
        """Connect action buttons to parent widget methods"""
        for group in self.findChildren(QWidget):
            for btn in group.findChildren(ModernButton):
                method_name = btn.property("method_name")
                if method_name and hasattr(parent_widget, method_name):
                    btn.clicked.connect(getattr(parent_widget, method_name))