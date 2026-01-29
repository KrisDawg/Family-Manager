# Family Manager - Getting Started

## Quick Start Guide

### Prerequisites

Before you begin, ensure you have:
- **Desktop App**: Running on `http://localhost:5000`
- **Python 3.7+**: For running the mobile app
- **Kivy 2.2+**: For desktop testing (optional for APK building)

### Step 1: Start the Desktop App

```bash
cd family_manager/
python3 main.py
```

The Flask API should start on `http://localhost:5000`

### Step 2: Test the Mobile App (Desktop)

```bash
cd kivy_app/
pip install -r requirements.txt
python3 main.py
```

You should see the mobile app with Material Design UI:
- **Dashboard**: Summary cards
- **Inventory**: Browse items
- **Shopping**: Manage list
- **Chores**: View assignments
- **Tasks**: Track projects
- **Notifications**: View alerts

### Step 3: Build Android APK

#### Setup Android Environment

1. **Install buildozer**:
   ```bash
   pip install buildozer
   ```

2. **Android SDK** (automatic with buildozer, but can be manual):
   - SDK location: `~/.buildozer/android/platform/android-sdk`
   - API Level: 33
   - Build Tools: 33.0.2

3. **Android NDK**:
   - NDK location: `~/.buildozer/android/platform/android-ndk-r25b`
   - Used for native module compilation

#### Build Debug APK

```bash
cd kivy_app/
buildozer android debug
```

**Output**: `bin/familymanager-0.1-debug.apk`

Test on emulator or device:
```bash
adb install bin/familymanager-0.1-debug.apk
```

#### Build Release APK

```bash
buildozer android release
```

**Output**: `bin/familymanager-0.1-release.apk`

### Step 4: Configure Connection

If not running on localhost:5000, edit `kivy_app/main.py`:

```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.api_client = APIClient(base_url="http://your-server:5000")
```

Then rebuild the APK.

## Features Overview

### Dashboard
- Quick summary of all metrics
- Touch cards to navigate to sections
- Auto-refresh on screen enter

### Inventory Management
- **Browse**: All items with quantity, category, expiration
- **Add**: New items with category selection
- **Offline**: Cached for fast access

### Shopping List
- **View**: All items with checkboxes
- **Add**: New items with optional quantity
- **Check**: Mark items as purchased
- **Sync**: Changes saved when online

### Chores
- **View**: Pending chores with due dates
- **Filter**: By assignee or status
- **Complete**: Mark as done

### Tasks
- **View**: Projects and tasks
- **Filter**: By status or project
- **Complete**: Mark complete

### Notifications
- **View**: All notifications
- **Priority**: Color-coded (high/urgent in red)
- **Read**: Mark notifications as read
- **Type**: Sorted by type (reminder, alert, chore, task, etc.)

## Offline Mode

The app automatically:
1. **Detects** loss of connection (checks every 30 seconds)
2. **Caches** GET requests (keeps data available)
3. **Queues** POST/PUT/DELETE (saves for later)
4. **Syncs** when connection restored
5. **Shows** "Working Offline" indicator (if implemented)

### Offline Behavior

| Action | Online | Offline |
|--------|--------|---------|
| View data | Live | Cached |
| Add/Edit/Delete | Immediate | Queued |
| Notifications | Real-time | Cached |
| Sync | Continuous | On reconnect |

## Troubleshooting

### "Cannot connect to server"

1. **Desktop app running?**
   ```bash
   curl http://localhost:5000/api/inventory
   ```
   Should return JSON array

2. **Android device/emulator network?**
   - Emulator: Reconnect to host
   - Device: Check WiFi connected
   - Check firewall allows port 5000

3. **Wrong server address?**
   - Edit `kivy_app/main.py`
   - Rebuild APK
   - Clear app data: `adb shell pm clear org.example.familymanager`

### "App crashes on startup"

1. **Check logs**:
   ```bash
   adb logcat | grep familymanager
   ```

2. **Common issues**:
   - Missing Kivy: `pip install -r requirements.txt`
   - Server offline: Start desktop app
   - Corrupted cache: Delete `mobile_cache.db`

### "Sync not working"

1. **Check connectivity**:
   ```bash
   adb shell ping localhost  # On emulator
   adb shell ping 192.168.x.x  # On device, use host IP
   ```

2. **Check pending requests**:
   - App stores in `mobile_cache.db`
   - Table: `pending_requests`
   - Check `retry_count` < 3

3. **Force sync**:
   - Go to Dashboard and back
   - Or restart app

## Performance Tips

### Faster App Startup
- Use release APK (smaller, optimized)
- Clear cache: `adb shell pm clear org.example.familymanager`

### Better Offline Performance
- Cache TTL defaults: 30-60 minutes
- Sync checks: Every 30 seconds
- Pending request retry: Up to 3 times

### Network Optimization
- Cache GET requests (default 30-60 min)
- Queue writes for offline
- Batch syncs (max 10 per check)

## Development Tips

### Adding New Features

1. **New API method** (api_client.py):
   ```python
   def get_custom_data(self) -> List[Dict]:
       result = self.get_with_cache('custom-endpoint', cache_ttl=30)
       return result if isinstance(result, list) else []
   ```

2. **New Screen** (main.py):
   ```python
   class CustomScreen(Screen):
       def __init__(self, api_client: APIClient, **kwargs):
           super().__init__(**kwargs)
           self.api_client = api_client
           self.name = 'custom'
           # Build UI...
   ```

3. **Register Screen**:
   ```python
   sm.add_widget(CustomScreen(self.api_client))
   sm.get_screen('dashboard').manager = sm
   ```

### Testing

```bash
# Install Kivy desktop
pip install kivy

# Run app
python3 main.py

# Test with different screen sizes
# Modify Window.size in main.py
```

### Debugging

1. **Print logging**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info(f"Debug: {data}")
   ```

2. **Android logcat**:
   ```bash
   adb logcat | grep "python\|java"
   ```

3. **Network inspection**:
   ```bash
   adb shell tcpdump -i any -w /sdcard/traffic.pcap
   ```

## Architecture Decisions

### Why Material Design?
- Modern, clean aesthetic
- Familiar to Android users
- Lightweight (minimal dependencies)
- Responsive and accessible

### Why Offline-First?
- Mobile networks unreliable
- Reduces server load
- Better user experience
- Works on airplane mode

### Why SQLite Cache?
- Lightweight, no extra server
- Local, fast access
- Easy to manage/clear
- Automatic expiration

### Why Kivy?
- Pure Python
- Single codebase for iOS/Android
- Material Design support
- Active community

## Security Notes

- No password storage (relies on desktop auth)
- API calls use plain HTTP (localhost only)
- Cache cleared on app uninstall
- Pending requests removed after 3 failed retries

## Next Steps

1. **Test Features**: Use mobile app with desktop app
2. **Customize Theme**: Edit Colors in main.py
3. **Add Screens**: Create new screens for products/budgets
4. **Publish**: Build release APK for Play Store
5. **Marketing**: Submit to Google Play Store

## Support

For issues:
1. Check logs: `adb logcat`
2. Test connectivity: Ping server
3. Clear cache: Uninstall and reinstall
4. Reset: Delete `mobile_cache.db`
