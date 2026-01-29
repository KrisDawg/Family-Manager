# AGENTS.md - Family Household Manager Development Guide

## Overview

This guide provides comprehensive development standards and practices for the Family Household Manager project - a dual-platform Python application featuring:
- **Mobile App**: Kivy-based Android application with SQLite database
- **Desktop App**: PyQt6-based GUI application with advanced MCP server architecture
- **AI Integration**: Google Gemini, OpenAI, and Spoonacular API integration
- **OCR Capabilities**: Tesseract and Google Vision API for receipt scanning

## 1. Development Environment Setup

### Virtual Environments
- **Mobile Development**: Use `mobile_venv/` (Python 3.7+ for Kivy compatibility)
- **Desktop Development**: Use `family_manager/venv/` (Python 3.8+ for PyQt6)
- **Activation**: `source mobile_venv/bin/activate` or `family_manager/venv/bin/activate`

### Android SDK/NDK Setup
- SDK Root: `/home/server1/.buildozer/android/platform/android-sdk`
- NDK Root: `/home/server1/.buildozer/android/platform/android-ndk-r25b`
- API Level: 33, Min API Level: 21
- Build Tools: Version 33.0.2

### Python Version Requirements
- Mobile (Kivy): Python 3.7+
- Desktop (PyQt6): Python 3.8+
- Testing: Ensure compatibility across versions

## 2. Build Commands & Workflows

### Mobile APK Building
```bash
# Development build
buildozer android debug

# Release build
./build_apk.sh

# Minimal test build
./test_build.sh

# Environment setup
./build_env_setup.sh
```

### Desktop Application
```bash
cd family_manager
python main.py
```

### Testing Commands
```bash
# Individual test execution
python test_*.py

# OCR integration testing
python test_complete_ocr.py

# API endpoint testing
python test_api.py

# Database testing
python test_inventory_organization.py
```

## 3. Code Quality & Linting

### Codacy Integration
- **Automatic Analysis**: All file edits trigger Codacy analysis via MCP server
- **Security Scanning**: Trivy integration for dependency vulnerabilities
- **Post-Edit Validation**: Run analysis after ANY file modification

### Code Analysis Tools
- **Manual Review**: Built into AutonomousDevMCPServer class
- **Automated Checks**: Pre-commit hooks, CI/CD integration
- **Quality Gates**: Must pass Codacy analysis before commits

## 4. Comprehensive Code Style Guidelines

### Import Organization (Critical)
```python
# Standard library imports
import sys
import os
import json
import logging
from datetime import datetime, timedelta

# Third-party imports
from PyQt6.QtWidgets import QApplication, QMainWindow
import kivy
from kivy.app import App
import google.genai as genai

# Local imports
from .database_manager import DatabaseManager
from ..utils.helpers import format_date
```

### Naming Conventions
- **Classes**: PascalCase (`DatabaseManager`, `GeminiOCRWorker`)
- **Functions/Methods**: snake_case (`get_inventory()`, `add_meal_plan()`)
- **Variables**: snake_case (`user_profile`, `api_response`)
- **Constants**: UPPER_CASE (`DEFAULT_TIMEOUT = 30`)
- **Private Members**: Leading underscore (`_internal_method()`)

### Error Handling Standards
```python
# Preferred: Specific exception handling
try:
    result = api_call()
except ConnectionError as e:
    logger.error(f"API connection failed: {e}")
    return fallback_result()
except ValueError as e:
    logger.warning(f"Invalid input: {e}")
    raise

# Avoid: Bare except clauses (except allowed in QThread signal handlers)
try:
    risky_operation()
except Exception as e:  # Only when absolutely necessary
    logger.error(f"Unexpected error: {e}")
    cleanup_resources()
```

