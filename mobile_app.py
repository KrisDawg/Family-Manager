from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.clock import Clock
import sqlite3
import os
from datetime import datetime, timedelta

# Optional imports for desktop development
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

# Set window size for development (will be ignored on mobile)
if platform != 'android':
    Window.size = (400, 700)

class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'family_manager_mobile.db')
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                qty REAL DEFAULT 1,
                unit TEXT,
                exp_date TEXT,
                location TEXT
            )
        ''')

        # Meals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                name TEXT NOT NULL,
                time TEXT DEFAULT '',
                ingredients TEXT,
                recipe TEXT
            )
        ''')

        # Shopping list table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                qty REAL DEFAULT 1,
                checked INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    def get_inventory(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_inventory_item(self, name, category, qty, unit, exp_date, location):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (name, category, qty, unit, exp_date, location)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, category, qty, unit, exp_date, location))
        conn.commit()
        conn.close()

    def get_shopping_list(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shopping_list ORDER BY checked, item")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_shopping_item(self, item, qty):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO shopping_list (item, qty, checked)
            VALUES (?, ?, 0)
        ''', (item, qty))
        conn.commit()
        conn.close()

    def toggle_shopping_item(self, item_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE shopping_list SET checked = 1 - checked WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

    def delete_shopping_item(self, item_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shopping_list WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

class InventoryScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint_y=0.1)
        title = Label(text='Inventory', font_size=24, bold=True)
        header.add_widget(title)
        layout.add_widget(header)

        # Buttons layout
        buttons_layout = BoxLayout(size_hint_y=0.1, spacing=5)

        # Add item button
        add_btn = Button(text='+ Add Item', background_color=(0.2, 0.8, 0.2, 1))
        add_btn.bind(on_press=self.show_add_dialog)
        buttons_layout.add_widget(add_btn)

        # Camera OCR button
        camera_btn = Button(text='📷 OCR Scan', background_color=(0.9, 0.6, 0.2, 1))
        camera_btn.bind(on_press=self.open_camera)
        buttons_layout.add_widget(camera_btn)

        layout.add_widget(buttons_layout)

        # Inventory list (scrollable)
        scroll = ScrollView(size_hint=(1, 0.8))
        self.inventory_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.inventory_grid.bind(minimum_height=self.inventory_grid.setter('height'))
        scroll.add_widget(self.inventory_grid)
        layout.add_widget(scroll)

        self.add_widget(layout)
        self.refresh_inventory()

    def refresh_inventory(self):
        self.inventory_grid.clear_widgets()
        items = self.db_manager.get_inventory()

        if not items:
            self.inventory_grid.add_widget(Label(text='No items in inventory', italic=True))
            return

        for item in items:
            item_layout = BoxLayout(size_hint_y=None, height=60, padding=5)
            item_layout.add_widget(Label(text=f"{item[1]} ({item[2]} {item[3]})", size_hint_x=0.7))
            item_layout.add_widget(Label(text=item[5] or 'No location', size_hint_x=0.3, italic=True))
            self.inventory_grid.add_widget(item_layout)

    def show_add_dialog(self, instance):
        # Simple add dialog for now
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.name_input = TextInput(hint_text='Item name', multiline=False)
        self.category_input = TextInput(hint_text='Category (optional)', multiline=False)
        self.qty_input = TextInput(hint_text='Quantity', text='1', multiline=False)
        self.unit_input = TextInput(hint_text='Unit', multiline=False)

        content.add_widget(self.name_input)
        content.add_widget(self.category_input)
        content.add_widget(self.qty_input)
        content.add_widget(self.unit_input)

        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        cancel_btn = Button(text='Cancel')
        save_btn = Button(text='Save', background_color=(0.2, 0.8, 0.2, 1))

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        content.add_widget(btn_layout)

        from kivy.uix.popup import Popup
        self.popup = Popup(title='Add Inventory Item', content=content, size_hint=(0.9, 0.7))

        cancel_btn.bind(on_press=self.popup.dismiss)
        save_btn.bind(on_press=self.save_item)

        self.popup.open()

    def save_item(self, instance):
        name = self.name_input.text.strip()
        if not name:
            return

        category = self.category_input.text.strip() or None
        try:
            qty = float(self.qty_input.text or 1)
        except ValueError:
            qty = 1.0
        unit = self.unit_input.text.strip() or None

        self.db_manager.add_inventory_item(name, category, qty, unit, None, None)
        self.popup.dismiss()
        self.refresh_inventory()

    def open_camera(self, instance):
        self.manager.current = 'camera'

class MealsScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint_y=0.1)
        title = Label(text='Meals', font_size=24, bold=True)
        header.add_widget(title)
        layout.add_widget(header)

        # Simple meals list for now
        scroll = ScrollView(size_hint=(1, 0.9))
        self.meals_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.meals_layout.bind(minimum_height=self.meals_layout.setter('height'))

        # Sample meals
        meals = [
            {'date': '2026-01-16', 'type': 'Breakfast', 'name': 'Oatmeal with fruit'},
            {'date': '2026-01-16', 'type': 'Lunch', 'name': 'Grilled chicken salad'},
            {'date': '2026-01-16', 'type': 'Dinner', 'name': 'Pasta with vegetables'}
        ]

        for meal in meals:
            meal_item = BoxLayout(size_hint_y=None, height=60, padding=5, orientation='vertical')
            meal_item.add_widget(Label(text=f"{meal['type']}: {meal['name']}", bold=True))
            meal_item.add_widget(Label(text=f"Date: {meal['date']}", font_size=12, color=(0.5, 0.5, 0.5, 1)))
            self.meals_layout.add_widget(meal_item)

        scroll.add_widget(self.meals_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)

class ShoppingScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint_y=0.1)
        title = Label(text='Shopping List', font_size=24, bold=True)
        header.add_widget(title)
        layout.add_widget(header)

        # Add item button
        add_btn = Button(text='+ Add Item', size_hint_y=0.1, background_color=(0.2, 0.8, 0.2, 1))
        add_btn.bind(on_press=self.show_add_dialog)
        layout.add_widget(add_btn)

        # Shopping list (scrollable)
        scroll = ScrollView(size_hint=(1, 0.8))
        self.shopping_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.shopping_grid.bind(minimum_height=self.shopping_grid.setter('height'))
        scroll.add_widget(self.shopping_grid)
        layout.add_widget(scroll)

        self.add_widget(layout)
        self.refresh_shopping_list()

    def refresh_shopping_list(self):
        self.shopping_grid.clear_widgets()
        items = self.db_manager.get_shopping_list()

        if not items:
            self.shopping_grid.add_widget(Label(text='No items in shopping list', italic=True))
            return

        for item in items:
            item_layout = BoxLayout(size_hint_y=None, height=60, padding=5)
            item_id, item_name, qty, checked = item

            # Checkbox-like button
            check_btn = Button(text='✓' if checked else '○', size_hint_x=0.2, background_color=(0.2, 0.8, 0.2, 1) if checked else (0.8, 0.8, 0.8, 1))
            check_btn.bind(on_press=lambda x, iid=item_id: self.toggle_item(iid))

            # Item text
            item_text = Label(text=f"{item_name} ({qty})", size_hint_x=0.6, strikethrough=checked)

            # Delete button
            delete_btn = Button(text='×', size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
            delete_btn.bind(on_press=lambda x, iid=item_id: self.delete_item(iid))

            item_layout.add_widget(check_btn)
            item_layout.add_widget(item_text)
            item_layout.add_widget(delete_btn)
            self.shopping_grid.add_widget(item_layout)

    def show_add_dialog(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.item_input = TextInput(hint_text='Item name', multiline=False)
        self.qty_input = TextInput(hint_text='Quantity', text='1', multiline=False)

        content.add_widget(self.item_input)
        content.add_widget(self.qty_input)

        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        cancel_btn = Button(text='Cancel')
        save_btn = Button(text='Save', background_color=(0.2, 0.8, 0.2, 1))

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        content.add_widget(btn_layout)

        from kivy.uix.popup import Popup
        self.popup = Popup(title='Add Shopping Item', content=content, size_hint=(0.9, 0.5))

        cancel_btn.bind(on_press=self.popup.dismiss)
        save_btn.bind(on_press=self.save_shopping_item)

        self.popup.open()

    def save_shopping_item(self, instance):
        item = self.item_input.text.strip()
        if not item:
            return

        try:
            qty = float(self.qty_input.text or 1)
        except ValueError:
            qty = 1.0

        self.db_manager.add_shopping_item(item, qty)
        self.popup.dismiss()
        self.refresh_shopping_list()

    def toggle_item(self, item_id):
        self.db_manager.toggle_shopping_item(item_id)
        self.refresh_shopping_list()

    def delete_item(self, item_id):
        self.db_manager.delete_shopping_item(item_id)
        self.refresh_shopping_list()

class CameraScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint_y=0.1)
        title = Label(text='Camera OCR', font_size=24, bold=True)
        header.add_widget(title)
        layout.add_widget(header)

        # Camera view (try to initialize, fallback to placeholder)
        try:
            self.camera = Camera(play=True, size_hint=(1, 0.7))
            self.camera.resolution = (640, 480)
            layout.add_widget(self.camera)
            self.camera_available = True
        except Exception as e:
            # Fallback for systems without camera
            placeholder = BoxLayout(size_hint=(1, 0.7))
            placeholder.add_widget(Label(text='Camera not available\n(simulated on desktop)', color=(0.7, 0.7, 0.7, 1)))
            layout.add_widget(placeholder)
            self.camera_available = False

        # Control buttons
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)

        capture_btn = Button(text='Capture & OCR', background_color=(0.2, 0.8, 0.2, 1))
        capture_btn.bind(on_press=self.capture_and_ocr)
        btn_layout.add_widget(capture_btn)

        back_btn = Button(text='Back', background_color=(0.8, 0.2, 0.2, 1))
        back_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(back_btn)

        layout.add_widget(btn_layout)

        self.add_widget(layout)

    def capture_and_ocr(self, instance):
        if not self.camera_available:
            # Simulate OCR for demo purposes
            extracted_text = "Demo OCR: Milk 2L, Bread 1 loaf, Eggs 12 count, Cheese 500g"
            self.show_ocr_results(extracted_text)
            return

        if not self.camera.texture:
            return

        # Capture current frame
        texture = self.camera.texture
        
        # Save image using Kivy's texture.save() method (Android compatible)
        if platform == 'android':
            # Use app's storage directory on Android
            from android.storage import app_storage_path
            temp_path = os.path.join(app_storage_path(), 'captured_image.png')
        else:
            temp_path = '/tmp/captured_image.png'
        
        # Save texture directly (no OpenCV needed)
        texture.save(temp_path, flipped=False)

        # Perform OCR (simplified - would need pytesseract)
        extracted_text = self.perform_ocr(temp_path)

        # Show results
        self.show_ocr_results(extracted_text)

    def perform_ocr(self, image_path):
        # Simplified OCR - in real implementation would use pytesseract
        # For now, just return a placeholder
        return "Sample OCR Text: Milk 2L, Bread 1 loaf, Eggs 12 count"

    def show_ocr_results(self, text):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        result_label = Label(text='Extracted Text:', bold=True)
        content.add_widget(result_label)

        text_area = TextInput(text=text, readonly=True, size_hint_y=0.6)
        content.add_widget(text_area)

        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        use_btn = Button(text='Use for Inventory', background_color=(0.2, 0.8, 0.2, 1))
        close_btn = Button(text='Close')

        btn_layout.add_widget(use_btn)
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)

        from kivy.uix.popup import Popup
        popup = Popup(title='OCR Results', content=content, size_hint=(0.9, 0.8))

        use_btn.bind(on_press=lambda x: self.process_ocr_text(text, popup))
        close_btn.bind(on_press=popup.dismiss)

        popup.open()

    def process_ocr_text(self, text, popup):
        # Simple parsing - split by commas and create inventory items
        items = [item.strip() for item in text.split(',') if item.strip()]

        for item_text in items:
            # Very basic parsing - in real app would be more sophisticated
            if ' ' in item_text:
                parts = item_text.split()
                name = ' '.join(parts[:-1])
                qty = 1.0
                unit = 'each'

                # Try to extract quantity
                try:
                    if parts[-1].isdigit():
                        qty = float(parts[-1])
                        unit = 'count' if qty > 1 else 'each'
                    elif any(char.isdigit() for char in parts[-1]):
                        # Handle cases like "2L", "1loaf"
                        qty_str = ''.join([c for c in parts[-1] if c.isdigit()])
                        if qty_str:
                            qty = float(qty_str)
                            unit = ''.join([c for c in parts[-1] if not c.isdigit()])
                except:
                    pass

                self.db_manager.add_inventory_item(name, 'OCR Import', qty, unit, None, None)

        popup.dismiss()

        # Switch to inventory screen
        self.manager.current = 'inventory'

    def go_back(self, instance):
        self.manager.current = 'inventory'

class DashboardScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint_y=0.1)
        title = Label(text='Dashboard', font_size=24, bold=True)
        header.add_widget(title)
        layout.add_widget(header)

        # Stats cards
        stats_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.9))

        # Inventory count
        inventory_count = len(self.db_manager.get_inventory())
        inv_card = BoxLayout(orientation='vertical', padding=10, size_hint_y=None, height=80)
        inv_card.add_widget(Label(text='Total Items', font_size=16, bold=True))
        inv_card.add_widget(Label(text=str(inventory_count), font_size=24, color=(0.2, 0.8, 0.2, 1)))
        stats_layout.add_widget(inv_card)

        # Today's date
        today_card = BoxLayout(orientation='vertical', padding=10, size_hint_y=None, height=80)
        today_card.add_widget(Label(text="Today's Date", font_size=16, bold=True))
        today_card.add_widget(Label(text=datetime.now().strftime('%Y-%m-%d'), font_size=18))
        stats_layout.add_widget(today_card)

        layout.add_widget(stats_layout)
        self.add_widget(layout)

class FamilyManagerMobileApp(App):
    def build(self):
        self.db_manager = DatabaseManager()

        # Screen manager for navigation
        sm = ScreenManager()

        # Add screens
        sm.add_widget(DashboardScreen(self.db_manager, name='dashboard'))
        sm.add_widget(InventoryScreen(self.db_manager, name='inventory'))
        sm.add_widget(MealsScreen(self.db_manager, name='meals'))
        sm.add_widget(ShoppingScreen(self.db_manager, name='shopping'))
        sm.add_widget(CameraScreen(self.db_manager, name='camera'))

        # Bottom navigation
        from kivy.uix.boxlayout import BoxLayout
        nav_layout = BoxLayout(size_hint_y=0.1, spacing=2, padding=2)

        dashboard_btn = Button(text='Dashboard', font_size=12)
        dashboard_btn.bind(on_press=lambda x: setattr(sm, 'current', 'dashboard'))

        inventory_btn = Button(text='Inventory', font_size=12)
        inventory_btn.bind(on_press=lambda x: setattr(sm, 'current', 'inventory'))

        meals_btn = Button(text='Meals', font_size=12)
        meals_btn.bind(on_press=lambda x: setattr(sm, 'current', 'meals'))

        shopping_btn = Button(text='Shopping', font_size=12)
        shopping_btn.bind(on_press=lambda x: setattr(sm, 'current', 'shopping'))

        nav_layout.add_widget(dashboard_btn)
        nav_layout.add_widget(inventory_btn)
        nav_layout.add_widget(meals_btn)
        nav_layout.add_widget(shopping_btn)

        # Main layout
        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(sm)
        main_layout.add_widget(nav_layout)

        return main_layout

if __name__ == '__main__':
    FamilyManagerMobileApp().run()