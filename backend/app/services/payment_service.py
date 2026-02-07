import stripe
import logging
from app.core.config import get_settings
from app.core.database import get_db_cursor
from app.models.payment_models import PaymentCreate, PaymentResponse

logger = logging.getLogger(__name__)
settings = get_settings()

try:
    stripe.api_key = settings.STRIPE_SECRET_KEY
except:
    logger.warning("Stripe API key not found in settings")

class PaymentService:
    @staticmethod
    def create_payment_intent(data: PaymentCreate, user_id: str) -> PaymentResponse:
        try:
            # 1. Create Stripe Payment Intent
            if not stripe.api_key:
                stripe.api_key = settings.STRIPE_SECRET_KEY
            
            if not stripe.api_key:
                logger.error("Stripe API Key is missing!")
                raise ValueError("Stripe API Key is not configured.")

            logger.info(f"Using Stripe Key: {stripe.api_key[:4]}...{stripe.api_key[-4:] if stripe.api_key else ''}")

            intent = stripe.PaymentIntent.create(
                amount=int(data.amount * 100),  # Convert to cents
                currency=data.currency.lower(),
                metadata={
                    "user_id": user_id,
                    "order_id": str(data.order_id) if data.order_id else "",
                    **(data.metadata or {})
                },
                automatic_payment_methods={"enabled": True},
            )

            # 2. Record in Database
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Payments (
                        UserId, OrderId, StripePaymentIntentId, Amount, Currency, Status
                    )
                    OUTPUT INSERTED.Id
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    data.order_id,
                    intent.id,
                    data.amount,
                    data.currency,
                    "Pending"  # Initial status for intent
                ))
            
            return PaymentResponse(
                client_secret=intent.client_secret,
                payment_intent_id=intent.id,
                amount=data.amount,
                currency=data.currency,
                status="Pending"
            )

        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            raise e

    @staticmethod
    def confirm_payment(payment_intent_id: str):
        """
        Verify payment status with Stripe and update DB
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            status_map = {
                "succeeded": "Succeeded",
                "processing": "Processing",
                "requires_payment_method": "Failed",
                "canceled": "Failed"
            }
            
            db_status = status_map.get(intent.status, "Pending")

            with get_db_cursor() as cursor:
                cursor.execute("""
                    UPDATE Payments 
                    SET Status = ?, ModifiedAt = GETDATE()
                    WHERE StripePaymentIntentId = ?
                """, (db_status, payment_intent_id))
                
            return db_status

        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            raise e
