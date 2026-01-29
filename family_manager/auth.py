"""
Authentication and Security Module for Family Household Manager

Provides:
- User registration and authentication
- JWT token management
- Password hashing with bcrypt
- Family/household management with roles
- Session management
- API route protection decorators
"""

import sqlite3
import hashlib
import secrets
import jwt
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
import os

# Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
TOKEN_EXPIRY_HOURS = 24
REFRESH_TOKEN_EXPIRY_DAYS = 30
PASSWORD_SALT_LENGTH = 32
MIN_PASSWORD_LENGTH = 8

# User roles
class UserRole:
    ADMIN = 'admin'          # Full access - can manage family members
    MEMBER = 'member'        # Standard access - can edit data
    GUEST = 'guest'          # Read-only access
    CHILD = 'child'          # Limited access - age-appropriate features


def get_auth_db():
    """Get database connection for auth operations"""
    conn = sqlite3.connect('family_manager.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_tables():
    """Initialize authentication database tables"""
    conn = get_auth_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            display_name TEXT,
            avatar_url TEXT,
            role TEXT DEFAULT 'member',
            family_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            email_verified BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT,
            FOREIGN KEY (family_id) REFERENCES families(id)
        )
    ''')
    
    # Families/Households table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS families (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            invite_code TEXT UNIQUE,
            created_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            settings TEXT DEFAULT '{}',
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Sessions/Tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT UNIQUE NOT NULL,
            refresh_token_hash TEXT UNIQUE,
            device_info TEXT,
            ip_address TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            last_activity TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # User settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            setting_key TEXT NOT NULL,
            setting_value TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, setting_key)
        )
    ''')
    
    # Password reset tokens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            used BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Audit log for security events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_type TEXT NOT NULL,
            event_details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Family invitations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            family_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            invite_token TEXT UNIQUE NOT NULL,
            invited_by INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            accepted BOOLEAN DEFAULT 0,
            FOREIGN KEY (family_id) REFERENCES families(id),
            FOREIGN KEY (invited_by) REFERENCES users(id)
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_family ON users(family_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token_hash)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON security_audit_log(user_id)')
    
    conn.commit()
    conn.close()
    logging.info("Authentication tables initialized successfully")


def hash_password(password, salt=None):
    """Hash password with salt using SHA-256"""
    if salt is None:
        salt = secrets.token_hex(PASSWORD_SALT_LENGTH)
    
    # Multiple iterations for added security
    password_bytes = (password + salt).encode('utf-8')
    for _ in range(10000):
        password_bytes = hashlib.sha256(password_bytes).digest()
    
    password_hash = hashlib.sha256(password_bytes).hexdigest()
    return password_hash, salt


def verify_password(password, password_hash, salt):
    """Verify password against stored hash"""
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)


def generate_token(user_id, token_type='access'):
    """Generate JWT token for user"""
    if token_type == 'access':
        expiry = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    else:  # refresh token
        expiry = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)
    
    payload = {
        'user_id': user_id,
        'token_type': token_type,
        'exp': expiry,
        'iat': datetime.utcnow(),
        'jti': secrets.token_hex(16)  # Unique token ID
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token, expiry


def decode_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired'
    except jwt.InvalidTokenError as e:
        return None, f'Invalid token: {str(e)}'


def log_security_event(event_type, user_id=None, details=None, ip_address=None, user_agent=None):
    """Log security-related events for audit"""
    try:
        conn = get_auth_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_audit_log (user_id, event_type, event_details, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, event_type, json.dumps(details) if details else None, ip_address, user_agent))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Failed to log security event: {e}")


