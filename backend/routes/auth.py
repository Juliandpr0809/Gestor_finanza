"""
Rutas de autenticación con JWT
"""
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError

from models import db, User, Category
from utils.jwt_utils import generate_access_token, get_user_id_from_header, AuthError
from schemas import UserRegisterSchema, UserLoginSchema
from utils.validators import validate_and_sanitize

auth_bp = Blueprint('auth', __name__)


@auth_bp.errorhandler(AuthError)
def handle_auth_error(err):
    """Convertir errores de JWT en respuestas JSON"""
    return jsonify({'error': str(err)}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar nuevo usuario y devolver JWT"""
    # Validar y sanitizar datos de entrada
    try:
        schema = UserRegisterSchema()
        validated_data = validate_and_sanitize(schema, request.get_json() or {})
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400

    email = validated_data['email'].lower()
    password = validated_data['password']
    username = validated_data.get('username', email.split('@')[0])

    # Verificar si el usuario ya existe
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Usuario ya existe'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email ya registrado'}), 409

    # Crear nuevo usuario
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(user)
    db.session.commit()

    # Inicializar categorías predefinidas
    from models import DEFAULT_CATEGORIES
    for cat_type, categories in DEFAULT_CATEGORIES.items():
        for cat in categories:
            category = Category(
                user_id=user.id,
                name=cat['name'],
                category_type=cat_type,
                icon=cat['icon'],
                color=cat['color'],
                is_default=True
            )
            db.session.add(category)

    db.session.commit()

    # Generar token - al registrarse, mantener sesión 30 días por defecto
    token = generate_access_token(user.id, user.email, remember_me=True)

    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'access_token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Iniciar sesión y devolver JWT"""
    try:
        # Validar y sanitizar datos de entrada
        try:
            schema = UserLoginSchema()
            validated_data = validate_and_sanitize(schema, request.get_json() or {})
        except ValidationError as err:
            return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
        
        identifier = validated_data['identifier'].lower().strip()
        password = validated_data['password']
        remember_me = validated_data.get('remember_me', False)

        # Buscar usuario por username o email
        user = User.query.filter(or_(User.username == identifier, User.email == identifier)).first()
        
        if not user:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        if not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        # Generar token con duración extendida si "Remember me" está activado
        token = generate_access_token(user.id, user.email, remember_me=remember_me)

        return jsonify({
            'message': 'Sesión iniciada',
            'access_token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Cerrar sesión (cliente debe eliminar el token)"""
    return jsonify({'message': 'Sesión cerrada. Elimine el token en el cliente.'}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Solicitar recuperación de contraseña"""
    try:
        from utils.password_reset import generate_reset_token, send_reset_email
        
        data = request.get_json() or {}
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'error': 'Email es requerido'}), 400
        
        # Buscar usuario por email
        user = User.query.filter_by(email=email).first()
        
        # Por seguridad, siempre responder "ok" aunque no exista el usuario
        # para evitar revelar qué emails están registrados
        if not user:
            return jsonify({
                'message': 'Si el email existe en nuestro sistema, recibirás instrucciones para cambiar tu contraseña'
            }), 200
        
        # Generar token de reset
        token = generate_reset_token(user.id)
        
        # Enviar email (en desarrollo muestra el token en consola)
        base_url = request.host_url.rstrip('/')
        reset_link = f"{base_url}/html/reset-password.html?token={token}"
        send_reset_email(user.email, token, reset_link)
        
        return jsonify({
            'message': 'Si el email existe en nuestro sistema, recibirás instrucciones para cambiar tu contraseña',
            'token': token  # En desarrollo, devolvemos el token para pruebas
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error procesando solicitud'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Cambiar contraseña con token de recuperación"""
    try:
        from utils.password_reset import validate_reset_token, mark_reset_as_used
        from werkzeug.security import generate_password_hash
        
        data = request.get_json() or {}
        token = data.get('token', '').strip()
        new_password = data.get('password', '').strip()
        
        if not token or not new_password:
            return jsonify({'error': 'Token y contraseña son requeridos'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        # Validar token
        validation = validate_reset_token(token)
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 400
        
        user_id = validation['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Cambiar contraseña
        user.password_hash = generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Marcar token como usado
        mark_reset_as_used(token)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Contraseña cambiada exitosamente'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Reset password error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error al cambiar contraseña'}), 500


@auth_bp.route('/validate-reset-token', methods=['POST'])
def validate_reset_token_endpoint():
    """Valida si un token de reset es válido"""
    try:
        from utils.password_reset import validate_reset_token
        
        data = request.get_json() or {}
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'valid': False, 'error': 'Token requerido'}), 400
        
        validation = validate_reset_token(token)
        
        return jsonify(validation), 200 if validation['valid'] else 400
        
    except Exception as e:
        current_app.logger.error(f"Token validation error: {str(e)}", exc_info=True)
        return jsonify({'valid': False, 'error': 'Error validando token'}), 500


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Obtener usuario actual desde el JWT"""
    user_id = get_user_id_from_header()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'preferred_currency': user.preferred_currency,
        'chat_initialized': user.chat_initialized
    }), 200
