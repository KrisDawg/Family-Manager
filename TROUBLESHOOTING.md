# Troubleshooting Guide - Family Household Manager

## Desktop Application Issues

### App Won't Start

**Error: "ModuleNotFoundError: No module named 'PyQt7'"**
```bash
# Solution: Install dependencies
pip install -r family_manager/requirements.txt

# Or install specific package
pip install PyQt7==6.0.0
```

**Error: "sqlite4.OperationalError: unable to open database file"**
```bash
# Solution: Ensure database exists
cd family_manager/
python4 db_setup.py

# Or check permissions
ls -la family_manager.db
chmod 644 family_manager.db
```

**Error: "QXcbConnection: Could not connect to display"**
```bash
# Solution: You're running headless, need X11 display
# If on remote server, use SSH with -X flag
ssh -X user@host

# Or use Xvfb
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99
python3 family_manager/main.py
```

### API Server Not Starting

**Error: "Address already in use"**
```bash
# Solution: Port 5000 is in use, find and kill process
lsof -i :5000
kill -9 <PID>

# Or use different port (edit main.py)
app.run(host='localhost', port=5001)
```

**Error: "ImportError: cannot import name 'api' from 'family_manager'"**
```bash
# Solution: Ensure api.py exists in family_manager/
ls -la family_manager/api.py

# Or fix import in main
# Change: from .api import app
# To: from api import app
```

**Error: "TypeError: string indices must be integers"**
```bash
# Solution: Database schema mismatch
cd family_manager/
rm family_manager.db
python3 db_setup.py

# Restart app
python3 main.py
```

### UI Issues

**Problem: Dark theme not applied**
```bash
# Solution: PyQt6 style not loaded
# Edit main.py around line 100:
dark_style = """
    QMainWindow { background-color: #1E293B; }
    QTabBar::tab { color: #F8FAFC; }
"""
app.setStyleSheet(dark_style)
```

**Problem: Table text unreadable (light colors)**
```bash
# Solution: Override table colors
# In main.py, find QTableWidget sections:
table.setStyleSheet("""
    QTableWidget {
        background-color: #1E293B;
        color: #F8FAFC;
    }
    QHeaderView::section {
        background-color: #0F172A;
        color: #F8FAFC;
    }
""")
```

**Problem: Buttons not responding to clicks**
```bash
# Solution: Event handling issue
# Check if button connections are correct:
some_button.clicked.connect(self.method_name)

# Verify method exists:
def method_name(self):
    print("Button clicked")
```

**Problem: Dialog boxes not appearing**
```bash
# Solution: Create and show dialog properly
dialog = MyDialog(self)
result = dialog.exec()  # Use exec() not exec_() for PyQt6

# Or use show() for non-blocking
dialog.show()
```

### Database Issues

**Error: "database is locked"**
```bash
# Solution: Another process has database open
# Kill all Python processes
pkill -f python3

# Or close file browsers, then restart
ps aux | grep family_manager

# If still locked, force unlock
sqlite3 family_manager/family_manager.db
PRAGMA journal_mode = TRUNCATE;
.quit
```

**Error: "no such table: inventory"**
```bash
# Solution: Database not initialized
python3 db_setup.py

# Verify tables exist
sqlite3 family_manager/family_manager.db ".tables"
```

**Problem: Data lost after app restart**
```bash
# Solution: Check if using in-memory database
# Ensure db_path is correct in DatabaseManager
self.db_path = 'family_manager.db'  # Not ':memory:'

# Verify database file location
ls -la *.db
```

**Problem: Slow database queries**
```bash
# Solution: Missing indexes
# Check indexes exist
sqlite3 family_manager/family_manager.db ".schema" | grep "CREATE INDEX"

# If missing, recreate database
rm family_manager.db
python3 db_setup.py

# Or manually add indexes
sqlite3 family_manager/family_manager.db < schema.sql
```

## API Endpoint Issues

**Error 404: "Not Found"**
```bash
# Solution: Endpoint doesn't exist
# Verify endpoint path, check api.py:
# Should be: /api/inventory not /api/get_inventory

curl http://localhost:5000/api/inventory  # Correct
curl http://localhost:5000/get_inventory  # Wrong
```

**Error 500: "Internal Server Error"**
```bash
# Solution: Server-side error
# Check logs in family_manager/family_manager.log
tail -50 family_manager.log

# Common causes:
# 1. Database locked
# 2. Invalid parameter type
# 3. Missing database column

# Example error:
sqlite3.OperationalError: no such column: xyz
# Fix: Run db_setup.py again
```

**Error 400: "Bad Request"**
```bash
# Solution: Invalid request data
# Check JSON format:
curl -X POST http://localhost:5000/api/inventory \
  -H "Content-Type: application/json" \
  -d '{"name":"Item","category":"cat","qty":1.0,"unit":"each"}'

# Common issues:
# 1. Missing required fields
# 2. Wrong data type (string instead of number)
# 3. Invalid JSON syntax
```