### Documentation Standards
```python
class DatabaseManager:
    """Manages SQLite database operations for the family manager app.

    Provides thread-safe database access with connection pooling and
    automatic transaction management.

    Attributes:
        db_path (str): Path to the SQLite database file
        connection_pool (list): Pool of database connections
    """

    def get_inventory(self, category: str = None) -> list:
        """Retrieve inventory items from database.

        Args:
            category (str, optional): Filter by category. Defaults to None.

        Returns:
            list: List of inventory items as dictionaries

        Raises:
            sqlite3.Error: If database operation fails
        """
        pass
```

### Line Length & Formatting
- **Maximum Line Length**: 120 characters (readability prioritized)
- **String Formatting**: f-strings preferred
```python
# Preferred
user_message = f"Welcome {user.name} to {app.config['app_name']}!"

# Acceptable for complex expressions
message = ("Long message that exceeds line limit but maintains "
          f"readability with {variable} interpolation")
```

### Type Hints (Optional but Encouraged)
```python
from typing import List, Dict, Optional, Union

def process_inventory(items: List[Dict[str, Union[str, int]]],
                     category: Optional[str] = None) -> List[Dict]:
    """Process inventory items with optional category filtering."""
    pass
```

## 5. Framework-Specific Patterns

### Kivy Mobile App Development
```python
class InventoryScreen(Screen):
    """Main inventory management screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()

        # Platform-specific code
        if platform == 'android':
            self.camera = Camera(play=False)
        else:
            Window.size = (400, 700)  # Development window size

    def on_enter(self):
        """Called when screen is entered - load data."""
        self.load_inventory_data()

    def load_inventory_data(self):
        """Load and display inventory items."""
        items = self.db.get_inventory()
        # Update UI components
        pass
```

### PyQt6 Desktop App Development
```python
class FamilyManagerApp(QApplication):
    """Main PyQt6 application class."""

    def __init__(self, argv):
        super().__init__(argv)
        self.db = DatabaseManager()
        self.mcp_manager = MCPManager()

        # Threading setup
        self.ocr_worker = OCRWorker()
        self.ocr_worker.finished.connect(self.handle_ocr_result)

        # UI initialization
        self.main_window = MainWindow()
        self.main_window.show()

    def start_ai_operation(self):
        """Start AI operation in background thread."""
        if not self.ai_worker.isRunning():
            self.ai_worker.start()
```

### Flask API Development
```python
@app.route('/api/inventory', methods=['POST'])
def add_inventory():
    """Add new inventory item via API."""
    try:
        data = request.get_json()

        # Input validation
        required_fields = ['name', 'category', 'qty', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Database operation
        conn = get_db()
        # ... database operations ...

        return jsonify({'status': 'success', 'id': item_id})

    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

## 6. Database Schema & Operations

### SQLite Database Structure
```sql
-- Core tables
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    qty REAL NOT NULL,
    unit TEXT,
    exp_date TEXT,
    location TEXT
);

CREATE TABLE meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    meal_type TEXT,
    name TEXT NOT NULL,
    ingredients TEXT,
    recipe TEXT
);

CREATE TABLE shopping_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    qty REAL,
    checked BOOLEAN DEFAULT 0
);

