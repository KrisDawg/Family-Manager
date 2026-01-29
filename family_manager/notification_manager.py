"""
Notification Manager for Family Household Manager
Handles notification creation, retrieval, preferences, and reminder scheduling
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification type constants"""
    REMINDER = "reminder"
    ALERT = "alert"
    TASK_ASSIGNED = "task_assigned"
    CHORE_DUE = "chore_due"
    EVENT_UPCOMING = "event_upcoming"
    BILL_DUE = "bill_due"
    INVENTORY_LOW = "inventory_low"
    RECURRING_EVENT = "recurring_event"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationManager:
    """Manage notifications, settings, and reminder scheduling"""

    def __init__(self, db_path: str = 'family_manager.db'):
        self.db_path = db_path
        self._initialize_user_settings()

    def _get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_user_settings(self):
        """Initialize default notification settings for all users"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get all family members
            cursor.execute("SELECT id FROM family_members")
            members = cursor.fetchall()

            for member in members:
                user_id = member['id']

                # Check if settings exist
                cursor.execute("SELECT id FROM notification_settings WHERE user_id = ?", (user_id,))
                if not cursor.fetchone():
                    # Create default settings
                    cursor.execute('''
                        INSERT INTO notification_settings
                        (user_id, reminder_enabled, alert_enabled, task_assigned_enabled,
                         chore_due_enabled, event_upcoming_enabled, bill_due_enabled,
                         inventory_low_enabled, recurring_event_enabled, advance_warning_hours,
                         notification_method)
                        VALUES (?, 1, 1, 1, 1, 1, 1, 1, 1, 24, 'in-app')
                    ''', (user_id,))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize user settings: {e}")

    def create_notification(self, recipient_id: int, notification_type: str, title: str,
                          message: str, priority: str = "normal", source_entity_type: Optional[str] = None,
                          source_entity_id: Optional[int] = None, action_url: Optional[str] = None,
                          scheduled_for: Optional[str] = None, expires_in_hours: int = 72) -> Optional[int]:
        """
        Create a new notification

        Args:
            recipient_id: ID of family member receiving notification
            notification_type: Type of notification (from NotificationType)
            title: Notification title
            message: Notification message
            priority: Priority level (low, normal, high, urgent)
            source_entity_type: Type of entity triggering notification
            source_entity_id: ID of the entity
            action_url: URL to navigate to when clicked
            scheduled_for: ISO datetime to schedule notification for (default: now)
            expires_in_hours: How long before notification expires (default: 72 hours)

        Returns:
            int: ID of created notification, or None if failed
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check user preferences
            if not self._should_notify_user(cursor, recipient_id, notification_type):
                logger.debug(f"Notification suppressed for user {recipient_id} (disabled in preferences)")
                conn.close()
                return None

            # Set default scheduled time to now if not specified
            if scheduled_for is None:
                scheduled_for = datetime.now().isoformat()

            # Calculate expiration time
            expires_at = (datetime.fromisoformat(scheduled_for) + timedelta(hours=expires_in_hours)).isoformat()

            cursor.execute('''
                INSERT INTO notifications
                (notification_type, recipient_id, title, message, priority, source_entity_type,
                 source_entity_id, action_url, scheduled_for, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (notification_type, recipient_id, title, message, priority, source_entity_type,
                  source_entity_id, action_url, scheduled_for, expires_at))

            notification_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Created notification {notification_id} for user {recipient_id}: {title}")
            return notification_id

        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return None

    def get_notifications(self, recipient_id: int, unread_only: bool = False,
                         notification_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Retrieve notifications for a user

        Args:
            recipient_id: ID of family member
            unread_only: Only retrieve unread notifications
            notification_type: Filter by notification type
            limit: Maximum number of notifications to retrieve

        Returns:
            list: List of notification dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "SELECT * FROM notifications WHERE recipient_id = ?"
            params = [recipient_id]

            if unread_only:
                query += " AND is_read = 0"

            if notification_type:
                query += " AND notification_type = ?"
                params.append(notification_type)

            # Only show non-expired notifications
            query += " AND (expires_at IS NULL OR expires_at > datetime('now'))"

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            notifications = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return notifications

        except Exception as e:
            logger.error(f"Failed to retrieve notifications: {e}")
            return []

    def get_unread_count(self, recipient_id: int) -> int:
        """Get count of unread notifications for a user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) FROM notifications
                WHERE recipient_id = ? AND is_read = 0
                AND (expires_at IS NULL OR expires_at > datetime('now'))
            ''', (recipient_id,))

            count = cursor.fetchone()[0]
            conn.close()
            return count

        except Exception as e:
            logger.error(f"Failed to get unread count: {e}")
            return 0

    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE notifications
                SET is_read = 1, read_at = datetime('now')
                WHERE id = ?
            ''', (notification_id,))

            conn.commit()
            conn.close()

            logger.info(f"Marked notification {notification_id} as read")
            return True

        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False

    def mark_all_as_read(self, recipient_id: int) -> bool:
        """Mark all unread notifications for a user as read"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE notifications
                SET is_read = 1, read_at = datetime('now')
                WHERE recipient_id = ? AND is_read = 0
            ''', (recipient_id,))

            conn.commit()
            conn.close()

            logger.info(f"Marked all notifications as read for user {recipient_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to mark all as read: {e}")
            return False

    def delete_notification(self, notification_id: int) -> bool:
        """Delete a notification"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))

            conn.commit()
            conn.close()

            logger.info(f"Deleted notification {notification_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete notification: {e}")
            return False

    def get_settings(self, user_id: int) -> Optional[Dict]:
        """Get notification settings for a user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM notification_settings WHERE user_id = ?", (user_id,))
            settings = cursor.fetchone()
            conn.close()

            return dict(settings) if settings else None

        except Exception as e:
            logger.error(f"Failed to retrieve settings: {e}")
            return None

    def update_settings(self, user_id: int, **kwargs) -> bool:
        """
        Update notification settings for a user

        Args:
            user_id: ID of family member
            **kwargs: Settings to update (reminder_enabled, alert_enabled, etc.)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Build dynamic UPDATE query
            valid_fields = {
                'reminder_enabled', 'alert_enabled', 'task_assigned_enabled',
                'chore_due_enabled', 'event_upcoming_enabled', 'bill_due_enabled',
                'inventory_low_enabled', 'recurring_event_enabled', 'advance_warning_hours',
                'notification_method', 'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'
            }

            updates = []
            params = []
            for key, value in kwargs.items():
                if key in valid_fields:
                    updates.append(f"{key} = ?")
                    params.append(value)

            if not updates:
                conn.close()
                return True  # No valid fields to update

            updates.append("updated_at = datetime('now')")
            params.append(user_id)

            query = f"UPDATE notification_settings SET {', '.join(updates)} WHERE user_id = ?"
            cursor.execute(query, params)

            conn.commit()
            conn.close()

            logger.info(f"Updated notification settings for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            return False

    def create_reminder(self, recipient_id: int, event_type: str, event_id: int,
                       event_title: str, event_date: str, event_time: Optional[str] = None,
                       advance_hours: Optional[int] = None) -> Optional[int]:
        """
        Create a scheduled reminder for an upcoming event

        Args:
            recipient_id: ID of family member to remind
            event_type: Type of event (chore, task, recurring_event, bill)
            event_id: ID of the event
            event_title: Title of the event
            event_date: ISO date of the event
            event_time: ISO time of the event
            advance_hours: Hours before event to send reminder (uses user default if not specified)

        Returns:
            int: ID of created reminder, or None if failed
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get user's advance warning preference if not specified
            if advance_hours is None:
                settings = self.get_settings(recipient_id)
                advance_hours = settings['advance_warning_hours'] if settings else 24

            # Calculate reminder time
            event_datetime = f"{event_date}T{event_time if event_time else '09:00'}"
            event_dt = datetime.fromisoformat(event_datetime)
            reminder_dt = event_dt - timedelta(hours=advance_hours)
            reminder_time = reminder_dt.isoformat()

            cursor.execute('''
                INSERT INTO notification_reminders
                (recipient_id, event_type, event_id, event_title, event_date, event_time, reminder_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (recipient_id, event_type, event_id, event_title, event_date, event_time, reminder_time))

            reminder_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Created reminder {reminder_id} for user {recipient_id}: {event_title}")
            return reminder_id

        except Exception as e:
            logger.error(f"Failed to create reminder: {e}")
            return None

    def get_due_reminders(self) -> List[Dict]:
        """Get all reminders that should be sent now"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            current_time = datetime.now().isoformat()

            cursor.execute('''
                SELECT * FROM notification_reminders
                WHERE is_sent = 0 AND is_dismissed = 0
                AND reminder_time <= ?
                ORDER BY reminder_time ASC
            ''', (current_time,))

            reminders = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return reminders

        except Exception as e:
            logger.error(f"Failed to retrieve due reminders: {e}")
            return []

    def send_reminder(self, reminder_id: int) -> bool:
        """
        Send a reminder and mark it as sent

        Args:
            reminder_id: ID of the reminder

        Returns:
            bool: True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get reminder details
            cursor.execute("SELECT * FROM notification_reminders WHERE id = ?", (reminder_id,))
            reminder = cursor.fetchone()

            if not reminder:
                conn.close()
                return False

            # Create notification from reminder
            reminder_dict = dict(reminder)
            notification_title = f"Reminder: {reminder_dict['event_title']}"
            notification_message = f"You have a {reminder_dict['event_type'].replace('_', ' ')} coming up"

            notification_id = self.create_notification(
                recipient_id=reminder_dict['recipient_id'],
                notification_type=NotificationType.REMINDER.value,
                title=notification_title,
                message=notification_message,
                priority="high",
                source_entity_type=reminder_dict['event_type'],
                source_entity_id=reminder_dict['event_id']
            )

            # Mark reminder as sent
            cursor.execute('''
                UPDATE notification_reminders
                SET is_sent = 1, sent_at = datetime('now')
                WHERE id = ?
            ''', (reminder_id,))

            conn.commit()
            conn.close()

            logger.info(f"Sent reminder {reminder_id} (notification {notification_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to send reminder: {e}")
            return False

    def dismiss_reminder(self, reminder_id: int) -> bool:
        """Mark a reminder as dismissed"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE notification_reminders
                SET is_dismissed = 1, dismissed_at = datetime('now')
                WHERE id = ?
            ''', (reminder_id,))

            conn.commit()
            conn.close()

            logger.info(f"Dismissed reminder {reminder_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to dismiss reminder: {e}")
            return False

    def cleanup_expired_notifications(self) -> int:
        """
        Delete expired notifications

        Returns:
            int: Number of notifications deleted
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM notifications
                WHERE expires_at IS NOT NULL AND expires_at < datetime('now')
            ''')

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired notifications")

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired notifications: {e}")
            return 0

    def _should_notify_user(self, cursor: sqlite3.Cursor, user_id: int, notification_type: str) -> bool:
        """Check if user should receive this type of notification"""
        try:
            # Map notification type to setting field
            type_to_setting = {
                NotificationType.REMINDER.value: 'reminder_enabled',
                NotificationType.ALERT.value: 'alert_enabled',
                NotificationType.TASK_ASSIGNED.value: 'task_assigned_enabled',
                NotificationType.CHORE_DUE.value: 'chore_due_enabled',
                NotificationType.EVENT_UPCOMING.value: 'event_upcoming_enabled',
                NotificationType.BILL_DUE.value: 'bill_due_enabled',
                NotificationType.INVENTORY_LOW.value: 'inventory_low_enabled',
                NotificationType.RECURRING_EVENT.value: 'recurring_event_enabled'
            }

            setting_field = type_to_setting.get(notification_type, 'alert_enabled')

            cursor.execute(f"SELECT {setting_field} FROM notification_settings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if result is None:
                return True  # Default to enabling if no settings found

            return bool(result[0])

        except Exception as e:
            logger.error(f"Failed to check notification preference: {e}")
            return True  # Default to enabling on error
