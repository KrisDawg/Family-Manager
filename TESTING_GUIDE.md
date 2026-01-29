# Testing Guide - Family Household Manager

## Overview

This guide covers testing strategies for the Family Household Manager system:
- **Unit Tests**: Individual components (database, API methods)
- **Integration Tests**: Full workflows (API endpoints, OCR, Gemini)
- **Manual Tests**: Desktop UI, mobile app, offline sync
- **Performance Tests**: Response times, memory usage

## Unit Tests

### Running Unit Tests

```bash
# All unit tests
python3 -m pytest tests/unit/ -v

# Specific test file
python3 -m pytest tests/unit/test_inventory_organization.py -v

# Stop on first failure
python3 -m pytest tests/unit/ -x

# Show print statements
python3 -m pytest tests/unit/ -s
```

### Test Files

#### test_inventory_organization.py
Tests inventory database operations:
- ✅ Add inventory items
- ✅ Retrieve inventory (all/by category)
- ✅ Update quantities and expiration
- ✅ Delete items
- ✅ Category filtering

Run:
```bash
python3 -m pytest tests/unit/test_inventory_organization.py -v
```

#### test_quantity_fix.py
Tests quantity validation:
- ✅ Accept valid quantities (integers, floats)
- ✅ Reject negative quantities
- ✅ Handle zero quantities
- ✅ Decimal precision

Run:
```bash
python3 -m pytest tests/unit/test_quantity_fix.py -v
```

#### test_ocr_dialog_fix.py
Tests OCR dialog integration:
- ✅ Dialog creation and display
- ✅ Response handling
- ✅ Error message display

Run:
```bash
python3 -m pytest tests/unit/test_ocr_dialog_fix.py -v
```

### Writing New Unit Tests

```python
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add source path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'family_manager'))

class TestNewFeature(unittest.TestCase):
    """Test cases for new feature."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.database = MockDatabase()
        self.feature = NewFeature(self.database)
    
    def tearDown(self):
        """Clean up after tests."""
        self.database.close()
    
    def test_feature_creates_record(self):
        """Test that feature creates database record."""
        result = self.feature.create_item("Test")
        
        self.assertEqual(result['name'], "Test")
        self.assertTrue(result['id'] > 0)
    
    def test_feature_validation(self):
        """Test input validation."""
        with self.assertRaises(ValueError):
            self.feature.create_item("")  # Empty name invalid
    
    @patch('requests.get')
    def test_api_call(self, mock_get):
        """Test API calls with mocking."""
        mock_get.return_value.json.return_value = {'status': 'ok'}
        
        result = self.feature.call_api()
        
        self.assertEqual(result['status'], 'ok')
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

## Integration Tests

### Running Integration Tests

```bash
# All integration tests
python3 -m pytest tests/integration/ -v

# Specific test
python3 -m pytest tests/integration/test_api.py -v

# Stop on first failure
python3 -m pytest tests/integration/ -x --tb=short
```

### Test Files

#### test_api.py
Tests REST API endpoints:
- ✅ GET /api/inventory
- ✅ POST /api/inventory (add items)
- ✅ PUT /api/inventory/:id (update)
- ✅ DELETE /api/inventory/:id (remove)
- ✅ GET /api/chores
- ✅ GET /api/tasks
- ✅ Error handling (400, 404, 500)

Run:
```bash
# Start server first
python3 family_manager/main.py &
sleep 2

# Run tests
python3 -m pytest tests/integration/test_api.py -v

# Stop server
pkill -f "python3 family_manager/main.py"
```

#### test_gemini_ocr.py
Tests Google Gemini OCR integration:
- ✅ Image processing
- ✅ Receipt parsing
- ✅ Item extraction
- ✅ Error handling

Prerequisites:
- Set `GEMINI_API_KEY` environment variable
- Test images in `tests/integration/test_images/`

Run:
```bash
export GEMINI_API_KEY="your_key_here"
python3 -m pytest tests/integration/test_gemini_ocr.py -v
```

#### test_complete_ocr.py
End-to-end OCR workflow:
- ✅ Receipt image upload
- ✅ Gemini API processing
- ✅ Item parsing
- ✅ Database insertion
- ✅ Inventory update

Run:
```bash
python3 -m pytest tests/integration/test_complete_ocr.py -v
```

### Creating Integration Tests

```python
import unittest
import json
import subprocess
import time
import requests

