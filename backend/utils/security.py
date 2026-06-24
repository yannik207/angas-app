# security.py
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt

# WARNING: In production, NEVER hardcode this.
# Read it from an environment variable (e.g., os.getenv("SECRET_KEY"))
SECRET_KEY = "your-super-secret-long-cryptographic-string"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setup the password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the plain password matches the hashed one in the database."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Creates a securely signed JWT."""
    to_encode = data.copy()

    # Set the expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
