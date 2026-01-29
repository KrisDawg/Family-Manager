"""
Automatic Notification Trigger System
Generates notifications based on system events and scheduled items
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class NotificationTriggers:
    """Automatically generate notifications based on system events"""

    def __init__(self, db_path: str = 'family_manager.db', notification_manager=None):
        self.db_path = db_path
        self.notification_manager = notification_manager

    def _get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def check_all_triggers(self):
        """Check all notification triggers and create notifications as needed"""
        logger.info("Running notification trigger check...")
        
        try:
            self.check_upcoming_chores()
            self.check_upcoming_tasks()
            self.check_upcoming_bills()
            self.check_upcoming_recurring_events()
            self.check_low_inventory()
            
            logger.info("Notification trigger check complete")
            return True
        except Exception as e:
            logger.error(f"Failed to run notification triggers: {e}")
            return False

    def check_upcoming_chores(self):
        """Create notifications for chores due within advance warning period"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get chores due in the next 24-48 hours (not already notified)
            now = datetime.now()
            warning_start = (now + timedelta(hours=23)).isoformat()
            warning_end = (now + timedelta(hours=25)).isoformat()

            cursor.execute('''
                SELECT c.*, fm.name as assignee_name 
                FROM chores c
                LEFT JOIN family_members fm ON c.assignee_id = fm.id
                WHERE c.status = 'pending' 
                AND c.due_date BETWEEN ? AND ?
                AND NOT EXISTS (
                    SELECT 1 FROM notifications 
                    WHERE source_entity_type = 'chore' 
                    AND source_entity_id = c.id
                    AND created_at > datetime('now', '-24 hours')
                )
            ''', (warning_start[:10], warning_end[:10]))

            chores = cursor.fetchall()

            for chore in chores:
                # Check user notification preferences
                cursor.execute('''
                    SELECT chore_due_enabled, advance_warning_hours 
                    FROM notification_settings 
                    WHERE user_id = ?
                ''', (chore['assignee_id'],))
                
                settings = cursor.fetchone()
                if not settings or not settings['chore_due_enabled']:
                    continue

                # Create notification
                if self.notification_manager:
                    title = f"Chore Due: {chore['name']}"
                    message = f"Your chore '{chore['name']}' is due on {chore['due_date']} at {chore['due_time']}"
                    
                    self.notification_manager.create_notification(
                        recipient_id=chore['assignee_id'],
                        notification_type='chore_due',
                        title=title,
                        message=message,
                        priority='normal',
                        source_entity_type='chore',
                        source_entity_id=chore['id']
                    )
                    
                    logger.info(f"Created chore due notification for chore {chore['id']}")

            conn.close()
        except Exception as e:
            logger.error(f"Failed to check upcoming chores: {e}")

    def check_upcoming_tasks(self):
        """Create notifications for tasks due within advance warning period"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get tasks due in the next 24-48 hours
            now = datetime.now()
            warning_start = (now + timedelta(hours=23)).isoformat()
            warning_end = (now + timedelta(hours=25)).isoformat()

            cursor.execute('''
                SELECT t.*, p.name as project_name
                FROM tasks t
                LEFT JOIN projects p ON t.project_id = p.id
                WHERE t.status IN ('pending', 'in_progress')
                AND t.due_date BETWEEN ? AND ?
                AND t.assigned_to_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM notifications 
                    WHERE source_entity_type = 'task' 
                    AND source_entity_id = t.id
                    AND created_at > datetime('now', '-24 hours')
                )
            ''', (warning_start[:10], warning_end[:10]))

            tasks = cursor.fetchall()

            for task in tasks:
                # Check user notification preferences
                cursor.execute('''
                    SELECT task_assigned_enabled 
                    FROM notification_settings 
                    WHERE user_id = ?
                ''', (task['assigned_to_id'],))
                
                settings = cursor.fetchone()
                if not settings or not settings['task_assigned_enabled']:
                    continue

                # Create notification
                if self.notification_manager:
                    project_info = f" (Project: {task['project_name']})" if task['project_name'] else ""
                    title = f"Task Due: {task['title']}"
                    message = f"Your task '{task['title']}'{project_info} is due on {task['due_date']}"
                    
                    priority = 'high' if task['priority'] >= 4 else 'normal'
                    
                    self.notification_manager.create_notification(
                        recipient_id=task['assigned_to_id'],
                        notification_type='task_assigned',
                        title=title,
                        message=message,
                        priority=priority,
                        source_entity_type='task',
                        source_entity_id=task['id']
                    )
                    
                    logger.info(f"Created task due notification for task {task['id']}")

            conn.close()
        except Exception as e:
            logger.error(f"Failed to check upcoming tasks: {e}")

    def check_upcoming_bills(self):
        """Create notifications for bills due within advance warning period"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get unpaid bills due in the next 24-48 hours
            now = datetime.now()
            warning_start = (now + timedelta(hours=23)).isoformat()
            warning_end = (now + timedelta(hours=25)).isoformat()

            cursor.execute('''
                SELECT * FROM bills
                WHERE paid = 0
                AND due_date BETWEEN ? AND ?
                AND NOT EXISTS (
                    SELECT 1 FROM notifications 
                    WHERE source_entity_type = 'bill' 
                    AND source_entity_id = id
                    AND created_at > datetime('now', '-24 hours')
                )
            ''', (warning_start[:10], warning_end[:10]))

            bills = cursor.fetchall()

            # Get all family members to notify (or default admin)
            cursor.execute('SELECT id FROM family_members WHERE role = "admin"')
            admin_members = cursor.fetchall()
            recipient_ids = [member['id'] for member in admin_members] if admin_members else [1]

            for bill in bills:
                for recipient_id in recipient_ids:
                    # Check user notification preferences
                    cursor.execute('''
                        SELECT bill_due_enabled 
                        FROM notification_settings 
                        WHERE user_id = ?
                    ''', (recipient_id,))
                    
                    settings = cursor.fetchone()
                    if not settings or not settings['bill_due_enabled']:
                        continue

                    # Create notification
                    if self.notification_manager:
                        title = f"Bill Due: {bill['name']}"
                        message = f"Bill '{bill['name']}' for ${bill['amount']:.2f} is due on {bill['due_date']}"
                        
                        priority = 'high' if bill['amount'] > 500 else 'normal'
                        
                        self.notification_manager.create_notification(
                            recipient_id=recipient_id,
                            notification_type='bill_due',
                            title=title,
                            message=message,
                            priority=priority,
                            source_entity_type='bill',
                            source_entity_id=bill['id']
                        )
                        
                        logger.info(f"Created bill due notification for bill {bill['id']}")

            conn.close()
        except Exception as e:
            logger.error(f"Failed to check upcoming bills: {e}")

    def check_upcoming_recurring_events(self):
        """Create notifications for recurring event instances within advance warning period"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get upcoming recurring event instances in the next 24-48 hours
            now = datetime.now()
            warning_start = (now + timedelta(hours=23)).isoformat()
            warning_end = (now + timedelta(hours=25)).isoformat()

            cursor.execute('''
                SELECT rei.*, re.title, re.created_by
                FROM recurring_event_instances rei
                JOIN recurring_events re ON rei.recurring_event_id = re.id
                WHERE re.is_active = 1
                AND rei.is_completed = 0
                AND rei.event_date BETWEEN ? AND ?
                AND NOT EXISTS (
                    SELECT 1 FROM notifications 
                    WHERE source_entity_type = 'recurring_event_instance' 
                    AND source_entity_id = rei.id
                    AND created_at > datetime('now', '-24 hours')
                )
            ''', (warning_start[:10], warning_end[:10]))

            instances = cursor.fetchall()

            for instance in instances:
                # Check user notification preferences
                cursor.execute('''
                    SELECT recurring_event_enabled 
                    FROM notification_settings 
                    WHERE user_id = ?
                ''', (instance['created_by'],))
                
                settings = cursor.fetchone()
                if not settings or not settings['recurring_event_enabled']:
                    continue

                # Create notification
                if self.notification_manager:
                    title = f"Upcoming Event: {instance['title']}"
                    message = f"Recurring event '{instance['title']}' is scheduled for {instance['event_date']} at {instance['event_time']}"
                    
                    self.notification_manager.create_notification(
                        recipient_id=instance['created_by'],
                        notification_type='recurring_event',
                        title=title,
                        message=message,
                        priority='normal',
                        source_entity_type='recurring_event_instance',
                        source_entity_id=instance['id']
                    )
                    
                    logger.info(f"Created recurring event notification for instance {instance['id']}")

            conn.close()
        except Exception as e:
            logger.error(f"Failed to check upcoming recurring events: {e}")

    def check_low_inventory(self):
        """Create notifications for low inventory items"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get inventory items with low quantity (less than 2 units)
            cursor.execute('''
                SELECT * FROM inventory
                WHERE qty <= 2
                AND qty > 0
                AND NOT EXISTS (
                    SELECT 1 FROM notifications 
                    WHERE source_entity_type = 'inventory' 
                    AND source_entity_id = id
                    AND created_at > datetime('now', '-48 hours')
                )
            ''')

            low_items = cursor.fetchall()

            if low_items:
                # Get all admin members to notify
                cursor.execute('SELECT id FROM family_members WHERE role = "admin"')
                admin_members = cursor.fetchall()
                recipient_ids = [member['id'] for member in admin_members] if admin_members else [1]

                for recipient_id in recipient_ids:
                    # Check user notification preferences
                    cursor.execute('''
                        SELECT inventory_low_enabled 
                        FROM notification_settings 
                        WHERE user_id = ?
                    ''', (recipient_id,))
                    
                    settings = cursor.fetchone()
                    if not settings or not settings['inventory_low_enabled']:
                        continue

                    # Create a summary notification for all low items
                    if self.notification_manager:
                        item_names = [item['name'] for item in low_items[:5]]
                        more_text = f" and {len(low_items) - 5} more" if len(low_items) > 5 else ""
                        
                        title = f"Low Inventory Alert: {len(low_items)} Item(s)"
                        message = f"The following items are running low: {', '.join(item_names)}{more_text}"
                        
                        self.notification_manager.create_notification(
                            recipient_id=recipient_id,
                            notification_type='inventory_low',
                            title=title,
                            message=message,
                            priority='normal',
                            source_entity_type='inventory',
                            source_entity_id=low_items[0]['id']  # Reference first low item
                        )
                        
                        logger.info(f"Created low inventory notification for {len(low_items)} items")

            conn.close()
        except Exception as e:
            logger.error(f"Failed to check low inventory: {e}")

    def check_overdue_items(self):
        """Create alert notifications for overdue chores, tasks, and bills"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            today = datetime.now().date().isoformat()

            # Overdue chores
            cursor.execute('''
                SELECT c.*, fm.name as assignee_name 
                FROM chores c
                LEFT JOIN family_members fm ON c.assignee_id = fm.id
                WHERE c.status = 'pending' 
                AND c.due_date < ?
                AND NOT EXISTS (
                    SELECT 1 FROM notifications 
                    WHERE source_entity_type = 'chore' 
                    AND source_entity_id = c.id
                    AND notification_type = 'alert'
                    AND created_at > datetime('now', '-24 hours')
                )
            ''', (today,))

            overdue_chores = cursor.fetchall()

            for chore in overdue_chores:
                if self.notification_manager:
                    title = f"⚠️ Overdue Chore: {chore['name']}"
                    message = f"Your chore '{chore['name']}' was due on {chore['due_date']}"
                    
                    self.notification_manager.create_notification(
                        recipient_id=chore['assignee_id'],
                        notification_type='alert',
                        title=title,
                        message=message,
                        priority='high',
                        source_entity_type='chore',
                        source_entity_id=chore['id']
                    )

            # Overdue tasks
            cursor.execute('''
                SELECT t.*, p.name as project_name
                FROM tasks t
                LEFT JOIN projects p ON t.project_id = p.id
                WHERE t.status IN ('pending', 'in_progress')
                AND t.due_date < ?
                AND t.assigned_to_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM notifications 
                    WHERE source_entity_type = 'task' 
                    AND source_entity_id = t.id
                    AND notification_type = 'alert'
                    AND created_at > datetime('now', '-24 hours')
                )
            ''', (today,))

            overdue_tasks = cursor.fetchall()

            for task in overdue_tasks:
                if self.notification_manager:
                    title = f"⚠️ Overdue Task: {task['title']}"
                    message = f"Your task '{task['title']}' was due on {task['due_date']}"
                    
                    self.notification_manager.create_notification(
                        recipient_id=task['assigned_to_id'],
                        notification_type='alert',
                        title=title,
                        message=message,
                        priority='high',
                        source_entity_type='task',
                        source_entity_id=task['id']
                    )

            # Overdue bills
            cursor.execute('''
                SELECT * FROM bills
                WHERE paid = 0
                AND due_date < ?
                AND NOT EXISTS (
                    SELECT 1 FROM notifications 
                    WHERE source_entity_type = 'bill' 
                    AND source_entity_id = id
                    AND notification_type = 'alert'
                    AND created_at > datetime('now', '-24 hours')
                )
            ''', (today,))

            overdue_bills = cursor.fetchall()

            # Get admin members
            cursor.execute('SELECT id FROM family_members WHERE role = "admin"')
            admin_members = cursor.fetchall()
            recipient_ids = [member['id'] for member in admin_members] if admin_members else [1]

            for bill in overdue_bills:
                for recipient_id in recipient_ids:
                    if self.notification_manager:
                        title = f"⚠️ Overdue Bill: {bill['name']}"
                        message = f"Bill '{bill['name']}' for ${bill['amount']:.2f} was due on {bill['due_date']}"
                        
                        self.notification_manager.create_notification(
                            recipient_id=recipient_id,
                            notification_type='alert',
                            title=title,
                            message=message,
                            priority='urgent',
                            source_entity_type='bill',
                            source_entity_id=bill['id']
                        )

            conn.close()
            logger.info("Checked for overdue items")
        except Exception as e:
            logger.error(f"Failed to check overdue items: {e}")