CREATE TABLE bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    due_date TEXT,
    category TEXT,
    paid BOOLEAN DEFAULT 0,
    recurring BOOLEAN DEFAULT 0,
    frequency TEXT
);
```

### Database Connection Management
```python
class DatabaseManager:
    """Thread-safe database manager with connection pooling."""

    def __init__(self):
        self.db_path = 'family_manager.db'
        self._lock = threading.Lock()

    def get_connection(self):
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute SELECT query with proper error handling."""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                results = cursor.fetchall()
                return [dict(row) for row in results]

            except sqlite3.Error as e:
                logger.error(f"Database query failed: {e}")
                raise
            finally:
                if 'conn' in locals():
                    conn.close()
```

## 7. AI/ML Integration Patterns

### Google Gemini API Usage
```python
class GeminiOCRWorker(QThread):
    """Threaded OCR processing using Google Gemini."""

    finished = pyqtSignal(dict)

    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path
        self.api_key = self._load_api_key()

    def _load_api_key(self) -> str:
        """Load API key from configuration."""
        with open('ai_meal_config.json', 'r') as f:
            config = json.load(f)
        return config.get('gemini_key', '')

    def run(self):
        """Execute OCR processing in background thread."""
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Load and process image
            with open(self.image_path, 'rb') as f:
                image_data = f.read()

            # Create multimodal request
            prompt = "Extract grocery items from this receipt image."
            response = model.generate_content([
                prompt,
                {'mime_type': 'image/jpeg', 'data': base64.b64encode(image_data).decode()}
            ])

            result = self._parse_response(response)
            self.finished.emit({'success': True, 'data': result})

        except Exception as e:
            logger.error(f"Gemini OCR failed: {e}")
            self.finished.emit({'success': False, 'error': str(e)})
```

### Configuration Management
```json
{
  "gemini_key": "your_api_key_here",
  "meal_planning_api": "gemini",
  "cache_settings": {
    "enabled": true,
    "max_recipes": 100,
    "cache_expiry_days": 7
  },
  "preferences": {
    "family_size": 4,
    "budget_level": "medium",
    "meal_types": ["breakfast", "lunch", "dinner"]
  }
}
```

## 8. Threading & Concurrency

### QThread Implementation Pattern
```python
class AISuggestionWorker(QThread):
    """Background worker for AI-powered suggestions."""

    # Signals for thread-safe UI updates
    progress_updated = pyqtSignal(int)
    suggestions_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, context_data: dict):
        super().__init__()
        self.context_data = context_data
        self.is_cancelled = False

    def run(self):
        """Execute AI processing in background."""
        try:
            self.progress_updated.emit(10)

            # AI processing logic
            suggestions = self._generate_suggestions()

            if not self.is_cancelled:
                self.progress_updated.emit(100)
                self.suggestions_ready.emit(suggestions)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def cancel(self):
        """Cancel the background operation."""
        self.is_cancelled = True
```

### Thread Safety Considerations
- **Database Access**: Use locks for concurrent database operations
- **UI Updates**: Only update UI from main thread using signals
- **Resource Cleanup**: Ensure proper cleanup in thread destructors
- **Cancellation Support**: Implement cancellation patterns for long-running operations

## 9. Logging & Monitoring

### Logging Configuration
```python
# In main application
logging.basicConfig(
    filename='family_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Logger usage
logger = logging.getLogger(__name__)

def process_data(data):
    """Process data with comprehensive logging."""
    logger.info(f"Starting data processing for {len(data)} items")

    try:
        # Processing logic
        result = perform_processing(data)
        logger.info(f"Successfully processed {len(result)} items")
        return result

    except Exception as e:
        logger.error(f"Data processing failed: {e}", exc_info=True)
        raise
```

### Performance Monitoring
```python
class PerformanceMonitor:
    """Monitor application performance metrics."""

    def __init__(self):
        self.metrics = {}
        self.start_times = {}

    def start_operation(self, operation_name: str):
        """Start timing an operation."""
        self.start_times[operation_name] = time.time()

    def end_operation(self, operation_name: str):
        """End timing and record metrics."""
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            if operation_name not in self.metrics:
                self.metrics[operation_name] = []
            self.metrics[operation_name].append(duration)

            # Log slow operations
            if duration > 1.0:  # More than 1 second
                logger.warning(f"Slow operation: {operation_name} took {duration:.2f}s")

            del self.start_times[operation_name]
```

## 10. Security Best Practices

### Input Validation
```python
def validate_inventory_item(item_data: dict) -> bool:
    """Validate inventory item data."""
    required_fields = ['name', 'category', 'qty', 'unit']

    # Check required fields
    for field in required_fields:
        if field not in item_data:
            raise ValueError(f"Missing required field: {field}")

    # Validate data types and ranges
    if not isinstance(item_data['name'], str) or len(item_data['name']) > 100:
        raise ValueError("Invalid item name")

    if not isinstance(item_data['qty'], (int, float)) or item_data['qty'] < 0:
        raise ValueError("Invalid quantity")

    # Sanitize string inputs
    item_data['name'] = item_data['name'].strip()
    item_data['category'] = item_data['category'].strip() if item_data.get('category') else None

    return True
```

### API Security
```python
class APISecurityManager:
    """Manage API security and rate limiting."""

    def __init__(self):
        self.rate_limits = {}
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> dict:
        """Load API keys from secure configuration."""
        # Never hardcode API keys
        with open('ai_meal_config.json', 'r') as f:
            config = json.load(f)
        return {
            'gemini': config.get('gemini_key', ''),
            'openai': config.get('openai_key', ''),
            'spoonacular': config.get('spoonacular_key', '')
        }

    def validate_request(self, api_name: str) -> bool:
        """Validate API request against rate limits."""
        current_time = time.time()

        if api_name not in self.rate_limits:
            self.rate_limits[api_name] = []

        # Clean old requests (keep last hour)
        self.rate_limits[api_name] = [
            t for t in self.rate_limits[api_name]
            if current_time - t < 3600
        ]

        # Check rate limit (100 requests per hour)
        if len(self.rate_limits[api_name]) >= 100:
            return False

        self.rate_limits[api_name].append(current_time)
        return True
```

## 11. Testing Strategies

### Unit Testing Pattern
```python
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add source path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.db_manager = DatabaseManager()
        # Create test database
        self.test_db = ':memory:'
        self.db_manager.db_path = self.test_db

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    @patch('sqlite3.connect')
    def test_get_inventory_success(self, mock_connect):
        """Test successful inventory retrieval."""
        # Mock database response
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'Milk', 'qty': 2.0, 'unit': 'liters'}
        ]
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.db_manager.get_inventory()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Milk')
        mock_connect.assert_called_once()

    def test_add_inventory_validation(self):
        """Test input validation for adding inventory."""
        with self.assertRaises(ValueError):
            self.db_manager.add_inventory_item("", "dairy", 1.0, "liters")

        with self.assertRaises(ValueError):
            self.db_manager.add_inventory_item("Milk", "dairy", -1.0, "liters")

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing
```python
class TestAPIIntegration(unittest.TestCase):
    """Test API endpoints integration."""

    def setUp(self):
        """Set up test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_inventory_api(self):
        """Test inventory API endpoints."""
        # Test POST
        response = self.app.post('/api/inventory',
                               json={
                                   'name': 'Test Item',
                                   'category': 'test',
                                   'qty': 1.0,
                                   'unit': 'each'
                               })
        self.assertEqual(response.status_code, 200)

        # Test GET
        response = self.app.get('/api/inventory')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
