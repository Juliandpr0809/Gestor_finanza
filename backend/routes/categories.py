"""
Rutas para gestión de categorías
"""
from flask import Blueprint, request, jsonify
from models import db, Category
from utils.jwt_utils import get_user_id_from_header, AuthError
from services.groq_service import suggest_category_with_ai

categories_bp = Blueprint('categories', __name__)

def get_user_id():
    """Obtener ID del usuario actual desde JWT"""
    try:
        return get_user_id_from_header(), None
    except AuthError as err:
        return None, ({'error': str(err)}, 401)

@categories_bp.route('', methods=['GET'])
def get_categories():
    """Obtener todas las categorías del usuario"""
    user_id, error = get_user_id()
    if error:
        return error
    
    category_type = request.args.get('type')  # income o expense
    
    query = Category.query.filter_by(user_id=user_id, parent_id=None)
    
    if category_type:
        query = query.filter_by(category_type=category_type)
    
    categories = query.all()
    
    def serialize_category(cat):
        return {
            'id': cat.id,
            'name': cat.name,
            'type': cat.category_type,
            'icon': cat.icon,
            'color': cat.color,
            'is_default': cat.is_default,
            'subcategories': [serialize_category(sub) for sub in (cat.subcategories or [])]
        }
    
    return jsonify([serialize_category(cat) for cat in categories]), 200

