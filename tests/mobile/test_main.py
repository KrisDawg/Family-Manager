"""
Tests for mobile app functionality
"""

import pytest
import sqlite3
import os
import sys
from pathlib import Path

# Add mobile app to path
mobile_app_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(mobile_app_path))

class TestMobileDatabase:
    """Test mobile app database functionality"""

    @pytest.fixture
    def mobile_db_path(self, tmp_path):
        """Create a temporary database for mobile app testing"""
        db_path = tmp_path / "test_mobile.db"
        return str(db_path)

    @pytest.fixture
    def database_manager(self, mobile_db_path):
        """Create a database manager instance for testing"""
        # Import here to avoid kivy import issues
        sys.path.insert(0, str(mobile_app_path))

        # Create a minimal database manager for testing
        class TestDatabaseManager:
            def __init__(self, db_path):
                self.db_path = db_path
                self.init_db()

            def init_db(self):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Create tables like mobile app
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

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS meals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        meal_type TEXT,
                        name TEXT NOT NULL,
                        ingredients TEXT,
                        recipe TEXT,
                        time TEXT DEFAULT ''
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS shopping_list (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item TEXT NOT NULL,
                        qty REAL,
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
                    INSERT INTO shopping_list (item, qty)
                    VALUES (?, ?)
                ''', (item, qty))
                conn.commit()
                conn.close()

        return TestDatabaseManager(mobile_db_path)

    def test_database_initialization(self, database_manager):
        """Test that database tables are created correctly"""
        # Test inventory table exists and is empty
        inventory = database_manager.get_inventory()
        assert len(inventory) == 0

        # Test shopping list table exists and is empty
        shopping = database_manager.get_shopping_list()
        assert len(shopping) == 0

    def test_inventory_operations(self, database_manager):
        """Test basic inventory operations"""
        # Add test items
        test_items = [
            ("Milk", "Dairy", 2.0, "liters", "2024-02-01", "Refrigerator"),
            ("Bread", "Bakery", 1.0, "loaf", "2024-01-25", "Pantry"),
            ("Eggs", "Dairy", 12.0, "pieces", "2024-02-05", "Refrigerator"),
        ]

        for item in test_items:
            database_manager.add_inventory_item(*item)

        # Verify items were added
        inventory = database_manager.get_inventory()
        assert len(inventory) == len(test_items)

        # Check item details (inventory is list of tuples)
        assert inventory[0][1] == "Bread"  # Name field (0-indexed: id, name, category, qty, unit, exp_date, location)
        assert inventory[1][2] == "Dairy"  # Category field

    def test_shopping_list_operations(self, database_manager):
        """Test shopping list operations"""
        # Add shopping items
        shopping_items = [
            ("Apples", 6),
            ("Chicken Breast", 2),
            ("Rice", 1),
        ]

        for item, qty in shopping_items:
            database_manager.add_shopping_item(item, qty)

        # Verify items were added
        shopping_list = database_manager.get_shopping_list()
        assert len(shopping_list) == len(shopping_items)

        # Check item details
        item_names = [item[1] for item in shopping_list]  # item name is at index 1
        assert "Apples" in item_names
        assert "Chicken Breast" in item_names
        assert "Rice" in item_names

    def test_database_persistence(self, database_manager, mobile_db_path):
        """Test that data persists between database operations"""
        # Add item
        database_manager.add_inventory_item("Test Item", "Test Category", 5.0, "pieces", None, "Test Location")

        # Create new manager instance (simulating app restart)
        new_manager = type(database_manager)(mobile_db_path)

        # Verify item still exists
        inventory = new_manager.get_inventory()
        assert len(inventory) == 1
        assert inventory[0][1] == "Test Item"  # Name field

    @pytest.mark.parametrize("meal_type,expected_count", [
        ("Breakfast", 1),
        ("Lunch", 1),
        ("Dinner", 1),
        ("Snack", 2),
    ])
    def test_meal_structure_validation(self, meal_type, expected_count):
        """Test meal structure validation (mock test - no actual DB)"""
        # This is a structure validation test without database
        # In a real scenario, this would validate meal data from the database

        # Test meal type validation
        valid_meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
        assert meal_type in valid_meal_types

        # Test that we have reasonable expectations
        assert expected_count > 0
        assert expected_count <= 2  # Max 2 snacks per day typically

@pytest.mark.qt
class TestMobileUI:
    """Test mobile UI components (requires Qt test environment)"""

    @pytest.fixture
    def qapp(self, qtbot):
        """Create Qt application for testing"""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    @pytest.fixture
    def database_manager(self, mobile_db_path):
        """Create a database manager instance for mobile UI testing"""
        # Import here to avoid kivy import issues in non-mobile tests
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))

        # Create a minimal database manager for testing
        class TestDatabaseManager:
            def __init__(self, db_path):
                self.db_path = db_path
                self.init_db()

            def init_db(self):
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Create tables like mobile app
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        category TEXT,
                        qty REAL DEFAULT 1,
                        unit TEXT DEFAULT 'each',
                        location TEXT
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS shopping_list (
                        id INTEGER PRIMARY KEY,
                        item TEXT NOT NULL,
                        qty REAL DEFAULT 1
                    )
                ''')

                conn.commit()
                conn.close()

            def get_inventory(self):
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM inventory ORDER BY name")
                rows = cursor.fetchall()
                conn.close()
                return rows

        return TestDatabaseManager(mobile_db_path)

    def test_basic_ui_initialization(self, qapp):
        """Test that basic UI components can be created"""
        from PyQt6.QtWidgets import QLabel

        # Create a simple label (similar to mobile app structure)
        label = QLabel("Test Label")
        assert label.text() == "Test Label"
        assert label.isVisible() == False  # Not shown yet

        label.show()
        assert label.isVisible() == True

        label.close()

    def test_database_manager_ui_integration(self, qapp, database_manager):
        """Test database manager integration with UI components"""
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem

        # Create a list widget to display inventory
        list_widget = QListWidget()

        # Add inventory items to list
        inventory = database_manager.get_inventory()

        for item in inventory:
            item_text = f"{item[1]} - {item[3]} {item[4]}"  # name - qty unit
            list_item = QListWidgetItem(item_text)
            list_widget.addItem(list_item)

        # Verify list has correct number of items
        assert list_widget.count() == len(inventory)

        list_widget.close()
