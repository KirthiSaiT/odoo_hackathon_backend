"""
Profile Service
Business logic for user profile management
"""
import logging
from typing import Optional
from datetime import datetime

from ..core.database import get_db_cursor
from ..models.profile_models import ProfileCreate, ProfileUpdate, ProfileResponse

logger = logging.getLogger(__name__)


class ProfileService:
    """Service class for profile operations"""

    @staticmethod
    def get_profile_by_user_id(user_id: str) -> Optional[ProfileResponse]:
        """Get user profile by user_id"""
        try:
            with get_db_cursor() as cursor:
                sql = """
                SELECT 
                    p.Id, p.UserId, p.EmployeeId,
                    p.FirstName, p.LastName, p.PhoneNumber,
                    p.AddressLine1, p.AddressLine2, p.City, p.State,
                    p.PostalCode, p.CountryId, p.ProfilePictureUrl,
                    p.DateOfBirth, p.CreatedAt, p.UpdatedAt,
                    c.Name as CountryName,
                    u.name as UserName, u.email as UserEmail, u.role as UserRole
                FROM UserProfiles p
                LEFT JOIN Countries c ON p.CountryId = c.Id
                LEFT JOIN Users u ON p.UserId = u.user_id
                WHERE p.UserId = ?
                """
                cursor.execute(sql, (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return ProfileResponse(
                    id=row[0],
                    user_id=str(row[1]),
                    employee_id=row[2],
                    first_name=row[3],
                    last_name=row[4],
                    phone_number=row[5],
                    address_line1=row[6],
                    address_line2=row[7],
                    city=row[8],
                    state=row[9],
                    postal_code=row[10],
                    country_id=row[11],
                    profile_picture_url=row[12],
                    date_of_birth=row[13],
                    created_at=row[14],
                    updated_at=row[15],
                    country_name=row[16],
                    user_name=row[17],
                    user_email=row[18],
                    user_role=row[19]
                )
        except Exception as e:
            logger.error(f"❌ Error getting profile for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def create_profile(user_id: str, data: ProfileCreate) -> ProfileResponse:
        """Create a new user profile"""
        try:
            with get_db_cursor() as cursor:
                sql = """
                INSERT INTO UserProfiles (
                    UserId, FirstName, LastName, PhoneNumber,
                    AddressLine1, AddressLine2, City, State,
                    PostalCode, CountryId, ProfilePictureUrl, DateOfBirth,
                    CreatedAt, UpdatedAt
                )
                OUTPUT INSERTED.Id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
                """
                cursor.execute(sql, (
                    user_id,
                    data.first_name,
                    data.last_name,
                    data.phone_number,
                    data.address_line1,
                    data.address_line2,
                    data.city,
                    data.state,
                    data.postal_code,
                    data.country_id,
                    data.profile_picture_url,
                    data.date_of_birth
                ))
                
                result = cursor.fetchone()
                profile_id = result[0]
                
                logger.info(f"✅ Created profile {profile_id} for user {user_id}")
                
                # Fetch and return the created profile
                return ProfileService._get_profile_by_id_internal(cursor, profile_id)
        except Exception as e:
            logger.error(f"❌ Error creating profile for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def update_profile(user_id: str, data: ProfileUpdate) -> Optional[ProfileResponse]:
        """Update an existing user profile"""
        try:
            with get_db_cursor() as cursor:
                # Build dynamic update query
                update_fields = []
                params = []
                
                if data.first_name is not None:
                    update_fields.append("FirstName = ?")
                    params.append(data.first_name)
                if data.last_name is not None:
                    update_fields.append("LastName = ?")
                    params.append(data.last_name)
                if data.phone_number is not None:
                    update_fields.append("PhoneNumber = ?")
                    params.append(data.phone_number)
                if data.address_line1 is not None:
                    update_fields.append("AddressLine1 = ?")
                    params.append(data.address_line1)
                if data.address_line2 is not None:
                    update_fields.append("AddressLine2 = ?")
                    params.append(data.address_line2)
                if data.city is not None:
                    update_fields.append("City = ?")
                    params.append(data.city)
                if data.state is not None:
                    update_fields.append("State = ?")
                    params.append(data.state)
                if data.postal_code is not None:
                    update_fields.append("PostalCode = ?")
                    params.append(data.postal_code)
                if data.country_id is not None:
                    update_fields.append("CountryId = ?")
                    params.append(data.country_id)
                if data.profile_picture_url is not None:
                    update_fields.append("ProfilePictureUrl = ?")
                    params.append(data.profile_picture_url)
                if data.date_of_birth is not None:
                    update_fields.append("DateOfBirth = ?")
                    params.append(data.date_of_birth)
                
                if not update_fields:
                    # No fields to update, just return current profile
                    return ProfileService.get_profile_by_user_id(user_id)
                
                # Always update UpdatedAt
                update_fields.append("UpdatedAt = GETDATE()")
                params.append(user_id)
                
                sql = f"""
                UPDATE UserProfiles
                SET {', '.join(update_fields)}
                OUTPUT INSERTED.Id
                WHERE UserId = ?
                """
                cursor.execute(sql, tuple(params))
                result = cursor.fetchone()
                
                if not result:
                    logger.warning(f"⚠️ Profile not found for user {user_id}")
                    return None
                
                profile_id = result[0]
                logger.info(f"✅ Updated profile {profile_id} for user {user_id}")
                
                return ProfileService._get_profile_by_id_internal(cursor, profile_id)
        except Exception as e:
            logger.error(f"❌ Error updating profile for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_or_create_profile(user_id: str) -> ProfileResponse:
        """Get existing profile or create an empty one"""
        profile = ProfileService.get_profile_by_user_id(user_id)
        if profile:
            return profile
        
        # Create empty profile
        return ProfileService.create_profile(user_id, ProfileCreate())

    @staticmethod
    def _get_profile_by_id_internal(cursor, profile_id: int) -> Optional[ProfileResponse]:
        """Internal helper to fetch profile by ID within existing transaction"""
        sql = """
        SELECT 
            p.Id, p.UserId, p.EmployeeId,
            p.FirstName, p.LastName, p.PhoneNumber,
            p.AddressLine1, p.AddressLine2, p.City, p.State,
            p.PostalCode, p.CountryId, p.ProfilePictureUrl,
            p.DateOfBirth, p.CreatedAt, p.UpdatedAt,
            c.Name as CountryName,
            u.name as UserName, u.email as UserEmail, u.role as UserRole
        FROM UserProfiles p
        LEFT JOIN Countries c ON p.CountryId = c.Id
        LEFT JOIN Users u ON p.UserId = u.user_id
        WHERE p.Id = ?
        """
        cursor.execute(sql, (profile_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return ProfileResponse(
            id=row[0],
            user_id=str(row[1]),
            employee_id=row[2],
            first_name=row[3],
            last_name=row[4],
            phone_number=row[5],
            address_line1=row[6],
            address_line2=row[7],
            city=row[8],
            state=row[9],
            postal_code=row[10],
            country_id=row[11],
            profile_picture_url=row[12],
            date_of_birth=row[13],
            created_at=row[14],
            updated_at=row[15],
            country_name=row[16],
            user_name=row[17],
            user_email=row[18],
            user_role=row[19]
        )