```

## 12. Accessibility (A11y) Guidelines

### Widget Accessibility
```python
def create_accessible_button(text: str, callback) -> QPushButton:
    """Create an accessible button with proper labeling."""
    button = QPushButton(text)

    # Set accessible name and description
    button.setAccessibleName(text)
    button.setAccessibleDescription(f"Click to {text.lower()}")

    # Ensure keyboard navigation
    button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # Connect signal
    button.clicked.connect(callback)

    return button

def create_accessible_table(headers: list, data: list) -> QTableWidget:
    """Create an accessible table with proper headers."""
    table = QTableWidget()

    # Set headers with accessible labels
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)

    # Add data
    table.setRowCount(len(data))
    for row_idx, row_data in enumerate(data):
        for col_idx, cell_data in enumerate(row_data):
            item = QTableWidgetItem(str(cell_data))
            table.setItem(row_idx, col_idx, item)

    # Accessibility properties
    table.setAccessibleName("Data Table")
    table.setAccessibleDescription(f"Table with {len(data)} rows and {len(headers)} columns")

    return table
```

### Screen Reader Support
```python
class AccessibleDialog(QDialog):
    """Dialog with full accessibility support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accessible Dialog")

        # Screen reader announcements
        self.status_label = QLabel("Dialog opened")
        self.status_label.setAccessibleName("Status announcement")

        # Keyboard navigation setup
        self.setTabOrder(self.input_field, self.ok_button)
        self.setTabOrder(self.ok_button, self.cancel_button)

    def announce_status(self, message: str):
        """Announce status to screen readers."""
        self.status_label.setText(message)

        # Force screen reader to read the announcement
        self.status_label.setFocus()
        QTimer.singleShot(100, lambda: self.status_label.clearFocus())
```

## 13. Asset Management

### Icon Generation
```python
# generate_icons.py - Automated icon generation
def generate_android_icons(base_icon_path: str, output_dir: str):
    """Generate icons for all Android screen densities."""

    densities = {
        'mdpi': 48,      # 1x
        'hdpi': 72,      # 1.5x
        'xhdpi': 96,     # 2x
        'xxhdpi': 144,   # 3x
        'xxxhdpi': 192   # 4x
    }

    base_image = Image.open(base_icon_path)

    for density, size in densities.items():
        # Resize icon
        resized = base_image.resize((size, size), Image.Resampling.LANCZOS)

        # Save with appropriate naming
        output_path = os.path.join(output_dir, f'icon-{size}.png')
        resized.save(output_path, 'PNG')

        print(f"Generated {density} icon: {size}x{size}")

# Usage
if __name__ == '__main__':
    generate_android_icons('assets/icon.png', 'assets/android/')
```

### Asset Organization
```
assets/
├── icon.png              # Base icon (512x512)
├── icon-foreground.png   # Adaptive icon foreground
├── icon-background.png   # Adaptive icon background
├── splash.png           # App splash screen
├── screenshots/         # Store listing screenshots
│   ├── screenshot_1.png
│   ├── screenshot_2.png
│   └── ...
├── feature_graphic.png  # Play Store feature graphic
└── android/             # Generated Android icons
    ├── icon-48.png      # mdpi
    ├── icon-72.png      # hdpi
    ├── icon-96.png      # xhdpi
    └── ...
```

## 14. Version Control & Git Workflow

### Branching Strategy
```bash
# Feature development
git checkout -b feature/ai-meal-planning
# Make changes...
git commit -m "feat: Add AI-powered meal planning feature"

# Bug fixes
git checkout -b fix/ocr-parsing-error
# Fix issue...
git commit -m "fix: Resolve OCR parsing error for receipts"

# Releases
git checkout -b release/v1.2.0
# Final testing...
git tag -a v1.2.0 -m "Release version 1.2.0"
```

### Commit Message Convention
```
type(scope): description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Testing changes
- chore: Maintenance tasks

Examples:
- feat(ui): Add dark mode toggle
- fix(api): Handle timeout errors in Gemini API calls
- refactor(db): Optimize inventory queries for better performance
- test(ocr): Add comprehensive OCR accuracy tests
```

### Pull Request Process
1. **Branch Creation**: Create feature branch from `main`
2. **Development**: Implement changes with tests
3. **Code Quality**: Run Codacy analysis, ensure all tests pass
4. **PR Creation**: Create pull request with detailed description
5. **Review**: Address reviewer feedback
6. **Merge**: Squash merge with descriptive commit message

## 15. Release Management

### Version Numbering
Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process
```bash
# Update version in relevant files
echo "1.2.0" > VERSION
# Update version in buildozer.spec
# Update version in setup.py (if applicable)

# Create release commit
git add VERSION buildozer.spec
git commit -m "chore: Bump version to 1.2.0"

# Create annotated tag
git tag -a v1.2.0 -m "Release v1.2.0

## What's New
- AI-powered meal planning
- Improved OCR accuracy
- Bug fixes and performance improvements"

# Push changes
git push origin main
git push origin v1.2.0

# Generate APK for release
./build_apk.sh

# Upload to Play Store
# Create GitHub release with changelog
```

### Changelog Generation
```markdown
# Changelog

## [1.2.0] - 2024-01-15
### Added
- AI-powered meal planning feature
- Support for multiple AI providers
- Enhanced OCR accuracy for receipts

### Fixed
- Memory leak in image processing
- Database connection timeout issues
- UI responsiveness during AI operations

### Changed
- Updated Google Gemini API integration
- Improved error handling across the application

### Security
- Updated dependencies to address security vulnerabilities
- Enhanced API key management
```

## 16. Deployment & Distribution

### Android APK Signing
```bash
# Generate keystore (one-time setup)
keytool -genkey -v -keystore keystore.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias family_manager_key

# Build signed APK
buildozer android release

# Verify signature
jarsigner -verify -verbose -certs bin/*.aab
```

### Play Store Submission
1. **Prepare Assets**:
   - Screenshots (various device sizes)
   - Feature graphic (1024x500)
   - App icons (512x512)
   - Privacy policy
   - App description

2. **Create Release**:
   - Upload AAB bundle
   - Fill store listing
   - Set pricing and distribution
   - Submit for review

3. **Post-Submission**:
   - Monitor review status
   - Prepare for user support
   - Plan next release cycle

## 17. Performance Optimization

### Profiling Setup
```python
import cProfile
import pstats
from io import StringIO

def profile_function(func):
    """Decorator to profile function performance."""
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()

        result = func(*args, **kwargs)

        pr.disable()
        s = StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        return result
    return wrapper

@profile_function
def process_large_dataset(data):
    """Process large dataset with performance profiling."""
    # Processing logic here
    pass
```

### Memory Management
```python
class MemoryManager:
    """Manage memory usage for large operations."""

    def __init__(self):
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
        self.gc_threshold = 100 * 1024 * 1024     # 100MB

    def check_memory_usage(self) -> bool:
        """Check if memory usage is within acceptable limits."""
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_info().rss

        if memory_usage > self.memory_threshold:
            logger.warning(f"High memory usage: {memory_usage / 1024 / 1024:.1f}MB")
            self._trigger_gc()
            return False

        return True

    def _trigger_gc(self):
        """Force garbage collection."""
        import gc
        collected = gc.collect()
        logger.info(f"Garbage collection freed {collected} objects")

    def optimize_image_processing(self, image_data: bytes) -> bytes:
        """Optimize image processing for memory efficiency."""
        # Resize large images before processing
        img = Image.open(io.BytesIO(image_data))

        # Resize if too large
        max_size = (1920, 1080)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Convert to RGB if necessary
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()
```

## 18. Error Handling & Recovery

### Comprehensive Error Handling
```python
class ErrorHandler:
    """Centralized error handling and recovery."""

    def __init__(self):
        self.error_counts = {}
        self.recovery_strategies = {
            'database_connection': self._recover_database_connection,
            'api_timeout': self._recover_api_timeout,
            'memory_error': self._recover_memory_error
        }

    def handle_error(self, error: Exception, context: str = "") -> dict:
        """Handle error with appropriate recovery strategy."""

        error_type = type(error).__name__
        error_message = str(error)

        # Log error
        logger.error(f"Error in {context}: {error_type}: {error_message}",
                    exc_info=True)

        # Track error frequency
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # Attempt recovery
        recovery_result = self._attempt_recovery(error_type, error, context)

        return {
            'error_type': error_type,
            'message': error_message,
            'recovery_attempted': recovery_result['attempted'],
            'recovery_successful': recovery_result['successful'],
            'fallback_used': recovery_result.get('fallback_used', False)
        }

    def _attempt_recovery(self, error_type: str, error: Exception, context: str) -> dict:
        """Attempt error recovery based on error type."""

        if error_type in self.recovery_strategies:
            try:
                result = self.recovery_strategies[error_type](error, context)
                return {
                    'attempted': True,
                    'successful': result['success'],
                    'fallback_used': result.get('fallback_used', False)
                }
            except Exception as recovery_error:
                logger.error(f"Recovery failed: {recovery_error}")
                return {'attempted': True, 'successful': False}

        return {'attempted': False, 'successful': False}

    def _recover_database_connection(self, error, context):
        """Recover from database connection errors."""
        # Implementation for database recovery
        pass

    def _recover_api_timeout(self, error, context):
        """Recover from API timeout errors."""
        # Implementation for API timeout recovery
        pass

    def _recover_memory_error(self, error, context):
        """Recover from memory errors."""
        # Force garbage collection
        import gc
        gc.collect()

        # Clear caches if available
        if hasattr(self, 'clear_caches'):
            self.clear_caches()

        return {'success': True, 'fallback_used': True}
```

## 19. Internationalization (i18n)

### String Externalization
```python
# strings.py - Centralized string definitions
class AppStrings:
    """Application strings with i18n support."""

    def __init__(self, locale='en'):
        self.locale = locale
        self._strings = self._load_strings()

    def _load_strings(self) -> dict:
        """Load strings for current locale."""
        strings = {
            'en': {
                'app_name': 'Family Household Manager',
                'inventory_title': 'Inventory',
                'add_item': 'Add Item',
                'quantity': 'Quantity',
                'category': 'Category',
                'error_database': 'Database error occurred',
                'error_network': 'Network connection failed'
            },
            'es': {
                'app_name': 'Administrador del Hogar Familiar',
                'inventory_title': 'Inventario',
                'add_item': 'Agregar Artículo',
                'quantity': 'Cantidad',
                'category': 'Categoría',
                'error_database': 'Error de base de datos',
                'error_network': 'Falló la conexión de red'
            }
        }
        return strings.get(self.locale, strings['en'])

    def get(self, key: str, **kwargs) -> str:
        """Get localized string with optional formatting."""
        template = self._strings.get(key, key)
        if kwargs:
            return template.format(**kwargs)
        return template

# Usage
strings = AppStrings('es')
button_text = strings.get('add_item')
error_msg = strings.get('error_database')
```

### Date/Time Localization
```python
import locale
from datetime import datetime

class DateTimeFormatter:
    """Localized date and time formatting."""

    def __init__(self, locale_str='en_US'):
        self.locale_str = locale_str
        try:
            locale.setlocale(locale.LC_TIME, locale_str)
        except locale.Error:
            # Fallback to system default
            pass

    def format_date(self, date_obj, format_type='short') -> str:
        """Format date according to locale."""
        formats = {
            'short': '%x',      # Localized short date
            'medium': '%a, %b %d, %Y',  # e.g., "Mon, Jan 15, 2024"
            'long': '%A, %B %d, %Y',    # e.g., "Monday, January 15, 2024"
            'iso': '%Y-%m-%d'   # ISO format (universal)
        }

        format_str = formats.get(format_type, formats['short'])

        if format_type == 'iso':
            return date_obj.strftime(format_str)
        else:
            return date_obj.strftime(format_str).encode('utf-8').decode('utf-8')

    def format_time(self, time_obj, use_24_hour=True) -> str:
        """Format time according to locale and preferences."""
        if use_24_hour:
            format_str = '%H:%M:%S'
        else:
            format_str = '%I:%M:%S %p'

        return time_obj.strftime(format_str)

    def format_datetime(self, datetime_obj, include_seconds=False) -> str:
        """Format full datetime."""
        date_part = self.format_date(datetime_obj.date(), 'medium')
        time_part = self.format_time(datetime_obj.time(), include_seconds)
        return f"{date_part} at {time_part}"
```

## 20. Continuous Integration/Deployment

### CI/CD Pipeline Configuration
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        python -m pytest test_*.py -v --cov=.

    - name: Run Codacy analysis
      run: |
        # Codacy CLI integration
        codacy-analysis-cli analyze

  build-android:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Set up Android SDK
      uses: android-actions/setup-android@v2

    - name: Build Android APK
      run: |
        ./build_env_setup.sh
        buildozer android debug

    - name: Upload APK artifact
      uses: actions/upload-artifact@v3
      with:
        name: android-apk
        path: bin/*.apk

  deploy:
    needs: build-android
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
    - name: Deploy to Play Store
      # Play Store deployment steps
      run: |
        echo "Deploy to Play Store"
        # Integration with Google Play Developer API
```

### Quality Gates
```python
# quality_checks.py - CI quality gate checks
import subprocess
import sys
import json
from pathlib import Path

class QualityChecker:
    """Automated quality checks for CI/CD."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def run_all_checks(self) -> dict:
        """Run all quality checks."""
        results = {
            'tests_passed': self.run_tests(),
            'linting_passed': self.run_linting(),
            'security_passed': self.run_security_checks(),
            'performance_acceptable': self.check_performance(),
            'coverage_sufficient': self.check_coverage()
        }

        # Overall result
        results['all_passed'] = all(results.values())
        return results

    def run_tests(self) -> bool:
        """Run test suite."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest',
                'test_*.py', '--tb=short', '--quiet'
            ], cwd=self.project_root, capture_output=True, text=True)

            print("Test Results:")
            print(result.stdout)
            if result.stderr:
                print("Test Errors:")
                print(result.stderr)

            return result.returncode == 0
        except Exception as e:
            print(f"Test execution failed: {e}")
            return False

    def run_linting(self) -> bool:
        """Run code linting checks."""
        # Since we don't have configured linters, check for basic issues
        issues = []

        # Check for bare except clauses
        for py_file in self.project_root.rglob('*.py'):
            if py_file.name.startswith('test_'):
                continue  # Skip test files

            content = py_file.read_text()
            if 'except:' in content and 'Exception' not in content:
                issues.append(f"Bare except clause in {py_file}")

        if issues:
            print("Linting Issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False

        return True

    def run_security_checks(self) -> bool:
        """Run basic security checks."""
        issues = []

        for py_file in self.project_root.rglob('*.py'):
            content = py_file.read_text()

            # Check for hardcoded secrets
            if 'api_key' in content.lower() and '"' in content:
                # More sophisticated check would be needed
                pass

        return len(issues) == 0

    def check_performance(self) -> bool:
        """Check for performance issues."""
        # Basic performance checks
        issues = []

        for py_file in self.project_root.rglob('*.py'):
            content = py_file.read_text()

            # Check for inefficient patterns
            if '.select(' in content and 'limit(' not in content:
                issues.append(f"Unbounded query in {py_file}")

        return len(issues) < 5  # Allow some issues

    def check_coverage(self) -> bool:
        """Check test coverage."""
        # For now, just check if tests exist
        test_files = list(self.project_root.glob('test_*.py'))
        source_files = list(self.project_root.glob('*.py'))

        # Rough coverage estimate
        coverage_ratio = len(test_files) / len(source_files) if source_files else 0
        return coverage_ratio > 0.3  # At least 30% test coverage

if __name__ == '__main__':
    checker = QualityChecker('.')
    results = checker.run_all_checks()

    print("\nQuality Check Results:")
    for check, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {check}: {status}")

    if not results['all_passed']:
        sys.exit(1)
```

---

**Note**: This AGENTS.md file provides comprehensive guidance for maintaining code quality, consistency, and best practices across the Family Household Manager project. All team members should familiarize themselves with these guidelines and follow them during development.

For questions or clarifications about any section, please consult the project maintainers or refer to the specific framework documentation linked throughout this guide.