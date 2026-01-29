# Family Manager Mobile App

Modern Material Design Kivy application for managing family household tasks, inventory, shopping lists, and more.

## Features

- **Dashboard**: Quick summary of all tasks, chores, shopping items, and notifications
- **Inventory Management**: Track grocery items, quantities, and expiration dates
- **Shopping Lists**: Create and manage shopping lists with checkmarks
- **Chores**: View and manage family chores with assignments
- **Tasks**: Manage projects and tasks with due dates
- **Notifications**: Receive and manage notifications about upcoming events
- **Offline Support**: Works without internet, syncs changes when back online
- **Material Design**: Modern, clean UI with Material Design colors and components

## Installation

### Prerequisites

- Python 3.7+
- Kivy 2.2+ (for desktop testing)
- buildozer 1.4+ (for APK building)

### Desktop Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python3 main.py
```

### Android APK Build

```bash
# Install buildozer if not already installed
pip install buildozer

# Build APK (requires Android SDK/NDK)
buildozer android debug

# Or release APK
buildozer android release

# APK will be in bin/ directory
```

## Architecture

### API Client (`api_client.py`)
- Handles all communication with desktop Flask API
- Automatic request caching for offline support
- Request queuing for offline sync
- Retry logic with exponential backoff
- Thread-safe operations

### Screens
- **Dashboard**: Main screen with quick access cards
- **Inventory**: Browse and manage inventory items
- **Shopping**: Manage shopping lists with checkmarks
- **Chores**: View pending chores
- **Tasks**: View pending tasks
- **Notifications**: View and manage notifications

### Color Scheme (Material Design)
- Primary: #3399FF (Blue)
- Accent: #FF8C1A (Orange)
- Error: #F2261A (Red)
- Success: #26CC4D (Green)
- Background: #F2F2F2 (Light Gray)

## Configuration

### Server Connection

Modify the base URL in `main.py` if using a non-local server:

```python
self.api_client = APIClient(base_url="http://your-server:5000")
```

### Offline Cache

Cache database is stored in `mobile_cache.db`. Automatic cleanup of expired cache entries happens during sync.

## API Integration

The app integrates with the desktop Flask API with 53 endpoints:

### Inventory (8 endpoints)
- GET/POST/PUT/DELETE inventory items
- List with category filtering

### Shopping List (8 endpoints)
- GET/POST/PUT/DELETE shopping items
- Check/uncheck items

### Meals (4 endpoints)
- GET/POST/DELETE meal plans

### Bills/Expenses (8 endpoints)
- GET/POST/PUT/DELETE bills
- Mark as paid

### Chores (6 endpoints)
- GET/POST/PUT/DELETE chores
- Mark complete

### Tasks (11 endpoints)
- GET/POST/PUT/DELETE tasks
- Manage projects
- Add comments

### Notifications (12 endpoints)
- GET/POST/PUT/DELETE notifications
- Mark read/unread
- Get unread count

## Features in Detail

### Offline Support

1. **Automatic Caching**: GET requests are cached for 30-60 minutes
2. **Request Queueing**: POST/PUT/DELETE requests are queued when offline
3. **Automatic Sync**: Pending requests are synced when back online
4. **Smart Retries**: Failed syncs retry up to 3 times

### Background Sync

The app automatically:
- Checks connectivity every 30 seconds
- Syncs pending requests when back online
- Updates UI after successful sync

### Error Handling

- Network timeouts: 5 seconds
- Automatic retry: 3 attempts with 30-60 second backoff
- Graceful degradation: Falls back to cached data

## Development

### Adding New Screens

1. Create a new Screen class inheriting from `kivy.uix.screenmanager.Screen`
2. Add API calls via `self.api_client`
3. Register in `FamilyManagerApp.build()`:
   ```python
   sm.add_widget(YourNewScreen(self.api_client))
   ```

### Adding New API Methods

1. Add method to `APIClient` class in `api_client.py`
2. Use `self.request()` for POST/PUT/DELETE (offline support)
3. Use `self.get_with_cache()` for GET (automatic caching)

## Performance

- Material Design UI renders smoothly at 60 FPS
- Asynchronous API calls prevent UI blocking
- Efficient caching reduces network traffic
- Background connectivity check (every 30 seconds)

## Troubleshooting

### App won't connect to server
1. Ensure desktop app is running: `python3 family_manager/main.py`
2. Check server is on `http://localhost:5000`
3. Check firewall settings allow local network access
4. Run `adb logcat` on Android to see detailed errors

### APK build fails
1. Ensure Android SDK/NDK are properly installed
2. Check `buildozer --help` for troubleshooting
3. Clear build cache: `buildozer android clean`
4. Try `buildozer android debug` first (easier than release)

### Offline sync not working
1. Check internet connection available
2. Ensure server is running
3. Check mobile_cache.db exists
4. Monitor logcat for sync errors

## License

Part of Family Household Manager project
