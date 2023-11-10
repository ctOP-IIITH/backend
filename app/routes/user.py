"""
This module defines the user routes for the FastAPI application.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, RequestDetails, ChangePassword
from app.schemas.token import TokenSchema
from app.models.user import User
from app.models.token_table import TokenTable
from app.database import get_session
from app.auth.auth import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_hashed_password,
)
from app.auth.auth_bearer import JWTBearer

router = APIRouter()


@router.post("/register")
def register_user(user: UserCreate, session: Session = Depends(get_session)):
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
    existing_user = session.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password = get_hashed_password(user.password)

    new_user = User(
        username=user.username, email=user.email, password=encrypted_password
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
    }


@router.get("/getusers")
def getusers(session: Session = Depends(get_session), _: str = Depends(JWTBearer())):
    """
    Returns a list of all users.

    Args:
        session (Session, optional): The database session. Defaults to Depends(get_session()).
        _ (str, optional): The JWT token. Defaults to Depends(JWTBearer()).

    Returns:
        list: A list of all users.
    """
    user = session.query(User).all()
    return user


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

    return {"message": "Password changed successfully"}