@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Obtener detalle de una categoría"""
    user_id, error = get_user_id()
    if error:
        return error
    
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    return jsonify({
        'id': category.id,
        'name': category.name,
        'type': category.category_type,
        'icon': category.icon,
        'color': category.color,
        'is_default': category.is_default,
        'parent_id': category.parent_id
    }), 200

@categories_bp.route('', methods=['POST'])
def create_category():
    """Crear nueva categoría personalizada"""
    user_id, error = get_user_id()
    if error:
        return error
    
    data = request.get_json()
    
    # Validar que tenga nombre y tipo (puede venir como 'type' o 'category_type')
    if not data:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    name = data.get('name', '').strip()
    category_type = data.get('category_type') or data.get('type')
    icon = data.get('icon', '📁').strip()
    color = data.get('color', '#7cb342').strip()
    
    if not name or not category_type:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    category = Category(
        user_id=user_id,
        name=name,
        category_type=category_type,
        icon=icon,
        color=color,
        parent_id=data.get('parent_id')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'message': 'Categoría creada exitosamente',
        'category': {
            'id': category.id,
            'name': category.name,
            'type': category.category_type,
            'icon': category.icon
        }
    }), 201

@categories_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Actualizar categoría"""
    user_id, error = get_user_id()
    if error:
        return error
    
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    # No permitir editar categorías predefinidas
    if category.is_default:
        return jsonify({'error': 'No se pueden editar categorías predefinidas'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        category.name = data['name']
    if 'icon' in data:
        category.icon = data['icon']
    if 'color' in data:
        category.color = data['color']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Categoría actualizada',
        'category': {
            'id': category.id,
            'name': category.name,
            'icon': category.icon
        }
    }), 200

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Eliminar categoría"""
    user_id, error = get_user_id()
    if error:
        return error
    
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    # No permitir eliminar categorías predefinidas
    if category.is_default:
        return jsonify({'error': 'No se pueden eliminar categorías predefinidas'}), 403
    
    # Validar que no tenga transacciones
    from models import Transaction
    if Transaction.query.filter_by(category_id=category_id).first():
        return jsonify({'error': 'No se puede eliminar una categoría con transacciones'}), 409
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Categoría eliminada'}), 200
# Catálogo de categorías con keywords canónicos (manual y sugerencias rápidas)
CATEGORY_KB = {
    'Comida': {
        'type': 'expense',
        'keywords': ['almuerzo', 'cena', 'desayuno', 'mercado', 'supermercado', 'restaurante', 'comida', 'hamburguesa', 'pizza', 'sushi', 'tacos', 'carulla', 'exito', 'd1', 'ara', 'jumbo', 'cafe', 'café', 'cerveza', 'bar', 'papas', 'pan', 'postre', 'helado']
    },
    'Transporte': {
        'type': 'expense',
        'keywords': ['uber', 'taxi', 'cabify', 'didi', 'indriver', 'picap', 'bus', 'transmilenio', 'sitp', 'metro', 'gasolina', 'combustible', 'peaje', 'parqueadero', 'mantenimiento', 'aceite', 'llanta', 'taller', 'moto', 'carro', 'bici', 'bicicleta', 'recarga', 'tullave']
    },
    'Vivienda': {
        'type': 'expense',
        'keywords': ['arriendo', 'alquiler', 'administracion', 'administración', 'casa', 'apto', 'apartamento', 'mueble', 'reparacion', 'reparación', 'plomero', 'pintura', 'conjunto']
    },
    'Servicios': {
        'type': 'expense',
        'keywords': ['luz', 'agua', 'gas', 'internet', 'claro', 'movistar', 'tigo', 'etb', 'celular', 'plan', 'recarga', 'enel', 'acueducto', 'energia', 'energía', 'tv']
    },
    'Entretenimiento': {
        'type': 'expense',
        'keywords': ['cine', 'pelicula', 'película', 'netflix', 'spotify', 'youtube', 'hbo', 'disney', 'juego', 'videojuego', 'steam', 'playstation', 'xbox', 'fiesta', 'bolera', 'concierto', 'entrada', 'boleta', 'suscripcion', 'suscripción', 'teatro']
    },
    'Salud': {
        'type': 'expense',
        'keywords': ['medicamento', 'farmacia', 'cruz verde', 'drogueria', 'droguería', 'droga', 'cita', 'medico', 'médico', 'doctor', 'dentista', 'odontologo', 'examen', 'salud', 'eps', 'prepagada', 'gimnasio', 'gym']
    },
    'Educación': {
        'type': 'expense',
        'keywords': ['curso', 'semestre', 'universidad', 'colegio', 'matricula', 'matrícula', 'pension', 'pensión', 'libro', 'cuaderno', 'utiles', 'útiles', 'clase', 'taller', 'udemy', 'platzi', 'coursera', 'idiomas']
    },
    'Ropa': {
        'type': 'expense',
        'keywords': ['camisa', 'camiseta', 'pantalon', 'pantalón', 'jean', 'zapatos', 'tenis', 'zapatilla', 'ropa', 'vestido', 'chaqueta', 'buzo', 'adidas', 'nike', 'zara', 'h&m', 'koaj']
    },
    'Ingresos': {
        'type': 'income',
        'keywords': ['nomina', 'nómina', 'salario', 'sueldo', 'pago', 'transferencia', 'deposito', 'depósito', 'honorarios', 'venta', 'freelance', 'cliente', 'abono']
    },
    'Otros': {
        'type': 'income',
        'keywords': ['regalo', 'bono', 'dividendo', 'premio', 'propina', 'extra', 'venta', 'bicicleta', 'bici']
    }
}

# Alias de nombre para mapear categorías del usuario (incluye nombres antiguos)
CATEGORY_ALIASES = {
    'Comida': ['comida', 'alimentacion', 'alimentación'],
    'Transporte': ['transporte'],
    'Vivienda': ['vivienda', 'hogar'],
    'Servicios': ['servicios', 'servicio'],
    'Entretenimiento': ['entretenimiento', 'ocio'],
    'Salud': ['salud', 'medico', 'médico'],
    'Educación': ['educacion', 'educación'],
    'Ropa': ['ropa', 'vestimenta'],
    'Ingresos': ['ingresos', 'otros ingresos', 'salario', 'freelance'],
    'Otros': ['otros', 'otros gastos', 'otros ingresos']
}


def match_user_category(canonical_name, categories):
    """Encontrar la categoría del usuario que corresponda al nombre canónico."""
    aliases = CATEGORY_ALIASES.get(canonical_name, [canonical_name])
    aliases_lower = [a.lower() for a in aliases]
    for user_cat in categories:
        user_name = user_cat.name.lower()
        if any(alias in user_name or user_name in alias for alias in aliases_lower):
            return user_cat
    return None

@categories_bp.route('/suggest', methods=['POST'])
def suggest_category():
    """Sugerir categoría usando IA basada en descripción con fallback local"""
    user_id, error = get_user_id()
    if error:
        return error
    
    data = request.get_json()
    
    if not data or not data.get('description'):
        return jsonify({'error': 'Descripción requerida'}), 400
    
    description = data.get('description', '').strip().lower()
    transaction_type = data.get('type', 'expense')
    
    # Obtener categorías disponibles del usuario
    user_categories = Category.query.filter_by(user_id=user_id, category_type=transaction_type).all()
    
    # 1. INTENTO LOCAL: Buscar palabras clave con nombres canónicos
    canonical_match = None
    suggested_local = None

    for canonical, meta in CATEGORY_KB.items():
        if meta['type'] != transaction_type:
            continue
        if any(k in description for k in meta['keywords']):
            canonical_match = canonical
            suggested_local = match_user_category(canonical, user_categories)
            break

    if canonical_match:
        return jsonify({
            'category': canonical_match,
            'confidence': 0.95 if suggested_local else 0.7,
            'ai_suggested': False,
            'exists': suggested_local is not None,
            'category_id': suggested_local.id if suggested_local else None,
            'source': 'local_keywords'
        }), 200
        
    # 2. INTENTO IA: Si falló local, usar Groq
    available_cats_names = [c.name for c in user_categories]
    if not available_cats_names:
        available_cats_names = [c for c, meta in CATEGORY_KB.items() if meta['type'] == transaction_type]

    suggestion = suggest_category_with_ai(description, transaction_type, data.get('language', 'es'), available_categories=available_cats_names)
    
    if suggestion.get('category'):
        # Verificar si la categoría existe en el tipo actual
        existing = Category.query.filter_by(
            user_id=user_id,
            name=suggestion['category'],
            category_type=transaction_type
        ).first()

        if existing:
            return jsonify({
                'category': suggestion['category'],
                'confidence': suggestion.get('confidence', 0),
                'ai_suggested': True,
                'exists': True,
                'category_id': existing.id,
                'source': 'ai_groq'
            }), 200

        # Si no existe en el tipo actual, verificar si existe en el OTRO tipo
        # Esto ayuda cuando el usuario describe un Ingreso estando en la pestaña Gasto
        other_type = 'income' if transaction_type == 'expense' else 'expense'
        existing_other = Category.query.filter_by(
            user_id=user_id,
            name=suggestion['category'],
            category_type=other_type
        ).first()

        if existing_other:
            return jsonify({
                'category': suggestion['category'],
                'confidence': suggestion.get('confidence', 0),
                'ai_suggested': True,
                'exists': True,
                'category_id': existing_other.id,
                'source': 'ai_groq_cross_type',
                'suggested_type': other_type
            }), 200
        
        # Si no existe en ninguno, devolver para crear en el tipo actual
        return jsonify({
            'category': suggestion['category'],
            'confidence': suggestion.get('confidence', 0),
            'ai_suggested': True,
            'exists': False,
            'category_id': None,
            'source': 'ai_groq'
        }), 200
    
    return jsonify({
        'category': None,
        'confidence': 0,
        'ai_suggested': False
    }), 200