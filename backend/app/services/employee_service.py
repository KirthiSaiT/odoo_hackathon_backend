"""
Employee/HR Service
Business logic for employee management
"""
from typing import Optional, List
from datetime import datetime
import logging
import random
import string

from app.core.database import get_db_cursor
from app.core.security import Security
from app.core.tenant import get_tenant_id
from app.models.employee_models import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
)

logger = logging.getLogger(__name__)


class EmployeeService:
    """Service for Employee/HR Management"""

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
    def create_employee(data: EmployeeCreate, created_by_id: Optional[int] = None) -> EmployeeResponse:
        """
        Create a new employee AND a corresponding User account
        Transactional: If either fails, rollback.
        """
        password = EmployeeService._generate_password()
        role_str = EmployeeService._map_role_to_string(data.role_id)
        
        try:
            with get_db_cursor() as cursor:
                # 1. Create User
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
                
                return EmployeeService.get_employee_by_id(emp_id)

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
                row = cursor.peek()
                
                if not row:
                    return None

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
                fields = []
                values = []
                
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

                new_role_id = None
                
                for model_field, db_col in field_map.items():
                    val = getattr(data, model_field)
                    if val is not None:
                        fields.append(f"{db_col} = ?")
                        values.append(val)
                        if model_field == 'role_id':
                            new_role_id = val
                
                if not fields:
                    return EmployeeService.get_employee_by_id(emp_id)

                fields.append("ModifiedAt = SYSDATETIME()")
                fields.append("ModifiedById = ?")
                values.append(modified_by_id)
                values.append(emp_id)

                sql = f"UPDATE Employees SET {', '.join(fields)} WHERE Id = ?"
                cursor.execute(sql, tuple(values))
                
                # Also update User role if role_id changed
                if new_role_id is not None:
                    cursor.execute("SELECT UserId FROM Employees WHERE Id = ?", (emp_id,))
                    row = cursor.fetchone()
                    if row and row[0]:
                        user_id = row[0]
                        role_str = EmployeeService._map_role_to_string(new_role_id)
                        cursor.execute("UPDATE Users SET role_id = ?, role = ? WHERE user_id = ?", 
                                     (new_role_id, role_str, user_id))

                return EmployeeService.get_employee_by_id(emp_id)
        except Exception as e:
            logger.error(f"❌ Error updating employee {emp_id}: {str(e)}")
            raise e

    @staticmethod
    def get_all_employees(page: int = 1, size: int = 10, search: str = None) -> EmployeeListResponse:
        """Fetch paginated list of employees"""
        offset = (page - 1) * size
        try:
            with get_db_cursor() as cursor:
                count_sql = "SELECT COUNT(*) FROM Employees WHERE IsActive = 1"
                params = []
                if search:
                    count_sql += " AND (FirstName LIKE ? OR LastName LIKE ? OR Email LIKE ?)"
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern, search_pattern])
                
                cursor.execute(count_sql, tuple(params))
                total = cursor.fetchone()[0]

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
