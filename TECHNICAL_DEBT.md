# Technical Debt & Roadmap - Family Household Manager

## Overview

This document tracks known technical debt, planned improvements, and future features. It helps prioritize work and maintain code quality as the project grows.

## Current Technical Debt

### HIGH PRIORITY (Should Address This Month)

#### 1. Mobile Screen Count Badges Not Real-Time
**Issue**: Dashboard cards show counts when app starts, but don't update when user adds items in other screens
**Impact**: Users see stale counts until they switch screens and back
**Severity**: Medium - UX issue, no data corruption
**Solution**: Implement EventBus or signals for screen-to-screen communication
**Effort**: 2-3 hours
**Status**: Not Started

```python
# Implement cross-screen signaling
class ScreenEventBus:
    _instance = None
    _listeners = {}
    
    @classmethod
    def emit(cls, event_name: str, data: dict):
        if event_name in cls._listeners:
            for callback in cls._listeners[event_name]:
                callback(data)
    
    @classmethod
    def listen(cls, event_name: str, callback):
        if event_name not in cls._listeners:
            cls._listeners[event_name] = []
        cls._listeners[event_name].append(callback)
```

#### 2. Missing Error Dialogs in Mobile App
**Issue**: Network errors, API failures, sync issues don't show user feedback
**Impact**: Users think app is frozen or doesn't know what went wrong
**Severity**: High - Critical for production
**Solution**: Add Popup dialogs for errors, loading states for API calls
**Effort**: 4-5 hours
**Status**: Not Started

```python
# Example: Add progress dialog during API call
def add_item(self):
    progress = Popup(title="Adding Item", size_hint=(0.6, 0.3))
    progress.open()
    
    try:
        result = self.api_client.add_inventory(...)
        progress.dismiss()
        show_success("Item added!")
    except Exception as e:
        progress.dismiss()
        show_error(f"Failed: {str(e)}")
```

#### 3. Mobile Cache TTL Not Configurable
**Issue**: Cache times hardcoded to 30-60 minutes, users can't adjust
**Impact**: Users may not see latest data, or excessive network usage
**Severity**: Low - Works but inflexible
**Solution**: Add settings screen to configure cache TTL
**Effort**: 3-4 hours
**Status**: Not Started

#### 4. No Authentication Mechanism
**Issue**: APIs are open to anyone who knows the URL
**Impact**: Desktop and mobile apps don't have access control
**Severity**: High - Major security risk for shared family data
**Solution**: Add simple token-based auth (hardcoded user ID for now)
**Effort**: 6-8 hours
**Status**: Not Started

```python
# Add auth headers to all mobile requests
headers = {
    'Authorization': f'Bearer {user_id}',
    'Content-Type': 'application/json'
}
response = requests.get(url, headers=headers)
```

#### 5. No Backup/Restore Feature
**Issue**: Users have no way to backup their data
**Impact**: If database is deleted, all data is lost forever
**Severity**: High - Data loss risk
**Solution**: Add export/import buttons in Settings tab
**Effort**: 5-6 hours
**Status**: Not Started

### MEDIUM PRIORITY (Address Before Production)

#### 6. Recurring Events Don't Handle Exceptions
**Issue**: Can't skip a single instance of recurring event (e.g., "skip chore this week")
**Impact**: Users must delete/recreate if they want to skip one instance
**Severity**: Medium - Workaround exists
**Solution**: Add recurring_event_exceptions table and skip logic
**Effort**: 4-5 hours
**Status**: Not Started

#### 7. Mobile Offline Mode Not Obvious
**Issue**: No visual indicator when app is offline
**Impact**: Users think network is working when it's not
**Severity**: Low - System works, just not clear
**Solution**: Add "Working Offline" banner at top of screen
**Effort**: 2-3 hours
**Status**: Not Started

