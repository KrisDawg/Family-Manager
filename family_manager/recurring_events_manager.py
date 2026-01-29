"""
Recurring Events Manager - Pattern generation and event instance management
Handles RRULE-compatible pattern creation and expansion for calendar events
"""

import sqlite3
import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class RecurringEventManager:
    """Manages recurring event patterns and instance generation."""

    def __init__(self, db_path: str = 'family_manager.db'):
        """Initialize the RecurringEventManager with database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

    def create_pattern(self, 
                      title: str,
                      pattern_type: str,
                      start_date: str,
                      created_by_id: int,
                      description: str = "",
                      color: str = "#3498db",
                      category: str = "general",
                      end_date: Optional[str] = None,
                      frequency: int = 1,
                      byday: Optional[str] = None,
                      bymonthday: Optional[int] = None,
                      bymonth: Optional[int] = None,
                      count: Optional[int] = None) -> int:
        """Create a new recurring event pattern.
        
        Args:
            title: Event title
            pattern_type: 'daily', 'weekly', 'monthly', 'yearly', or 'custom'
            start_date: ISO format date string (YYYY-MM-DD)
            created_by_id: Family member ID who created the event
            description: Event description
            color: Hex color code (#RRGGBB)
            category: Event category for grouping
            end_date: Optional end date (YYYY-MM-DD). None = no end date
            frequency: Interval frequency (1=every 1, 2=every 2, etc.)
            byday: Comma-separated day abbreviations (MO,TU,WE,TH,FR,SA,SU)
            bymonthday: Day of month (1-31)
            bymonth: Month (1-12)
            count: Total number of occurrences
            
        Returns:
            int: Newly created recurring_event_id
            
        Raises:
            ValueError: If pattern configuration is invalid
        """
        try:
            # Validate pattern type
            valid_types = ['daily', 'weekly', 'monthly', 'yearly', 'custom']
            if pattern_type not in valid_types:
                raise ValueError(f"Invalid pattern_type: {pattern_type}. Must be one of {valid_types}")

            # Validate dates
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                if end_date:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    if end_dt < start_dt:
                        raise ValueError("end_date must be after start_date")
            except ValueError as e:
                raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {e}")

            # Build RRULE string
            rrule = self._build_rrule(pattern_type, frequency, byday, bymonthday, bymonth, count)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert recurring event
            cursor.execute('''
                INSERT INTO recurring_events
                (title, description, color, category, pattern_type, start_date, 
                 end_date, rrule_string, created_by, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (title, description, color, category, pattern_type, start_date,
                  end_date, rrule, created_by_id))

            event_id = cursor.lastrowid

            # Insert pattern configuration
            cursor.execute('''
                INSERT INTO recurring_patterns
                (recurring_event_id, frequency, byday, bymonthday, bymonth, count, interval_description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, frequency, byday, bymonthday, bymonth, count,
                  self._describe_pattern(pattern_type, frequency, byday, bymonthday, bymonth)))

            conn.commit()
            conn.close()

            logger.info(f"Created recurring event '{title}' (ID: {event_id}) with pattern '{pattern_type}'")
            return event_id

        except Exception as e:
            logger.error(f"Failed to create recurring pattern: {e}")
            raise

    def generate_instances(self, 
                          recurring_event_id: int,
                          months_ahead: int = 24) -> List[Dict]:
        """Generate individual event instances from a recurring pattern.
        
        Expands a recurring event pattern into individual calendar instances.
        Instances within the next `months_ahead` months are generated.
        
        Args:
            recurring_event_id: ID of the recurring event to expand
            months_ahead: Number of months to generate instances for (default 24)
            
        Returns:
            List[Dict]: List of generated instances with dates and times
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get recurring event details
            cursor.execute('SELECT * FROM recurring_events WHERE id = ?', (recurring_event_id,))
            event = cursor.fetchone()

            if not event:
                raise ValueError(f"Recurring event {recurring_event_id} not found")

            # Get pattern details
            cursor.execute('SELECT * FROM recurring_patterns WHERE recurring_event_id = ?', 
                          (recurring_event_id,))
            pattern = cursor.fetchone()

            conn.close()

            # Parse dates
            start_date = datetime.strptime(event['start_date'], '%Y-%m-%d').date()
            end_date = None
            if event['end_date']:
                end_date = datetime.strptime(event['end_date'], '%Y-%m-%d').date()

            # Calculate generation window
            today = datetime.now().date()
            window_end = today + timedelta(days=30 * months_ahead)

            # Generate instances based on pattern type
            instances = []
            pattern_type = event['pattern_type']

            if pattern_type == 'daily':
                instances = self._generate_daily_instances(
                    start_date, end_date, window_end, pattern['frequency'])

            elif pattern_type == 'weekly':
                instances = self._generate_weekly_instances(
                    start_date, end_date, window_end, pattern['frequency'], pattern['byday'])

            elif pattern_type == 'monthly':
                instances = self._generate_monthly_instances(
                    start_date, end_date, window_end, pattern['frequency'], pattern['bymonthday'])

            elif pattern_type == 'yearly':
                instances = self._generate_yearly_instances(
                    start_date, end_date, window_end, pattern['frequency'], 
                    pattern['bymonthday'], pattern['bymonth'])

            elif pattern_type == 'custom':
                if event['rrule_string']:
                    instances = self._generate_rrule_instances(
                        event['rrule_string'], start_date, end_date, window_end)

            # Apply count limit if specified
            if pattern['count']:
                instances = instances[:pattern['count']]

            logger.info(f"Generated {len(instances)} instances for recurring event {recurring_event_id}")
            return instances

        except Exception as e:
            logger.error(f"Failed to generate instances for event {recurring_event_id}: {e}")
            raise

    def save_instances(self, recurring_event_id: int, instances: List[Dict]) -> None:
        """Save generated instances to database.
        
        Args:
            recurring_event_id: ID of the recurring event
            instances: List of instance dictionaries with event_date and event_time
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clear existing instances for this event
            cursor.execute('DELETE FROM recurring_event_instances WHERE recurring_event_id = ?',
                          (recurring_event_id,))

            # Insert new instances
            for instance in instances:
                cursor.execute('''
                    INSERT INTO recurring_event_instances
                    (recurring_event_id, event_date, event_time, is_completed)
                    VALUES (?, ?, ?, 0)
                ''', (recurring_event_id, instance['event_date'], instance['event_time']))

            conn.commit()
            conn.close()

            logger.info(f"Saved {len(instances)} instances for recurring event {recurring_event_id}")

        except Exception as e:
            logger.error(f"Failed to save instances: {e}")
            raise

    def modify_single_instance(self, 
                              instance_id: int,
                              title: Optional[str] = None,
                              description: Optional[str] = None,
                              color: Optional[str] = None,
                              notes: Optional[str] = None) -> None:
        """Modify a single instance without affecting the pattern.
        
        Args:
            instance_id: ID of the specific instance to modify
            title: Override title for this instance
            description: Override description for this instance
            color: Override color for this instance
            notes: Completion or modification notes
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update instance with overrides
            update_fields = ['is_overridden = 1']
            params = []

            if title is not None:
                update_fields.append('override_title = ?')
                params.append(title)

            if description is not None:
                update_fields.append('override_description = ?')
                params.append(description)

            if color is not None:
                update_fields.append('override_color = ?')
                params.append(color)

            if notes is not None:
                update_fields.append('override_notes = ?')
                params.append(notes)

            params.append(instance_id)

            query = f"UPDATE recurring_event_instances SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(query, params)

            conn.commit()
            conn.close()

            logger.info(f"Modified instance {instance_id}")

        except Exception as e:
            logger.error(f"Failed to modify instance {instance_id}: {e}")
            raise

    def mark_instance_complete(self, instance_id: int, notes: str = "") -> None:
        """Mark a specific instance as completed.
        
        Args:
            instance_id: ID of the instance to mark complete
            notes: Optional completion notes
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE recurring_event_instances
                SET is_completed = 1, completion_date = CURRENT_DATE, 
                    completion_notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (notes, instance_id))

            conn.commit()
            conn.close()

            logger.info(f"Marked instance {instance_id} as completed")

        except Exception as e:
            logger.error(f"Failed to mark instance complete: {e}")
            raise

    def delete_recurring_event(self, recurring_event_id: int) -> None:
        """Delete a recurring event and all its instances.
        
        Args:
            recurring_event_id: ID of the recurring event to delete
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete instances first (foreign key constraint)
            cursor.execute('DELETE FROM recurring_event_instances WHERE recurring_event_id = ?',
                          (recurring_event_id,))

            # Delete pattern configuration
            cursor.execute('DELETE FROM recurring_patterns WHERE recurring_event_id = ?',
                          (recurring_event_id,))

            # Delete the recurring event
            cursor.execute('DELETE FROM recurring_events WHERE id = ?', (recurring_event_id,))

            conn.commit()
            conn.close()

            logger.info(f"Deleted recurring event {recurring_event_id} and all instances")

        except Exception as e:
            logger.error(f"Failed to delete recurring event: {e}")
            raise

    def validate_rrule(self, rrule_string: str) -> Tuple[bool, str]:
        """Validate an RRULE string.
        
        Args:
            rrule_string: iCalendar RRULE format string
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Basic RRULE validation
            if not rrule_string.startswith('RRULE:'):
                return False, "RRULE must start with 'RRULE:'"

            # Parse components
            parts = rrule_string[6:].split(';')
            freq = None
            valid_freqs = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']

            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    if key == 'FREQ':
                        freq = value
                        if freq not in valid_freqs:
                            return False, f"Invalid FREQ: {freq}. Must be one of {valid_freqs}"

            if not freq:
                return False, "RRULE must contain FREQ parameter"

            return True, "Valid RRULE"

        except Exception as e:
            return False, f"RRULE validation error: {str(e)}"

    # ===== PRIVATE HELPER METHODS =====

    def _build_rrule(self, pattern_type: str, frequency: int, byday: Optional[str],
                    bymonthday: Optional[int], bymonth: Optional[int],
                    count: Optional[int]) -> str:
        """Build an iCalendar RRULE string from pattern parameters."""
        
        freq_map = {
            'daily': 'DAILY',
            'weekly': 'WEEKLY',
            'monthly': 'MONTHLY',
            'yearly': 'YEARLY'
        }

        rrule = f"RRULE:FREQ={freq_map.get(pattern_type, 'DAILY')}"

        if frequency > 1:
            rrule += f";INTERVAL={frequency}"

        if byday:
            rrule += f";BYDAY={byday}"

        if bymonthday:
            rrule += f";BYMONTHDAY={bymonthday}"

        if bymonth:
            rrule += f";BYMONTH={bymonth}"

        if count:
            rrule += f";COUNT={count}"

        return rrule

    def _describe_pattern(self, pattern_type: str, frequency: int, byday: Optional[str],
                         bymonthday: Optional[int], bymonth: Optional[int]) -> str:
        """Create human-readable pattern description."""
        
        freq_text = {
            'daily': 'Daily',
            'weekly': 'Weekly',
            'monthly': 'Monthly',
            'yearly': 'Yearly'
        }

        desc = freq_text.get(pattern_type, 'Custom')

        if frequency > 1:
            desc += f" every {frequency} times"

        if byday:
            day_map = {
                'MO': 'Monday', 'TU': 'Tuesday', 'WE': 'Wednesday', 'TH': 'Thursday',
                'FR': 'Friday', 'SA': 'Saturday', 'SU': 'Sunday'
            }
            days = [day_map.get(d.strip(), d) for d in byday.split(',')]
            desc += f" on {', '.join(days)}"

        if bymonthday:
            desc += f" on day {bymonthday}"

        if bymonth:
            month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April',
                        5: 'May', 6: 'June', 7: 'July', 8: 'August',
                        9: 'September', 10: 'October', 11: 'November', 12: 'December'}
            desc += f" in {month_map.get(bymonth, str(bymonth))}"

        return desc

    def _generate_daily_instances(self, start_date, end_date, window_end, frequency: int) -> List[Dict]:
        """Generate daily recurring instances."""
        instances = []
        current = start_date
        count = 0

        while current <= window_end and (end_date is None or current <= end_date):
            if current >= start_date:
                instances.append({
                    'event_date': current.isoformat(),
                    'event_time': '09:00'
                })
            current += timedelta(days=frequency)

        return instances

    def _generate_weekly_instances(self, start_date, end_date, window_end, frequency: int,
                                  byday: Optional[str]) -> List[Dict]:
        """Generate weekly recurring instances."""
        instances = []

        # Parse byday string (MO,TU,WE,TH,FR,SA,SU)
        day_map = {'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6}
        target_days = set()

        if byday:
            for day in byday.split(','):
                day = day.strip()
                if day in day_map:
                    target_days.add(day_map[day])
        else:
            # Default to start date's day of week
            target_days.add(start_date.weekday())

        current = start_date
        while current <= window_end and (end_date is None or current <= end_date):
            if current.weekday() in target_days:
                instances.append({
                    'event_date': current.isoformat(),
                    'event_time': '09:00'
                })
            current += timedelta(days=1)

        return instances

    def _generate_monthly_instances(self, start_date, end_date, window_end, frequency: int,
                                   bymonthday: Optional[int]) -> List[Dict]:
        """Generate monthly recurring instances."""
        instances = []
        current = start_date
        month_count = 0

        target_day = bymonthday if bymonthday else start_date.day

        while month_count < 240:  # Arbitrary limit
            if current > window_end or (end_date and current > end_date):
                break

            # Calculate next month
            try:
                instance_date = current.replace(day=min(target_day, self._days_in_month(current)))
                if instance_date >= start_date:
                    instances.append({
                        'event_date': instance_date.isoformat(),
                        'event_time': '09:00'
                    })
            except ValueError:
                pass

            # Add months
            month_count += frequency
            year = current.year + (current.month + frequency - 1) // 12
            month = ((current.month + frequency - 1) % 12) + 1
            current = current.replace(year=year, month=month)

        return instances

    def _generate_yearly_instances(self, start_date, end_date, window_end, frequency: int,
                                 bymonthday: Optional[int], bymonth: Optional[int]) -> List[Dict]:
        """Generate yearly recurring instances."""
        instances = []
        year = start_date.year

        target_day = bymonthday if bymonthday else start_date.day
        target_month = bymonth if bymonth else start_date.month

        while year <= window_end.year:
            try:
                instance_date = datetime(year, target_month, target_day).date()
                if instance_date >= start_date and instance_date <= window_end:
                    if end_date is None or instance_date <= end_date:
                        instances.append({
                            'event_date': instance_date.isoformat(),
                            'event_time': '09:00'
                        })
            except ValueError:
                pass

            year += frequency

        return instances

    def _generate_rrule_instances(self, rrule_string: str, start_date, end_date,
                                 window_end) -> List[Dict]:
        """Generate instances from a custom RRULE string (simplified implementation)."""
        # This is a simplified version - a full implementation would use the rrule library
        # For now, treat it as a custom pattern and default to monthly
        return self._generate_monthly_instances(start_date, end_date, window_end, 1, None)

    def _days_in_month(self, date) -> int:
        """Get number of days in a month."""
        if date.month == 12:
            next_month = date.replace(year=date.year + 1, month=1, day=1)
        else:
            next_month = date.replace(month=date.month + 1, day=1)
        return (next_month - timedelta(days=1)).day
