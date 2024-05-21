from fastapi import Depends, APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from app.models import subscription
from app.schemas.subscribe import Subscription, SubscriptionDetails
from app.database import get_session
from app.auth.auth import (
    token_required,
)
from app.utils.om2m_lib import Om2m
from app.config.settings import OM2M_URL, MOBIUS_XM2MRI

router = APIRouter()

om2m = Om2m(MOBIUS_XM2MRI, OM2M_URL)


@router.post("/subscribe")
@token_required
def subscribe_to_node(
    request: Request,
    subscription_to_node: Subscription,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Subscribes to a node.

    Args:
        subscription :: The subscription details to subscribe
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Returns:
        dict: A dictionary containing a success message.
    """
    if current_user is None:
        return {"message": "Invalid token"}

    _ = request

    rn = "sub-" + str(current_user.id)
    no_of_subscriptions = len(
        session.query(subscription.Subscription)
        .filter(
            subscription.Subscription.user_id == current_user.id,
            subscription.Subscription.node_id == subscription_to_node.node_id,
        )
        .all()
    )
    rn += "-" + str(no_of_subscriptions)
    r = om2m.create_subscription(
        subscription_to_node.node_id + "/Data", rn, subscription_to_node.url
    )
    # return the message from response
    if r.status_code != 201:
        # return {"code": r.status_code, "message": r.text}
        raise HTTPException(status_code=r.status_code, detail=r.text)

    else:
        # save the subscription in the database
        new_subscription = subscription.Subscription(
            user_id=current_user.id,
            url=subscription_to_node.url,
            node_id=subscription_to_node.node_id,
            status="active",
        )
        session.add(new_subscription)
        session.commit()
        return {"message": "Subscribed to node"}


@router.post("/get-subscriptions")
@token_required
def get_subscriptions(
    request: Request,
    subscriptionDetails: SubscriptionDetails,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Get subscriptions of a node.

    Args:
        subscriptionDetails :: The subscription details to get
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Returns:
        dict: A dictionary containing the subscriptions.
    """
    if current_user is None:
        return {"message": "Invalid token"}

    # find all the subscriptions of the user from the user id and node id
    subscriptions = (
        session.query(subscription.Subscription)
        .filter(
            subscription.Subscription.user_id == current_user.id,
            subscription.Subscription.node_id == subscriptionDetails.node_id,
        )
        .all()
    )

    return subscriptions


@router.get("/get-user-subscriptions")
@token_required
def get_user_subscriptions(
    request: Request, session: Session = Depends(get_session), current_user=None
):
    """
    Get all the subscriptions of a user.

    Args:
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Returns:
        dict: A dictionary containing the subscriptions.
    """
    if current_user is None:
        return {"message": "Invalid token"}
    # find all the subscriptions of the user from the user id
    subscriptions = (
        session.query(subscription.Subscription)
        .filter(subscription.Subscription.user_id == current_user.id)
        .all()
    )

    return subscriptions
