# AGENTS.md - Family Household Manager Development Guide

This document provides development guidelines and commands for working with the Family Household Manager, a PyQt6-based desktop application with Flask API integration.

## Project Structure

- **main.py** - Main PyQt6 GUI application with inventory, meals, shopping, bills, and calendar tabs
- **api.py** - Flask REST API for mobile/web sync functionality
- **db_setup.py** - SQLite database schema creation and initialization
- **requirements.txt** - Python dependencies list
- **family_manager.db** - SQLite database file (created on first run)

## Build/Run Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt install tesseract-ocr  # Required for OCR functionality

# Setup Google Vision API (optional, for better OCR)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### Running the Application
```bash
# Run main GUI application
python3 main.py

# Run web API server (for mobile sync)
python3 api.py
# Server runs on http://localhost:5000

# Initialize database (first time setup)
python3 db_setup.py
```

### Testing Commands
```bash
# Run syntax check on all Python files
python3 -m py_compile main.py api.py db_setup.py

# Test imports and dependencies
python3 -c "
import PyQt6
import pytesseract
import cv2
import sqlite3
import flask
print('All core dependencies available')
"

# Test OCR functionality (requires test image)
python3 -c "
import pytesseract
from PIL import Image
print('OCR engine available:', pytesseract.get_languages(config=''))
"
```

### Code Quality Commands
```bash
# Check for common issues (if linting tools available)
python3 -m flake8 *.py --max-line-length=100 --ignore=E501,W503

# Type checking (if mypy installed)
python3 -m mypy *.py --ignore-missing-imports

# Security scan for dependencies (if safety installed)
python3 -m safety check -r requirements.txt
```

## Code Style Guidelines

### Import Organization
```python
# Standard library imports first
import sys
import sqlite3
import csv
from datetime import datetime, timedelta

# Third-party imports second
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow
from PIL import Image
import pytesseract

# Local/conditional imports last
try:
    from google.cloud import vision
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `FamilyManagerApp`, `AddItemDialog`)
- **Functions/Methods**: snake_case (e.g., `create_dashboard_tab`, `load_inventory`)
- **Variables**: snake_case (e.g., `inventory_table`, `current_row`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `VISION_AVAILABLE`)
- **Database columns**: snake_case (e.g., `exp_date`, `meal_type`)

### PyQt6 UI Patterns
- Use `QDialog` for modal forms with `get_data()` methods
- Connect signals immediately after widget creation: `btn.clicked.connect(self.handler)`
- Use `QMessageBox` for user notifications (info, warning, about)
- Implement proper layout management (QVBoxLayout, QHBoxLayout, QFormLayout)
- Set tooltips for important widgets: `widget.setToolTip("Description")`

### Database Operations
```python
# Always use parameterized queries
cursor.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))

# Close connections properly
conn = sqlite3.connect('family_manager.db')
try:
    cursor = conn.cursor()
    # Database operations
    conn.commit()
finally:
    conn.close()

# Use context managers when possible
with sqlite3.connect('family_manager.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory")
    result = cursor.fetchone()
```

### Error Handling
- Use try/except blocks for external API calls (Google Vision, file operations)
- Show user-friendly messages via `QMessageBox.warning()` or `QMessageBox.information()`
- Log technical errors to console: `print(f"Error: {e}")`
- Handle missing optional dependencies gracefully with try/except ImportError

### Threading
- Use `QThread` for long-running operations (OCR, image processing)
- Implement worker classes inheriting from `QThread`
- Use signals for thread communication: `finished = pyqtSignal(str)`
- Start threads with `self.worker.start()`

### File Organization
- Dialog classes defined before main application class
- Utility functions defined at module level (e.g., `deskew()`, `remove_lines()`)
- Tab creation methods grouped by functionality
- Event handler methods named descriptively (e.g., `add_inventory_item`)

### Constants and Configuration
- Stylesheets defined as class attributes with multi-line strings
- Magic numbers extracted to named constants
- Database queries as multi-line strings with proper indentation

### Data Validation
- Validate user input in dialog `accept()` methods
- Check for selected rows before table operations: `if current_row < 0: return`
- Ensure proper data types before database insertion
- Handle edge cases (empty strings, None values)

### API Design (Flask)
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Return JSON responses: `return jsonify({'status': 'ok'})`
- Implement proper error handling and status codes
- Use `sqlite3.Row` for dictionary-like cursor results

### Image Processing
- Preprocess images for OCR: resize, grayscale, adaptive threshold
- Handle different image formats gracefully
- Implement fallback OCR methods (Vision → Tesseract)
- Use OpenCV for image manipulation, PIL for final OCR

### Chart Integration
- Import matplotlib conditionally with try/except ImportError
- Provide user feedback if matplotlib not available
- Create simple, readable charts with proper labels
- Handle empty datasets gracefully

### Security Considerations
- Validate all user inputs before database operations
- Use parameterized queries to prevent SQL injection
- Sanitize file paths and handle file operations safely
- Implement proper authentication for API endpoints

### Performance Guidelines
- Minimize database connections (reuse when possible)
- Use efficient queries with proper indexing
- Implement pagination for large datasets if needed
- Cache frequently accessed data in memory

### GUI Responsiveness
- Move blocking operations to separate threads
- Provide progress feedback for long operations
- Update UI elements safely from main thread
- Implement proper cleanup in thread destructors

## Development Workflow

1. **Before making changes**: Run syntax checks on modified files
2. **During development**: Test frequently with real GUI environment
3. **After changes**: Verify database operations and API functionality
4. **Before commit**: Ensure all files compile and imports work correctly

## Platform-Specific Notes

- **Linux**: Requires X11/Wayland display server for GUI
- **Windows**: Use `venv\Scripts\activate` for virtual environment
- **macOS**: May need additional display server configuration

## Dependencies and Alternatives

- **Core**: PyQt6, SQLite3 (built-in)
- **OCR**: pytesseract (primary), google-cloud-vision (optional fallback)
- **Image**: opencv-python, Pillow
- **Charts**: matplotlib (optional, for visualization)
- **API**: Flask (web sync functionality)
- **System**: tesseract-ocr (system package)

Always verify dependencies are available before using optional features.