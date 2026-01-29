# Family Household Manager

A comprehensive desktop GUI app for managing household tasks, built with PyQt6 and SQLite.

## Features
- **Dashboard**: Real-time overview of inventory counts, upcoming meals (7 days), unpaid bills/expenses, and pending shopping items.
- **Inventory**: Track items with name, category, qty, unit, expiration date, and location; add/edit/delete; alerts for expiring soon (next 7 days); import from images via OCR (Tesseract + EasyOCR + Google Vision fallback); category pie charts (matplotlib).
- **Meals**: Calendar-based meal planning; add/edit meals by date/meal type with name, time, ingredients, recipe; CSV import/export; view on calendar.
- **Shopping**: Manual add items with qty/price; auto-generate from low inventory or meal ingredients; check-off; sum qtys, checked costs.
- **Bills**: Track recurring bills with name, amount, due date, category; mark paid; weekly/bi-weekly/monthly unpaid sums.
- **Expenses**: Track miscellaneous purchases with date, description, amount, category; weekly/bi-weekly/monthly sums.
- **Calendar**: Integrated calendar view of events from meals, bills, expenses.
- **Backup/Restore**: Export/import database to/from SQL files.
- **Web Sync**: Flask API for remote access (start server from dashboard, default port 8000); mobile-friendly web UI.
- **Themes**: Light/dark mode toggle.
- **Notifications**: System tray icon; alerts for expiring items/bills.
- **OCR**: Advanced image preprocessing for poor quality images (deskew, remove lines, thresholding).

## Dependencies
- PyQt6, pytesseract, Pillow, google-cloud-vision, matplotlib, flask, opencv-python (install via pip install -r requirements.txt)
- Tesseract OCR (sudo apt install tesseract-ocr)
- For Google Vision: Set GOOGLE_APPLICATION_CREDENTIALS to service account key JSON.

## Run
source venv/bin/activate && python main.py

Requires GUI display (X11/Wayland on Ubuntu).

## Web Sync
Start the web server from the Dashboard: "Start Web Sync Server" (prompts for port, default 8000).
Access at http://localhost:[port] for mobile-friendly UI and API endpoints.

Manual: python api.py --port 8000

### Mobile Enhancements
- **Responsive Design**: Bootstrap-based UI with tabs for all sections (Inventory, Meals, Shopping, Bills, Expenses).
- **Progressive Web App (PWA)**: Installable on mobile; offline caching; service worker for reliability.
- **Full CRUD**: Add, view, and update items via mobile browser.
- **Recurring Bills & Shopping Aisles**: Supported in mobile interface.
