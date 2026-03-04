"""
EJEMPLO DE INTEGRACIÓN EN CHAT.PY
Este archivo muestra cómo modificar el endpoint send_message
para usar la IA mejorada con function calling y confirmación visual
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import User, Transaction, Account, Category
from extensions import db
from services.ai_service_improved import ImprovedAIService

chat_bp = Blueprint('chat', __name__)

# Inicializar servicio de IA mejorado
improved_ai = ImprovedAIService()

@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """
    Endpoint principal del chat con IA mejorada
    Maneja function calling y confirmaciones visuales
    """
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Mensaje vacío'}), 400
    
    try:
        # Obtener historial de conversación (últimos 5 mensajes)
        conversation_history = get_recent_conversation(user.id, limit=5)
        
        # Procesar mensaje con IA mejorada (Strategy 1: Function Calling)
        ai_response = improved_ai.chat_with_function_calling(
            user_message=user_message,
            user_id=user.id,
            conversation_history=conversation_history
        )
        
        # Manejar respuesta según tipo
        if ai_response['type'] == 'function_call':
            return handle_function_call(ai_response, user)
        
        elif ai_response['type'] == 'text':
            # Respuesta conversacional normal
            save_message(user.id, user_message, ai_response['message'])
            return jsonify({
                'response': ai_response['message'],
                'type': 'text'
            })
        
        else:
            return jsonify({'error': 'Tipo de respuesta desconocido'}), 500
            
    except Exception as e:
        print(f"Error en send_message: {str(e)}")
        return jsonify({
            'error': 'Lo siento, ocurrió un error procesando tu mensaje.',
            'details': str(e)
        }), 500


def handle_function_call(ai_response, user):
    """
    Maneja las llamadas a funciones detectadas por la IA
    """
    function_name = ai_response['function']
    arguments = ai_response['arguments']
    requires_confirmation = ai_response.get('requires_confirmation', False)
    response_text = ai_response.get('response_text', '')
    
    # Guardar mensaje del usuario y respuesta de IA
    save_message(user.id, arguments.get('original_message', ''), response_text)
    
    # FUNCIÓN: create_transaction
    if function_name == 'create_transaction':
        
        if requires_confirmation:
            # Preparar datos para confirmación visual
            tx_data = prepare_transaction_data(arguments, user.id)
            
            return jsonify({
                'response': response_text,
                'type': 'confirmation_required',
                'requires_confirmation': True,
                'transaction_data': tx_data,
                'function': 'create_transaction'
            })
        
        else:
            # Crear transacción directamente (sin confirmación)
            try:
                transaction = create_transaction_from_ai(arguments, user.id)
                return jsonify({
                    'response': f"✅ {response_text}\n\nTransacción registrada exitosamente.",
                    'type': 'success',
                    'transaction_id': transaction.id
                })
            except ValueError as e:
                return jsonify({
                    'response': f"❌ Error: {str(e)}",
                    'type': 'error'
                }), 400
    
    # FUNCIÓN: get_financial_summary
    elif function_name == 'get_financial_summary':
        summary = generate_financial_summary(arguments, user.id)
        return jsonify({
            'response': response_text,
            'type': 'summary',
            'data': summary
        })
    
    # FUNCIÓN: create_account
    elif function_name == 'create_account':
        if requires_confirmation:
            return jsonify({
                'response': response_text,
                'type': 'confirmation_required',
                'requires_confirmation': True,
                'account_data': arguments,
                'function': 'create_account'
            })
        else:
            try:
                account = create_account_from_ai(arguments, user.id)
                return jsonify({
                    'response': f"✅ Cuenta '{account.name}' creada exitosamente.",
                    'type': 'success',
                    'account_id': account.id
                })
            except Exception as e:
                return jsonify({
                    'response': f"❌ Error: {str(e)}",
                    'type': 'error'
                }), 400
    
    else:
        return jsonify({
            'error': f'Función desconocida: {function_name}'
        }), 400


@chat_bp.route('/confirm-transaction', methods=['POST'])
@jwt_required()
def confirm_transaction():
    """
    Endpoint para confirmar y guardar transacción desde UI de confirmación
    """
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    data = request.get_json()
    
    try:
        # Crear transacción
        transaction = create_transaction_from_confirmation(data, user.id)
        
        # Guardar mensaje de confirmación
        save_message(
            user.id,
            'confirmar',
            f"✅ Transacción de {transaction.transaction_type} por ${abs(transaction.amount):.2f} registrada."
        )
        
        return jsonify({
            'success': True,
            'transaction_id': transaction.id,
            'message': 'Transacción registrada exitosamente',
            'new_balance': transaction.account.balance
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@chat_bp.route('/confirm-account', methods=['POST'])
@jwt_required()
def confirm_account():
    """
    Endpoint para confirmar y crear cuenta desde UI de confirmación
    """
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    data = request.get_json()
    
    try:
        account = create_account_from_ai(data, user.id)
        
        return jsonify({
            'success': True,
            'account_id': account.id,
            'message': f"Cuenta '{account.name}' creada exitosamente"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# FUNCIONES HELPER
# ============================================================================

def prepare_transaction_data(arguments, user_id):
    """
    Prepara datos de transacción para el componente de confirmación visual
    """
    # Buscar cuenta
    account = find_account_fuzzy(arguments.get('account_name', ''), user_id)
    account_name = account.name if account else arguments.get('account_name', 'Sin cuenta')
    
    # Buscar categoría
    category = find_category_fuzzy(arguments.get('category', ''), user_id)
    category_name = category.name if category else arguments.get('category', 'Sin categoría')
    
    return {
        'amount': abs(arguments['amount']),
        'type': arguments['type'],
        'account': account_name,
        'account_id': account.id if account else None,
        'category': category_name,
        'category_id': category.id if category else None,
        'description': arguments.get('description', ''),
        'date': arguments.get('date', datetime.now().strftime('%d/%m/%Y'))
    }


def create_transaction_from_ai(arguments, user_id):
    """
    Crea transacción desde argumentos extraídos por la IA
    """
    # Validar campos requeridos
    if 'amount' not in arguments or 'type' not in arguments:
        raise ValueError("Faltan datos obligatorios: amount y type")
    
    # Buscar cuenta (fuzzy matching)
    account = find_account_fuzzy(arguments.get('account_name', ''), user_id)
    if not account:
        raise ValueError(f"No encontré la cuenta '{arguments.get('account_name')}'")
    
    # Buscar categoría (fuzzy matching)
    category = find_category_fuzzy(arguments.get('category', ''), user_id)
    
    # Crear transacción
    transaction = Transaction(
        user_id=user_id,
        account_id=account.id,
        category_id=category.id if category else None,
        amount=arguments['amount'],
        description=arguments.get('description', ''),
        transaction_type=arguments['type'],
        date=parse_date(arguments.get('date')) or datetime.now()
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return transaction


def create_transaction_from_confirmation(data, user_id):
    """
    Crea transacción desde datos confirmados por el usuario
    """
    # Validar cuenta
    if not data.get('account_id'):
        raise ValueError("Cuenta no especificada")
    
    account = Account.query.filter_by(
        id=data['account_id'],
        user_id=user_id
    ).first()
    
    if not account:
        raise ValueError("Cuenta no encontrada")
    
    # Crear transacción
    transaction = Transaction(
        user_id=user_id,
        account_id=account.id,
        category_id=data.get('category_id'),
        amount=data['amount'] if data['type'] == 'income' else -abs(data['amount']),
        description=data.get('description', ''),
        transaction_type=data['type'],
        date=parse_date(data.get('date')) or datetime.now()
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return transaction


def create_account_from_ai(arguments, user_id):
    """
    Crea cuenta desde argumentos de la IA
    """
    name = arguments.get('name', '').strip()
    if not name:
        raise ValueError("El nombre de la cuenta es obligatorio")
    
    # Verificar que no exista
    existing = Account.query.filter_by(
        user_id=user_id,
        name=name
    ).first()
    
    if existing:
        raise ValueError(f"Ya existe una cuenta con el nombre '{name}'")
    
    # Crear cuenta
    account = Account(
        user_id=user_id,
        name=name,
        account_type=arguments.get('type', 'other'),
        balance=arguments.get('initial_balance', 0.0),
        currency=arguments.get('currency', 'USD')
    )
    
    db.session.add(account)
    db.session.commit()
    
    return account


def find_account_fuzzy(account_name, user_id):
    """
    Busca cuenta usando fuzzy matching
    """
    if not account_name:
        # Devolver cuenta principal si existe
        return Account.query.filter_by(
            user_id=user_id,
            is_primary=True
        ).first()
    
    from rapidfuzz import fuzz, process
    
    # Obtener todas las cuentas del usuario
    accounts = Account.query.filter_by(user_id=user_id).all()
    if not accounts:
        return None
    
    # Fuzzy matching
    account_names = {acc.name: acc for acc in accounts}
    match = process.extractOne(
        account_name,
        account_names.keys(),
        scorer=fuzz.ratio,
        score_cutoff=70
    )
    
    if match:
        return account_names[match[0]]
    
    return None


def find_category_fuzzy(category_name, user_id):
    """
    Busca categoría usando fuzzy matching
    """
    if not category_name:
        return None
    
    from rapidfuzz import fuzz, process
    
    categories = Category.query.filter_by(user_id=user_id).all()
    if not categories:
        return None
    
    category_names = {cat.name: cat for cat in categories}
    match = process.extractOne(
        category_name,
        category_names.keys(),
        scorer=fuzz.ratio,
        score_cutoff=70
    )
    
    if match:
        return category_names[match[0]]
    
    return None


def generate_financial_summary(arguments, user_id):
    """
    Genera resumen financiero según parámetros
    """
    period = arguments.get('period', 'month')
    summary_type = arguments.get('type', 'overview')
    
    # Implementar lógica de resumen según necesidades
    # Este es un ejemplo básico
    
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Determinar rango de fechas
    if period == 'month':
        start_date = datetime.now().replace(day=1)
    elif period == 'week':
        start_date = datetime.now() - timedelta(days=7)
    else:
        start_date = datetime.now().replace(day=1)
    
    # Calcular totales
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date >= start_date
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expense = sum(abs(t.amount) for t in transactions if t.amount < 0)
    balance = total_income - total_expense
    
    return {
        'period': period,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'transaction_count': len(transactions)
    }


def get_recent_conversation(user_id, limit=5):
    """
    Obtiene últimos mensajes de conversación
    Retorna lista de {role: 'user'|'assistant', content: '...'}
    """
    # Implementar según tu modelo de ChatMessage
    # Ejemplo:
    from models import ChatMessage
    
    messages = ChatMessage.query.filter_by(
        user_id=user_id
    ).order_by(
        ChatMessage.created_at.desc()
    ).limit(limit * 2).all()
    
    conversation = []
    for msg in reversed(messages):
        conversation.append({
            'role': msg.role,  # 'user' o 'assistant'
            'content': msg.content
        })
    
    return conversation


def save_message(user_id, user_message, ai_response):
    """
    Guarda mensajes de la conversación en BD
    """
    from models import ChatMessage
    
    # Guardar mensaje del usuario
    user_msg = ChatMessage(
        user_id=user_id,
        role='user',
        content=user_message,
        created_at=datetime.now()
    )
    db.session.add(user_msg)
    
    # Guardar respuesta de la IA
    ai_msg = ChatMessage(
        user_id=user_id,
        role='assistant',
        content=ai_response,
        created_at=datetime.now()
    )
    db.session.add(ai_msg)
    
    db.session.commit()


def parse_date(date_string):
    """
    Parsea fecha desde string flexible
    """
    if not date_string:
        return None
    
    try:
        # Intentar formato DD/MM/YYYY
        return datetime.strptime(date_string, '%d/%m/%Y')
    except:
        try:
            # Intentar formato YYYY-MM-DD
            return datetime.strptime(date_string, '%Y-%m-%d')
        except:
            return None


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

"""
FLUJO COMPLETO:

1. Usuario envía: "gasté 50 dólares en el supermercado"
   
2. send_message() procesa con improved_ai.chat_with_function_calling()
   
3. IA devuelve:
   {
       'type': 'function_call',
       'function': 'create_transaction',
       'arguments': {
           'amount': -50,
           'type': 'expense',
           'account_name': 'cuenta principal',
           'category': 'alimentación',
           'description': 'supermercado'
       },
       'requires_confirmation': True,
       'response_text': '¿Quieres registrar un gasto de $50 en supermercado?'
   }
   
4. handle_function_call() retorna JSON con requires_confirmation=True

5. Frontend recibe respuesta y muestra TransactionConfirmationComponent

6. Usuario confirma con checkbox

7. Frontend llama a /confirm-transaction

8. confirm_transaction() crea la transacción en BD

9. Responde con success=True

10. Frontend muestra "✅ ¡Guardado!" y actualiza balances
"""
