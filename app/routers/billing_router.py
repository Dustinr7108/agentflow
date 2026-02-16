"""Billing router - Stripe subscriptions and usage tracking."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models import User, UsageRecord
from app.schemas import UsageStats
from app.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/usage", response_model=UsageStats)
def get_usage(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current month's usage stats."""
    totals = (
        db.query(
            func.coalesce(func.sum(UsageRecord.tokens_used), 0).label("tokens"),
            func.coalesce(func.sum(UsageRecord.cost_usd), 0).label("cost"),
        )
        .filter(UsageRecord.user_id == user.id)
        .first()
    )

    limits = {
        "free": 10,
        "starter": settings.STARTER_RUNS,
        "pro": settings.PRO_RUNS,
        "enterprise": settings.ENTERPRISE_RUNS,
    }

    return UsageStats(
        runs_this_month=user.runs_this_month,
        total_tokens=totals.tokens,
        total_cost_usd=round(float(totals.cost), 4),
        plan=user.plan,
        runs_limit=limits.get(user.plan, 10),
    )


@router.post("/checkout")
def create_checkout(plan: str, user: User = Depends(get_current_user)):
    """Create a Stripe Checkout session for upgrading."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    price_map = {
        "starter": settings.STRIPE_PRICE_STARTER,
        "pro": settings.STRIPE_PRICE_PRO,
        "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
    }

    price_id = price_map.get(plan)
    if not price_id:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")

    session = stripe.checkout.Session.create(
        customer_email=user.email,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"https://awesomeai.life/billing?success=true",
        cancel_url=f"https://awesomeai.life/billing?canceled=true",
        metadata={"user_id": user.id, "plan": plan},
    )

    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        plan = session.get("metadata", {}).get("plan")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")

        if user_id and plan:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.plan = plan
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        user = db.query(User).filter(User.stripe_subscription_id == subscription["id"]).first()
        if user:
            user.plan = "free"
            user.stripe_subscription_id = None
            db.commit()

    return {"status": "ok"}
