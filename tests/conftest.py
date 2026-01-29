"""
Shared test configuration and fixtures for Family Household Manager
"""

import os
import sys
import pytest
import tempfile
import sqlite3
from pathlib import Path

# Add source directories to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "family_manager"))

@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root path"""
    return project_root

@pytest.fixture(scope="session")
def test_db_path():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    # Initialize test database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create test tables
        cursor.execute('''
            CREATE TABLE inventory (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                qty REAL NOT NULL DEFAULT 1,
                unit TEXT DEFAULT 'each',
                exp_date TEXT,
                location TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE meals (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                meal_type TEXT,
                name TEXT NOT NULL,
                ingredients TEXT,
                recipe TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE shopping_list (
                id INTEGER PRIMARY KEY,
                item TEXT NOT NULL,
                qty REAL DEFAULT 1,
                checked INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

        yield db_path

    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

@pytest.fixture
def sample_inventory_data():
    """Sample inventory data for testing"""
    return [
        {"name": "Milk", "category": "dairy", "qty": 2.0, "unit": "liters", "exp_date": "2024-02-01"},
        {"name": "Bread", "category": "bakery", "qty": 1.0, "unit": "loaf", "exp_date": "2024-01-25"},
        {"name": "Eggs", "category": "dairy", "qty": 12.0, "unit": "each", "exp_date": "2024-02-05"},
        {"name": "Chicken Breast", "category": "meat", "qty": 1.5, "unit": "kg", "exp_date": "2024-01-22"}
    ]

@pytest.fixture
def mock_ai_config():
    """Mock AI configuration for testing"""
    return {
        "gemini_key": "test_key_123",
        "meal_planning_api": "gemini",
        "cache_settings": {"enabled": False},
        "preferences": {
            "family_size": 4,
            "budget_level": "medium",
            "meal_types": ["breakfast", "lunch", "dinner"]
        }
    }

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables and configurations"""
    # Mock environment variables
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")  # For headless Qt testing
    monkeypatch.setenv("KIVY_NO_ARGS", "1")  # For headless Kivy testing

    # Mock config file
    mock_config = {
        "gemini_key": "test_key_123",
        "openai_key": "",
        "spoonacular_key": "",
        "meal_planning_api": "gemini"
    }

    # Create temporary config file
    import json
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_config, f)
        config_path = f.name

    monkeypatch.setattr('builtins.open', lambda *args, **kwargs: open(config_path, *args, **kwargs))

    yield

    # Cleanup
    if os.path.exists(config_path):
        os.unlink(config_path)

# Qt-specific test setup
def pytest_configure(config):
    """Configure pytest for Qt testing"""
    try:
        import pytestqt
        config.addinivalue_line("markers", "qt: mark test as requiring Qt")
    except ImportError:
        pass

def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle Qt tests"""
    for item in items:
        # Mark tests that import Qt modules
        if any(module in str(item.fspath) for module in ['PyQt6', 'kivy']):
            item.add_marker(pytest.mark.qt)

        # Mark slow tests
        if 'slow' in item.keywords or 'integration' in item.keywords:
            item.add_marker(pytest.mark.slow)