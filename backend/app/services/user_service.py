"""
User Configuration Service
Business logic for user management
"""
from typing import Optional, List
import logging
import random
import string

from app.core.database import get_db_cursor
from app.core.security import Security
from app.core.tenant import get_tenant_id
from app.models.user_models import (
    UserCreate, UserUpdate, UserResponse, UserListResponse
)

logger = logging.getLogger(__name__)


class UserService:
    """Service for User Configuration Management"""

    @staticmethod
    def _generate_password(prefix: str = "odoo@", length: int = 3) -> str:
        """Generate a random password like odoo@123"""
        random_digits = ''.join(random.choices(string.digits, k=length))
        return f"{prefix}{random_digits}"

    @staticmethod
    def _map_role_to_string(role_id: int) -> str:
        """Map numeric RoleId to string Role for Users table"""
        if role_id == 1:
            return "ADMIN"
        elif role_id == 2:
            return "INTERNAL"
        else:
            return "PORTAL"

    @staticmethod
    def get_all_users(page: int = 1, size: int = 10, search: str = None) -> UserListResponse:
        """Fetch paginated list of users"""
        offset = (page - 1) * size
        try:
            with get_db_cursor() as cursor:
                count_sql = "SELECT COUNT(*) FROM Users WHERE 1=1"
                params = []
                if search:
                    count_sql += " AND (name LIKE ? OR email LIKE ?)"
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern])
                
                cursor.execute(count_sql, tuple(params))
                total = cursor.fetchone()[0]

                sql = """
                SELECT 
                    u.user_id, u.name, u.email, u.role, u.role_id, u.is_active, u.created_at,
                    r.role_name
                FROM Users u
                LEFT JOIN Roles r ON u.role_id = r.role_id
                WHERE 1=1
                """
                
                if search:
                    sql += " AND (u.name LIKE ? OR u.email LIKE ?)"
                
                sql += " ORDER BY u.created_at DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                params.extend([offset, size])
                
                cursor.execute(sql, tuple(params))
                rows = cursor.fetchall()
                
                items = []
                for row in rows:
                    items.append(UserResponse(
                        user_id=str(row[0]),
                        name=row[1],
                        email=row[2],
                        role=row[3] or '',
                        role_id=row[4] or 0,
                        is_active=bool(row[5]),
                        created_at=row[6],
                        role_name=row[7]
                    ))
                    
                return UserListResponse(items=items, total=total, page=page, size=size)
        except Exception as e:
            logger.error(f"❌ Error getting users: {str(e)}")
            raise e

    @staticmethod
    def create_user(data: UserCreate, created_by_str: str = 'ADMIN') -> UserResponse:
        """Create a new user"""
        password = data.password or UserService._generate_password()
        role_str = UserService._map_role_to_string(data.role_id)

        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT 1 FROM Users WHERE email = ?", (data.email,))
                if cursor.fetchone():
                    raise ValueError(f"Email {data.email} is already registered")

                password_hash = Security.hash_password(password)
                tenant_id = get_tenant_id()
                
                sql = """
                INSERT INTO Users (tenant_id, name, email, password_hash, role, role_id, is_active, is_email_verified, created_by, created_at)
                OUTPUT INSERTED.user_id, INSERTED.created_at
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, SYSDATETIME())
                """
                cursor.execute(sql, (
                    tenant_id,
                    data.name,
                    data.email,
                    password_hash,
                    role_str,
                    data.role_id,
                    data.is_active,
                    created_by_str
                ))
                row = cursor.fetchone()
                if not row:
                    raise Exception("Failed to create User")
                
                user_id = str(row[0])
                created_at = row[1]
                
                cursor.execute("SELECT role_name FROM Roles WHERE role_id = ?", (data.role_id,))
                role_row = cursor.fetchone()
                role_name = role_row[0] if role_row else None

                return UserResponse(
                    user_id=user_id,
                    name=data.name,
                    email=data.email,
                    role=role_str,
                    role_id=data.role_id,
                    is_active=data.is_active,
                    created_at=created_at,
                    role_name=role_name
                )
        except Exception as e:
            logger.error(f"❌ Error creating user: {str(e)}")
            raise e

    @staticmethod
    def update_user(user_id: str, data: UserUpdate) -> Optional[UserResponse]:
        """Update user details"""
        try:
            with get_db_cursor() as cursor:
                fields = []
                values = []
                
                if data.name is not None:
                    fields.append("name = ?")
                    values.append(data.name)
                
                if data.email is not None:
                    fields.append("email = ?")
                    values.append(data.email)
                    
                if data.role_id is not None:
                    fields.append("role_id = ?")
                    values.append(data.role_id)
                    role_str = UserService._map_role_to_string(data.role_id)
                    fields.append("role = ?")
                    values.append(role_str)
                    
                if data.is_active is not None:
                    fields.append("is_active = ?")
                    values.append(data.is_active)

                if data.password is not None:
                    password_hash = Security.hash_password(data.password)
                    fields.append("password_hash = ?")
                    values.append(password_hash)

                if not fields:
                     return UserService._get_user_by_id_internal(cursor, user_id)

                values.append(user_id)
                sql = f"UPDATE Users SET {', '.join(fields)} WHERE user_id = ?"
                cursor.execute(sql, tuple(values))
                
                return UserService._get_user_by_id_internal(cursor, user_id)
        except Exception as e:
            logger.error(f"❌ Error updating user {user_id}: {str(e)}")
            raise e

    @staticmethod
    def _get_user_by_id_internal(cursor, user_id):
        """Helper to fetch user within existing cursor"""
        cursor.execute("SELECT user_id, name, email, role, role_id, is_active, created_at FROM Users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row: return None
        
        role_name = None
        if row[4]:
             cursor.execute("SELECT role_name FROM Roles WHERE role_id = ?", (row[4],))
             r_row = cursor.fetchone()
             if r_row: role_name = r_row[0]

        return UserResponse(
            user_id=str(row[0]),
            name=row[1],
            email=row[2],
            role=row[3],
            role_id=row[4],
            is_active=bool(row[5]),
            created_at=row[6],
            role_name=role_name
        )

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Soft delete a user (set is_active = 0)"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("UPDATE Users SET is_active = 0 WHERE user_id = ?", (user_id,))
                logger.info(f"✅ Soft deleted User {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Error deleting user {user_id}: {str(e)}")
            raise e