```python
# Add banner to main screen
def on_offline(self):
    banner = BoxLayout(size_hint_y=None, height='40dp')
    banner.add_widget(Label(text='[color=ff0000]●[/color] Working Offline',
                           markup=True))
    self.screen_box.add_widget(banner)
```

#### 8. No Notification Preferences UI
**Issue**: Only admin can change notification types in database
**Impact**: Non-admin users can't control if they get notifications
**Severity**: Medium - Data exists but inaccessible
**Solution**: Add Settings dialog in desktop and mobile to configure notifications
**Effort**: 4-5 hours
**Status**: Not Started

#### 9. Notification Deduplication Weak
**Issue**: Spam prevention uses 24-48 hour windows, but still repeats for same item
**Impact**: Users get notification daily for same low-inventory item
**Severity**: Low - Annoying but not breaking
**Solution**: Track last-notified item + type in notifications table
**Effort**: 2-3 hours
**Status**: Not Started

#### 10. Mobile Layout Not Responsive
**Issue**: UI breaks on larger screens (tablets, landscape mode)
**Impact**: App doesn't adapt to different devices
**Severity**: Low - Works on phones
**Solution**: Use adaptive layouts, test on multiple screen sizes
**Effort**: 6-8 hours
**Status**: Not Started

### LOW PRIORITY (Nice-to-Have, Post-MVP)

#### 11. No Real Push Notifications
**Issue**: Mobile app only checks server every 30 seconds
**Impact**: Users don't get instant alerts
**Severity**: Low - Polling works for family app
**Solution**: Implement Firebase Cloud Messaging (FCM)
**Effort**: 10-12 hours
**Status**: Planned for Phase 6

#### 12. No Data Visualization
**Issue**: No charts or graphs for spending, inventory trends
**Impact**: Hard to analyze patterns
**Severity**: Low - Not required for MVP
**Solution**: Add matplotlib/plotly for charts
**Effort**: 8-10 hours
**Status**: Planned for Phase 7

#### 13. No Recipe Suggestions
**Issue**: Meal planner doesn't suggest recipes based on inventory
**Impact**: Users plan meals manually
**Severity**: Low - Enhancement feature
**Solution**: Integrate with Spoonacular recipe API
**Effort**: 6-8 hours
**Status**: Planned for Phase 7

#### 14. No Shared Budgets
**Issue**: Each expense is independent, no family budget tracking
**Impact**: No central spending limit
**Severity**: Low - Workaround: track manual
**Solution**: Add shared_budgets table and category limits
**Effort**: 5-6 hours
**Status**: Planned for Phase 8

#### 15. iOS App Not Started
**Issue**: Only Android APK built, iOS folks can't use
**Impact**: 50% of users potentially blocked
**Severity**: Medium - Significant market
**Solution**: Use Kivy iOS backend for iOS app
**Effort**: 15-20 hours
**Status**: Planned for Phase 9

## Code Quality Issues

### Type Hints Missing
**Impact**: Harder to debug, IDE autocomplete limited
**Files Affected**: family_manager/main.py, family_manager/api.py, kivy_app/main.py
**Priority**: Low - Code works
**Solution**: Add type hints to all function signatures
**Effort**: 8-10 hours

```python
# Before
def add_inventory(item_data):
    return db.add(item_data)

# After
def add_inventory(self, item_data: Dict[str, Union[str, float]]) -> Dict[str, Any]:
    return self.db.add(item_data)
```

### Limited Documentation
**Impact**: New developers can't understand code flow
**Files Affected**: kivy_app/api_client.py, family_manager/notification_triggers.py
**Priority**: Medium - Important for maintenance
**Solution**: Add docstrings to all classes and methods
**Effort**: 6-8 hours

### Error Handling Inconsistent
**Impact**: Some errors handled gracefully, others crash app
**Areas**: Mobile app network errors, desktop dialog exceptions
**Priority**: Medium - Should be consistent
**Solution**: Create centralized ErrorHandler class
**Effort**: 5-6 hours

