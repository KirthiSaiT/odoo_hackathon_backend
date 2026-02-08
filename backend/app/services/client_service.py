"""
Client Service
Handles business logic for Client management and Payments
"""
from typing import List, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, status
from app.core.database import get_db_cursor
from app.models.client_models import ClientCreate, ClientUpdate, ClientResponse, PaymentCreate, PaymentResponse
from app.core.security import Security

class ClientService:
    
    @staticmethod
    def create_client(client_data: ClientCreate, created_by: str, tenant_id: str) -> ClientResponse:
        """
        Create a new client and associated user account
        """
        with get_db_cursor() as cursor:
            # 1. Check if email already exists in Users
            cursor.execute("SELECT user_id FROM Users WHERE email = ?", (client_data.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered as a User")
            
            # Check Clients table - assuming Email column exists there too
            try:
                cursor.execute("SELECT Id FROM Clients WHERE Email = ?", (client_data.email,))
                if cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Email already registered as a Client")
            except Exception:
                # Table might not exist yet, but we will handle that separately
                pass

            # 2. Create User Account (Role 'CLIENT')
            hashed_password = Security.hash_password(client_data.password)
            
            # Insert into Users using correct snake_case columns
            import uuid
            user_id = str(uuid.uuid4())
            role = 'PORTAL'

            cursor.execute("""
                INSERT INTO Users (user_id, tenant_id, name, email, password_hash, role, is_active, is_email_verified, created_at, created_by)
                OUTPUT INSERTED.user_id
                VALUES (?, ?, ?, ?, ?, ?, 1, 1, SYSDATETIME(), ?)
            """, (user_id, tenant_id, client_data.client_name, client_data.email, hashed_password, role, created_by))
            
            # 3. Insert into Clients
            # Clients table has PascalCase columns based on client_schema.sql
            cursor.execute("""
                INSERT INTO Clients (UserId, ClientName, Email, ContactPerson, SubscriptionStatus, CreatedBy, IsActive, CreatedAt)
                OUTPUT INSERTED.Id, INSERTED.CreatedAt
                VALUES (?, ?, ?, ?, ?, ?, 1, GETDATE())
            """, (user_id, client_data.client_name, client_data.email, client_data.contact_person, "Pending", created_by))
            
            client_row = cursor.fetchone()
            client_id = client_row.Id
            created_at = client_row.CreatedAt

            # 4. Create Subscription if Product ID provided
            product_name = "N/A"
            if client_data.product_id:
                try:
                    start_date = client_data.subscription_start_date or datetime.now()
                    cursor.execute("""
                        INSERT INTO Subscriptions (ClientId, ProductId, Amount, Status, CreatedBy, StartDate, PaymentFrequency)
                        VALUES (?, ?, ?, 'Pending', ?, ?, ?)
                    """, (client_id, client_data.product_id, client_data.amount, created_by, start_date, client_data.payment_frequency))
                    
                    # Fetch product name for email
                    cursor.execute("SELECT Name FROM Products WHERE Id = ?", (client_data.product_id,))
                    p_row = cursor.fetchone()
                    if p_row:
                        product_name = p_row.Name
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to create subscription for client {client_id}: {e}")
                    raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")

            # Generate Reset Token for the new user
            reset_token = Security.create_password_reset_token(user_id, tenant_id)

            # Store Reset Token in Database to make it valid
            try:
                from app.core.config import get_settings
                from datetime import timedelta
                settings = get_settings()
                expires_at = datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
                
                cursor.execute("""
                    INSERT INTO PasswordResetTokens (tenant_id, user_id, token, expires_at, created_by)
                    VALUES (?, ?, ?, ?, ?)
                """, (tenant_id, user_id, reset_token, expires_at, created_by))
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to store reset token for client {client_id}: {e}")
                # We optionaly might want to fail here if we consider the link critical
                # But let's allow it to proceed and just log if it's a minor DB issue 
                # (though usually it means table is missing)

            # Send Enhanced Welcome Email
            from app.services.email_service import EmailService
            EmailService.send_welcome_email(
                to_email=client_data.email,
                name=client_data.client_name,
                password=client_data.password,
                product_name=product_name,
                amount=client_data.amount or 0.0,
                frequency=client_data.payment_frequency or "N/A",
                start_date=str(client_data.subscription_start_date or datetime.now().date()),
                reset_token=reset_token
            )

            return ClientResponse(
                id=client_id,
                user_id=user_id,
                client_name=client_data.client_name,
                email=client_data.email,
                contact_person=client_data.contact_person,
                subscription_status="Pending",
                is_active=True,
                created_at=created_at,
                created_by=created_by
            )

    @staticmethod
    def sync_portal_users(cursor):
        """
        Ensure all users with role 'PORTAL' have a corresponding record in Clients table.
        This handles the case where users sign up via the frontend but don't get a Client record immediately.
        """
        try:
            # Find PORTAL users who are NOT in Clients table
            cursor.execute("""
                SELECT u.user_id, u.name, u.email, u.created_by
                FROM Users u
                LEFT JOIN Clients c ON u.user_id = c.UserId
                WHERE u.role = 'PORTAL' AND c.Id IS NULL
            """)
            missing_users = cursor.fetchall()
            
            for user in missing_users:
                # Insert into Clients
                # Default SubscriptionStatus to 'Pending'
                cursor.execute("""
                    INSERT INTO Clients (UserId, ClientName, Email, ContactPerson, SubscriptionStatus, CreatedBy, IsActive, CreatedAt)
                    VALUES (?, ?, ?, ?, ?, ?, 1, GETDATE())
                """, (user.user_id, user.name, user.email, user.name, "Pending", user.created_by or 'SYSTEM'))
                # No commit here, handled by context manager
        except Exception as e:
            # Log error but don't fail the entire request, just continue with what we have
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to sync portal users: {e}")

    @staticmethod
    def get_all_clients(page: int = 1, size: int = 10, search: Optional[str] = None) -> Tuple[List[ClientResponse], int]:
        """Get all clients with pagination, including subscription details"""
        offset = (page - 1) * size
        
        with get_db_cursor() as cursor:
            # First, sync any missing portal users
            ClientService.sync_portal_users(cursor)

            # Base Query with JOINs
            query = """
                SELECT 
                    c.Id, c.UserId, c.ClientName, c.Email, c.ContactPerson, c.SubscriptionStatus, c.IsActive, c.CreatedAt, c.CreatedBy,
                    s.Id as SubscriptionId, s.ProductId, p.Name as ProductName, s.Amount, s.PaymentFrequency, s.StartDate
                FROM Clients c
                LEFT JOIN Subscriptions s ON c.Id = s.ClientId
                LEFT JOIN Products p ON s.ProductId = p.Id
                WHERE c.IsActive = 1
            """
            params = []
            
            if search:
                query += " AND (c.ClientName LIKE ? OR c.Email LIKE ? OR c.ContactPerson LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            # Get Total Count
            count_query = f"SELECT COUNT(*) FROM ({query}) AS CountTable"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Get Data
            query += " ORDER BY c.CreatedAt DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            params.extend([offset, size])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            clients = [
                ClientResponse(
                    id=row.Id,
                    user_id=row.UserId,
                    client_name=row.ClientName,
                    email=row.Email,
                    contact_person=row.ContactPerson,
                    subscription_status=row.SubscriptionStatus,
                    is_active=row.IsActive,
                    created_at=row.CreatedAt,
                    created_by=row.CreatedBy,
                    # Subscription fields
                    subscription_id=row.SubscriptionId,
                    product_id=row.ProductId,
                    product_name=row.ProductName,
                    amount=float(row.Amount) if row.Amount is not None else 0.0,
                    payment_frequency=row.PaymentFrequency,
                    subscription_start_date=row.StartDate
                ) for row in rows
            ]
            
            return clients, total

    @staticmethod
    def get_client_by_id(client_id: int) -> Optional[ClientResponse]:
        """Get client by ID with subscription details"""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.Id, c.UserId, c.ClientName, c.Email, c.ContactPerson, c.SubscriptionStatus, c.IsActive, c.CreatedAt, c.CreatedBy,
                    s.Id as SubscriptionId, s.ProductId, p.Name as ProductName, s.Amount, s.PaymentFrequency, s.StartDate
                FROM Clients c
                LEFT JOIN Subscriptions s ON c.Id = s.ClientId
                LEFT JOIN Products p ON s.ProductId = p.Id
                WHERE c.Id = ? AND c.IsActive = 1
            """, (client_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            return ClientResponse(
                id=row.Id,
                user_id=row.UserId,
                client_name=row.ClientName,
                email=row.Email,
                contact_person=row.ContactPerson,
                subscription_status=row.SubscriptionStatus,
                is_active=row.IsActive,
                created_at=row.CreatedAt,
                created_by=row.CreatedBy,
                # Subscription fields
                subscription_id=row.SubscriptionId,
                product_id=row.ProductId,
                product_name=row.ProductName,
                amount=float(row.Amount) if row.Amount is not None else 0.0,
                payment_frequency=row.PaymentFrequency,
                subscription_start_date=row.StartDate
            )

    @staticmethod
    def update_client(client_id: int, client_data: ClientUpdate) -> Optional[ClientResponse]:
        """Update client details"""
        with get_db_cursor() as cursor:
            # Check existence
            cursor.execute("SELECT Id FROM Clients WHERE Id = ? AND IsActive = 1", (client_id,))
            if not cursor.fetchone():
                return None

            updates = []
            params = []
            
            if client_data.client_name:
                updates.append("ClientName = ?")
                params.append(client_data.client_name)
            if client_data.email:
                updates.append("Email = ?")
                params.append(client_data.email)
            if client_data.contact_person:
                updates.append("ContactPerson = ?")
                params.append(client_data.contact_person)
            if client_data.subscription_status:
                updates.append("SubscriptionStatus = ?")
                params.append(client_data.subscription_status)
            if client_data.is_active is not None:
                updates.append("IsActive = ?")
                params.append(client_data.is_active)
                
            if not updates:
                return ClientService.get_client_by_id(client_id)
                
            params.append(client_id)
            query = f"UPDATE Clients SET {', '.join(updates)} WHERE Id = ?"
            cursor.execute(query, params)
            
            # If Client Name or Email changed, ideally update User table too
            if client_data.client_name or client_data.email:
                user_updates = []
                user_params = []
                if client_data.client_name:
                    user_updates.append("Name = ?")
                    user_params.append(client_data.client_name)
                if client_data.email:
                    user_updates.append("Email = ?")
                    user_params.append(client_data.email)
                
                # Get UserId first
                cursor.execute("SELECT UserId FROM Clients WHERE Id = ?", (client_id,))
                row = cursor.fetchone()
                if row:
                    user_id = row.UserId
                    user_params.append(user_id)
                    user_query = f"UPDATE Users SET {', '.join(user_updates)} WHERE user_id = ?"
                    cursor.execute(user_query, user_params)

            # Update Subscription if fields provided
            if client_data.product_id or client_data.amount is not None or client_data.payment_frequency or client_data.subscription_start_date:
                # Check if subscription exists
                cursor.execute("SELECT Id FROM Subscriptions WHERE ClientId = ?", (client_id,))
                sub_row = cursor.fetchone()
                
                if sub_row:
                    # Update existing subscription
                    sub_updates = []
                    sub_params = []
                    
                    if client_data.product_id:
                        sub_updates.append("ProductId = ?")
                        sub_params.append(client_data.product_id)
                    if client_data.amount is not None:
                        sub_updates.append("Amount = ?")
                        sub_params.append(client_data.amount)
                    if client_data.payment_frequency:
                        sub_updates.append("PaymentFrequency = ?")
                        sub_params.append(client_data.payment_frequency)
                    if client_data.subscription_start_date:
                        sub_updates.append("StartDate = ?")
                        sub_params.append(client_data.subscription_start_date)
                    
                    if sub_updates:
                         sub_params.append(sub_row.Id)
                         cursor.execute(f"UPDATE Subscriptions SET {', '.join(sub_updates)} WHERE Id = ?", sub_params)
                
                else:
                    # Create new subscription
                    # Only if we have minimal details (ProductId is usually key)
                    if client_data.product_id and client_data.amount is not None:
                        cursor.execute("""
                            INSERT INTO Subscriptions (ClientId, ProductId, Amount, PaymentFrequency, StartDate, Status, CreatedBy)
                            VALUES (?, ?, ?, ?, ?, 'Pending', 'SYSTEM')
                        """, (client_id, client_data.product_id, client_data.amount, 
                              client_data.payment_frequency or 'Monthly', 
                              client_data.subscription_start_date or datetime.now()))

            return ClientService.get_client_by_id(client_id)

    @staticmethod
    def delete_client(client_id: int) -> bool:
        """Soft delete client"""
        with get_db_cursor() as cursor:
            cursor.execute("UPDATE Clients SET IsActive = 0 WHERE Id = ?", (client_id,))
            
            # Also deactivate User?
            cursor.execute("SELECT UserId FROM Clients WHERE Id = ?", (client_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE Users SET IsActive = 0 WHERE Id = ?", (row.UserId,))
                
                
            return True

    @staticmethod
    def reset_client_password(client_id: int, updated_by: str) -> bool:
        """
        Reset client password and email them the new one
        """
        import secrets
        import string
        
        with get_db_cursor() as cursor:
            # Get Client and User details
            cursor.execute("SELECT UserId, ClientName, Email FROM Clients WHERE Id = ? AND IsActive = 1", (client_id,))
            client = cursor.fetchone()
            
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")
                
            # Generate random password
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            new_password = ''.join(secrets.choice(alphabet) for i in range(12))
            
            # Hash password
            hashed_password = Security.hash_password(new_password)
            
            # Update User
            cursor.execute("UPDATE Users SET password_hash = ? WHERE user_id = ?", (hashed_password, client.UserId))
            
            # Send Email
            from app.services.email_service import EmailService
            EmailService.send_new_password_email(client.Email, client.ClientName, new_password)
            
            return True

    # =================
    # PAYMENT LOGIC
    # =================
    
    @staticmethod
    def record_payment(payment_data: PaymentCreate, created_by: str) -> PaymentResponse:
        """Record a new payment"""
        with get_db_cursor() as cursor:
            # Insert Payment
            cursor.execute("""
                INSERT INTO Payments (ClientId, SubscriptionId, Amount, PaymentMethod, PaymentDate, Notes, CreatedBy)
                OUTPUT INSERTED.Id, INSERTED.CreatedAt
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (payment_data.client_id, payment_data.subscription_id, payment_data.amount, 
                  payment_data.payment_method, payment_data.payment_date, payment_data.notes, created_by))
            
            row = cursor.fetchone()
            
            # Update Subscription Status if needed (Simulated logic)
            # If we had a SubscriptionId, we might update its 'NextInvoiceDate' or 'Status'
            
            return PaymentResponse(
                id=row.Id,
                client_id=payment_data.client_id,
                amount=payment_data.amount,
                payment_method=payment_data.payment_method,
                transaction_id=payment_data.transaction_id,
                payment_date=payment_data.payment_date,
                notes=payment_data.notes,
                created_at=row.CreatedAt,
                created_by=created_by
            )

    @staticmethod
    def get_client_payments(client_id: int) -> List[PaymentResponse]:
        """Get payment history for a client"""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT Id, ClientId, Amount, PaymentMethod, TransactionId, PaymentDate, Notes, CreatedAt, CreatedBy
                FROM Payments
                WHERE ClientId = ?
                ORDER BY PaymentDate DESC
            """, (client_id,))
            
            rows = cursor.fetchall()
            return [
                PaymentResponse(
                    id=row.Id,
                    client_id=row.ClientId,
                    amount=row.Amount,
                    payment_method=row.PaymentMethod,
                    transaction_id=row.TransactionId,
                    payment_date=row.PaymentDate,
                    notes=row.Notes,
                    created_at=row.CreatedAt,
                    created_by=row.CreatedBy
                ) for row in rows
            ]
