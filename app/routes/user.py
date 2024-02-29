"""
This module defines the user routes for the FastAPI application.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request

from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, RequestDetails, ChangePassword
from app.schemas.token import TokenSchema, TokenRefresh
from app.models.user import User
from app.models.token_table import TokenTable
from app.database import get_session
from app.auth.auth import (
    decode_refresh_jwt,
    create_access_token,
    create_refresh_token,
    verify_password,
    get_hashed_password,
    token_required,
    admin_required,
)

router = APIRouter()


@router.post("/create-user")
@token_required
@admin_required
def register_user(
    user: UserCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Registers a new user.

    Args:
        user (UserCreate): The user details.
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Raises:
        HTTPException: If the email is already registered.

    Returns:
        dict: A dictionary containing a success message.
    """
    _, _ = current_user, request
    existing_user = session.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password = get_hashed_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=encrypted_password,
        user_type=user.user_type,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "user created successfully"}


@router.post("/login", response_model=TokenSchema)
def login(request: RequestDetails, db: Session = Depends(get_session)):
    """
    Authenticates a user and returns access and refresh tokens.

    Args:
        request (requestdetails): The request containing the user's email and password.
        db (Session, optional): The database session. Defaults to Depends(get_session()).

    Raises:
        HTTPException: If the email or password is incorrect.

    Returns:
        dict: A dictionary containing the access and refresh tokens.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email"
        )
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = TokenTable(
        user_id=user.id, access_token=access, refresh_token=refresh, status=True
    )
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }


@router.get("/profile")
@token_required
def profile(
    request: Request, session: Session = Depends(get_session), current_user=None
):
    """
    Returns the profile of the user.

    Args:
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Returns:
        dict: A dictionary containing the user's profile.
    """
    # use request to avoid pycharm warning
    _ = request
    user = session.query(User).filter(User.id == current_user.id).first()
    return {
        "username": user.username,
        "email": user.email,
        "user_type": user.user_type,
    }


@router.post("/token/refresh", response_model=TokenSchema)
def refresh_token(token: TokenRefresh, db: Session = Depends(get_session)):
    """
    Refreshes an access token using a refresh token.

    Args:
        token (TokenRefresh): The refresh token.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the refresh token is invalid.

    Returns:
        dict: A dictionary containing the new access token.
    """
    payload = decode_refresh_jwt(token.refresh_token)
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid refresh token.")

    access_token = create_access_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/getusers")
@token_required
def getusers(
    request: Request, session: Session = Depends(get_session), current_user=None
):
    """
    Returns a list of all users.

    Args:
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Returns:
        list: A list of all users.
    """
    # use request to avoid pycharm warning
    _ = request, current_user
    user = session.query(User).all()
    return user


@router.get("/am-i-admin")
@token_required
@admin_required
def am_i_admin(
    request: Request, session: Session = Depends(get_session), current_user=None
):
    """
    Checks if the user is an admin.

    Args:
        session (Session, optional): The database session. Defaults to Depends(get_session()).

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    _, _ = request, session

    # stringify dict
    return {"admin": True, "username": current_user.username}


@router.post("/change-password")
def change_password(request: ChangePassword, db: Session = Depends(get_session)):
    """
    Changes the password of the user with the given email address.

    Args:
        request (changepassword): The request containing the old and new passwords.
        db (Session, optional): The database session. Defaults to Depends(get_session()).

    Raises:
        HTTPException: If the user is not found or the old password is incorrect.

    Returns:
        dict: A dictionary containing a success message.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    if not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
        )

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()

    # TODO: Add to db, last password changed
    return {"message": "Password changed successfully"}