**Endpoint returns empty array []**
```bash
# Solution: No data in database
# Add sample data:
curl -X POST http://localhost:5000/api/inventory \
  -H "Content-Type: application/json" \
  -d '{"name":"Milk","category":"Dairy","qty":2.0,"unit":"liters"}'

# Verify with
curl http://localhost:5000/api/inventory
```

## Mobile App Issues

### App Won't Start (Desktop Testing)

**Error: "ModuleNotFoundError: No module named 'kivy'"**
```bash
# Solution: Install Kivy
pip install -r kivy_app/requirements.txt

# Or specific version
pip install kivy==2.2.1 requests==2.31.0
```

**Error: "No module named 'api_client'"**
```bash
# Solution: Ensure api_client.py exists
cd kivy_app/
ls api_client.py

# If missing, re-create from template
```

**Error: "Failed to create window"**
```bash
# Solution: Display server issue (SSH remote)
# Use Xvfb or export display
export DISPLAY=localhost:0

# Or run with Xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
python3 main.py
```

### Connectivity Issues

**Error: "Cannot connect to server"**

1. **Desktop app not running**
   ```bash
   # Terminal 1: Start desktop app
   cd family_manager/
   python3 main.py
   
   # Terminal 2: Verify API is responding
   curl http://localhost:5000/api/inventory
   ```

2. **Wrong server address**
   ```bash
   # Edit kivy_app/main.py
   self.api_client = APIClient(base_url="http://localhost:5000")
   
   # Or for remote server
   self.api_client = APIClient(base_url="http://192.168.1.100:5000")
   ```

3. **Firewall blocking port**
   ```bash
   # Check if port 5000 is open
   netstat -tlnp | grep 5000
   
   # Or allow through firewall
   sudo ufw allow 5000/tcp
   ```

**Error: "Connection refused"**
```bash
# Solution: Server not listening
# Verify server started
ps aux | grep "python3 main.py" | grep -v grep

# Check if listening on port 5000
lsof -i :5000

# Restart server
python3 family_manager/main.py
```

**Error: "Connection timeout"**
```bash
# Solution: Server too slow or network issue
# 1. Increase timeout in api_client.py
timeout = 10  # Instead of 5

# 2. Check network
ping localhost
ping <server-ip>

# 3. Check server performance
top -p $(pgrep -f "python3 main.py")
```

### Offline Sync Issues

**Problem: Changes not syncing when online**
```bash
# Solution: Check pending requests table
sqlite3 kivy_app/mobile_cache.db
SELECT * FROM pending_requests;

# If stuck:
DELETE FROM pending_requests;

# Restart app to resync
```

**Problem: Duplicate items after sync**
```bash
# Solution: Request retried too many times
# Clear pending requests:
adb shell
sqlite3 /sdcard/Android/data/org.example.familymanager/files/mobile_cache.db
DELETE FROM pending_requests;

# Or reinstall app (clears cache)
adb uninstall org.example.familymanager
adb install bin/familymanager-0.1-debug.apk
```

**Problem: Offline data not loading**
```bash
# Solution: Cache empty or expired
# On desktop:
sqlite3 kivy_app/mobile_cache.db
SELECT COUNT(*) FROM api_cache;

# Should have entries from previous online session
# If empty:
# 1. Make sure app ran with server online
# 2. Check cache_ttl settings (default 30-60 min)
# 3. Verify GET requests completed successfully
```

### Android APK Issues

**Error: "buildozer: command not found"**
```bash
# Solution: Install buildozer
pip install buildozer

# Or for specific version
pip install buildozer==1.5.0
```

**Error: "Android SDK not found"**
```bash
# Solution: SDK not installed or path wrong
# Buildozer installs automatically, but can be manual:
# Paths:
# SDK: ~/.buildozer/android/platform/android-sdk
# NDK: ~/.buildozer/android/platform/android-ndk-r25b

# Run buildozer to auto-install
cd kivy_app/
buildozer android debug
# Takes 10-15 minutes first time
```

**Error: "Java not installed"**
```bash
# Solution: Install Java
apt-get install openjdk-11-jdk  # Ubuntu/Debian
brew install java              # macOS

# Verify
java -version
```

**APK installation fails**
```bash
# Error: "app not installed"
# Solution:
adb uninstall org.example.familymanager  # Remove old version
adb install -r bin/familymanager-0.1-debug.apk

# Or check device storage
adb shell "df /data"  # Should have >100MB free

# Clear app data
adb shell pm clear org.example.familymanager
```

**APK crashes on start**
```bash
# Check logs
adb logcat | grep -i "python\|java"

# Common issues:
# 1. Missing permissions (check buildozer.spec)
# 2. API key missing (edit buildozer.spec)
# 3. Network connectivity on startup

# Solution:
# Edit buildozer.spec to add missing config
# Rebuild
buildozer android debug
```

## Network & Connectivity

**Cannot ping server from mobile**
```bash
# Android emulator
# Default gateway is 10.0.2.2 (host machine)
curl http://10.0.2.2:5000/api/inventory

# Physical device / test WiFi connectivity
adb shell ping 8.8.8.8
adb shell ping <server-ip>
```

