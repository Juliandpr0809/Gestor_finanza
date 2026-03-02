"""JWT utility helpers"""
import jwt
from datetime import datetime, timedelta
from flask import current_app, request

class AuthError(Exception):
    """Custom auth error for JWT issues"""


def _get_secret_and_config(remember_me=False):
    app = current_app
    secret = app.config.get('JWT_SECRET_KEY') or app.config.get('SECRET_KEY')
    algorithm = app.config.get('JWT_ALGORITHM', 'HS256')
    
    # Usar expiración más larga si "Remember me" está activado
    if remember_me:
        expires_minutes = app.config.get('JWT_REMEMBER_TOKEN_EXPIRES_MIN', 30 * 24 * 60)
    else:
        expires_minutes = app.config.get('JWT_ACCESS_TOKEN_EXPIRES_MIN', 60 * 24)
    
    return secret, algorithm, expires_minutes


def generate_access_token(user_id: int, email: str, remember_me: bool = False) -> str:
    """Generate a signed JWT access token"""
    secret, algorithm, expires_minutes = _get_secret_and_config(remember_me)
    now = datetime.utcnow()
    payload = {
        'sub': user_id,
        'email': email,
        'iat': now,
        'exp': now + timedelta(minutes=expires_minutes),
        'remember_me': remember_me
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_access_token(token: str) -> dict:
    """Decode and validate JWT access token"""
    secret, algorithm, _ = _get_secret_and_config()
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise AuthError('Token expirado') from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError('Token inválido') from exc


def get_user_id_from_header():
    """Extract user_id from Authorization Bearer token"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthError('Falta header Authorization')

    token = auth_header.split(' ')[1]
    payload = decode_access_token(token)
    user_id = payload.get('sub')
    if not user_id:
        raise AuthError('Token sin usuario')
    return user_id
