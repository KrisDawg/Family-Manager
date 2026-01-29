# Family Manager Mobile App

A mobile version of the Family Household Manager built with Kivy for cross-platform compatibility (Android, iOS, Desktop).

## Features

- **Dashboard**: Overview of inventory count and today's date
- **Inventory Management**: Add, view, and manage household inventory items
- **Meals Planning**: View meal plans and schedules
- **Shopping List**: Create and manage shopping lists with check-off functionality

## Installation

### Desktop Development
```bash
# Create virtual environment
python3 -m venv mobile_venv
source mobile_venv/bin/activate  # Linux/Mac
# mobile_venv\Scripts\activate   # Windows

# Install Kivy
pip install kivy

# Run the app
python mobile_app.py
```

### Android Build (requires Buildozer)
```bash
# Install buildozer
pip install buildozer

# Configure buildozer.spec as needed
buildozer init  # or copy the provided buildozer.spec

# Build APK
buildozer android debug

# Deploy to device
buildozer android deploy run
```

## Database

The app uses SQLite with the following tables:
- `inventory`: Household items with categories, quantities, expiration dates
- `meals`: Meal planning and recipes
- `shopping_list`: Shopping items with check-off status

Database is automatically created on first run.

## Architecture

- **Kivy Framework**: Cross-platform UI framework
- **ScreenManager**: Navigation between different app sections
- **SQLite**: Local database for data persistence
- **Mobile-optimized UI**: Touch-friendly interface with portrait orientation

## Development

The mobile app is a gradual port from the desktop PyQt6 version, focusing on:
1. Core database functionality
2. Essential features (inventory, shopping)
3. Mobile-optimized UI/UX
4. Platform-specific optimizations

## File Structure

```
mobile_app.py          # Main application
buildozer.spec         # Android build configuration
family_manager_mobile.db  # SQLite database (created automatically)
```

## Requirements

- Python 3.7+
- Kivy 2.3+
- SQLite3 (built-in)

For Android builds:
- Buildozer
- Android SDK/NDK (handled by buildozer)