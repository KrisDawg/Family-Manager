"""
Family Manager Mobile App
Modern Kivy application with Material Design
"""

import logging
import os
import threading
import socket
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.progressbar import ProgressBar
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behavioural.recycleview_behavior import RecycleViewBehavior
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.refreshlayout import RefreshLayout
from datetime import datetime, timedelta
from api_client import APIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Window configuration
Window.size = (400, 700)  # Mobile aspect ratio


class Colors:
    """Material Design color palette"""
    PRIMARY = (0.2, 0.6, 0.95, 1)          # Blue
    PRIMARY_DARK = (0.15, 0.5, 0.85, 1)
    ACCENT = (1, 0.55, 0.1, 1)             # Orange
    BACKGROUND = (0.95, 0.95, 0.95, 1)
    SURFACE = (1, 1, 1, 1)
    TEXT_PRIMARY = (0.2, 0.2, 0.2, 1)
    TEXT_SECONDARY = (0.6, 0.6, 0.6, 1)
    ERROR = (0.95, 0.15, 0.1, 1)
    SUCCESS = (0.15, 0.8, 0.3, 1)


class ModernButton(Button):
    """Material Design button"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Colors.PRIMARY
        self.size_hint_y = None
        self.height = dp(48)
        self.font_size = dp(16)


class ModernCard(BoxLayout):
    """Material Design card"""
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with self.canvas.before:
            Color(*Colors.SURFACE)
            RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(4)])


class LoadingDialog:
    """Helper class for showing loading spinners"""
    
    @staticmethod
    def show(title: str = 'Loading...') -> Popup:
        """Show a loading dialog with spinner"""
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        label = Label(text=title, size_hint_y=None, height=dp(40),
                     font_size=dp(14), color=Colors.TEXT_PRIMARY)
        
        # Simple animated progress bar
        progress = ProgressBar(size_hint_y=None, height=dp(4))
        
        box.add_widget(label)
        box.add_widget(progress)
        
        popup = Popup(title='Processing', content=box, size_hint=(0.8, 0.3))
        
        # Animate progress bar
        anim = Animation(value=100, duration=2)
        progress.bind(value=lambda w, v: anim.start(w) if v >= 100 else None)
        anim.start(progress)
        
        return popup


class ConnectivityManager:
    """Manages network connectivity detection"""
    
    @staticmethod
    def is_online() -> bool:
        """Check if device has internet connection"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except (socket.timeout, socket.error):
            return False


