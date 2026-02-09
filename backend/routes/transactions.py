"""
Rutas para gestión de transacciones
"""
from flask import Blueprint, request, jsonify
from models import db, Transaction, Account, Category
from datetime import datetime, timedelta
from utils.jwt_utils import get_user_id_from_header, AuthError

transactions_bp = Blueprint('transactions', __name__)

def get_user_id():
    """Obtener ID del usuario actual desde JWT"""
    try:
        return get_user_id_from_header(), None
    except AuthError as err:
        return None, ({'error': str(err)}, 401)

@transactions_bp.route('', methods=['GET'])
def get_transactions():
    """Obtener transacciones con filtros opcionales"""
    user_id, error = get_user_id()
    if error:
        return error
    
    # Parámetros de filtro
    account_id = request.args.get('account_id', type=int)
    category_id = request.args.get('category_id', type=int)
    transaction_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Transaction.query.filter_by(user_id=user_id)
    
    if account_id:
        query = query.filter_by(account_id=account_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.fromisoformat(end_date))
    
    transactions = query.order_by(Transaction.transaction_date.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'account_id': t.account_id,
            'account_name': t.account.name,
            'account_currency': t.account.currency,
            'category_id': t.category_id,
            'category_name': t.category.name,
            'category_icon': t.category.icon,
            'type': t.transaction_type,
            'amount': abs(t.amount),  # Siempre positivo
            'description': t.description,
            'date': t.transaction_date.isoformat(),
            'created_at': t.created_at.isoformat()
        } for t in transactions.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': transactions.total,
            'pages': transactions.pages
        }
    }), 200

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Obtener detalle de una transacción"""
    user_id, error = get_user_id()
    if error:
        return error
    
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transacción no encontrada'}), 404
    
    return jsonify({
        'id': transaction.id,
        'account_id': transaction.account_id,
        'category_id': transaction.category_id,
        'type': transaction.transaction_type,
        'amount': transaction.amount,
        'description': transaction.description,
        'notes': transaction.notes,
        'date': transaction.transaction_date.isoformat(),
        'created_at': transaction.created_at.isoformat()
    }), 200

@transactions_bp.route('', methods=['POST'])
def create_transaction():
    """Crear nueva transacción"""
    user_id, error = get_user_id()
    if error:
        return error
    
    data = request.get_json()
    
    required = ['account_id', 'category_id', 'type', 'amount']
    if not data or not all(data.get(field) for field in required):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    # Validar que la cuenta y categoría pertenezcan al usuario
    account = Account.query.filter_by(id=data['account_id'], user_id=user_id).first()
    category = Category.query.filter_by(id=data['category_id'], user_id=user_id).first()
    
    if not account or not category:
        return jsonify({'error': 'Cuenta o categoría no válida'}), 404
    
    # Normalizar monto siempre como valor absoluto positivo
    amount = abs(float(data['amount']))

    # Crear transacción con monto positivo y tipo explícito
    transaction = Transaction(
        user_id=user_id,
        account_id=data['account_id'],
        category_id=data['category_id'],
        transaction_type=data['type'],
        amount=amount,
        description=data.get('description', ''),
        notes=data.get('notes', ''),
        transaction_date=datetime.fromisoformat(data.get('date', datetime.utcnow().isoformat()))
    )
    
    # Actualizar saldo de la cuenta según tipo (income suma, expense resta)
    if data['type'] == 'income':
        account.current_balance += amount
    else:
        account.current_balance -= amount
    
    db.session.add(transaction)
    db.session.add(account)  # Asegurarse de que la cuenta se guarda
    db.session.commit()
    
    return jsonify({
        'message': 'Transacción creada exitosamente',
        'transaction': {
            'id': transaction.id,
            'amount': amount,  # Siempre positivo
            'type': transaction.transaction_type,
            'account_balance': account.current_balance
        }
    }), 201

@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Actualizar transacción"""
    user_id, error = get_user_id()
    if error:
        return error
    
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transacción no encontrada'}), 404
    
    data = request.get_json()
    
    # Revertir monto anterior de la cuenta usando monto positivo
    account = transaction.account
    prev_amount = abs(transaction.amount)
    if transaction.transaction_type == 'income':
        account.current_balance -= prev_amount
    else:
        account.current_balance += prev_amount
    
    # Normalizar nuevo monto
    if 'amount' in data:
        transaction.amount = abs(float(data['amount']))
    if 'type' in data:
        transaction.transaction_type = data['type']
    if 'category_id' in data:
        transaction.category_id = data['category_id']
    if 'description' in data:
        transaction.description = data['description']
    if 'notes' in data:
        transaction.notes = data['notes']
    
    # Aplicar nuevo monto a la cuenta (income suma, expense resta)
    new_amount = abs(transaction.amount)
    if transaction.transaction_type == 'income':
        account.current_balance += new_amount
    else:
        account.current_balance -= new_amount
    
    db.session.add(account)  # Asegurarse de que la cuenta se guarda
    db.session.commit()
    
    return jsonify({
        'message': 'Transacción actualizada',
        'account_balance': account.current_balance,
        'amount': new_amount if transaction.transaction_type == 'income' else -new_amount
    }), 200

