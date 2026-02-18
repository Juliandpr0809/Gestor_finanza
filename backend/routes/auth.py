"""
Rutas de autenticación con JWT
"""
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

    token = generate_access_token(user.id, user.email)

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

        # Buscar usuario por username o email
        user = User.query.filter(or_(User.username == identifier, User.email == identifier)).first()
        
        if not user:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        if not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        token = generate_access_token(user.id, user.email)

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
