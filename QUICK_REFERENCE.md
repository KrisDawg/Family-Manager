# Quick Reference: Common Commands

## Desktop App

### Start Application
```bash
cd family_manager/
python3 main.py
```

### Run Tests
```bash
# All tests
python3 -m pytest tests/

# Unit tests only
python3 -m pytest tests/unit/

# Integration tests only
python3 -m pytest tests/integration/

# Specific test
python3 -m pytest tests/unit/test_inventory_organization.py -v
```

### Check Syntax
```bash
python3 -m py_compile family_manager/main.py
python3 -m py_compile family_manager/api.py
```

### Database Operations
```bash
# Backup database
cp family_manager/family_manager.db family_manager/family_manager.db.backup

# Reset database (destructive!)
rm family_manager/family_manager.db
python3 family_manager/db_setup.py
```

### Lint/Format Code
```bash
# Check for obvious issues
python3 -m py_compile family_manager/*.py

# View code style issues (if configured)
# pylint family_manager/*.py
# flake8 family_manager/*.py
```

## Mobile App (Kivy)

### Desktop Testing
```bash
cd kivy_app/
pip install -r requirements.txt
python3 main.py
```

### Build Debug APK
```bash
cd kivy_app/
buildozer android debug
# Output: bin/familymanager-0.1-debug.apk
adb install bin/familymanager-0.1-debug.apk
```

### Build Release APK
```bash
cd kivy_app/
buildozer android release
# Output: bin/familymanager-0.1-release.apk
```

### Clear Build Cache
```bash
cd kivy_app/
buildozer android clean
```

### View Build Logs
```bash
buildozer android debug -- logcat
# Or in separate terminal
adb logcat | grep -i "python\|family"
```

### Install on Device/Emulator
```bash
# Install debug APK
adb install -r bin/familymanager-0.1-debug.apk

# Uninstall
adb uninstall org.example.familymanager

# Clear app data
adb shell pm clear org.example.familymanager
```

### Run App after Install
```bash
adb shell am start -n org.example.familymanager/.MailApplication
```

## API Server

### Start Flask Server
```bash
cd family_manager/
python3 main.py
# Server runs on http://localhost:5000
```

### Test API Endpoint
```bash
# Get all inventory
curl http://localhost:5000/api/inventory

# Add item
curl -X POST http://localhost:5000/api/inventory \
  -H "Content-Type: application/json" \
  -d '{"name":"Milk","category":"Dairy","qty":2.0,"unit":"liters"}'

# Update item
curl -X PUT http://localhost:5000/api/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"qty":3.0}'

# Delete item
curl -X DELETE http://localhost:5000/api/inventory/1

# Get notifications
curl http://localhost:5000/api/notifications

# Get bills
curl http://localhost:5000/api/bills

# Get chores
curl http://localhost:5000/api/chores
```

### View API Logs
```bash
# Logs stored in family_manager/
tail -f family_manager_api.log
tail -f family_manager.log
```

## Database Management

### View Database Contents (SQLite)
```bash
sqlite3 family_manager/family_manager.db

# Common queries
.tables
.schema inventory
SELECT * FROM inventory;
SELECT COUNT(*) FROM inventory;
SELECT * FROM notifications WHERE user_id = 1;

# Backup
.backup backup.db

# Exit
.quit
```

### Export Data
```bash
# Export to CSV
sqlite3 -header -csv family_manager/family_manager.db \
  "SELECT * FROM inventory;" > inventory_export.csv

# Export entire database
sqlite3 family_manager/family_manager.db .dump > database_backup.sql
```

### Import Data
```bash
# Restore from SQL dump
sqlite3 family_manager/family_manager.db < database_backup.sql
```

## Python Environment

### Create Virtual Environment
```bash
# Desktop
cd family_manager/
python3 -m venv venv
source venv/bin/activate

# Mobile
cd /home/server1/Desktop/meal-plan-inventory
python3 -m venv mobile_venv
source mobile_venv/bin/activate
```

### Install Dependencies
```bash
# Desktop
pip install -r family_manager/requirements.txt

# Mobile
pip install -r kivy_app/requirements.txt
```

### Check Python Version
```bash
python3 --version
# Required: 3.7+ for mobile, 3.8+ for desktop
```

### List Installed Packages
```bash
pip list
pip freeze > requirements_frozen.txt
```

## Git Operations

### Check Status
```bash
git status
git log --oneline -10
```