```python
class ErrorHandler:
    @staticmethod
    def handle(error: Exception, context: str = "") -> Dict:
        logger.error(f"{context}: {error}")
        
        if isinstance(error, ConnectionError):
            return {'message': 'Network not available', 'severity': 'warning'}
        elif isinstance(error, ValueError):
            return {'message': 'Invalid input', 'severity': 'error'}
        else:
            return {'message': 'Unexpected error', 'severity': 'critical'}
```

### Hardcoded Values
**Impact**: Can't easily change configuration
**Examples**: Cache TTL (30-60 min), API timeout (5 sec), notification interval (1 hour)
**Priority**: Medium - Limits flexibility
**Solution**: Move to config file or environment variables
**Effort**: 3-4 hours

```python
# Create config.py
class Config:
    CACHE_TTL_MINUTES = 60
    API_TIMEOUT_SECONDS = 5
    NOTIFICATION_CHECK_INTERVAL_HOURS = 1
    MAX_RETRIES = 3
```

## Testing Gaps

### Mobile App UI Not Tested
**Coverage**: 0% automated
**Impact**: UI bugs only found during manual testing
**Priority**: Medium - Critical for production
**Solution**: Add Kivy UI tests with pytest
**Effort**: 10-12 hours

```python
# Example Kivy test
class TestInventoryScreen(unittest.TestCase):
    def setUp(self):
        self.app = FamilyManagerApp()
        self.screen = InventoryScreen(self.app.api_client)
    
    def test_add_button_opens_dialog(self):
        add_button = self.screen.ids.add_button
        add_button.trigger_action()
        self.assertIsNotNone(self.screen.add_dialog)
```

### Notification Triggers Not Tested
**Coverage**: 0% automated
**Impact**: Bugs in trigger logic only found if user notices wrong notification
**Priority**: High - Critical for feature
**Solution**: Add unit tests for each trigger type
**Effort**: 6-8 hours

```python
class TestNotificationTriggers(unittest.TestCase):
    def setUp(self):
        self.triggers = NotificationTriggers(self.mock_db)
    
    def test_low_inventory_trigger(self):
        # Add item with qty=2
        self.db.add_inventory("Milk", qty=2.0)
        self.triggers.check_low_inventory()
        # Verify notification created
```

### Integration Tests Limited
**Coverage**: API endpoints only
**Missing**: Mobile ↔ Desktop sync, offline workflow, end-to-end scenarios
**Priority**: Medium
**Effort**: 10+ hours

### Performance Tests Not Automated
**Impact**: Don't know if repo caused performance regression
**Priority**: Low
**Solution**: Add performance baseline tests
**Effort**: 5-6 hours

## Performance Optimizations

### Database Query Optimization
**Issue**: Some queries scan full table
**Impact**: Slower as data grows (1000+ items)
**Solution**: Verify all WHERE clauses have indexes
**Effort**: 4-5 hours

```bash
# Check query performance
sqlite3 family_manager/family_manager.db
EXPLAIN QUERY PLAN SELECT * FROM inventory WHERE category='Dairy';
-- Should use index, not full table scan
```

### Image Processing
**Issue**: Large receipt images processed at full resolution
**Impact**: Slow OCR with memory usage
**Solution**: Resize images before Gemini API call
**Effort**: 3-4 hours

### Caching Strategy
**Issue**: All GET requests cached equally
**Impact**: Stale data for frequently-changing items (shopping list)
**Solution**: Differentiate TTL by endpoint (shopping: 5min, inventory: 30min)
**Effort**: 3-4 hours

## Security Improvements

### Vulnerability Audit
Run Trivy on dependencies:
```bash
trivy fs .
trivy image org.example.familymanager
```

### Dependency Updates
Check for vulnerabilities:
```bash
pip audit
pip check
```

Priorities:
1. **Critical**: Security vulnerabilities
2. **High**: Major version upgrades with breaking changes
3. **Medium**: Minor version upgrades
4. **Low**: Patch updates

