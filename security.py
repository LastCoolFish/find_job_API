import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from decouple import config
from passlib.context import CryptContext

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=60, cast=int)
REFRESH_TOKEN_EXPIRE_DAYS = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)
REFRESH_TOKEN_LIFETIME = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

BCRYPT_MAX_BYTES = 72

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def ensure_fits_bcrypt(password: str) -> None:
    """
    bcrypt only uses the first 72 bytes of a password and silently ignores the rest,
    so anything longer is rejected instead of being truncated. Multi-byte characters
    count per byte.

    :param password: the plain-text password
    :return: None
    :raises ValueError: if the password is longer than 72 bytes in UTF-8
    """
    if len(password.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError(f"password must be at most {BCRYPT_MAX_BYTES} bytes in UTF-8")


async def hash_password(password: str) -> str:
    """
    Hashes a password with bcrypt. Hashing is CPU-bound, so it runs in a worker
    thread instead of blocking the event loop.

    :param password: the plain-text password
    :return: the bcrypt hash (salt and cost included)
    """
    return await asyncio.to_thread(pwd_context.hash, password)


async def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    """
    Checks a password against a stored hash, off the event loop. \n
    Never raises on a bad hash: a missing hash (`None`, e.g. unknown user) or a value that
    is not a bcrypt hash (e.g. the `'!'` marker of a locked account) simply doesn't match.
    In those cases a dummy verification still runs, so response time doesn't reveal
    whether the account exists.

    :param plain_password: the plain-text password to check
    :param hashed_password: the stored hash, or None
    :return: True if the password matches the hash
    """
    if hashed_password is not None:
        try:
            return await asyncio.to_thread(pwd_context.verify, plain_password, hashed_password)
        except ValueError:  # includes passlib's UnknownHashError
            pass
    await asyncio.to_thread(pwd_context.dummy_verify)
    return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Creates a signed JWT access token.

    :param subject: who the token is for (the user id, as a string - JWT requires `sub` to be a string)
    :param expires_delta: custom lifetime; defaults to ACCESS_TOKEN_EXPIRE_MINUTES
    :return: the encoded token
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({"sub": subject, "iat": now, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Verifies a token's signature and expiry and returns its payload.

    :param token: the encoded JWT
    :return: the payload (always has `sub` and `exp`), or None if the token is invalid,
        expired, tampered with or missing required claims
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "sub"]})
    except jwt.InvalidTokenError:
        return None


def create_refresh_token() -> str:
    """
    Creates an opaque refresh token: random, URL-safe, not a JWT. It carries no data -
    its meaning lives only in the database row its hash points to.

    :return: a new random token (64 characters)
    """
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """
    Hashes a refresh token for storage and lookup. SHA-256 is enough here (unlike for
    passwords): the token is long and random, so it can't be guessed or brute-forced.

    :param token: the plain refresh token
    :return: its SHA-256 hex digest (64 characters)
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