### Commit Changes
```bash
git add family_manager/main.py
git commit -m "feat: Add new feature"

# Or add all
git add -A
git commit -m "feat: Update entire system"
```

### Branch Management
```bash
# List branches
git branch

# Create branch
git checkout -b feature/new-screen

# Switch branch
git checkout main

# Delete branch
git branch -d feature/new-screen
```

### View Changes
```bash
# Diff current changes
git diff
git diff family_manager/main.py

# Diff staged changes
git diff --staged

# View commit history
git log --oneline
git log family_manager/api.py
```

## Development Workflow

### Before Committing Code
```bash
# 1. Check syntax
python3 -m py_compile family_manager/main.py

# 2. Run tests
python3 -m pytest tests/

# 3. Start app to test
python3 family_manager/main.py &
sleep 2

# 4. Test API
curl http://localhost:5000/api/inventory

# 5. Commit
git add -A
git commit -m "fix: Resolve issue"
```

### During Development
```bash
# Terminal 1: Run desktop app
cd family_manager/
python3 main.py

# Terminal 2: Test API
while true; do
  curl http://localhost:5000/api/inventory
  sleep 5
done

# Terminal 3: Mobile testing
cd kivy_app/
python3 main.py
```

### After Changes
```bash
# Verify syntax
python3 -m py_compile family_manager/*.py kivy_app/*.py

# Test core functionality
python3 -m pytest tests/unit/ -v

# Check database integrity
sqlite3 family_manager/family_manager.db "PRAGMA integrity_check;"
```

## Maintenance Tasks

### Weekly
```bash
# Backup database
cp family_manager/family_manager.db family_manager/family_manager.db.$(date +%Y%m%d).backup

# Check logs for errors
grep ERROR family_manager.log

# Update dependencies (if needed)
pip list --outdated
```

### Monthly
```bash
# Clean cache files
rm -rf family_manager/__pycache__
find . -type d -name __pycache__ -exec rm -rf {} +

# Review database size
du -h family_manager/family_manager.db

# Verify backup integrity
sqlite3 family_manager/family_manager.db.backup "PRAGMA integrity_check;"

# Clean old logs
ls -lh family_manager_*.log
# Archive if >100MB
```

### Before Release
```bash
# Full test suite
python3 -m pytest tests/ -v --cov

# Build both APKs
cd kivy_app/
buildozer android debug
buildozer android release

# Verify APKs
ls -lh bin/*.apk

# Test on real device
adb install -r bin/familymanager-0.1-debug.apk
```

## Troubleshooting

### App won't start
```bash
# Check Python version
python3 --version

# Check imports
python3 -c "import PyQt6; print('PyQt6 OK')"
python3 -c "import kivy; print('Kivy OK')"

# Run with verbose errors
python3 -u family_manager/main.py 2>&1 | head -50
```

### Database locked
```bash
# Check processes
lsof family_manager/family_manager.db

# Kill process (careful!)
kill -9 <PID>

# Or restart app
```

### APK installation fails
```bash
# Check device space
adb shell "df /data"

# Uninstall first
adb uninstall org.example.familymanager

# Install with reinstall flag
adb install -r bin/familymanager-0.1-debug.apk
```

### Network issues
```bash
# Test server connectivity
ping localhost
curl -v http://localhost:5000/

# From device/emulator
adb shell ping <host-ip>
adb shell curl http://<host-ip>:5000/
```

## Performance Monitoring

### CPU Usage
```bash
top -p $(pgrep -f "python3 family_manager/main.py")
```

### Memory Usage
```bash
ps aux | grep family_manager
# Check RSS (resident set size) column
```

### Database Performance
```bash
sqlite3 family_manager/family_manager.db
EXPLAIN QUERY PLAN SELECT * FROM inventory WHERE category='Dairy';
```

### API Response Times
```bash
time curl http://localhost:5000/api/inventory
# Lower is better, should be <100ms
```

## Recovery Procedures

### Restore from Backup
```bash
# Stop app first
pkill -f "python3 family_manager/main.py"

# Restore
cp family_manager/family_manager.db.backup family_manager/family_manager.db

# Restart app
python3 family_manager/main.py
```

### Factory Reset Mobile App
```bash
adb uninstall org.example.familymanager
adb shell rm -rf /sdcard/Android/data/org.example.familymanager
adb install bin/familymanager-0.1-debug.apk
```

### Clear All Cache
```bash
cd kivy_app/
rm -f mobile_cache.db
cd ../family_manager/
rm -f family_manager.db
python3 db_setup.py  # Reinitialize
```
