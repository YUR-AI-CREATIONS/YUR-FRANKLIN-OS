"""
FRANKLIN OS - Stripe Payment Integration
Handles user authentication via Stripe checkout and payment processing
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime, timezone
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Import Stripe checkout from emergentintegrations
# from emergentintegrations.payments.stripe.checkout import (
#     StripeCheckout,
#     CheckoutSessionResponse,
#     CheckoutStatusResponse,
#     CheckoutSessionRequest
# )

# Simple Stripe implementation
import stripe
from pydantic import BaseModel
from typing import Optional

class CheckoutSessionRequest(BaseModel):
    amount: int  # Amount in cents (e.g. 999 = $9.99)
    currency: str = "usd"
    product_name: str
    success_url: str
    cancel_url: str
    metadata: Optional[Dict[str, str]] = None

class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str

class CheckoutStatusResponse(BaseModel):
    status: str
    payment_status: str
    amount_total: int
    currency: str
    metadata: Optional[Dict] = None

class WebhookResponse(BaseModel):
    event_id: str
    event_type: str
    session_id: Optional[str] = None
    payment_status: Optional[str] = None

class StripeCheckout:
    def __init__(self, api_key: str, webhook_url: Optional[str] = None, webhook_secret: Optional[str] = None):
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret or os.environ.get("STRIPE_WEBHOOK_SECRET")

    async def create_checkout_session(self, request: CheckoutSessionRequest) -> CheckoutSessionResponse:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': request.currency,
                    'product_data': {
                        'name': request.product_name,
                    },
                    'unit_amount': request.amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata=request.metadata or {},
        )
        return CheckoutSessionResponse(session_id=session.id, url=session.url)

    async def get_checkout_status(self, session_id: str) -> CheckoutStatusResponse:
        session = stripe.checkout.Session.retrieve(session_id)
        return CheckoutStatusResponse(
            status=session.status or "unknown",
            payment_status=session.payment_status or "unknown",
            amount_total=session.amount_total or 0,
            currency=session.currency or "usd",
            metadata=dict(session.metadata) if session.metadata else None
        )

    async def handle_webhook(self, payload: bytes, signature: str) -> WebhookResponse:
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f"Invalid webhook signature: {e}")

        session_id = None
        payment_status = None
        if event.type in (
            'checkout.session.completed',
            'checkout.session.async_payment_succeeded',
            'checkout.session.async_payment_failed',
        ):
            obj = event.data.object
            session_id = obj.id
            payment_status = obj.payment_status

        return WebhookResponse(
            event_id=event.id,
            event_type=event.type,
            session_id=session_id,
            payment_status=payment_status,
        )

# Create router
payment_router = APIRouter(prefix="/api/payments", tags=["payments"])
webhook_router = APIRouter(prefix="/api/webhook", tags=["webhooks"])

# MongoDB setup
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]
payment_transactions = db.payment_transactions
users = db.users

# Stripe API Key
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Subscription packages - FIXED on backend (security)
PACKAGES = {
    "free": {"amount": 0.0, "name": "Free Tier", "features": ["Basic access", "1 project", "Community support"]},
    "starter": {"amount": 9.99, "name": "Starter", "features": ["Full IDE access", "5 projects", "Email support", "1M context window"]},
    "pro": {"amount": 29.99, "name": "Professional", "features": ["Unlimited projects", "Priority support", "Team collaboration", "Advanced agents"]},
    "enterprise": {"amount": 99.99, "name": "Enterprise", "features": ["Custom deployment", "Dedicated support", "SLA guarantee", "White-label options"]}
}

# Request/Response Models
class CreateCheckoutRequest(BaseModel):
    package_id: str = Field(..., description="Package identifier: free, starter, pro, enterprise")
    origin_url: str = Field(..., description="Frontend origin URL for redirects")
    user_email: Optional[str] = Field(None, description="User email for the subscription")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")

class CheckoutResponse(BaseModel):
    url: str
    session_id: str
    package: str
    amount: float

class PaymentStatusResponse(BaseModel):
    status: str
    payment_status: str
    package: str
    amount: float
    user_email: Optional[str] = None

class UserSubscription(BaseModel):
    email: str
    package_id: str
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None

# ============================================================================
# CHECKOUT ENDPOINTS
# ============================================================================

@payment_router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(request: CreateCheckoutRequest, http_request: Request):
    """Create a Stripe checkout session for subscription"""
    
    # Validate package
    if request.package_id not in PACKAGES:
        raise HTTPException(status_code=400, detail=f"Invalid package: {request.package_id}")
    
    package = PACKAGES[request.package_id]
    
    # Free tier doesn't need payment
    if request.package_id == "free":
        # Create user directly
        if request.user_email:
            await users.update_one(
                {"email": request.user_email},
                {"$set": {
                    "email": request.user_email,
                    "package_id": "free",
                    "status": "active",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }},
                upsert=True
            )
        return CheckoutResponse(
            url=f"{request.origin_url}/dashboard?subscription=free",
            session_id="free_tier_no_payment",
            package="free",
            amount=0.0
        )
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    # Build URLs from frontend origin
    success_url = f"{request.origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{request.origin_url}/payment/cancel"

    # Initialize Stripe
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)

    # Create metadata (Stripe metadata values must be strings)
    checkout_metadata = {
        "package_id": request.package_id,
        "package_name": package["name"],
        "source": "franklin_os"
    }
    if request.user_email:
        checkout_metadata["user_email"] = request.user_email
    if request.metadata:
        checkout_metadata.update(request.metadata)

    # Create checkout session (amount converted to cents)
    checkout_request = CheckoutSessionRequest(
        amount=int(package["amount"] * 100),
        currency="usd",
        product_name=package["name"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=checkout_metadata
    )
    
    try:
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # MANDATORY: Create payment transaction record BEFORE redirect
        await payment_transactions.insert_one({
            "session_id": session.session_id,
            "package_id": request.package_id,
            "package_name": package["name"],
            "amount": package["amount"],
            "currency": "usd",
            "user_email": request.user_email,
            "metadata": checkout_metadata,
            "payment_status": "initiated",
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })
        
        return CheckoutResponse(
            url=session.url,
            session_id=session.session_id,
            package=request.package_id,
            amount=package["amount"]
        )
        
    except Exception as e:
        logging.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")


@payment_router.get("/status/{session_id}", response_model=PaymentStatusResponse)
async def get_payment_status(session_id: str, http_request: Request):
    """Get payment status and update database"""
    
    if session_id == "free_tier_no_payment":
        return PaymentStatusResponse(
            status="complete",
            payment_status="free",
            package="free",
            amount=0.0
        )
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    # Check if already processed
    existing = await payment_transactions.find_one({"session_id": session_id})
    if existing and existing.get("payment_status") == "paid":
        return PaymentStatusResponse(
            status=existing.get("status", "complete"),
            payment_status="paid",
            package=existing.get("package_id", "unknown"),
            amount=existing.get("amount", 0),
            user_email=existing.get("user_email")
        )

    # Initialize Stripe and check status
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)
    
    try:
        status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction record
        update_data = {
            "status": status.status,
            "payment_status": status.payment_status,
            "updated_at": datetime.now(timezone.utc)
        }
        
        await payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        # If payment successful, create/update user
        if status.payment_status == "paid" and existing:
            user_email = existing.get("user_email") or (status.metadata or {}).get("user_email")
            if user_email:
                await users.update_one(
                    {"email": user_email},
                    {"$set": {
                        "email": user_email,
                        "package_id": existing.get("package_id"),
                        "status": "active",
                        "stripe_session_id": session_id,
                        "subscribed_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }},
                    upsert=True
                )
        
        return PaymentStatusResponse(
            status=status.status,
            payment_status=status.payment_status,
            package=existing.get("package_id", "unknown") if existing else "unknown",
            amount=status.amount_total / 100,
            user_email=existing.get("user_email") if existing else None
        )
        
    except Exception as e:
        logging.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@payment_router.get("/packages")
async def get_packages():
    """Get available subscription packages"""
    return {"packages": PACKAGES}


@payment_router.get("/user/{email}")
async def get_user_subscription(email: str):
    """Get user subscription details"""
    user = await users.find_one({"email": email})
    if not user:
        return {"subscribed": False, "package_id": None}
    
    return {
        "subscribed": True,
        "package_id": user.get("package_id"),
        "status": user.get("status"),
        "subscribed_at": user.get("subscribed_at")
    }


# ============================================================================
# WEBHOOK ENDPOINT
# ============================================================================

@webhook_router.post("/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")

    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)

    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update payment transaction
        if webhook_response.session_id:
            await payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {
                    "webhook_event_type": webhook_response.event_type,
                    "webhook_event_id": webhook_response.event_id,
                    "payment_status": webhook_response.payment_status,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
        
        return {"status": "received", "event_id": webhook_response.event_id}
        
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
