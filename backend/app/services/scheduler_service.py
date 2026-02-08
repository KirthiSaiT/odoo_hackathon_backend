"""
Scheduler Service
Handles background tasks and scheduled jobs (e.g., overdue payment reminders)
"""
import asyncio
import logging
from datetime import datetime, timedelta
from app.services.email_service import EmailService
from app.core.database import get_db_cursor

logger = logging.getLogger(__name__)

class SchedulerService:
    _is_running = False
    
    @classmethod
    async def start_scheduler(cls):
        """Start the background scheduler"""
        if cls._is_running:
            return
            
        cls._is_running = True
        logger.info("🕒 Scheduler Service Started")
        
        # Run immediately on startup (for demo purposes) or wait
        asyncio.create_task(cls._run_daily_checks())

    @classmethod
    async def _run_daily_checks(cls):
        """Loop to run daily checks"""
        while cls._is_running:
            try:
                logger.info("Running daily background checks...")
                await cls.check_overdue_payments()
                
                # Wait for 24 hours (or less for testing, say 1 hour)
                # For hackathon/demo, maybe every 10 minutes?
                # Let's set it to check every hour.
                await asyncio.sleep(3600) 
                
            except Exception as e:
                logger.error(f"❌ Error in scheduler: {str(e)}")
                await asyncio.sleep(60) # Wait a bit on error

    @staticmethod
    async def check_overdue_payments():
        """
        Check for overdue subscriptions and send email reminders
        """
        logger.info("Checking for overdue payments...")
        
        # Mock logic as we don't have full Subscription model details or data
        # Real query would be:
        # SELECT s.Id, s.NextInvoiceDate, s.TotalPrice, c.Email, c.ClientName
        # FROM Subscriptions s
        # JOIN Clients c ON s.ClientId = c.Id
        # WHERE s.Status = 'Pending' AND s.NextInvoiceDate < GETDATE()
        
        try:
            with get_db_cursor() as cursor:
                # Assuming simple query based on Clients table "SubscriptionStatus"
                # This is a placeholder as actual Subscription table linkage might vary
                # We'll use Clients table directly if it has enough info or join
                
                # Let's assume we send to Clients with 'Pending' status created > 30 days ago
                query = """
                    SELECT Id, ClientName, Email, SubscriptionStatus, CreatedAt
                    FROM Clients
                    WHERE SubscriptionStatus = 'Pending'
                      AND CreatedAt < DATEADD(day, -30, GETDATE())
                """
                cursor.execute(query)
                overdue_clients = cursor.fetchall()
                
                for client in overdue_clients:
                    # Send Email
                    EmailService.send_overdue_reminder(
                        to_email=client.Email,
                        client_name=client.ClientName,
                        amount=0.0, # Placeholder
                        due_date=client.CreatedAt # Placeholder
                    )
                    logger.info(f"📧 Sent overdue reminder to {client.Email}")
                    
        except Exception as e:
            logger.error(f"Failed to check overdue payments: {str(e)}")
