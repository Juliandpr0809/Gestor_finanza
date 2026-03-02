"""
Utilidades para recuperación de contraseña
"""
import secrets
from datetime import datetime, timedelta
from models import PasswordResetToken, db, User

def generate_reset_token(user_id: int) -> str:
    """Genera un token único para reset de contraseña"""
    # Limpiar tokens expirados del usuario
    PasswordResetToken.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    # Generar token seguro (32 bytes = 256 bits)
    token = secrets.token_urlsafe(32)
    
    # Crear registro de reset
    reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    db.session.add(reset_token)
    db.session.commit()
    
    return token

def validate_reset_token(token: str) -> dict:
    """Valida un token de reset de contraseña"""
    reset_record = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_record:
        return {'valid': False, 'error': 'Token inválido'}
    
    if not reset_record.is_valid():
        return {'valid': False, 'error': 'Token expirado o ya fue utilizado'}
    
    user = User.query.get(reset_record.user_id)
    if not user:
        return {'valid': False, 'error': 'Usuario no encontrado'}
    
    return {
        'valid': True,
        'user_id': user.id,
        'email': user.email,
        'token': token
    }

def mark_reset_as_used(token: str):
    """Marca un token de reset como utilizado"""
    reset_record = PasswordResetToken.query.filter_by(token=token).first()
    if reset_record:
        reset_record.used_at = datetime.utcnow()
        db.session.commit()

def send_reset_email(user_email: str, token: str, reset_link: str):
    """
    Envía email de recuperación de contraseña
    En desarrollo, solo imprime el link
    En producción, usa un servicio de email como SendGrid o AWS SES
    """
    # Link para cambiar contraseña
    reset_url = f"{reset_link}?token={token}"
    
    print(f"\n{'='*60}")
    print(f"📧 EMAIL DE RECUPERACIÓN DE CONTRASEÑA")
    print(f"{'='*60}")
    print(f"Para: {user_email}")
    print(f"\nLink de reset (válido por 24 horas):")
    print(f"{reset_url}")
    print(f"\nO copia este token:")
    print(f"{token}")
    print(f"{'='*60}\n")
    
    # TODO: Implementar envío real de email
    # from flask_mail import Mail, Message
    # mail = Mail()
    # msg = Message(
    #     subject='Recupera tu contraseña - OrdenC',
    #     recipients=[user_email],
    #     html=f'''
    #         <p>Hemos recibido una solicitud para recuperar tu contraseña.</p>
    #         <p>Haz clic en el siguiente link para cambiarla:</p>
    #         <a href="{reset_url}">Cambiar contraseña</a>
    #         <p>Este link expira en 24 horas.</p>
    #     '''
    # )
    # mail.send(msg)