class OfflineIndicator(Label):
    """Shows offline status indicator"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(32)
        self.font_size = dp(12)
        self.padding = dp(8)
        self.is_online = True
        
        # Start monitoring connectivity
        Clock.schedule_interval(self._check_connectivity, 5)  # Check every 5 seconds
    
    def _check_connectivity(self, dt):
        """Periodically check connectivity"""
        was_online = self.is_online
        self.is_online = ConnectivityManager.is_online()
        
        if self.is_online:
            self.text = '🟢 Online'
            self.color = Colors.SUCCESS
        else:
            self.text = '🔴 Offline - Data will sync when connection is restored'
            self.color = Colors.ERROR
        
        # Only update if status changed
        return was_online == self.is_online


# ==========================================
# SCREEN 1: DASHBOARD
# ==========================================

class DashboardScreen(Screen):
    """Home/Dashboard screen showing summary cards"""
    
    def __init__(self, api_client: APIClient, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.name = 'dashboard'
        
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        
        # Offline indicator
        self.offline_indicator = OfflineIndicator()
        layout.add_widget(self.offline_indicator)
        
        # Header
        header = Label(text='📊 Family Manager', size_hint_y=None, height=dp(60),
                      font_size=dp(24), bold=True, color=Colors.TEXT_PRIMARY)
        layout.add_widget(header)
        
        # Scroll area for cards
        scroll = ScrollView(size_hint=(1, 1))
        cards_layout = GridLayout(cols=1, spacing=dp(12), size_hint_y=None)
        cards_layout.bind(minimum_height=cards_layout.setter('height'))
        
        # Summary cards (10 total)
        self.inventory_card = self._create_summary_card("📦 Inventory", "0 items", self._go_to_inventory)
        self.shopping_card = self._create_summary_card("🛒 Shopping", "0 items", self._go_to_shopping)
        self.chores_card = self._create_summary_card("🧹 Chores", "0 pending", self._go_to_chores)
        self.tasks_card = self._create_summary_card("✅ Tasks", "0 pending", self._go_to_tasks)
        self.bills_card = self._create_summary_card("💰 Bills", "0 bills", self._go_to_bills)
        self.meals_card = self._create_summary_card("🍽️ Meals", "0 planned", self._go_to_meals)
        self.family_card = self._create_summary_card("👥 Family", "0 members", self._go_to_family)
        self.notifications_card = self._create_summary_card("🔔 Notifications", "0 unread", self._go_to_notifications)
        self.settings_card = self._create_summary_card("⚙️ Settings", "Configuration", self._go_to_settings)
        
        cards_layout.add_widget(self.inventory_card)
        cards_layout.add_widget(self.shopping_card)
        cards_layout.add_widget(self.chores_card)
        cards_layout.add_widget(self.tasks_card)
        cards_layout.add_widget(self.bills_card)
        cards_layout.add_widget(self.meals_card)
        cards_layout.add_widget(self.family_card)
        cards_layout.add_widget(self.notifications_card)
        cards_layout.add_widget(self.settings_card)
        
        scroll.add_widget(cards_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _create_summary_card(self, title: str, subtitle: str, callback) -> ModernCard:
        """Create a summary card"""
        card = ModernCard(size_hint_y=None, height=dp(100))
        inner = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(4))
        
        title_label = Label(text=title, size_hint_y=None, height=dp(32),
                          font_size=dp(18), bold=True, color=Colors.TEXT_PRIMARY)
        subtitle_label = Label(text=subtitle, size_hint_y=None, height=dp(24),
                             font_size=dp(14), color=Colors.TEXT_SECONDARY)
        
        inner.add_widget(title_label)
        inner.add_widget(subtitle_label)
        
        card.bind(on_touch_down=lambda x, y=callback: y() if card.collide_point(*x.pos) else None)
        card.add_widget(inner)
        
        return card
    
    def on_enter(self):
        """Refresh data when screen is displayed"""
        self._update_summary()
    
    def _update_summary(self):
        """Update summary card data"""
        # Get inventory count
        inventory = self.api_client.get_inventory()
        self.inventory_card.children[0].children[1].text = f"{len(inventory)} items"
        
        # Get shopping count
        shopping = self.api_client.get_shopping_list()
        unchecked = [x for x in shopping if not x.get('checked', 0)]
        self.shopping_card.children[0].children[1].text = f"{len(unchecked)} items"
        
        # Get chores count
        chores = self.api_client.get_chores(status='pending')
        self.chores_card.children[0].children[1].text = f"{len(chores)} pending"
        
        # Get tasks count
        tasks = self.api_client.get_tasks(status='pending')
        self.tasks_card.children[0].children[1].text = f"{len(tasks)} pending"
        
        # Get bills count
        bills = self.api_client.get_bills()
        self.bills_card.children[0].children[1].text = f"{len(bills)} bills"
        
        # Get meals count
        meals = self.api_client.get_meals()
        self.meals_card.children[0].children[1].text = f"{len(meals)} planned"
        
        # Get family members count
        family = self.api_client.get_family_members()
        self.family_card.children[0].children[1].text = f"{len(family)} members"
        
        # Get unread notifications
        unread = self.api_client.get_unread_count()
        self.notifications_card.children[0].children[1].text = f"{unread} unread"
    
    def _go_to_inventory(self):
        """Navigate to inventory screen"""
        self.manager.current = 'inventory'
    
    def _go_to_shopping(self):
        """Navigate to shopping screen"""
        self.manager.current = 'shopping'
    
    def _go_to_chores(self):
        """Navigate to chores screen"""
        self.manager.current = 'chores'
    
    def _go_to_tasks(self):
        """Navigate to tasks screen"""
        self.manager.current = 'tasks'
    
    def _go_to_bills(self):
        """Navigate to bills screen"""
        self.manager.current = 'bills'
    
    def _go_to_meals(self):
        """Navigate to meals screen"""
        self.manager.current = 'meals'
    
    def _go_to_family(self):
        """Navigate to family screen"""
        self.manager.current = 'family'
    
    def _go_to_notifications(self):
        """Navigate to notifications screen"""
        self.manager.current = 'notifications'
    
    def _go_to_settings(self):
        """Navigate to settings screen"""
        self.manager.current = 'settings'


# ==========================================
# SCREEN 2: INVENTORY
# ==========================================

class InventoryScreen(Screen):
    """Inventory management screen"""
    
    def __init__(self, api_client: APIClient, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.name = 'inventory'
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        # Header with add button
        header_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        back_btn = ModernButton(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=lambda x: self._go_back())
        header_layout.add_widget(back_btn)
        
        title = Label(text='📦 Inventory', size_hint_x=0.6, font_size=dp(18), bold=True)
        header_layout.add_widget(title)
        
        add_btn = ModernButton(text='+', size_hint_x=0.2, background_color=Colors.SUCCESS)
        add_btn.bind(on_press=lambda x: self._show_add_dialog())
        header_layout.add_widget(add_btn)
        
        layout.add_widget(header_layout)
        
        # Items list
        self.items_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.items_layout.bind(minimum_height=self.items_layout.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.items_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Refresh inventory when screen is displayed"""
        self._load_inventory()
    
    def _load_inventory(self):
        """Load and display inventory items"""
        self.items_layout.clear_widgets()
        
        items = self.api_client.get_inventory()
        
        if not items:
            self.items_layout.add_widget(Label(text='No items yet', color=Colors.TEXT_SECONDARY))
            return
        
        for item in items:
            item_card = self._create_item_card(item)
            self.items_layout.add_widget(item_card)
    
    def _create_item_card(self, item: dict) -> ModernCard:
        """Create an inventory item card"""
        card = ModernCard(size_hint_y=None, height=dp(80))
        inner = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
        
        # Name and category
        name_text = f"{item.get('name', 'Unknown')}"
        if item.get('category'):
            name_text += f" ({item['category']})"
        
        name_label = Label(text=name_text, size_hint_y=None, height=dp(24),
                         font_size=dp(14), bold=True, color=Colors.TEXT_PRIMARY)
        inner.add_widget(name_label)
        
        # Quantity
        qty_text = f"Qty: {item.get('qty', 0)} {item.get('unit', '')}"
        if item.get('exp_date'):
            qty_text += f" | Expires: {item['exp_date']}"
        
        qty_label = Label(text=qty_text, size_hint_y=None, height=dp(20),
                        font_size=dp(12), color=Colors.TEXT_SECONDARY)
        inner.add_widget(qty_label)
        
        inner.add_widget(Label(size_hint_y=None, height=dp(1)))  # Spacer
        
        card.add_widget(inner)
        return card
    
    def _show_add_dialog(self):
        """Show dialog to add new inventory item"""
        dialog = Popup(title='Add Inventory Item', size_hint=(0.9, 0.7))
        
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        name_input = TextInput(hint_text='Item name', multiline=False, size_hint_y=None, height=dp(40))
        category_spinner = Spinner(
            text='Category',
            values=('Produce', 'Dairy', 'Meat', 'Pantry', 'Frozen', 'Other'),
            size_hint_y=None,
            height=dp(40)
        )
        qty_input = TextInput(hint_text='Quantity', input_filter='float', multiline=False,
                            size_hint_y=None, height=dp(40))
        unit_spinner = Spinner(
            text='Unit',
            values=('pcs', 'kg', 'lb', 'L', 'L', 'box', 'pack'),
            size_hint_y=None,
            height=dp(40)
        )
        
        content.add_widget(name_input)
        content.add_widget(category_spinner)
        content.add_widget(qty_input)
        content.add_widget(unit_spinner)
        
        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        
        def save_item():
            if name_input.text and qty_input.text:
                self.api_client.add_inventory(
                    name=name_input.text,
                    category=category_spinner.text if category_spinner.text != 'Category' else 'Other',
                    qty=float(qty_input.text),
                    unit=unit_spinner.text if unit_spinner.text != 'Unit' else 'pcs'
                )
                dialog.dismiss()
                self._load_inventory()
        
        save_btn = ModernButton(text='Save')
        save_btn.bind(on_press=lambda x: save_item())
        button_layout.add_widget(save_btn)
        
        cancel_btn = ModernButton(text='Cancel', background_color=Colors.ERROR)
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(button_layout)
        dialog.content = content
        dialog.open()
    
    def _go_back(self):
        """Go back to dashboard"""
        self.manager.current = 'dashboard'