@transactions_bp.route('/stats/monthly', methods=['GET'])
def get_monthly_stats():
    """Obtener estadísticas mensuales"""
    user_id, error = get_user_id()
    if error:
        return error
    
    month_str = request.args.get('month', datetime.utcnow().strftime('%Y-%m'))
    start_date = datetime.fromisoformat(f'{month_str}-01')
    end_date = start_date + timedelta(days=32)
    end_date = end_date.replace(day=1) - timedelta(days=1)
    
    income = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'income',
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).scalar() or 0
    
    expenses = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).scalar() or 0
    
    return jsonify({
        'month': month_str,
        'income': income,
        'expenses': expenses,
        'net': income - expenses
    }), 200
@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """
    SOLO PARA EL USUARIO: Borrar una transacción
    Restaura el balance de la cuenta automáticamente
    """
    user_id, error = get_user_id()
    if error:
        return error
    
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transacción no encontrada'}), 404
    
    # Obtener datos para respuesta
    account = transaction.account
    amount_reversed = transaction.amount
    
    # Revertir el balance: hacer lo opuesto a lo que se hizo cuando se creó
    if transaction.transaction_type == 'expense':
        account.current_balance += amount_reversed  # Fue gasto, se restó → ahora suma
    else:  # income
        account.current_balance -= amount_reversed  # Fue ingreso, se sumó → ahora resta
    account.updated_at = db.func.now()
    
    # Eliminar transacción
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Transacción eliminada: {transaction.description}',
        'amount_reversed': -amount_reversed,
        'account': account.name,
        'new_account_balance': account.current_balance,
        'currency': account.currency
    }), 200

@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
def edit_transaction(transaction_id):
    """
    SOLO PARA EL USUARIO: Editar una transacción existente
    Ajusta automáticamente el balance de la cuenta
    """
    user_id, error = get_user_id()
    if error:
        return error
    
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transacción no encontrada'}), 404
    
    data = request.get_json()
    
    # Datos anteriores
    old_amount = transaction.amount
    old_description = transaction.description
    old_account_id = transaction.account_id
    
    # Actualizar campos si se proporcionan
    if 'description' in data:
        transaction.description = data['description']
    
    if 'amount' in data:
        new_amount = float(data['amount'])
        # Si el usuario dice "gasto de 50" pero era expense, el amount es -50
        if transaction.transaction_type == 'expense' and new_amount > 0:
            new_amount = -new_amount
        transaction.amount = new_amount
    
    if 'transaction_type' in data:
        transaction.transaction_type = data['transaction_type']
    
    if 'transaction_date' in data:
        transaction.transaction_date = datetime.fromisoformat(data['transaction_date'])
    
    if 'account_id' in data:
        # Si cambió de cuenta, ajustar balances
        new_account_id = data['account_id']
        new_account = Account.query.filter_by(id=new_account_id, user_id=user_id).first()
        
        if not new_account:
            return jsonify({'error': 'Cuenta destino no encontrada'}), 404
        
        old_account = Account.query.get(old_account_id)
        
        # Revertir en cuenta anterior
        old_account.current_balance -= old_amount
        # Aplicar en cuenta nueva
        new_account.current_balance += (transaction.amount if 'amount' not in data else float(data['amount']))
        
        transaction.account_id = new_account_id
    else:
        # Si no cambió de cuenta, solo ajustar por diferencia de monto
        account = transaction.account
        if 'amount' in data:
            amount_diff = transaction.amount - old_amount
            account.current_balance += amount_diff
    
    transaction.updated_at = db.func.now()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Transacción actualizada',
        'transaction_id': transaction.id,
        'changes': {
            'description': {
                'old': old_description,
                'new': transaction.description
            },
            'amount': {
                'old': old_amount,
                'new': transaction.amount
            }
        },
        'new_account_balance': transaction.account.current_balance,
        'currency': transaction.account.currency
    }), 200

@transactions_bp.route('/<int:transaction_id>/restore', methods=['POST'])
def restore_transaction(transaction_id):
    """
    SOLO PARA EL USUARIO: Marcar transacción como "restaurada"
    (No la elimina, solo registra que fue revertida)
    Útil para deshacer transacciones sin perder el historial
    """
    user_id, error = get_user_id()
    if error:
        return error
    
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transacción no encontrada'}), 404
    
    account = transaction.account
    
    # Revertir el monto
    account.current_balance -= transaction.amount
    
    # Marcar como restaurada (agregar nota)
    transaction.notes = f"Restaurada el {datetime.now().isoformat()} - Monto revertido: {transaction.amount}"
    transaction.updated_at = db.func.now()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Transacción restaurada: {transaction.description}',
        'amount_restored': -transaction.amount,
        'new_account_balance': account.current_balance,
        'currency': account.currency
    }), 200