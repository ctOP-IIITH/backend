"""
This module provides functions for decoding JWT tokens.
"""

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from jwt.exceptions import InvalidTokenError

from app.config.settings import ALGORITHM, JWT_SECRET_KEY


def decode_jwt(jwtoken: str) -> dict:
    """
    Decode and verify the JWT token.

    Args:
    - jwtoken (str): JWT token to decode.

    Returns:
    - dict: Decoded payload if the token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None


class JWTBearer(HTTPBearer):
    """
    JWTBearer is a subclass of HTTPBearer that verifies JWT tokens.
    """

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request):
        credentials = await super().__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        """
        Verify the JWT token.

        Args:
        - jwtoken (str): JWT token to verify.

        Returns:
        - bool: True if the token is valid, False otherwise.
        """
        is_token_valid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except InvalidTokenError:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid


jwt_bearer = JWTBearer()
