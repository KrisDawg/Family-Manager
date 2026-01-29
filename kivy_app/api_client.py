"""
Family Manager Mobile App - API Client Service
Handles all communication with desktop Flask API
Supports offline caching and background sync
"""

import requests
import json
import sqlite3
import logging
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Thread, Lock
import time

logger = logging.getLogger(__name__)

# Request timeout configuration
REQUEST_TIMEOUT = 8  # Increased to 8 seconds for slower connections
CONNECT_TIMEOUT = 5   # Connection attempt timeout
RETRY_DELAY = 2       # Delay between retries (seconds)


class APIClient:
    """
    Handles all API communication with desktop server
    Features: caching, offline support, retry logic, thread-safe operations
    """

    def __init__(self, base_url: str = "http://localhost:5000", cache_db: str = "mobile_cache.db"):
        self.base_url = base_url.rstrip('/')
        self.cache_db = cache_db
        self.session = requests.Session()
        self.lock = Lock()
        self.is_online = False
        self.last_sync = None

        # Initialize cache database
        self._init_cache_db()

        # Check connectivity in background
        Thread(target=self._check_connectivity, daemon=True).start()

    def _init_cache_db(self):
        """Initialize SQLite cache database"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()

            # Cache table for API responses
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_cache (
                    key TEXT PRIMARY KEY,
                    endpoint TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT
                )
            ''')

            # Pending requests (for offline sync)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TEXT
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Cache database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")

    def _check_connectivity(self):
        """Periodically check server connectivity"""
        while True:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/inventory",
                    timeout=2
                )
                self.is_online = response.status_code < 500
            except:
                self.is_online = False

            time.sleep(30)  # Check every 30 seconds

    def test_server_connection(self) -> Any:
        """Test if API server is reachable and return status message
        
        Returns:
            Tuple[bool, str]: (is_reachable, status_message)
        """
        try:
            # Extract host and port from base_url
            url_parts = self.base_url.replace('http://', '').replace('https://', '').split(':')
            host = url_parts[0]
            port = int(url_parts[1]) if len(url_parts) > 1 else (443 if self.base_url.startswith('https') else 80)
            
            # Try to connect
            socket.create_connection((host, port), timeout=CONNECT_TIMEOUT)
            return True, f"✅ Server reachable at {self.base_url}"
        except socket.timeout:
            return False, f"⏱️ Connection timeout - Server at {self.base_url} is slow or unreachable"
        except socket.error as e:
            return False, f"❌ Cannot connect to {self.base_url}: {str(e)}"
        except Exception as e:
            return False, f"❓ Connection check failed: {str(e)}"

    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status"""
        is_reachable, message = self.test_server_connection()
        
        return {
            'is_online': self.is_online,
            'is_reachable': is_reachable,
            'server_url': self.base_url,
            'status_message': message,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }

    def _get_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from endpoint and parameters"""
        params_str = json.dumps(params, sort_keys=True) if params else ""
        return f"{endpoint}:{params_str}"

    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached response if valid"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()

            cursor.execute(
                'SELECT response FROM api_cache WHERE key = ? AND (expires_at IS NULL OR expires_at > datetime("now"))',
                (key,)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    def _cache_response(self, key: str, endpoint: str, response: Dict, ttl_minutes: int = 60):
        """Cache API response"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()

            expires_at = (datetime.now() + timedelta(minutes=ttl_minutes)).isoformat() if ttl_minutes else None

            cursor.execute(
                'INSERT OR REPLACE INTO api_cache (key, endpoint, response, expires_at) VALUES (?, ?, ?, ?)',
                (key, endpoint, json.dumps(response), expires_at)
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Cache write error: {e}")

    def get_with_cache(self, endpoint: str, params: Optional[Dict] = None, cache_ttl: int = 60) -> Optional[Dict]:
        """GET request with automatic caching"""
        cache_key = self._get_cache_key(endpoint, params)

        # Try cache first
        cached = self._get_cached(cache_key)
        if cached:
            logger.info(f"Cache HIT: {endpoint}")
            return cached

        # Fetch from server
        if self.is_online:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/{endpoint}",
                    params=params,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    self._cache_response(cache_key, endpoint, data, cache_ttl)
                    logger.info(f"Cache UPDATE: {endpoint}")
                    return data
            except Exception as e:
                logger.error(f"GET {endpoint} error: {e}")

        # Return cached if available (even if expired)
        return self._get_cached(cache_key)

    def request(self, method: str, endpoint: str, data: Optional[Dict] = None,
               params: Optional[Dict] = None, require_sync: bool = False) -> Optional[Dict]:
        """
        Make HTTP request with offline support
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without /api/)
            data: Request body data
            params: Query parameters
            require_sync: Queue for sync if offline
        
        Returns:
            Response JSON or None
        """
        url = f"{self.base_url}/api/{endpoint}"

        if not self.is_online:
            if require_sync and method != 'GET':
                self._queue_request(method, endpoint, data)
                logger.info(f"Queued {method} {endpoint} for offline sync")
            
            # Return cached response if available
            return self._get_cached(self._get_cache_key(endpoint, params))

        try:
            kwargs = {'timeout': REQUEST_TIMEOUT}
            if params:
                kwargs['params'] = params
            if data:
                kwargs['json'] = data

            response = self.session.request(method, url, **kwargs)

            if response.status_code == 200 and method == 'GET':
                # Cache successful GET responses
                self._cache_response(
                    self._get_cache_key(endpoint, params),
                    endpoint,
                    response.json() if response.text else {}
                )

            if 200 <= response.status_code < 300:
                return response.json() if response.text else {'status': 'ok'}
            else:
                logger.error(f"{method} {endpoint} returned {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"{method} {endpoint} TIMEOUT - Server not responding within {REQUEST_TIMEOUT}s")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"{method} {endpoint} CONNECTION ERROR - Cannot reach {self.base_url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"{method} {endpoint} REQUEST ERROR: {e}")
            return None
        except Exception as e:
            logger.error(f"{method} {endpoint} UNEXPECTED ERROR: {e}")
            return None

    def _queue_request(self, method: str, endpoint: str, data: Optional[Dict]):
        """Queue request for offline sync"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()

            cursor.execute(
                'INSERT INTO pending_requests (method, endpoint, data) VALUES (?, ?, ?)',
                (method, endpoint, json.dumps(data) if data else None)
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to queue request: {e}")

    def sync_pending_requests(self) -> int:
        """Sync queued requests when back online"""
        if not self.is_online:
            return 0

        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, method, endpoint, data FROM pending_requests
                WHERE retry_count < 3
                ORDER BY created_at ASC
                LIMIT 10
            ''')

            pending = cursor.fetchall()
            synced = 0

            for req_id, method, endpoint, data_str in pending:
                data = json.loads(data_str) if data_str else None

                result = self.request(method, endpoint, data)

                if result:
                    # Remove from queue
                    cursor.execute('DELETE FROM pending_requests WHERE id = ?', (req_id,))
                    synced += 1
                else:
                    # Increment retry count
                    cursor.execute(
                        'UPDATE pending_requests SET retry_count = retry_count + 1, last_retry = datetime("now") WHERE id = ?',
                        (req_id,)
                    )

            conn.commit()
            conn.close()

            if synced > 0:
                logger.info(f"Synced {synced} pending requests")
                self.last_sync = datetime.now()

            return synced

        except Exception as e:
            logger.error(f"Sync error: {e}")
            return 0

    # ==========================================
    # INVENTORY ENDPOINTS
    # ==========================================

    def get_inventory(self, category: Optional[str] = None) -> List[Dict]:
        """Get all inventory items"""
        params = {'category': category} if category else None
        result = self.get_with_cache('inventory', params=params, cache_ttl=30)
        return result if isinstance(result, list) else []

    def add_inventory(self, name: str, category: str, qty: float, unit: str,
                     exp_date: Optional[str] = None, location: Optional[str] = None) -> Optional[Dict]:
        """Add new inventory item"""
        data = {
            'name': name,
            'category': category,
            'qty': qty,
            'unit': unit,
            'exp_date': exp_date,
            'location': location
        }
        return self.request('POST', 'inventory', data, require_sync=True)

    def update_inventory(self, item_id: int, **kwargs) -> Optional[Dict]:
        """Update inventory item"""
        return self.request('PUT', f'inventory/{item_id}', kwargs, require_sync=True)

    def delete_inventory(self, item_id: int) -> bool:
        """Delete inventory item"""
        return self.request('DELETE', f'inventory/{item_id}', require_sync=True) is not None

    # ==========================================
    # SHOPPING LIST ENDPOINTS
    # ==========================================

    def get_shopping_list(self) -> List[Dict]:
        """Get shopping list"""
        result = self.get_with_cache('shopping-list', cache_ttl=30)
        return result if isinstance(result, list) else []

    def add_shopping_item(self, item: str, qty: Optional[float] = None,
                         category: Optional[str] = None) -> Optional[Dict]:
        """Add shopping item"""
        data = {'item': item, 'qty': qty, 'category': category}
        return self.request('POST', 'shopping-list', data, require_sync=True)

    def update_shopping_item(self, item_id: int, **kwargs) -> Optional[Dict]:
        """Update shopping item"""
        return self.request('PUT', f'shopping-list/{item_id}', kwargs, require_sync=True)

    def delete_shopping_item(self, item_id: int) -> bool:
        """Delete shopping item"""
        return self.request('DELETE', f'shopping-list/{item_id}', require_sync=True) is not None

    # ==========================================
    # MEALS ENDPOINTS
    # ==========================================

    def get_meals(self, date: Optional[str] = None) -> List[Dict]:
        """Get meals for a date"""
        params = {'date': date} if date else None
        result = self.get_with_cache('meals', params=params, cache_ttl=30)
        return result if isinstance(result, list) else []

    def add_meal(self, date: str, meal_type: str, name: str,
                ingredients: Optional[List[str]] = None) -> Optional[Dict]:
        """Add meal plan entry"""
        data = {
            'date': date,
            'meal_type': meal_type,
            'name': name,
            'ingredients': ingredients or []
        }
        return self.request('POST', 'meals', data, require_sync=True)

    def delete_meal(self, meal_id: int) -> bool:
        """Delete meal"""
        return self.request('DELETE', f'meals/{meal_id}', require_sync=True) is not None

    # ==========================================
    # BILLS ENDPOINTS
    # ==========================================

    def get_bills(self, status: Optional[str] = None) -> List[Dict]:
        """Get bills"""
        params = {'status': status} if status else None
        result = self.get_with_cache('bills', params=params, cache_ttl=30)
        return result if isinstance(result, list) else []

    def add_bill(self, name: str, amount: float, due_date: str,
                category: Optional[str] = None, recurring: bool = False) -> Optional[Dict]:
        """Add bill"""
        data = {
            'name': name,
            'amount': amount,
            'due_date': due_date,
            'category': category,
            'recurring': recurring
        }
        return self.request('POST', 'bills', data, require_sync=True)

    def mark_bill_paid(self, bill_id: int) -> bool:
        """Mark bill as paid"""
        return self.request('PUT', f'bills/{bill_id}', {'paid': 1}, require_sync=True) is not None

    def delete_bill(self, bill_id: int) -> bool:
        """Delete bill"""
        return self.request('DELETE', f'bills/{bill_id}', require_sync=True) is not None

    # ==========================================
    # CHORES ENDPOINTS
    # ==========================================

    def get_chores(self, assignee_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict]:
        """Get chores"""
        params = {}
        if assignee_id:
            params['assignee_id'] = assignee_id
        if status:
            params['status'] = status
        result = self.get_with_cache('chores', params=params if params else None, cache_ttl=30)
        return result if isinstance(result, list) else []

    def add_chore(self, name: str, assignee_id: int, due_date: str,
                 due_time: str = "09:00", priority: int = 1) -> Optional[Dict]:
        """Add chore"""
        data = {
            'name': name,
            'assignee_id': assignee_id,
            'due_date': due_date,
            'due_time': due_time,
            'priority': priority
        }
        return self.request('POST', 'chores', data, require_sync=True)

    def mark_chore_complete(self, chore_id: int) -> bool:
        """Mark chore as complete"""
        return self.request('PUT', f'chores/{chore_id}', {'status': 'completed'}, require_sync=True) is not None

    def delete_chore(self, chore_id: int) -> bool:
        """Delete chore"""
        return self.request('DELETE', f'chores/{chore_id}', require_sync=True) is not None

    # ==========================================
    # TASKS ENDPOINTS
    # ==========================================

    def get_tasks(self, status: Optional[str] = None, project_id: Optional[int] = None) -> List[Dict]:
        """Get tasks"""
        params = {}
        if status:
            params['status'] = status
        if project_id:
            params['project_id'] = project_id
        result = self.get_with_cache('tasks', params=params if params else None, cache_ttl=30)
        return result if isinstance(result, list) else []

    def add_task(self, project_id: int, title: str, assigned_to_id: int,
                due_date: str, priority: int = 2) -> Optional[Dict]:
        """Add task"""
        data = {
            'project_id': project_id,
            'title': title,
            'assigned_to_id': assigned_to_id,
            'due_date': due_date,
            'priority': priority
        }
        return self.request('POST', 'tasks', data, require_sync=True)

    def mark_task_complete(self, task_id: int) -> bool:
        """Mark task as complete"""
        return self.request('PUT', f'tasks/{task_id}', {'status': 'completed'}, require_sync=True) is not None

    # ==========================================
    # NOTIFICATIONS ENDPOINTS
    # ==========================================

    def get_notifications(self, unread_only: bool = False) -> List[Dict]:
        """Get notifications"""
        params = {'unread_only': 'true' if unread_only else 'false'}
        result = self.get_with_cache('notifications', params=params, cache_ttl=10)
        return result if isinstance(result, list) else []

    def mark_notification_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        return self.request('PUT', f'notifications/{notification_id}',
                          {'is_read': 1}, require_sync=True) is not None

    def get_unread_count(self) -> int:
        """Get unread notification count"""
        result = self.get_with_cache('notifications/unread-count', cache_ttl=5)
        return result.get('unread_count', 0) if result else 0

    def clear_notification(self, notification_id: int) -> bool:
        """Delete notification"""
        return self.request('DELETE', f'notifications/{notification_id}', require_sync=True) is not None

    # ==========================================
    # FAMILY MEMBERS ENDPOINTS
    # ==========================================

    def get_family_members(self) -> List[Dict]:
        """Get all family members"""
        result = self.get_with_cache('family-members', cache_ttl=60)
        return result if isinstance(result, list) else []

    def add_family_member(self, name: str, email: Optional[str] = None,
                         role: str = "member") -> Optional[Dict]:
        """Add family member"""
        data = {'name': name, 'email': email, 'role': role}
        return self.request('POST', 'family-members', data, require_sync=True)