class TestNewIntegration(unittest.TestCase):
    """Test new API integration."""
    
    @classmethod
    def setUpClass(cls):
        """Start server once for all tests."""
        cls.server = subprocess.Popen(
            ['python3', 'family_manager/main.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)  # Wait for server startup
        cls.base_url = "http://localhost:5000"
    
    @classmethod
    def tearDownClass(cls):
        """Stop server after all tests."""
        cls.server.terminate()
        cls.server.wait()
    
    def test_api_workflow(self):
        """Test complete API workflow."""
        # Add item
        response = requests.post(
            f"{self.base_url}/api/inventory",
            json={
                "name": "Test Item",
                "category": "test",
                "qty": 1.0,
                "unit": "each"
            }
        )
        self.assertEqual(response.status_code, 200)
        item_id = response.json()['id']
        
        # Retrieve item
        response = requests.get(f"{self.base_url}/api/inventory/{item_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], "Test Item")
        
        # Update item
        response = requests.put(
            f"{self.base_url}/api/inventory/{item_id}",
            json={"qty": 2.0}
        )
        self.assertEqual(response.status_code, 200)
        
        # Delete item
        response = requests.delete(f"{self.base_url}/api/inventory/{item_id}")
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

## Manual Testing

### Desktop App Testing

#### Startup & UI
1. Start app: `python3 family_manager/main.py`
2. ✅ Window appears with correct size
3. ✅ All 11 tabs visible and clickable
4. ✅ Dark theme applied (correct colors)
5. ✅ No errors in startup logs

#### Inventory Tab
1. Go to Inventory tab
2. ✅ Existing items display correctly
3. ✅ "Add Item" button opens dialog
4. ✅ Fill form and click "Add" creates item
5. ✅ Item appears in table immediately
6. ✅ Edit and delete buttons work
7. ✅ Category filter works
8. ✅ Expiration date formats correctly

#### Shopping List
1. Go to Shopping tab
2. ✅ Items display with checkboxes
3. ✅ Clicking checkbox toggles status
4. ✅ "Add" button creates new item
5. ✅ Delete removes item
6. ✅ List persists after app restart

#### Chores & Tasks
1. Verify chores display with due dates
2. ✅ Complete button marks chore done
3. ✅ Rotate button assigns to next person
4. ✅ Tasks show projects correctly
5. ✅ Comments can be added

#### Recurring Events
1. Create recurring event (daily, weekly, monthly)
2. ✅ Event instances appear on calendar
3. ✅ Edit dialog shows pattern
4. ✅ Pattern can be modified
5. ✅ Delete removes all instances

#### Notifications
1. ✅ Automatic notifications appear hourly
2. ✅ Notifications show priority levels (color-coded)
3. ✅ Mark as read functionality works
4. ✅ Delete button removes notification
5. ✅ Settings dialog controls notification types

### Mobile App Testing (Desktop)

```bash
cd kivy_app/
python3 main.py
```

#### Dashboard Screen
1. ✅ 5 summary cards display
2. ✅ Cards show current counts
3. ✅ Touching cards navigates to section
4. ✅ Placeholder cards for bills, expenses

#### Inventory Screen
1. ✅ Items display in list
2. ✅ Add dialog works
3. ✅ Category selection shows in dropdown
4. ✅ New items appear immediately
5. ✅ Delete function removes items

#### Shopping Screen
1. ✅ Shopping list items display
2. ✅ Checkboxes toggle items
3. ✅ Add button creates items
4. ✅ Changes persist (check after close/reopen)

#### Chores Screen
1. ✅ Pending chores display
2. ✅ Due dates show correctly
3. ✅ Assignee shown
4. ✅ Completed chores appear grayed out

#### Notifications
1. ✅ All notifications display
2. ✅ Color-coded by priority
3. ✅ Recent notifications at top
4. ✅ Notification counts accurate

### Mobile App Testing (Android)

#### Prerequisites
- Android device or emulator
- Debug APK built: `buildozer android debug`

#### Installation
```bash
adb install -r bin/familymanager-0.1-debug.apk
adb shell am start -n org.example.familymanager/.MailApplication
```

#### Testing
1. ✅ App launches and displays correctly
2. ✅ All screens accessible via navigation
3. ✅ Buttons responsive to touch
4. ✅ TextInput fields work
5. ✅ Dialogs display and function

#### Offline Mode
1. Turn off WiFi/mobile data
2. ✅ "Working Offline" text appears (optional)
3. ✅ Can still view cached data
4. ✅ Add/edit/delete actions are queued
5. ✅ No crashes or errors
6. Re-enable network
7. ✅ Pending actions sync automatically
8. ✅ No duplicate entries

#### Network Recovery
1. Start app with network on
2. Turn network off
3. ✅ Add item (queued)
4. Turn network on
5. ✅ Item syncs successfully
6. ✅ No duplicate items
7. ✅ Data consistent with desktop

### API Endpoint Testing

Use curl to test all endpoints:

```bash
# Inventory Endpoints
curl -X GET http://localhost:5000/api/inventory
curl -X GET http://localhost:5000/api/inventory/1
curl -X GET http://localhost:5000/api/inventory?category=Dairy
curl -X POST http://localhost:5000/api/inventory \
  -H "Content-Type: application/json" \
  -d '{"name":"Item","category":"cat","qty":1.0,"unit":"each"}'
curl -X PUT http://localhost:5000/api/inventory/1 -d '{"qty":2.0}'
curl -X DELETE http://localhost:5000/api/inventory/1

# Other Endpoints
curl -X GET http://localhost:5000/api/shopping-list
curl -X GET http://localhost:5000/api/chores
curl -X GET http://localhost:5000/api/tasks
curl -X GET http://localhost:5000/api/bills
curl -X GET http://localhost:5000/api/notifications
curl -X GET http://localhost:5000/api/recurring-events
```

Expected responses:
- ✅ GET returns 200 with JSON array
- ✅ POST returns 200 with created object
- ✅ PUT returns 200 with updated object
- ✅ DELETE returns 200 with success message
- ✅ Invalid ID returns 404
- ✅ Invalid data returns 400

## Performance Testing

### Startup Time
```bash
time python3 family_manager/main.py &
# Should complete startup <5 seconds
```

### Database Query Performance
```bash
# Time common queries
sqlite3 family_manager/family_manager.db

-- Get all inventory (should be <100ms)
.timer ON
SELECT * FROM inventory;

-- Get inventory by category (should be <50ms)
SELECT * FROM inventory WHERE category='Dairy';

-- Get notifications (should be <100ms)
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 100;

-- Get chores with rotation (should be <200ms)
SELECT c.*, cr.assigned_to FROM chores c
LEFT JOIN chore_rotation cr ON c.id = cr.chore_id;
```

### Memory Usage
```bash
# Monitor while app runs
watch -n 1 'ps aux | grep family_manager | grep -v grep'

# Desktop app should use <500MB
# Mobile app should use <200MB
```

### API Response Times
```bash
# Measure endpoint response times
for i in {1..10}; do
  time curl http://localhost:5000/api/inventory > /dev/null
done

# Most requests <100ms
# Worst case <500ms
```

## Continuous Testing

### Pre-Commit Checks
```bash
#!/bin/bash
# Save as .git/hooks/pre-commit

echo "Running syntax checks..."
python3 -m py_compile family_manager/*.py kivy_app/*.py || exit 1

echo "Running unit tests..."
python3 -m pytest tests/unit/ --tb=short || exit 1

echo "✅ All checks passed!"
```

### CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r family_manager/requirements.txt
        pip install pytest pytest-cov
    
    - name: Syntax check
      run: |
        python3 -m py_compile family_manager/*.py
        python3 -m py_compile kivy_app/*.py
    
    - name: Run unit tests
      run: python3 -m pytest tests/unit/ -v
    
    - name: Run integration tests
      run: |
        python3 family_manager/main.py &
        sleep 2
        python3 -m pytest tests/integration/ -v
        pkill -f "python3 family_manager/main.py"
    
    - name: Coverage
      run: python3 -m pytest tests/ --cov=family_manager --cov-report=term-missing
```

## Test Coverage

### Current Coverage
- Database operations: 85%
- API endpoints: 80%
- UI components: 45% (manual testing)
- Mobile app: 30% (API client only)

### Improving Coverage
1. Add tests for notification triggers
2. Add tests for recurring event manager
3. Test error paths (invalid input, network failure)
4. Test concurrent operations
5. Add mobile UI tests (Kivy testing framework)

## Debugging Tests

### Verbose Output
```bash
# Show all print statements
python3 -m pytest tests/ -v -s

# Show assertions
python3 -m pytest tests/ -vv

# Full traceback
python3 -m pytest tests/ --tb=long
```

### Single Test
```bash
# Run single test
python3 -m pytest tests/unit/test_inventory_organization.py::TestInventoryDatabase::test_add_item -v

# With output
python3 -m pytest tests/unit/test_inventory_organization.py::TestInventoryDatabase::test_add_item -vs
```

### Breakpoint Debugging
```python
# In test file
def test_something(self):
    result = some_function()
    breakpoint()  # Will pause execution
    assert result == expected
```

Then run with:
```bash
python3 -m pytest tests/unit/test_file.py -v -s --pdb
```

## Regression Testing

### Smoke Tests (Quick)
```bash
python3 -m pytest tests/unit/ -v
curl http://localhost:5000/api/inventory
python3 kivy_app/main.py &
```

### Full Test Suite
```bash
# Run everything
python3 -m pytest tests/ -v --cov

# Should complete in <2 minutes
# All tests should pass
```

## Known Issues & Workarounds

### Issue: "Database is locked"
**Cause**: Multiple processes accessing DB
**Fix**: Restart app, close file explorers

### Issue: "API returns 500"
**Cause**: Invalid query or database error
**Fix**: Check logs, restart server

### Issue: "Mobile app slow"
**Cause**: Slow network or large dataset
**Fix**: Use offline mode, check cache frequency

## Test Data

### Sample Inventory
```python
items = [
    {"name": "Milk", "category": "Dairy", "qty": 2.0, "unit": "liters"},
    {"name": "Bread", "category": "Bakery", "qty": 1.0, "unit": "each"},
    {"name": "Apples", "category": "Produce", "qty": 5.0, "unit": "pieces"},
]
```

### Sample Chores
```python
chores = [
    {"name": "Clean Kitchen", "assigned_to": "Parent1", "due_date": "2024-01-15"},
    {"name": "Wash Dishes", "assigned_to": "Child1", "due_date": "2024-01-15"},
]
```

### Sample Tasks
```python
tasks = [
    {"name": "Complete Math", "project": "Homework", "priority": "high"},
    {"name": "Fix Bicycle", "project": "Chores", "priority": "normal"},
]
```
