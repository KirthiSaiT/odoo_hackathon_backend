"""
Role & Rights Service
Business logic for role and access rights management
"""
from typing import Optional, List
import logging

from app.core.database import get_db_cursor
from app.models.shared_models import LookupItem, LookupResponse, StatsResponse
from app.models.role_models import (
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse,
    UserRight, UserRightsResponse
)

logger = logging.getLogger(__name__)


class RoleService:
    """Service for Role & Rights Management"""

    @staticmethod
    def get_lookups() -> LookupResponse:
        """Fetch all lookup tables for frontend dropdowns"""
        try:
            with get_db_cursor() as cursor:
                def get_list(table):
                    cursor.execute(f"SELECT Id, Name FROM {table} WHERE IsActive = 1 ORDER BY Name")
                    return [LookupItem(id=row[0], name=row[1]) for row in cursor.fetchall()]
                
                cursor.execute("SELECT role_id, role_name FROM Roles WHERE is_active = 1 ORDER BY role_name")
                roles = [LookupItem(id=row[0], name=row[1]) for row in cursor.fetchall()]

                return LookupResponse(
                    genders=get_list("Genders"),
                    marital_statuses=get_list("MaritalStatuses"),
                    blood_groups=get_list("BloodGroups"),
                    departments=get_list("Departments"),
                    designations=get_list("Designations"),
                    employment_types=get_list("EmploymentTypes"),
                    employment_statuses=get_list("EmploymentStatuses"),
                    countries=get_list("Countries"),
                    roles=roles
                )
        except Exception as e:
            logger.error(f"❌ Error fetching lookups: {str(e)}")
            raise e

    @staticmethod
    def get_dashboard_stats() -> StatsResponse:
        """Fetch dashboard statistics"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Users WHERE is_active = 1")
                total_users = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM Employees WHERE IsActive = 1")
                active_employees = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM Roles WHERE is_active = 1")
                total_roles = cursor.fetchone()[0]

                try:
                    cursor.execute("SELECT COUNT(DISTINCT module_key) FROM RoleRights")
                    total_modules = cursor.fetchone()[0]
                    if total_modules == 0: total_modules = 5
                except:
                    total_modules = 5

                return StatsResponse(
                    total_users=total_users,
                    active_employees=active_employees,
                    total_roles=total_roles,
                    total_modules=total_modules
                )
        except Exception as e:
            logger.error(f"❌ Error getting stats: {str(e)}")
            return StatsResponse(total_users=0, active_employees=0, total_roles=0, total_modules=0)

    @staticmethod
    def get_user_rights(user_id: str) -> UserRightsResponse:
        """Fetch access rights for a user"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT Id, UserId, ModuleKey, CanView, CanCreate, CanUpdate, CanDelete 
                    FROM UserRights 
                    WHERE UserId = ?
                """, (user_id,))
                rows = cursor.fetchall()
                
                rights = []
                for row in rows:
                    rights.append(UserRight(
                        id=row[0],
                        user_id=row[1],
                        module_key=row[2],
                        can_view=bool(row[3]),
                        can_create=bool(row[4]),
                        can_update=bool(row[5]),
                        can_delete=bool(row[6])
                    ))
                
                return UserRightsResponse(user_id=str(user_id), rights=rights)
        except Exception as e:
            logger.error(f"❌ Error getting rights for user {user_id}: {str(e)}")
            return UserRightsResponse(user_id=str(user_id), rights=[])

    @staticmethod
    def save_user_rights(user_id: str, rights: List[UserRight]):
        """Save access rights for a user (Delete & Insert)"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("DELETE FROM UserRights WHERE UserId = ?", (user_id,))
                
                if not rights:
                    return

                insert_sql = """
                INSERT INTO UserRights (UserId, ModuleKey, CanView, CanCreate, CanUpdate, CanDelete)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                
                params = []
                for r in rights:
                    params.append((
                        user_id, r.module_key, 
                        r.can_view, r.can_create, r.can_update, r.can_delete
                    ))
                
                cursor.executemany(insert_sql, params)
                logger.info(f"✅ Saved {len(rights)} rights for User {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error saving rights for user {user_id}: {str(e)}")
            raise e

    # =====================
    # ROLE CRUD OPERATIONS
    # =====================

    @staticmethod
    def get_all_roles(page: int = 1, size: int = 10, search: str = None) -> RoleListResponse:
        """Fetch paginated list of roles"""
        offset = (page - 1) * size
        try:
            with get_db_cursor() as cursor:
                count_sql = "SELECT COUNT(*) FROM Roles WHERE 1=1"
                params = []
                if search:
                    count_sql += " AND (role_name LIKE ? OR description LIKE ?)"
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern])
                
                cursor.execute(count_sql, tuple(params))
                total = cursor.fetchone()[0]

                sql = """
                SELECT role_id, role_name, description, is_active, created_at
                FROM Roles
                WHERE 1=1
                """
                
                if search:
                    sql += " AND (role_name LIKE ? OR description LIKE ?)"
                
                sql += " ORDER BY role_id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                params.extend([offset, size])
                
                cursor.execute(sql, tuple(params))
                rows = cursor.fetchall()
                
                items = []
                for row in rows:
                    items.append(RoleResponse(
                        role_id=row[0],
                        role_name=row[1],
                        description=row[2],
                        is_active=bool(row[3]),
                        created_at=row[4]
                    ))
                    
                return RoleListResponse(items=items, total=total, page=page, size=size)
        except Exception as e:
            logger.error(f"❌ Error getting roles: {str(e)}")
            raise e

    @staticmethod
    def create_role(data: RoleCreate) -> RoleResponse:
        """Create a new role"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT 1 FROM Roles WHERE role_name = ?", (data.role_name,))
                if cursor.fetchone():
                    raise ValueError(f"Role '{data.role_name}' already exists")

                sql = """
                INSERT INTO Roles (role_name, description, is_active, created_at)
                OUTPUT INSERTED.role_id, INSERTED.created_at
                VALUES (?, ?, ?, SYSDATETIME())
                """
                cursor.execute(sql, (data.role_name, data.description, data.is_active))
                row = cursor.fetchone()
                if not row:
                    raise Exception("Failed to create Role")
                
                return RoleResponse(
                    role_id=row[0],
                    role_name=data.role_name,
                    description=data.description,
                    is_active=data.is_active,
                    created_at=row[1]
                )
        except Exception as e:
            logger.error(f"❌ Error creating role: {str(e)}")
            raise e

    @staticmethod
    def update_role(role_id: int, data: RoleUpdate) -> Optional[RoleResponse]:
        """Update role details"""
        try:
            with get_db_cursor() as cursor:
                fields = []
                values = []
                
                if data.role_name is not None:
                    fields.append("role_name = ?")
                    values.append(data.role_name)
                
                if data.description is not None:
                    fields.append("description = ?")
                    values.append(data.description)
                    
                if data.is_active is not None:
                    fields.append("is_active = ?")
                    values.append(data.is_active)

                if not fields:
                    return RoleService._get_role_by_id(cursor, role_id)

                values.append(role_id)
                sql = f"UPDATE Roles SET {', '.join(fields)} WHERE role_id = ?"
                cursor.execute(sql, tuple(values))
                
                return RoleService._get_role_by_id(cursor, role_id)
        except Exception as e:
            logger.error(f"❌ Error updating role {role_id}: {str(e)}")
            raise e

    @staticmethod
    def _get_role_by_id(cursor, role_id: int) -> Optional[RoleResponse]:
        """Helper to fetch role within existing cursor"""
        cursor.execute("SELECT role_id, role_name, description, is_active, created_at FROM Roles WHERE role_id = ?", (role_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return RoleResponse(
            role_id=row[0],
            role_name=row[1],
            description=row[2],
            is_active=bool(row[3]),
            created_at=row[4]
        )

    @staticmethod
    def delete_role(role_id: int) -> bool:
        """Soft delete a role (set is_active = 0)"""
        try:
            if role_id <= 3:
                raise ValueError("Cannot delete system roles (Admin, Employee, User)")
            
            with get_db_cursor() as cursor:
                cursor.execute("UPDATE Roles SET is_active = 0 WHERE role_id = ?", (role_id,))
                return True
        except Exception as e:
            logger.error(f"❌ Error deleting role {role_id}: {str(e)}")
            raise e