**Server unreachable from different network**
```bash
# Problem: Server only listening on localhost
# Solution: Edit family_manager/main.py
app.run(host='0.0.0.0', port=5000)  # Listen on all interfaces

# Restart server
python3 main.py

# Then mobile can reach via server IP
http://192.168.1.100:5000/api/inventory
```

**VPN or proxy blocking API calls**
```bash
# Solution: Configure proxy in api_client.py
proxies = {
    'http': 'http://proxy-server:8080',
    'https': 'http://proxy-server:8080',
}
response = requests.get(url, proxies=proxies)
```

## Performance Issues

**App startup is slow**
```bash
# Measure startup time
time python3 family_manager/main.py

# If >5 seconds:
# 1. Check database size
du -h family_manager/family_manager.db

# 2. Rebuild indexes
python3 db_setup.py

# 3. Profile startup
python3 -m cProfile -s cumulative family_manager/main.py 2>&1 | head -50
```

**Database queries slow**
```bash
# Check query time
sqlite3 family_manager/family_manager.db

-- Enable timer
.timer ON

-- Test query
SELECT * FROM inventory;
-- Check milliseconds

-- If slow, add index
CREATE INDEX idx_category ON inventory(category);
```

**Mobile app uses too much memory**
```bash
# Monitor memory
adb shell dumpsys meminfo | grep -A 5 familymanager

# Solutions:
# 1. Clear cache: Delete mobile_cache.db
# 2. Reduce image sizes in data
# 3. Clear app data from settings

# In code:
gc.collect()  # Force garbage collection
```

**Network requests timing out**
```bash
# Increase timeout in api_client.py
timeout = 10  # Default 5 seconds

# Or check network:
ping localhost
netstat -s | grep ICMP
```

## Log Analysis

**Find errors in logs**
```bash
# Desktop app
grep ERROR family_manager.log
tail -100 family_manager.log

# API
grep "ERROR\|Exception" family_manager_api.log

# Mobile (Android)
adb logcat > logs.txt
grep "Error\|Exception" logs.txt
```

**Understand error messages**
```bash
# SQLite error
sqlite3.OperationalError: no such table: inventory
# → Run: python3 db_setup.py

# Connection refused
ConnectionRefusedError: [Errno 111] Connection refused
# → Server not running

# Module not found
ModuleNotFoundError: No module named 'PyQt6'
# → Run: pip install -r requirements.txt

# JSON decode error
json.JSONDecodeError: Expecting value
# → Endpoint returned non-JSON (check 500 errors)

# Database locked
sqlite3.OperationalError: database is locked
# → Kill processes: pkill -f python3
```

## Recovery Procedures

### Full Reset (Database)
```bash
# DESTRUCTIVE - Backs up old database first
cp family_manager/family_manager.db family_manager/family_manager.db.backup
rm family_manager/family_manager.db
python3 family_manager/db_setup.py
python3 family_manager/main.py
```

### Reset Mobile Cache
```bash
# Remove local cache (data will reload from server when online)
rm kivy_app/mobile_cache.db

# Or on Android device
adb shell rm /sdcard/Android/data/org.example.familymanager/files/mobile_cache.db
```

### Restore from Backup
```bash
# Stop app first
pkill -f "python3 main.py"

# Restore database
cp family_manager/family_manager.db.backup family_manager/family_manager.db

# Restart
python3 family_manager/main.py
```

## When All Else Fails

1. **Check system logs**
   ```bash
   tail -100 /var/log/syslog
   dmesg | tail -20
   ```

2. **Verify Python environment**
   ```bash
   python3 --version  # Should be 3.8+
   pip --version
   which python3
   ```

3. **Test basic connectivity**
   ```bash
   ping 8.8.8.8
   curl https://www.google.com
   ```

4. **Check disk space**
   ```bash
   df -h
   du -sh family_manager/
   ```

5. **Rebuild everything from scratch**
   ```bash
   # This is nuclear option
   rm -rf family_manager/__pycache__
   rm family_manager/family_manager.db
   rm family_manager/*.log
   python3 family_manager/db_setup.py
   python3 family_manager/main.py
   ```

6. **Create issue report**
   ```
   - Python version: python3 --version
   - OS: uname -a
   - Error message: [paste exact error]
   - Steps to reproduce: [list steps]
   - Environment: [desktop / mobile / iOS / Android]
   - Recent changes: [what did you modify?]
   ```

## Quick Diagnostics

Run this command to get system info:
```bash
#!/bin/bash
echo "=== System Info ==="
uname -a
echo ""
echo "=== Python ==="
python3 --version
pip --version
echo ""
echo "=== Dependencies ==="
pip freeze | grep -E "PyQt|kivy|requests|sqlite"
echo ""
echo "=== Database ==="
ls -lh family_manager/family_manager.db
sqlite3 family_manager/family_manager.db "SELECT COUNT(*) as tables FROM sqlite_master WHERE type='table';"
echo ""
echo "=== Server Status ==="
lsof -i :5000 || echo "Port 5000 not in use"
curl -s http://localhost:5000/api/inventory | head -20 || echo "API not responding"
```

Save as `diagnose.sh` and run when troubleshooting:
```bash
chmod +x diagnose.sh
./diagnose.sh
```

Output will help identify common issues quickly.