class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def register_user(username, email, password, display_name=None):
        """Register a new user"""
        # Validate input
        if not username or not email or not password:
            return None, "Username, email, and password are required"
        
        if len(password) < MIN_PASSWORD_LENGTH:
            return None, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
        
        if not '@' in email or not '.' in email:
            return None, "Invalid email format"
        
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                conn.close()
                return None, "Username or email already exists"
            
            # Hash password
            password_hash, salt = hash_password(password)
            
            # Create family for new user (they can invite others later)
            cursor.execute('''
                INSERT INTO families (name, invite_code)
                VALUES (?, ?)
            ''', (f"{display_name or username}'s Family", secrets.token_urlsafe(16)))
            
            family_id = cursor.lastrowid
            
            # Create user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, display_name, role, family_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, display_name or username, UserRole.ADMIN, family_id))
            
            user_id = cursor.lastrowid
            
            # Update family with creator
            cursor.execute('UPDATE families SET created_by = ? WHERE id = ?', (user_id, family_id))
            
            # Create default user settings
            default_settings = {
                'notifications_enabled': True,
                'dark_mode': False,
                'expiry_warning_days': 3,
                'low_stock_threshold': 2,
                'default_location': 'Kitchen',
                'language': 'en',
                'currency': 'USD'
            }
            
            for key, value in default_settings.items():
                cursor.execute('''
                    INSERT INTO user_settings (user_id, setting_key, setting_value)
                    VALUES (?, ?, ?)
                ''', (user_id, key, json.dumps(value)))
            
            conn.commit()
            conn.close()
            
            # Log event
            log_security_event('user_registered', user_id, {'username': username, 'email': email})
            
            return user_id, None
            
        except Exception as e:
            logging.error(f"User registration failed: {e}")
            return None, f"Registration failed: {str(e)}"
    
    @staticmethod
    def login(username_or_email, password, device_info=None, ip_address=None):
        """Authenticate user and create session"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            # Find user by username or email
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, role, family_id, is_active, display_name
                FROM users 
                WHERE (username = ? OR email = ?) AND is_active = 1
            ''', (username_or_email, username_or_email))
            
            user = cursor.fetchone()
            
            if not user:
                log_security_event('login_failed', None, {'username': username_or_email, 'reason': 'user_not_found'}, ip_address)
                conn.close()
                return None, "Invalid credentials"
            
            # Verify password
            if not verify_password(password, user['password_hash'], user['salt']):
                log_security_event('login_failed', user['id'], {'reason': 'wrong_password'}, ip_address)
                conn.close()
                return None, "Invalid credentials"
            
            # Generate tokens
            access_token, access_expiry = generate_token(user['id'], 'access')
            refresh_token, refresh_expiry = generate_token(user['id'], 'refresh')
            
            # Store session
            token_hash = hashlib.sha256(access_token.encode()).hexdigest()
            refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO user_sessions (user_id, token_hash, refresh_token_hash, device_info, ip_address, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user['id'], token_hash, refresh_token_hash, device_info, ip_address, access_expiry.isoformat()))
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.utcnow().isoformat(), user['id']))
            
            conn.commit()
            conn.close()
            
            # Log successful login
            log_security_event('login_success', user['id'], {'device': device_info}, ip_address)
            
            return {
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'display_name': user['display_name'],
                    'role': user['role'],
                    'family_id': user['family_id']
                },
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': access_expiry.isoformat()
            }, None
            
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return None, f"Login failed: {str(e)}"
    
    @staticmethod
    def logout(token):
        """Invalidate user session"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Get user_id before deactivating session
            cursor.execute('SELECT user_id FROM user_sessions WHERE token_hash = ?', (token_hash,))
            session = cursor.fetchone()
            
            if session:
                cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE token_hash = ?', (token_hash,))
                conn.commit()
                log_security_event('logout', session['user_id'])
            
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Logout failed: {e}")
            return False
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Generate new access token using refresh token"""
        try:
            payload, error = decode_token(refresh_token)
            
            if error:
                return None, error
            
            if payload.get('token_type') != 'refresh':
                return None, 'Invalid token type'
            
            conn = get_auth_db()
            cursor = conn.cursor()
            
            # Verify refresh token is still valid in database
            refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            cursor.execute('''
                SELECT user_id FROM user_sessions 
                WHERE refresh_token_hash = ? AND is_active = 1
            ''', (refresh_token_hash,))
            
            session = cursor.fetchone()
            if not session:
                conn.close()
                return None, 'Session not found or expired'
            
            # Generate new access token
            access_token, access_expiry = generate_token(payload['user_id'], 'access')
            
            # Update session with new token hash
            new_token_hash = hashlib.sha256(access_token.encode()).hexdigest()
            cursor.execute('''
                UPDATE user_sessions 
                SET token_hash = ?, expires_at = ?, last_activity = ?
                WHERE refresh_token_hash = ?
            ''', (new_token_hash, access_expiry.isoformat(), datetime.utcnow().isoformat(), refresh_token_hash))
            
            conn.commit()
            conn.close()
            
            return {
                'access_token': access_token,
                'expires_at': access_expiry.isoformat()
            }, None
            
        except Exception as e:
            logging.error(f"Token refresh failed: {e}")
            return None, f"Token refresh failed: {str(e)}"
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user information by ID"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, display_name, avatar_url, role, family_id, 
                       is_active, email_verified, created_at, last_login
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return dict(user)
            return None
            
        except Exception as e:
            logging.error(f"Get user failed: {e}")
            return None
    
    @staticmethod
    def update_user_profile(user_id, updates):
        """Update user profile information"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            allowed_fields = ['display_name', 'avatar_url', 'email']
            update_parts = []
            values = []
            
            for field, value in updates.items():
                if field in allowed_fields:
                    update_parts.append(f"{field} = ?")
                    values.append(value)
            
            if not update_parts:
                conn.close()
                return False, "No valid fields to update"
            
            update_parts.append("updated_at = ?")
            values.append(datetime.utcnow().isoformat())
            values.append(user_id)
            
            cursor.execute(f'''
                UPDATE users SET {", ".join(update_parts)} WHERE id = ?
            ''', values)
            
            conn.commit()
            conn.close()
            
            log_security_event('profile_updated', user_id, {'fields': list(updates.keys())})
            
            return True, None
            
        except Exception as e:
            logging.error(f"Update profile failed: {e}")
            return False, f"Update failed: {str(e)}"
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password"""
        try:
            if len(new_password) < MIN_PASSWORD_LENGTH:
                return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
            
            conn = get_auth_db()
            cursor = conn.cursor()
            
            # Get current password hash
            cursor.execute('SELECT password_hash, salt FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "User not found"
            
            # Verify current password
            if not verify_password(current_password, user['password_hash'], user['salt']):
                log_security_event('password_change_failed', user_id, {'reason': 'wrong_current_password'})
                conn.close()
                return False, "Current password is incorrect"
            
            # Hash new password with new salt
            new_hash, new_salt = hash_password(new_password)
            
            cursor.execute('''
                UPDATE users SET password_hash = ?, salt = ?, updated_at = ? WHERE id = ?
            ''', (new_hash, new_salt, datetime.utcnow().isoformat(), user_id))
            
            # Invalidate all existing sessions
            cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            log_security_event('password_changed', user_id)
            
            return True, None
            
        except Exception as e:
            logging.error(f"Password change failed: {e}")
            return False, f"Password change failed: {str(e)}"
    
    @staticmethod
    def get_user_settings(user_id):
        """Get all settings for a user"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            cursor.execute('SELECT setting_key, setting_value FROM user_settings WHERE user_id = ?', (user_id,))
            settings = cursor.fetchall()
            conn.close()
            
            return {row['setting_key']: json.loads(row['setting_value']) for row in settings}
            
        except Exception as e:
            logging.error(f"Get settings failed: {e}")
            return {}
    
    @staticmethod
    def update_user_setting(user_id, key, value):
        """Update a single user setting"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_settings (user_id, setting_key, setting_value, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (user_id, setting_key) 
                DO UPDATE SET setting_value = ?, updated_at = ?
            ''', (user_id, key, json.dumps(value), datetime.utcnow().isoformat(),
                  json.dumps(value), datetime.utcnow().isoformat()))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logging.error(f"Update setting failed: {e}")
            return False


class FamilyService:
    """Service for family/household management"""
    
    @staticmethod
    def get_family(family_id):
        """Get family information"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT f.*, u.display_name as creator_name
                FROM families f
                LEFT JOIN users u ON f.created_by = u.id
                WHERE f.id = ?
            ''', (family_id,))
            
            family = cursor.fetchone()
            conn.close()
            
            if family:
                return dict(family)
            return None
            
        except Exception as e:
            logging.error(f"Get family failed: {e}")
            return None
    
    @staticmethod
    def get_family_members(family_id):
        """Get all members of a family"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, display_name, avatar_url, role, is_active, last_login
                FROM users WHERE family_id = ?
            ''', (family_id,))
            
            members = cursor.fetchall()
            conn.close()
            
            return [dict(m) for m in members]
            
        except Exception as e:
            logging.error(f"Get family members failed: {e}")
            return []
    
    @staticmethod
    def invite_member(family_id, email, role, invited_by_user_id):
        """Invite a new member to the family"""
        try:
            if role not in [UserRole.MEMBER, UserRole.GUEST, UserRole.CHILD]:
                return None, "Invalid role for invitation"
            
            conn = get_auth_db()
            cursor = conn.cursor()
            
            # Check if user already exists with this email
            cursor.execute('SELECT id, family_id FROM users WHERE email = ?', (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                conn.close()
                return None, "User with this email already exists"
            
            # Create invitation
            invite_token = secrets.token_urlsafe(32)
            expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
            
            cursor.execute('''
                INSERT INTO family_invitations (family_id, email, role, invite_token, invited_by, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (family_id, email, role, invite_token, invited_by_user_id, expires_at))
            
            conn.commit()
            conn.close()
            
            log_security_event('member_invited', invited_by_user_id, {'email': email, 'family_id': family_id})
            
            return invite_token, None
            
        except Exception as e:
            logging.error(f"Invite member failed: {e}")
            return None, f"Invitation failed: {str(e)}"
    
    @staticmethod
    def accept_invitation(invite_token, username, password, display_name=None):
        """Accept a family invitation and create user account"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            # Find valid invitation
            cursor.execute('''
                SELECT * FROM family_invitations 
                WHERE invite_token = ? AND accepted = 0 AND expires_at > ?
            ''', (invite_token, datetime.utcnow().isoformat()))
            
            invitation = cursor.fetchone()
            
            if not invitation:
                conn.close()
                return None, "Invalid or expired invitation"
            
            # Validate input
            if len(password) < MIN_PASSWORD_LENGTH:
                conn.close()
                return None, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
            
            # Check username availability
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return None, "Username already taken"
            
            # Create user with family
            password_hash, salt = hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, display_name, role, family_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, invitation['email'], password_hash, salt, 
                  display_name or username, invitation['role'], invitation['family_id']))
            
            user_id = cursor.lastrowid
            
            # Mark invitation as accepted
            cursor.execute('UPDATE family_invitations SET accepted = 1 WHERE id = ?', (invitation['id'],))
            
            # Create default settings
            default_settings = {
                'notifications_enabled': True,
                'dark_mode': False,
                'expiry_warning_days': 3,
                'low_stock_threshold': 2
            }
            
            for key, value in default_settings.items():
                cursor.execute('''
                    INSERT INTO user_settings (user_id, setting_key, setting_value)
                    VALUES (?, ?, ?)
                ''', (user_id, key, json.dumps(value)))
            
            conn.commit()
            conn.close()
            
            log_security_event('invitation_accepted', user_id, {'family_id': invitation['family_id']})
            
            return user_id, None
            
        except Exception as e:
            logging.error(f"Accept invitation failed: {e}")
            return None, f"Acceptance failed: {str(e)}"
    
    @staticmethod
    def update_member_role(family_id, user_id, new_role, updated_by_user_id):
        """Update a family member's role"""
        try:
            if new_role not in [UserRole.ADMIN, UserRole.MEMBER, UserRole.GUEST, UserRole.CHILD]:
                return False, "Invalid role"
            
            conn = get_auth_db()
            cursor = conn.cursor()
            
            # Verify requesting user is admin
            cursor.execute('SELECT role FROM users WHERE id = ? AND family_id = ?', (updated_by_user_id, family_id))
            requester = cursor.fetchone()
            
            if not requester or requester['role'] != UserRole.ADMIN:
                conn.close()
                return False, "Only admins can change roles"
            
            # Don't allow removing last admin
            if new_role != UserRole.ADMIN:
                cursor.execute('''
                    SELECT COUNT(*) as admin_count FROM users 
                    WHERE family_id = ? AND role = 'admin' AND id != ?
                ''', (family_id, user_id))
                
                if cursor.fetchone()['admin_count'] == 0:
                    # Check if target user was the only admin
                    cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
                    target = cursor.fetchone()
                    if target and target['role'] == UserRole.ADMIN:
                        conn.close()
                        return False, "Cannot remove the last admin"
            
            # Update role
            cursor.execute('UPDATE users SET role = ?, updated_at = ? WHERE id = ? AND family_id = ?',
                          (new_role, datetime.utcnow().isoformat(), user_id, family_id))
            
            conn.commit()
            conn.close()
            
            log_security_event('role_changed', updated_by_user_id, 
                             {'target_user': user_id, 'new_role': new_role, 'family_id': family_id})
            
            return True, None
            
        except Exception as e:
            logging.error(f"Update role failed: {e}")
            return False, f"Role update failed: {str(e)}"
    
    @staticmethod
    def remove_member(family_id, user_id, removed_by_user_id):
        """Remove a member from the family"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            # Verify requesting user is admin
            cursor.execute('SELECT role FROM users WHERE id = ? AND family_id = ?', (removed_by_user_id, family_id))
            requester = cursor.fetchone()
            
            if not requester or requester['role'] != UserRole.ADMIN:
                conn.close()
                return False, "Only admins can remove members"
            
            # Can't remove yourself if you're the last admin
            if user_id == removed_by_user_id:
                cursor.execute('''
                    SELECT COUNT(*) as admin_count FROM users 
                    WHERE family_id = ? AND role = 'admin' AND id != ?
                ''', (family_id, user_id))
                
                if cursor.fetchone()['admin_count'] == 0:
                    conn.close()
                    return False, "Cannot remove yourself as the last admin"
            
            # Deactivate user (soft delete)
            cursor.execute('UPDATE users SET is_active = 0, family_id = NULL, updated_at = ? WHERE id = ? AND family_id = ?',
                          (datetime.utcnow().isoformat(), user_id, family_id))
            
            # Invalidate all their sessions
            cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            log_security_event('member_removed', removed_by_user_id, 
                             {'removed_user': user_id, 'family_id': family_id})
            
            return True, None
            
        except Exception as e:
            logging.error(f"Remove member failed: {e}")
            return False, f"Removal failed: {str(e)}"
    
    @staticmethod
    def update_family_settings(family_id, settings, user_id):
        """Update family settings"""
        try:
            conn = get_auth_db()
            cursor = conn.cursor()
            
            # Verify user is admin
            cursor.execute('SELECT role FROM users WHERE id = ? AND family_id = ?', (user_id, family_id))
            user = cursor.fetchone()
            
            if not user or user['role'] != UserRole.ADMIN:
                conn.close()
                return False, "Only admins can update family settings"
            
            cursor.execute('UPDATE families SET settings = ? WHERE id = ?', 
                          (json.dumps(settings), family_id))
            
            conn.commit()
            conn.close()
            
            return True, None
            
        except Exception as e:
            logging.error(f"Update family settings failed: {e}")
            return False, f"Update failed: {str(e)}"


# Flask decorators for route protection
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Decode and validate token
        payload, error = decode_token(token)
        
        if error:
            return jsonify({'error': error}), 401
        
        # Verify session is still active
        conn = get_auth_db()
        cursor = conn.cursor()
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        cursor.execute('''
            SELECT user_id FROM user_sessions 
            WHERE token_hash = ? AND is_active = 1 AND expires_at > ?
        ''', (token_hash, datetime.utcnow().isoformat()))
        
        session = cursor.fetchone()
        conn.close()
        
        if not session:
            return jsonify({'error': 'Session expired or invalid'}), 401
        
        # Store user info in flask g object
        g.user_id = payload['user_id']
        g.user = AuthService.get_user_by_id(payload['user_id'])
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(*roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if g.user['role'] not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_family_access(f):
    """Decorator to require user belongs to a family"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not g.user.get('family_id'):
            return jsonify({'error': 'No family associated with account'}), 403
        
        g.family_id = g.user['family_id']
        return f(*args, **kwargs)
    
    return decorated_function


# Initialize tables when module is imported
try:
    init_auth_tables()
except Exception as e:
    logging.error(f"Failed to initialize auth tables: {e}")
