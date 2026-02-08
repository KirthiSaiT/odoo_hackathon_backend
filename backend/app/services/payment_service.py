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
            # Refresh settings to ensure we get the latest
            current_settings = get_settings()
            
            # Explicitly set the key before use
            stripe.api_key = current_settings.STRIPE_SECRET_KEY
            
            # Debug logging
            if stripe.api_key:
                masked_key = f"{stripe.api_key[:4]}...{stripe.api_key[-4:]}"
                logger.info(f"Using Stripe Key: {masked_key}")
            else:
                logger.error("Stripe API Key is MISSING in settings at runtime!")
                raise ValueError("Stripe API Key is not configured.")

            # 1. Create Stripe Payment Intent
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
                # Use default value for OrderId if None (assuming DB allows NULL or has default)
                # But looking at schema, OrderId is nullable.
                order_id_val = str(data.order_id) if data.order_id else None
                
                cursor.execute("""
                    INSERT INTO Payments (
                        UserId, OrderId, StripePaymentIntentId, Amount, Currency, Status, CreatedAt, ModifiedAt
                    )
                    OUTPUT INSERTED.Id
                    VALUES (?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
                """, (
                    user_id,
                    order_id_val,
                    intent.id,
                    data.amount,
                    data.currency,
                    "Pending"
                ))
            
            return PaymentResponse(
                client_secret=intent.client_secret,
                payment_intent_id=intent.id,
                amount=data.amount,
                currency=data.currency,
                status="Pending"
            )

        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe Authentication Error: {str(e)}")
            raise HTTPException(status_code=500, detail="Payment gateway authentication failed")
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
