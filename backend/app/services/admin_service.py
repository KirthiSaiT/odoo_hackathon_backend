"""
Admin/Employee Service
Business logic for employee management
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging
import random
import string

from app.core.database import get_db_cursor
from app.core.security import Security
from app.core.tenant import get_tenant_id
from app.models.admin_models import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, 
    LookupResponse, LookupItem, EmployeeListResponse,
    UserCreate, UserUpdate, UserResponse, UserListResponse, StatsResponse,
    UserRight, UserRightsResponse,
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse
)

logger = logging.getLogger(__name__)

class AdminService:
    """Service for Admin & Employee Management"""

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
            return "EMPLOYEE"
        else:
            return "PORTAL"

    @staticmethod
    def get_lookups() -> LookupResponse:
        """Fetch all lookup tables for frontend dropdowns"""
        try:
            with get_db_cursor() as cursor:
                def get_list(table):
                    cursor.execute(f"SELECT Id, Name FROM {table} WHERE IsActive = 1 ORDER BY Name")
                    return [LookupItem(id=row[0], name=row[1]) for row in cursor.fetchall()]
                
                # Special handling for Roles (role_id, role_name)
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
    def create_employee(data: EmployeeCreate, created_by_id: Optional[int] = None) -> EmployeeResponse:
        """
        Create a new employee AND a corresponding User account
        Transactional: If either fails, rollback.
        """
        password = AdminService._generate_password()
        role_str = AdminService._map_role_to_string(data.role_id)
        
        try:
            with get_db_cursor() as cursor:  # Implicit transaction
                # 1. Create User
                # Check for existing email in Users
                cursor.execute("SELECT 1 FROM Users WHERE email = ?", (data.email,))
                if cursor.fetchone():
                    raise ValueError(f"Email {data.email} is already registered as a User")

                # Insert User
                tenant_id = get_tenant_id()
                user_sql = """
                INSERT INTO Users (tenant_id, name, email, password_hash, role, role_id, is_active, is_email_verified, created_by)
                OUTPUT INSERTED.user_id
                VALUES (?, ?, ?, ?, ?, ?, 1, 1, 'ADMIN')
                """
                password_hash = Security.hash_password(password)
                cursor.execute(user_sql, (
                    tenant_id,
                    f"{data.first_name} {data.last_name or ''}".strip(),
                    data.email,
                    password_hash,
                    role_str,
                    data.role_id
                ))
                user_row = cursor.fetchone()
                if not user_row:
                    raise Exception("Failed to create User record")
                user_id = str(user_row[0])

                # 2. Create Employee
                emp_sql = """
                INSERT INTO Employees (
                    FirstName, LastName, Email, PhoneNumber, Password,
                    DateOfBirth, GenderId, MaritalStatusId, BloodGroupId,
                    DateOfJoining, DesignationId, DepartmentId, EmploymentType,
                    EmploymentStatus, AddressLine1, AddressLine2, City, State,
                    PostalCode, CountryId, AdditionalNotes, RoleId, UserId,
                    CreatedById, IsActive
                )
                OUTPUT INSERTED.Id
                VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?
                )
                """
                cursor.execute(emp_sql, (
                    data.first_name, data.last_name, data.email, data.phone_number, password,
                    data.date_of_birth, data.gender_id, data.marital_status_id, data.blood_group_id,
                    data.date_of_joining, data.designation_id, data.department_id, data.employment_type,
                    data.employment_status, data.address_line1, data.address_line2, data.city, data.state,
                    data.postal_code, data.country_id, data.additional_notes, data.role_id, user_id,
                    created_by_id, data.is_active
                ))
                emp_row = cursor.fetchone()
                if not emp_row:
                    raise Exception("Failed to create Employee record")
                emp_id = emp_row[0]
                
                logger.info(f"✅ Created Employee {emp_id} linked to User {user_id}")
                
                # Retrieve full employee details for response
                return AdminService.get_employee_by_id(emp_id)

        except Exception as e:
            logger.error(f"❌ Error creating employee: {str(e)}")
            raise e

    @staticmethod
    def get_employee_by_id(emp_id: int) -> Optional[EmployeeResponse]:
        """Fetch single employee with joined data"""
        try:
            with get_db_cursor() as cursor:
                sql = """
                SELECT 
                    e.Id, e.FirstName, e.LastName, e.Email, e.PhoneNumber,
                    e.DateOfBirth, e.GenderId, e.MaritalStatusId, e.BloodGroupId,
                    e.DateOfJoining, e.DesignationId, e.DepartmentId, e.EmploymentType,
                    e.EmploymentStatus, e.AddressLine1, e.AddressLine2, e.City, e.State,
                    e.PostalCode, e.CountryId, e.AdditionalNotes, e.RoleId, e.IsActive,
                    e.CreatedAt, e.UserId,
                    
                    g.Name as GenderName,
                    ms.Name as MaritalStatusName,
                    bg.Name as BloodGroupName,
                    dep.Name as DepartmentName,
                    des.Name as DesignationName,
                    et.Name as EmploymentTypeName,
                    es.Name as EmploymentStatusName,
                    c.Name as CountryName,
                    r.role_name as RoleName
                    
                FROM Employees e
                LEFT JOIN Genders g ON e.GenderId = g.Id
                LEFT JOIN MaritalStatuses ms ON e.MaritalStatusId = ms.Id
                LEFT JOIN BloodGroups bg ON e.BloodGroupId = bg.Id
                LEFT JOIN Departments dep ON e.DepartmentId = dep.Id
                LEFT JOIN Designations des ON e.DesignationId = des.Id
                LEFT JOIN EmploymentTypes et ON e.EmploymentType = et.Id
                LEFT JOIN EmploymentStatuses es ON e.EmploymentStatus = es.Id
                LEFT JOIN Countries c ON e.CountryId = c.Id
                LEFT JOIN Roles r ON e.RoleId = r.role_id
                WHERE e.Id = ?
                """
                cursor.execute(sql, (emp_id,))
                row = cursor.peek() # Use generic mapping or manual
                
                if not row:
                    return None

                # Manual mapping from tuple to Pydantic
                # Adjust indices based on SELECT order
                return EmployeeResponse(
                    id=row[0], first_name=row[1], last_name=row[2], email=row[3], phone_number=row[4],
                    date_of_birth=row[5], gender_id=row[6], marital_status_id=row[7], blood_group_id=row[8],
                    date_of_joining=row[9], designation_id=row[10], department_id=row[11], employment_type=row[12],
                    employment_status=row[13], address_line1=row[14], address_line2=row[15], city=row[16], state=row[17],
                    postal_code=row[18], country_id=row[19], additional_notes=row[20], role_id=row[21], is_active=bool(row[22]),
                    created_at=row[23], user_id=str(row[24]) if row[24] else None,
                    
                    gender_name=row[25], marital_status_name=row[26], blood_group_name=row[27],
                    department_name=row[28], designation_name=row[29], employment_type_name=row[30],
                    employment_status_name=row[31], country_name=row[32], role_name=row[33]
                )
        except Exception as e:
            logger.error(f"❌ Error getting employee {emp_id}: {str(e)}")
            return None

    @staticmethod
    def update_employee(emp_id: int, data: EmployeeUpdate, modified_by_id: int) -> Optional[EmployeeResponse]:
        """Update employee details"""
        try:
            with get_db_cursor() as cursor:
                # Build dynamic update query
                fields = []
                values = []
                
                # Manual mapping of Pydantic fields to DB columns
                field_map = {
                    'first_name': 'FirstName', 'last_name': 'LastName', 'email': 'Email',
                    'phone_number': 'PhoneNumber', 'date_of_birth': 'DateOfBirth',
                    'gender_id': 'GenderId', 'marital_status_id': 'MaritalStatusId',
                    'blood_group_id': 'BloodGroupId', 'date_of_joining': 'DateOfJoining',
                    'designation_id': 'DesignationId', 'department_id': 'DepartmentId',
                    'employment_type': 'EmploymentType', 'employment_status': 'EmploymentStatus',
                    'address_line1': 'AddressLine1', 'address_line2': 'AddressLine2',
                    'city': 'City', 'state': 'State', 'postal_code': 'PostalCode',
                    'country_id': 'CountryId', 'additional_notes': 'AdditionalNotes',
                    'role_id': 'RoleId', 'is_active': 'IsActive'
                }

                # Helper for role update tracking
                new_role_id = None
                
                for model_field, db_col in field_map.items():
                    val = getattr(data, model_field)
                    if val is not None:
                        fields.append(f"{db_col} = ?")
                        values.append(val)
                        if model_field == 'role_id':
                            new_role_id = val
                
                if not fields:
                    return AdminService.get_employee_by_id(emp_id)

                fields.append("ModifiedAt = SYSDATETIME()")
                fields.append("ModifiedById = ?")
                values.append(modified_by_id)
                values.append(emp_id) # For WHERE clause

                sql = f"UPDATE Employees SET {', '.join(fields)} WHERE Id = ?"
                cursor.execute(sql, tuple(values))
                
                # Also update User role if role_id changed and user exists
                if new_role_id is not None:
                    # Get UserId from Employee
                    cursor.execute("SELECT UserId FROM Employees WHERE Id = ?", (emp_id,))
                    row = cursor.fetchone()
                    if row and row[0]:
                        user_id = row[0]
                        role_str = AdminService._map_role_to_string(new_role_id)
                        cursor.execute("UPDATE Users SET role_id = ?, role = ? WHERE user_id = ?", 
                                     (new_role_id, role_str, user_id))

                return AdminService.get_employee_by_id(emp_id)
        except Exception as e:
            logger.error(f"❌ Error updating employee {emp_id}: {str(e)}")
            raise e

    @staticmethod
    def get_all_employees(page: int = 1, size: int = 10, search: str = None) -> EmployeeListResponse:
        """Fetch paginated list of employees"""
        offset = (page - 1) * size
        try:
            with get_db_cursor() as cursor:
                # Count total
                count_sql = "SELECT COUNT(*) FROM Employees WHERE IsActive = 1"
                params = []
                if search:
                    count_sql += " AND (FirstName LIKE ? OR LastName LIKE ? OR Email LIKE ?)"
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern, search_pattern])
                
                cursor.execute(count_sql, tuple(params))
                total = cursor.fetchone()[0]

                # Fetch items
                sql = """
                SELECT 
                    e.Id, e.FirstName, e.LastName, e.Email, e.PhoneNumber,
                    e.DateOfBirth, e.GenderId, e.MaritalStatusId, e.BloodGroupId,
                    e.DateOfJoining, e.DesignationId, e.DepartmentId, e.EmploymentType,
                    e.EmploymentStatus, e.AddressLine1, e.AddressLine2, e.City, e.State,
                    e.PostalCode, e.CountryId, e.AdditionalNotes, e.RoleId, e.IsActive,
                    e.CreatedAt, e.UserId,
                    
                    g.Name as GenderName,
                    ms.Name as MaritalStatusName,
                    bg.Name as BloodGroupName,
                    dep.Name as DepartmentName,
                    des.Name as DesignationName,
                    et.Name as EmploymentTypeName,
                    es.Name as EmploymentStatusName,
                    c.Name as CountryName,
                    r.role_name as RoleName
                    
                FROM Employees e
                LEFT JOIN Genders g ON e.GenderId = g.Id
                LEFT JOIN MaritalStatuses ms ON e.MaritalStatusId = ms.Id
                LEFT JOIN BloodGroups bg ON e.BloodGroupId = bg.Id
                LEFT JOIN Departments dep ON e.DepartmentId = dep.Id
                LEFT JOIN Designations des ON e.DesignationId = des.Id
                LEFT JOIN EmploymentTypes et ON e.EmploymentType = et.Id
                LEFT JOIN EmploymentStatuses es ON e.EmploymentStatus = es.Id
                LEFT JOIN Countries c ON e.CountryId = c.Id
                LEFT JOIN Roles r ON e.RoleId = r.role_id
                WHERE e.IsActive = 1
                """
                
                if search:
                    sql += " AND (e.FirstName LIKE ? OR e.LastName LIKE ? OR e.Email LIKE ?)"
                
                
                sql += " ORDER BY e.CreatedAt DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                params.extend([offset, size])
                
                cursor.execute(sql, tuple(params))
                rows = cursor.fetchall()

                items = []
                for row in rows:
                    items.append(EmployeeResponse(
                        id=row[0], first_name=row[1], last_name=row[2], email=row[3], phone_number=row[4],
                        date_of_birth=row[5], gender_id=row[6], marital_status_id=row[7], blood_group_id=row[8],
                        date_of_joining=row[9], designation_id=row[10], department_id=row[11], employment_type=row[12],
                        employment_status=row[13], address_line1=row[14], address_line2=row[15], city=row[16], state=row[17],
                        postal_code=row[18], country_id=row[19], additional_notes=row[20], role_id=row[21], is_active=bool(row[22]),
                        created_at=row[23], user_id=str(row[24]) if row[24] else None,
                        
                        gender_name=row[25], marital_status_name=row[26], blood_group_name=row[27],
                        department_name=row[28], designation_name=row[29], employment_type_name=row[30],
                        employment_status_name=row[31], country_name=row[32], role_name=row[33]
                    ))

                return EmployeeListResponse(items=items, total=total, page=page, size=size)

        except Exception as e:
            logger.error(f"❌ Error listing employees: {str(e)}")
            raise e

    @staticmethod
    def get_all_users(page: int = 1, size: int = 10, search: str = None) -> UserListResponse:
        """Fetch paginated list of users"""
        offset = (page - 1) * size
        try:
            with get_db_cursor() as cursor:
                # Count total
                count_sql = "SELECT COUNT(*) FROM Users WHERE 1=1" # logical delete? Users usually hard delete or is_active
                params = []
                if search:
                    count_sql += " AND (name LIKE ? OR email LIKE ?)"
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern])
                
                cursor.execute(count_sql, tuple(params))
                total = cursor.fetchone()[0]

                # Fetch items
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
                        # last_login removed
                        role_name=row[7]
                    ))
                    
                return UserListResponse(items=items, total=total, page=page, size=size)
        except Exception as e:
            logger.error(f"❌ Error getting users: {str(e)}")
            raise e

    @staticmethod
    def create_user(data: UserCreate, created_by_str: str = 'ADMIN') -> UserResponse:
        """Create a new user"""
        password = data.password or AdminService._generate_password()
        
        # Determine role string from role_id if not provided logic (though we usually map it)
        role_str = AdminService._map_role_to_string(data.role_id)

        try:
            with get_db_cursor() as cursor:
                # Check email
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
                
                # Fetch role name for response
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
                    role_str = AdminService._map_role_to_string(data.role_id)
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
                     # Fetch existing to return
                     return AdminService._get_user_by_id_internal(cursor, user_id)

                values.append(user_id)
                sql = f"UPDATE Users SET {', '.join(fields)} WHERE user_id = ?"
                cursor.execute(sql, tuple(values))
                
                return AdminService._get_user_by_id_internal(cursor, user_id)
        except Exception as e:
            logger.error(f"❌ Error updating user {user_id}: {str(e)}")
            raise e

    @staticmethod
    def _get_user_by_id_internal(cursor, user_id):
        """Helper to fetch user within existing cursor"""
        cursor.execute("SELECT user_id, name, email, role, role_id, is_active, created_at FROM Users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row: return None
        
        # Get role name
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
    def get_dashboard_stats() -> StatsResponse:
        """Fetch dashboard statistics"""
        try:
            with get_db_cursor() as cursor:
                # Total Users (Active)
                cursor.execute("SELECT COUNT(*) FROM Users WHERE is_active = 1")
                total_users = cursor.fetchone()[0]

                # Active Employees
                cursor.execute("SELECT COUNT(*) FROM Employees WHERE IsActive = 1")
                active_employees = cursor.fetchone()[0]

                # Total Roles
                cursor.execute("SELECT COUNT(*) FROM Roles WHERE is_active = 1")
                total_roles = cursor.fetchone()[0]

                # Total Modules (Count distinct modules from RoleRights or standard set)
                # Fallback to logic: count distinct module_key? Or check RoleRights table?
                # Assuming simple fixed count or distinct if possible.
                # Let's try counting distinct module_id from RoleRights if table exists
                try:
                    # Check if RoleRights table has data
                    cursor.execute("SELECT COUNT(DISTINCT module_key) FROM RoleRights")
                    total_modules = cursor.fetchone()[0]
                    if total_modules == 0: total_modules = 5 # Default
                except:
                    total_modules = 5 # Default fallback

                return StatsResponse(
                    total_users=total_users,
                    active_employees=active_employees,
                    total_roles=total_roles,
                    total_modules=total_modules
                )
        except Exception as e:
            logger.error(f"❌ Error getting stats: {str(e)}")
            # Return zeros on error to prevent ui crash
            return StatsResponse(total_users=0, active_employees=0, total_roles=0, total_modules=0)

    @staticmethod
    def get_user_rights(user_id: int) -> UserRightsResponse:
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
    def save_user_rights(user_id: int, rights: List[UserRight]):
        """Save access rights for a user (Delete & Insert)"""
        try:
            with get_db_cursor() as cursor:
                # 1. Delete existing rights
                cursor.execute("DELETE FROM UserRights WHERE UserId = ?", (user_id,))
                
                # 2. Insert new rights
                if not rights:
                    return

                insert_sql = """
                INSERT INTO UserRights (UserId, ModuleKey, CanView, CanCreate, CanUpdate, CanDelete)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                
                params = []
                for r in rights:
                    # Ensure only checked permissions are stored? Or store all.
                    # Ideally store all defined module rights.
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
                # Count total
                count_sql = "SELECT COUNT(*) FROM Roles WHERE 1=1"
                params = []
                if search:
                    count_sql += " AND (role_name LIKE ? OR description LIKE ?)"
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern])
                
                cursor.execute(count_sql, tuple(params))
                total = cursor.fetchone()[0]

                # Fetch items
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
                # Check if role name already exists
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
                    # No changes, fetch and return existing
                    return AdminService._get_role_by_id(cursor, role_id)

                values.append(role_id)
                sql = f"UPDATE Roles SET {', '.join(fields)} WHERE role_id = ?"
                cursor.execute(sql, tuple(values))
                
                return AdminService._get_role_by_id(cursor, role_id)
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
            # Prevent deleting system roles (Admin=1, Employee=2, User=3)
            if role_id <= 3:
                raise ValueError("Cannot delete system roles (Admin, Employee, User)")
            
            with get_db_cursor() as cursor:
                cursor.execute("UPDATE Roles SET is_active = 0 WHERE role_id = ?", (role_id,))
                return True
        except Exception as e:
            logger.error(f"❌ Error deleting role {role_id}: {str(e)}")
            raise e

    # =====================
    # DELETE OPERATIONS
    # =====================

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

    @staticmethod
    def delete_employee(emp_id: int) -> bool:
        """Soft delete an employee (set IsActive = 0)"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("UPDATE Employees SET IsActive = 0 WHERE Id = ?", (emp_id,))
                logger.info(f"✅ Soft deleted Employee {emp_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Error deleting employee {emp_id}: {str(e)}")
            raise e