# ==========================================
# SCREEN 3: SHOPPING LIST
# ==========================================

class ShoppingScreen(Screen):
    """Shopping list management screen"""
    
    def __init__(self, api_client: APIClient, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.name = 'shopping'
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        # Header
        header_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        back_btn = ModernButton(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=lambda x: self._go_back())
        header_layout.add_widget(back_btn)
        
        title = Label(text='🛒 Shopping List', size_hint_x=0.6, font_size=dp(18), bold=True)
        header_layout.add_widget(title)
        
        add_btn = ModernButton(text='+', size_hint_x=0.2, background_color=Colors.SUCCESS)
        add_btn.bind(on_press=lambda x: self._show_add_dialog())
        header_layout.add_widget(add_btn)
        
        layout.add_widget(header_layout)
        
        # Items list
        self.items_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.items_layout.bind(minimum_height=self.items_layout.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.items_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Refresh shopping list when screen is displayed"""
        self._load_shopping()
    
    def _load_shopping(self):
        """Load and display shopping list"""
        self.items_layout.clear_widgets()
        
        items = self.api_client.get_shopping_list()
        
        if not items:
            self.items_layout.add_widget(Label(text='Shopping list is empty', color=Colors.TEXT_SECONDARY))
            return
        
        for item in items:
            item_card = self._create_item_card(item)
            self.items_layout.add_widget(item_card)
    
    def _create_item_card(self, item: dict) -> ModernCard:
        """Create shopping item card"""
        card = ModernCard(size_hint_y=None, height=dp(60))
        inner = BoxLayout(padding=dp(8), spacing=dp(8))
        
        # Checkbox button
        check_btn = Button(text='☐' if not item.get('checked') else '☑',
                          size_hint_x=None, width=dp(40), background_color=Colors.PRIMARY)
        item_id = item.get('id')
        check_btn.bind(on_press=lambda x, i=item_id, c=item.get('checked'): 
                      self._toggle_item(i, c))
        inner.add_widget(check_btn)
        
        # Item text
        item_text = item.get('item', 'Unknown')
        if item.get('qty'):
            item_text += f" (x{item['qty']})"
        
        text_label = Label(text=item_text, font_size=dp(14))
        inner.add_widget(text_label)
        
        card.add_widget(inner)
        return card
    
    def _toggle_item(self, item_id: int, currently_checked: bool):
        """Toggle shopping item checked status"""
        self.api_client.update_shopping_item(item_id, checked=0 if currently_checked else 1)
        self._load_shopping()
    
    def _show_add_dialog(self):
        """Show dialog to add shopping item"""
        dialog = Popup(title='Add Shopping Item', size_hint=(0.9, 0.5))
        
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        item_input = TextInput(hint_text='Item name', multiline=False, size_hint_y=None, height=dp(40))
        qty_input = TextInput(hint_text='Quantity (optional)', input_filter='float', multiline=False,
                            size_hint_y=None, height=dp(40))
        
        content.add_widget(item_input)
        content.add_widget(qty_input)
        
        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        
        def save_item():
            if item_input.text:
                qty = float(qty_input.text) if qty_input.text else None
                self.api_client.add_shopping_item(item_input.text, qty=qty)
                dialog.dismiss()
                self._load_shopping()
        
        save_btn = ModernButton(text='Add')
        save_btn.bind(on_press=lambda x: save_item())
        button_layout.add_widget(save_btn)
        
        cancel_btn = ModernButton(text='Cancel', background_color=Colors.ERROR)
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(button_layout)
        dialog.content = content
        dialog.open()
    
    def _go_back(self):
        """Go back to dashboard"""
        self.manager.current = 'dashboard'


# ==========================================
# SCREEN 4: NOTIFICATIONS
# ==========================================

class NotificationsScreen(Screen):
    """Notifications center screen"""
    
    def __init__(self, api_client: APIClient, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.name = 'notifications'
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        # Header
        header_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        back_btn = ModernButton(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=lambda x: self._go_back())
        header_layout.add_widget(back_btn)
        
        title = Label(text='🔔 Notifications', size_hint_x=0.8, font_size=dp(18), bold=True)
        header_layout.add_widget(title)
        
        layout.add_widget(header_layout)
        
        # Notifications list
        self.notif_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.notif_layout.bind(minimum_height=self.notif_layout.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.notif_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Refresh notifications when screen is displayed"""
        self._load_notifications()
    
    def _load_notifications(self):
        """Load and display notifications"""
        self.notif_layout.clear_widgets()
        
        notifications = self.api_client.get_notifications()
        
        if not notifications:
            self.notif_layout.add_widget(Label(text='No notifications', color=Colors.TEXT_SECONDARY))
            return
        
        for notif in notifications:
            notif_card = self._create_notification_card(notif)
            self.notif_layout.add_widget(notif_card)
    
    def _create_notification_card(self, notif: dict) -> ModernCard:
        """Create notification card"""
        card = ModernCard(size_hint_y=None, height=dp(100))
        inner = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
        
        # Title
        title_label = Label(text=notif.get('title', 'Notification'),
                          size_hint_y=None, height=dp(24),
                          font_size=dp(14), bold=True, color=Colors.TEXT_PRIMARY)
        inner.add_widget(title_label)
        
        # Message
        message_label = Label(text=notif.get('message', '')[:100],
                            size_hint_y=None, height=dp(32),
                            font_size=dp(12), color=Colors.TEXT_SECONDARY)
        inner.add_widget(message_label)
        
        # Priority badge
        priority = notif.get('priority', 'normal')
        priority_color = Colors.ERROR if priority in ['urgent', 'high'] else Colors.PRIMARY
        priority_label = Label(text=priority.upper(),
                             size_hint_y=None, height=dp(16),
                             font_size=dp(10), color=priority_color)
        inner.add_widget(priority_label)
        
        card.add_widget(inner)
        return card
    
    def _go_back(self):
        """Go back to dashboard"""
        self.manager.current = 'dashboard'


# ==========================================
# CHORES & TASKS SCREENS (Basic templates)
# ==========================================

class ChoresScreen(Screen):
    """Chores management screen"""
    
    def __init__(self, api_client: APIClient, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.name = 'chores'
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        back_btn = ModernButton(text='← Back', size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(back_btn)
        
        title = Label(text='🧹 Chores', size_hint_y=None, height=dp(50),
                     font_size=dp(20), bold=True, color=Colors.TEXT_PRIMARY)
        layout.add_widget(title)
        
        self.chores_list = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.chores_list.bind(minimum_height=self.chores_list.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.chores_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Load chores when screen is displayed"""
        self.chores_list.clear_widgets()
        chores = self.api_client.get_chores(status='pending')
        
        if not chores:
            self.chores_list.add_widget(Label(text='No pending chores!',
                                             color=Colors.TEXT_SECONDARY))
            return
        
        for chore in chores:
            card = ModernCard(size_hint_y=None, height=dp(80))
            inner = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
            
            name = Label(text=chore.get('name', ''),
                        size_hint_y=None, height=dp(24),
                        font_size=dp(14), bold=True, color=Colors.TEXT_PRIMARY)
            due = Label(text=f"Due: {chore.get('due_date', '')}",
                       size_hint_y=None, height=dp(20),
                       font_size=dp(12), color=Colors.TEXT_SECONDARY)
            
            inner.add_widget(name)
            inner.add_widget(due)
            card.add_widget(inner)
            self.chores_list.add_widget(card)


class TasksScreen(Screen):
    """Tasks management screen"""
    
    def __init__(self, api_client: APIClient, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.name = 'tasks'
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        back_btn = ModernButton(text='← Back', size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(back_btn)
        
        title = Label(text='✅ Tasks', size_hint_y=None, height=dp(50),
                     font_size=dp(20), bold=True, color=Colors.TEXT_PRIMARY)
        layout.add_widget(title)
        
        self.tasks_list = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.tasks_list.bind(minimum_height=self.tasks_list.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.tasks_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Load tasks when screen is displayed"""
        self.tasks_list.clear_widgets()
        tasks = self.api_client.get_tasks(status='pending')
        
        if not tasks:
            self.tasks_list.add_widget(Label(text='No pending tasks!', 
                                            color=Colors.TEXT_SECONDARY))
            return
        
        for task in tasks:
            card = ModernCard(size_hint_y=None, height=dp(80))
            inner = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
            
            title = Label(text=task.get('title', ''),
                         size_hint_y=None, height=dp(24),
                         font_size=dp(14), bold=True, color=Colors.TEXT_PRIMARY)
            due = Label(text=f"Due: {task.get('due_date', '')}",
                       size_hint_y=None, height=dp(20),
                       font_size=dp(12), color=Colors.TEXT_SECONDARY)
            
            inner.add_widget(title)
            inner.add_widget(due)
            card.add_widget(inner)
            self.tasks_list.add_widget(card)


# ==========================================
# SCREEN 7: BILLS
# ==========================================

class BillsScreen(Screen):
    """Bills management screen"""
    
    def __init__(self, api_client: APIClient, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.name = 'bills'
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        back_btn = ModernButton(text='← Back', size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(back_btn)
        
        title = Label(text='💰 Bills', size_hint_y=None, height=dp(50),
                     font_size=dp(20), bold=True, color=Colors.TEXT_PRIMARY)
        layout.add_widget(title)
        
        # Add bill button
        add_btn = ModernButton(text='+ Add Bill')
        add_btn.bind(on_press=self._show_add_bill_dialog)
        layout.add_widget(add_btn)
        
        self.bills_list = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.bills_list.bind(minimum_height=self.bills_list.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.bills_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Load bills when screen is displayed"""
        self.bills_list.clear_widgets()
        bills = self.api_client.get_bills()
        
        if not bills:
            self.bills_list.add_widget(Label(text='No bills tracked!', 
                                            color=Colors.TEXT_SECONDARY))
            return
        
        for bill in bills:
            card = ModernCard(size_hint_y=None, height=dp(90))
            inner = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
            
            name = Label(text=bill.get('name', ''),
                        size_hint_y=None, height=dp(24),
                        font_size=dp(14), bold=True, color=Colors.TEXT_PRIMARY)
            amount = Label(text=f"${bill.get('amount', 0):.2f}",
                          size_hint_y=None, height=dp(24),
                          font_size=dp(14), color=Colors.TEXT_PRIMARY)
            due = Label(text=f"Due: {bill.get('due_date', '')}",
                       size_hint_y=None, height=dp(20),
                       font_size=dp(12), color=Colors.TEXT_SECONDARY)
            
            inner.add_widget(name)
            inner.add_widget(amount)
            inner.add_widget(due)
            card.add_widget(inner)
            self.bills_list.add_widget(card)
    
    def _show_add_bill_dialog(self, instance):
        """Show dialog to add new bill"""
        box = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        
        name_input = TextInput(hint_text='Bill name', size_hint_y=None, height=dp(48),
                              multiline=False)
        amount_input = TextInput(hint_text='Amount (0.00)', size_hint_y=None, height=dp(48),
                                multiline=False, input_filter='float')
        due_input = TextInput(hint_text='Due date (YYYY-MM-DD)', size_hint_y=None, height=dp(48),
                            multiline=False)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        
        def add_bill(btn):
            try:
                if not name_input.text or not amount_input.text or not due_input.text:
                    self._show_error("Please fill all fields")
                    return
                
                # Show loading dialog
                loading_dialog = LoadingDialog.show('Adding bill...')
                
                def do_add_bill():
                    """Run in background thread"""
                    try:
                        self.api_client.add_bill({
                            'name': name_input.text,
                            'amount': float(amount_input.text),
                            'due_date': due_input.text,
                            'category': 'bill',
                            'paid': False
                        })
                        # Schedule main thread update
                        Clock.schedule_once(lambda dt: self._finish_add_bill(dialog, loading_dialog), 0)
                    except Exception as e:
                        Clock.schedule_once(lambda dt: self._show_error(f"Error: {str(e)}"), 0)
                        loading_dialog.dismiss()
                
                thread = threading.Thread(target=do_add_bill)
                thread.daemon = True
                thread.start()
                
            except ValueError:
                self._show_error("Invalid amount or date format")
            except Exception as e:
                self._show_error(f"Error: {str(e)}")
        
        add_btn = ModernButton(text='Add')
        add_btn.bind(on_press=add_bill)
        cancel_btn = ModernButton(text='Cancel')
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(cancel_btn)
        
        box.add_widget(Label(text='Add New Bill', size_hint_y=None, height=dp(32),
                            font_size=dp(16), bold=True))
        box.add_widget(name_input)
        box.add_widget(amount_input)
        box.add_widget(due_input)
        box.add_widget(btn_layout)
        
        dialog = Popup(title='New Bill',
                      content=box,
                      size_hint=(0.9, 0.5))
        dialog.open()
    
    def _finish_add_bill(self, dialog, loading_dialog):
        """Finish adding bill and refresh list"""
        loading_dialog.dismiss()
        dialog.dismiss()
        self.on_enter()
        self._show_success("Bill added!")
    
        
        dialog = Popup(title='New Bill',
                      content=box,
                      size_hint=(0.9, 0.5))
        dialog.open()
    
    def _show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=message, color=Colors.ERROR))
        btn = ModernButton(text='OK')
        content.add_widget(btn)
        
        popup = Popup(title='Error', content=content, size_hint=(0.8, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def _show_success(self, message):
        """Show success popup"""
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=message, color=Colors.SUCCESS))
        btn = ModernButton(text='OK')
        content.add_widget(btn)
        
        popup = Popup(title='Success', content=content, size_hint=(0.8, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()


# ==========================================
# SCREEN 8: MEALS
# ==========================================

class MealsScreen(Screen):
    """Meal planning screen"""
    
    def __init__(self, api_client: APIClient, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.name = 'meals'
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        back_btn = ModernButton(text='← Back', size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(back_btn)
        
        title = Label(text='🍽️ Meals', size_hint_y=None, height=dp(50),
                     font_size=dp(20), bold=True, color=Colors.TEXT_PRIMARY)
        layout.add_widget(title)
        
        # Add meal button
        add_btn = ModernButton(text='+ Add Meal')
        add_btn.bind(on_press=self._show_add_meal_dialog)
        layout.add_widget(add_btn)
        
        self.meals_list = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.meals_list.bind(minimum_height=self.meals_list.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.meals_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Load meals when screen is displayed"""
        self.meals_list.clear_widgets()
        meals = self.api_client.get_meals()
        
        if not meals:
            self.meals_list.add_widget(Label(text='No meals planned!', 
                                            color=Colors.TEXT_SECONDARY))
            return
        
        for meal in meals:
            card = ModernCard(size_hint_y=None, height=dp(80))
            inner = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
            
            name = Label(text=meal.get('name', ''),
                        size_hint_y=None, height=dp(24),
                        font_size=dp(14), bold=True, color=Colors.TEXT_PRIMARY)
            date = Label(text=f"Date: {meal.get('date', '')}",
                        size_hint_y=None, height=dp(20),
                        font_size=dp(12), color=Colors.TEXT_SECONDARY)
            meal_type = Label(text=f"Type: {meal.get('meal_type', 'unknown')}",
                             size_hint_y=None, height=dp(20),
                             font_size=dp(12), color=Colors.TEXT_SECONDARY)
            
            inner.add_widget(name)
            inner.add_widget(date)
            inner.add_widget(meal_type)
            card.add_widget(inner)
            self.meals_list.add_widget(card)
    
    def _show_add_meal_dialog(self, instance):
        """Show dialog to add new meal"""
        box = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        
        name_input = TextInput(hint_text='Meal name', size_hint_y=None, height=dp(48),
                              multiline=False)
        date_input = TextInput(hint_text='Date (YYYY-MM-DD)', size_hint_y=None, height=dp(48),
                              multiline=False)
        type_spinner = Spinner(
            text='breakfast',
            values=('breakfast', 'lunch', 'dinner', 'snack'),
            size_hint_y=None,
            height=dp(48)
        )
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        
        def add_meal(btn):
            try:
                if not name_input.text or not date_input.text:
                    self._show_error("Please fill all fields")
                    return
                
                # Show loading dialog
                loading_dialog = LoadingDialog.show('Adding meal...')
                
                def do_add_meal():
                    """Run in background thread"""
                    try:
                        self.api_client.add_meal(
                            date=date_input.text,
                            meal_type=type_spinner.text,
                            name=name_input.text
                        )
                        # Schedule main thread update
                        Clock.schedule_once(lambda dt: self._finish_add_meal(dialog, loading_dialog), 0)
                    except Exception as e:
                        Clock.schedule_once(lambda dt: self._show_error(f"Error: {str(e)}"), 0)
                        loading_dialog.dismiss()
                
                thread = threading.Thread(target=do_add_meal)
                thread.daemon = True
                thread.start()
                
            except Exception as e:
                self._show_error(f"Error: {str(e)}")
        
        add_btn = ModernButton(text='Add')
        add_btn.bind(on_press=add_meal)
        cancel_btn = ModernButton(text='Cancel')
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())
        
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(cancel_btn)
        
        box.add_widget(Label(text='Add New Meal', size_hint_y=None, height=dp(32),
                            font_size=dp(16), bold=True))
        box.add_widget(name_input)
        box.add_widget(date_input)
        box.add_widget(type_spinner)
        box.add_widget(btn_layout)
        
        dialog = Popup(title='New Meal',
                      content=box,
                      size_hint=(0.9, 0.6))
        dialog.open()
    
    def _finish_add_meal(self, dialog, loading_dialog):
        """Finish adding meal and refresh list"""
        loading_dialog.dismiss()
        dialog.dismiss()
        self.on_enter()
        self._show_success("Meal added!")
    
    def _show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=message, color=Colors.ERROR))
        btn = ModernButton(text='OK')
        content.add_widget(btn)
        
        popup = Popup(title='Error', content=content, size_hint=(0.8, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def _show_success(self, message):
        """Show success popup"""
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=message, color=Colors.SUCCESS))
        btn = ModernButton(text='OK')
        content.add_widget(btn)
        
        popup = Popup(title='Success', content=content, size_hint=(0.8, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()


# ==========================================
# SCREEN 9: FAMILY MEMBERS
# ==========================================

class FamilyScreen(Screen):
    """Family members management screen"""
    
    def __init__(self, api_client: APIClient, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.name = 'family'
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        back_btn = ModernButton(text='← Back', size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(back_btn)
        
        title = Label(text='👥 Family', size_hint_y=None, height=dp(50),
                     font_size=dp(20), bold=True, color=Colors.TEXT_PRIMARY)
        layout.add_widget(title)
        
        self.family_list = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.family_list.bind(minimum_height=self.family_list.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.family_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Load family members when screen is displayed"""
        self.family_list.clear_widgets()
        members = self.api_client.get_family_members()
        
        if not members:
            self.family_list.add_widget(Label(text='No family members found!', 
                                             color=Colors.TEXT_SECONDARY))
            return
        
        for member in members:
            card = ModernCard(size_hint_y=None, height=dp(70))
            inner = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
            
            name = Label(text=member.get('name', ''),
                        size_hint_y=None, height=dp(24),
                        font_size=dp(14), bold=True, color=Colors.TEXT_PRIMARY)
            role = Label(text=f"Role: {member.get('role', 'member')}",
                        size_hint_y=None, height=dp(20),
                        font_size=dp(12), color=Colors.TEXT_SECONDARY)
            
            inner.add_widget(name)
            inner.add_widget(role)
            card.add_widget(inner)
            self.family_list.add_widget(card)


# ==========================================
# SCREEN 10: SETTINGS
# ==========================================

class SettingsScreen(Screen):
    """Settings and configuration screen"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'settings'
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(12))
        
        back_btn = ModernButton(text='← Back', size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(back_btn)
        
        title = Label(text='⚙️ Settings', size_hint_y=None, height=dp(50),
                     font_size=dp(20), bold=True, color=Colors.TEXT_PRIMARY)
        layout.add_widget(title)
        
        scroll = ScrollView()
        settings_layout = BoxLayout(orientation='vertical', spacing=dp(16), 
                                   size_hint_y=None, padding=dp(12))
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        # API URL Setting
        api_label = Label(text='API Server URL', size_hint_y=None, height=dp(32),
                         font_size=dp(14), bold=True, color=Colors.TEXT_PRIMARY)
        self.api_url_input = TextInput(text='http://localhost:5000',
                                       size_hint_y=None, height=dp(48),
                                       multiline=False)
        
        # Cache TTL Setting
        cache_label = Label(text='Cache TTL (minutes)', size_hint_y=None, height=dp(32),
                           font_size=dp(14), bold=True, color=Colors.TEXT_PRIMARY)
        self.cache_ttl_input = TextInput(text='60', size_hint_y=None, height=dp(48),
                                        multiline=False, input_filter='int')
        
        # Save button
        save_btn = ModernButton(text='Save Settings', size_hint_y=None, height=dp(48))
        save_btn.bind(on_press=self._save_settings)
        
        # Test connection button
        test_btn = ModernButton(text='Test Connection', size_hint_y=None, height=dp(48))
        test_btn.bind(on_press=self._test_connection)
        
        # About info
        about_label = Label(text='Family Manager v0.1', size_hint_y=None, height=dp(32),
                           font_size=dp(12), color=Colors.TEXT_SECONDARY)
        
        settings_layout.add_widget(api_label)
        settings_layout.add_widget(self.api_url_input)
        settings_layout.add_widget(cache_label)
        settings_layout.add_widget(self.cache_ttl_input)
        settings_layout.add_widget(save_btn)
        settings_layout.add_widget(test_btn)
        settings_layout.add_widget(Label(size_hint_y=None, height=dp(32)))
        settings_layout.add_widget(about_label)
        
        scroll.add_widget(settings_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _save_settings(self, instance):
        """Save settings and apply changes"""
        try:
            # Update API client base URL
            self.app.api_client.base_url = self.api_url_input.text
            
            # Update cache TTL
            ttl = int(self.cache_ttl_input.text)
            self.app.api_client.cache_ttl = ttl
            
            self._show_success("Settings saved!")
        except ValueError:
            self._show_error("Invalid cache TTL value (must be integer)")
        except Exception as e:
            self._show_error(f"Error: {str(e)}")
    
    def _test_connection(self, instance):
        """Test connection to API server"""
        # Show loading dialog
        loading_dialog = LoadingDialog.show('Testing connection...')
        
        def do_test():
            """Run test in background thread"""
            try:
                is_reachable, message = self.app.api_client.test_server_connection()
                Clock.schedule_once(lambda dt: self._finish_test(loading_dialog, message), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(f"Test failed: {str(e)}"), 0)
                loading_dialog.dismiss()
        
        thread = threading.Thread(target=do_test)
        thread.daemon = True
        thread.start()
    
    def _finish_test(self, loading_dialog, message):
        """Finish connection test"""
        loading_dialog.dismiss()
        if '✅' in message:
            self._show_success(message)
        else:
            self._show_error(message)
    
    def _show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=message, color=Colors.ERROR))
        btn = ModernButton(text='OK')
        content.add_widget(btn)
        
        popup = Popup(title='Error', content=content, size_hint=(0.8, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def _show_success(self, message):
        """Show success popup"""
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=message, color=Colors.SUCCESS))
        btn = ModernButton(text='OK')
        content.add_widget(btn)
        
        popup = Popup(title='Success', content=content, size_hint=(0.8, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()


# ==========================================
# MAIN APP CLASS
# ==========================================

class FamilyManagerApp(App):
    """Main Kivy application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client = APIClient(base_url="http://localhost:5000")
    
    def build(self):
        """Build the app UI"""
        self.title = "Family Manager"
        
        # Create screen manager
        sm = ScreenManager(transition=FadeTransition())
        
        # Add all screens (10 total)
        sm.add_widget(DashboardScreen(self.api_client))
        sm.add_widget(InventoryScreen(self.api_client))
        sm.add_widget(ShoppingScreen(self.api_client))
        sm.add_widget(ChoresScreen(self.api_client))
        sm.add_widget(TasksScreen(self.api_client))
        sm.add_widget(NotificationsScreen(self.api_client))
        sm.add_widget(BillsScreen(self.api_client))
        sm.add_widget(MealsScreen(self.api_client))
        sm.add_widget(FamilyScreen(self.api_client))
        sm.add_widget(SettingsScreen(self))  # Pass app instance, not api_client
        
        # Set initial screen
        sm.current = 'dashboard'
        
        return sm


if __name__ == '__main__':
    FamilyManagerApp().run()