### API Rate Limiting
**Issue**: No rate limiting on API endpoints
**Impact**: Potential for DDoS or excessive API usage
**Solution**: Add Flask-Limiter
**Effort**: 3-4 hours

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/inventory')
@limiter.limit("100/hour")
def get_inventory():
    pass
```

### SQL Injection Prevention
**Status**: ✅ Using parameterized queries
**Verification**: Code review completed, no vulnerabilities found

### CORS Configuration
**Issue**: Open CORS allows any domain
**Impact**: Security risk for cross-origin attacks
**Solution**: Whitelist specific origins
**Effort**: 2-3 hours

```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000", "http://192.168.1.100:3000"])
```

## Roadmap

### Phase 5 (Current)
- ✅ Phase 5a: Mobile app scaffolding (COMPLETE)
- 🔄 Phase 5b: Additional mobile screens (IN PROGRESS)
- 🔄 Phase 5c: Polish & testing (READY)

### Phase 6 (Production Ready)
- Add error dialogs to mobile
- Implement settings screen (cache, notifications, API URL)
- Add offline indicator
- Comprehensive testing
- Security audit

### Phase 7 (Enhanced Features)
- Data visualization (charts, graphs)
- Recipe suggestions
- Advanced meal planning
- Expense categorization
- Budget limits and alerts

### Phase 8 (Family Features)
- Shared budgets
- Permission levels (admin/member)
- Activity log
- Family calendar
- Message passing between members

### Phase 9 (Multi-Platform)
- iOS app (Kivy iOS backend)
- Web dashboard (React/Vue frontend)
- Cloud sync (Firebase or custom)
- Data export (CSV, PDF reports)

### Phase 10+ (Advanced)
- Machine learning for budget predictions
- Integration with grocery delivery APIs
- Smart shopping list (recipe ingredient matching)
- NFC/barcode scanning for inventory
- Computer vision for food recognition

## Deprecation Timeline

### Planned Removals
- Python 3.7 support (Phase 6) - EOL in June 2023
- PyQt5 support (Phase 8) - Migrate to PyQt6
- SQLite for very large data (Phase 10) - Use PostgreSQL option

### API Version Deprecation
- API v1 endpoints marked as deprecated in Phase 7
- v1 support removed in Phase 8
- v2 becomes standard going forward

## Maintenance Schedule

### Weekly
- Monitor for errors in logs
- Check for critical security vulnerabilities
- Verify backups working

### Monthly
- Update dependencies
- Code review for technical debt issues
- Performance analysis

### Quarterly
- Full security audit
- Database optimization review
- User feedback analysis for next phase

### Yearly
- Major version release planning
- Architecture review
- Long-term roadmap update

## Metrics to Track

### Code Quality
- Test coverage (target: >80%)
- Code duplication (target: <5%)
- Complexity score (target: <10 avg)

### Performance
- API response time (target: <100ms)
- Mobile app startup (target: <3s)
- Database query time (target: <50ms)

### Reliability
- Uptime (target: >99.9%)
- Error rate (target: <0.1%)
- User-facing bugs reported (trend)

### User Experience
- Mobile app crashes (target: <1 per 1000 launches)
- Data sync failures (target: >99% success)
- User satisfaction (feedback surveys)

## Getting Started with Debt

Choose one of these to start:
1. **Quick Win**: Add error dialogs to mobile (2-3 hours) → Big UX improvement
2. **Important**: Add authentication (6-8 hours) → Security critical
3. **Future-Proof**: Add config file (3-4 hours) → Enables many future features
4. **Stability**: Mobile unit tests (6-8 hours) → Prevents regressions

## Questions?

For technical debt discussions, review:
- Code issues documented in comments (search for `TODO`, `FIXME`, `HACK`)
- Open issues in version control
- Performance profiling reports
- User feedback and bug reports
