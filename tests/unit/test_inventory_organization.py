"""
Unit tests for inventory organization functionality
"""

import pytest
import sqlite3
from pathlib import Path

class TestInventoryOrganization:
    """Test cases for hierarchical inventory organization"""

    @pytest.fixture
    def db_connection(self, test_db_path):
        """Provide a database connection for testing"""
        conn = sqlite3.connect(test_db_path)
        conn.row_factory = sqlite3.Row

        # Clean database for each test
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory")
        cursor.execute("DELETE FROM meals")
        cursor.execute("DELETE FROM shopping_list")
        conn.commit()

        yield conn
        conn.close()

    def test_sample_inventory_data_structure(self, sample_inventory_data):
        """Test that sample inventory data has correct structure"""
        assert len(sample_inventory_data) > 0

        for item in sample_inventory_data:
            required_fields = ['name', 'category', 'qty', 'unit']
            for field in required_fields:
                assert field in item, f"Missing required field: {field}"
                assert item[field] is not None, f"Field {field} cannot be None"

            # Validate quantity is numeric and positive
            assert isinstance(item['qty'], (int, float)), "Quantity must be numeric"
            assert item['qty'] > 0, "Quantity must be positive"

    def test_inventory_hierarchy_sample_data(self, db_connection):
        """Test adding sample hierarchical inventory data"""

        sample_items = [
            {"name": "Whole Milk", "category": "🥬 Food & Groceries", "subcategory": "🥛 Dairy & Eggs",
             "qty": 1, "unit": "gallon", "location": "Refrigerator"},
            {"name": "Sharp Cheddar Cheese", "category": "🥬 Food & Groceries", "subcategory": "🥛 Dairy & Eggs",
             "qty": 8, "unit": "oz", "location": "Refrigerator"},
            {"name": "Chicken Breast", "category": "🥬 Food & Groceries", "subcategory": "🍖 Meat & Poultry",
             "qty": 2, "unit": "lbs", "location": "Freezer"},
            {"name": "Bananas", "category": "🥬 Food & Groceries", "subcategory": "🍎 Fruits",
             "qty": 6, "unit": "count", "location": "Counter"},
        ]

        # Add sample items to database
        cursor = db_connection.cursor()

        for item in sample_items:
            cursor.execute('''
                INSERT INTO inventory (name, category, qty, unit, location)
                VALUES (?, ?, ?, ?, ?)
            ''', (item['name'], item['category'], item['qty'], item['unit'], item['location']))

        db_connection.commit()

        # Verify items were added
        cursor.execute("SELECT COUNT(*) FROM inventory")
        count = cursor.fetchone()[0]
        assert count == len(sample_items)

        # Test category counts
        cursor.execute("SELECT category, COUNT(*) FROM inventory GROUP BY category ORDER BY category")
        category_counts = cursor.fetchall()

        assert len(category_counts) == 1  # All items are in "🥬 Food & Groceries"
        assert category_counts[0][0] == "🥬 Food & Groceries"
        assert category_counts[0][1] == len(sample_items)

    def test_inventory_queries_by_category(self, db_connection):
        """Test querying inventory items by category"""

        # Insert test data
        test_items = [
            ("Milk", "Dairy", 2.0, "liters"),
            ("Bread", "Bakery", 1.0, "loaf"),
            ("Chicken", "Meat", 1.5, "kg"),
            ("Apples", "Fruits", 6.0, "pieces"),
        ]

        cursor = db_connection.cursor()
        for item in test_items:
            cursor.execute('''
                INSERT INTO inventory (name, category, qty, unit)
                VALUES (?, ?, ?, ?)
            ''', item)

        db_connection.commit()

        # Test category filtering
        cursor.execute("SELECT name FROM inventory WHERE category = ? ORDER BY name", ("Dairy",))
        dairy_items = [row[0] for row in cursor.fetchall()]
        assert dairy_items == ["Milk"]

        cursor.execute("SELECT name FROM inventory WHERE category = ? ORDER BY name", ("Fruits",))
        fruit_items = [row[0] for row in cursor.fetchall()]
        assert fruit_items == ["Apples"]

        # Test count by category
        cursor.execute("SELECT category, COUNT(*) FROM inventory GROUP BY category ORDER BY category")
        results = cursor.fetchall()

        # Convert sqlite3.Row objects to tuples for comparison
        results_as_tuples = [(row[0], row[1]) for row in results]
        expected_categories = [("Bakery", 1), ("Dairy", 1), ("Fruits", 1), ("Meat", 1)]
        assert results_as_tuples == expected_categories

    def test_inventory_data_validation(self, db_connection):
        """Test inventory data validation and constraints"""

        cursor = db_connection.cursor()

        # Test valid data insertion
        cursor.execute('''
            INSERT INTO inventory (name, category, qty, unit)
            VALUES (?, ?, ?, ?)
        ''', ("Test Item", "Test Category", 5.0, "pieces"))

        db_connection.commit()

        # Verify insertion
        cursor.execute("SELECT * FROM inventory WHERE name = ?", ("Test Item",))
        item = cursor.fetchone()
        assert item is not None
        assert item['name'] == "Test Item"
        assert item['category'] == "Test Category"
        assert item['qty'] == 5.0
        assert item['unit'] == "pieces"

    def test_inventory_quantity_validation(self, db_connection):
        """Test inventory quantity validation and storage"""
        cursor = db_connection.cursor()

        # Test valid positive quantity
        cursor.execute('''
            INSERT INTO inventory (name, category, qty, unit)
            VALUES (?, ?, ?, ?)
        ''', ("Valid Item", "Test", 5.0, "pieces"))
        db_connection.commit()

        cursor.execute("SELECT qty FROM inventory WHERE name = ?", ("Valid Item",))
        result = cursor.fetchone()
        assert result[0] == 5.0

        # Test zero quantity (edge case)
        cursor.execute('''
            INSERT INTO inventory (name, category, qty, unit)
            VALUES (?, ?, ?, ?)
        ''', ("Zero Item", "Test", 0.0, "pieces"))
        db_connection.commit()

        cursor.execute("SELECT qty FROM inventory WHERE name = ?", ("Zero Item",))
        result = cursor.fetchone()
        assert result[0] == 0.0

        # Note: Database allows any numeric value. Application logic should validate.

        # Note: This test demonstrates that database-level constraints should be added
        # in a production environment for data integrity

    def test_inventory_location_tracking(self, db_connection):
        """Test inventory location tracking functionality"""

        test_items = [
            ("Refrigerator Item", "Dairy", "Refrigerator"),
            ("Pantry Item", "Dry Goods", "Pantry"),
            ("Freezer Item", "Frozen", "Freezer"),
        ]

        cursor = db_connection.cursor()

        for name, category, location in test_items:
            cursor.execute('''
                INSERT INTO inventory (name, category, location, qty, unit)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, category, location, 1.0, "each"))

        db_connection.commit()

        # Test location-based queries
        cursor.execute("SELECT name FROM inventory WHERE location = ? ORDER BY name", ("Refrigerator",))
        fridge_items = [row[0] for row in cursor.fetchall()]
        assert fridge_items == ["Refrigerator Item"]

        cursor.execute("SELECT location, COUNT(*) FROM inventory GROUP BY location ORDER BY location")
        location_counts = cursor.fetchall()
        assert len(location_counts) == 3

        # Verify all locations are represented
        locations = [row[0] for row in location_counts]
        assert "Refrigerator" in locations
        assert "Pantry" in locations
        assert "Freezer" in locations