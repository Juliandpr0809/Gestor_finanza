"""
Rutas para gestión de cuentas
"""
from flask import Blueprint, request, jsonify
from models import db, Account, Transaction
from utils.jwt_utils import get_user_id_from_header, AuthError

accounts_bp = Blueprint('accounts', __name__)

def get_user_id():
    """Obtener ID del usuario actual desde JWT"""
    try:
        return get_user_id_from_header(), None
    except AuthError as err:
        return None, ({'error': str(err)}, 401)

@accounts_bp.route('', methods=['GET'])
def get_accounts():
    """Obtener todas las cuentas del usuario"""
    user_id, error = get_user_id()
    if error:
        return error
    
    accounts = Account.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': acc.id,
        'name': acc.name,
        'account_type': acc.account_type,
        'currency': acc.currency,
        'current_balance': acc.current_balance,
        'is_active': acc.is_active,
        'created_at': acc.created_at.isoformat()
    } for acc in accounts]), 200

@accounts_bp.route('/<int:account_id>', methods=['GET'])
def get_account(account_id):
    """Obtener detalle de una cuenta"""
    user_id, error = get_user_id()
    if error:
        return error
    
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    
    if not account:
        return jsonify({'error': 'Cuenta no encontrada'}), 404
    
    return jsonify({
        'id': account.id,
        'name': account.name,
        'account_type': account.account_type,
        'currency': account.currency,
        'initial_balance': account.initial_balance,
        'current_balance': account.current_balance,
        'is_active': account.is_active,
        'created_at': account.created_at.isoformat()
    }), 200

@accounts_bp.route('', methods=['POST'])
def create_account():
    """Crear nueva cuenta"""
    user_id, error = get_user_id()
    if error:
        return error
    
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('account_type'):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    account = Account(
        user_id=user_id,
        name=data['name'],
        account_type=data['account_type'],
        currency=data.get('currency', 'USD'),
        initial_balance=float(data.get('initial_balance', 0)),
        current_balance=float(data.get('initial_balance', 0))
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'message': 'Cuenta creada exitosamente',
        'account': {
            'id': account.id,
            'name': account.name,
            'account_type': account.account_type,
            'currency': account.currency,
            'current_balance': account.current_balance
        }
    }), 201

@accounts_bp.route('/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    """Actualizar cuenta"""
    user_id, error = get_user_id()
    if error:
        return error
    
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    
    if not account:
        return jsonify({'error': 'Cuenta no encontrada'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        account.name = data['name']
    if 'account_type' in data:
        account.account_type = data['account_type']
    if 'currency' in data:
        account.currency = data['currency']
    if 'is_active' in data:
        account.is_active = data['is_active']
    # Permitir ajustar saldos manualmente si se envían
    if 'initial_balance' in data:
        try:
            account.initial_balance = float(data['initial_balance'])
        except (TypeError, ValueError):
            return jsonify({'error': 'initial_balance inválido'}), 400
    if 'current_balance' in data:
        try:
            account.current_balance = float(data['current_balance'])
        except (TypeError, ValueError):
            return jsonify({'error': 'current_balance inválido'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Cuenta actualizada',
        'account': {
            'id': account.id,
            'name': account.name,
            'current_balance': account.current_balance
        }
    }), 200

@accounts_bp.route('/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Eliminar cuenta"""
    user_id, error = get_user_id()
    if error:
        return error
    
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    
    if not account:
        return jsonify({'error': 'Cuenta no encontrada'}), 404
    
    # Validar que no tenga transacciones - ELIMINADO para permitir borrado en cascada
    # if Transaction.query.filter_by(account_id=account_id).first():
    #     return jsonify({'error': 'No se puede eliminar una cuenta con transacciones'}), 409
    
    db.session.delete(account)
    db.session.commit()
    
    return jsonify({'message': 'Cuenta eliminada'}), 200

@accounts_bp.route('/stats', methods=['GET'])
def get_account_stats():
    """Obtener estadísticas de todas las cuentas"""
    user_id, error = get_user_id()
    if error:
        return error
    
    accounts = Account.query.filter_by(user_id=user_id).all()
    total_balance = sum(acc.current_balance for acc in accounts)
    
    return jsonify({
        'total_accounts': len(accounts),
        'total_balance': total_balance,
        'accounts': [{
            'id': acc.id,
            'name': acc.name,
            'balance': acc.current_balance
        } for acc in accounts]
    }), 200
@accounts_bp.route('/<int:account_id>/set-balance', methods=['POST'])
def set_account_balance(account_id):
    """
    SOLO PARA EL USUARIO: Establecer balance manualmente
    El usuario tiene control total de sus propias cuentas
    """
    user_id, error = get_user_id()
    if error:
        return error
    
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    
    if not account:
        return jsonify({'error': 'Cuenta no encontrada'}), 404
    
    data = request.get_json()
    new_balance = data.get('balance')
    reason = data.get('reason', 'Ajuste manual del usuario')
    
    if new_balance is None:
        return jsonify({'error': 'Debe proporcionar un nuevo balance'}), 400
    
    try:
        new_balance = float(new_balance)
    except (ValueError, TypeError):
        return jsonify({'error': 'Balance debe ser un número'}), 400
    
    # Guardar balance anterior para auditoría
    old_balance = account.current_balance
    
    # Actualizar balance
    account.current_balance = new_balance
    account.updated_at = db.func.now()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'account_id': account.id,
        'account_name': account.name,
        'old_balance': old_balance,
        'new_balance': new_balance,
        'currency': account.currency,
        'reason': reason,
        'message': f'Balance actualizado de {account.currency} {old_balance} a {account.currency} {new_balance}'
    }), 200

@accounts_bp.route('/<int:account_id>/reset-balance', methods=['POST'])
def reset_account_balance(account_id):
    """
    SOLO PARA EL USUARIO: Resetear balance al saldo inicial
    """
    user_id, error = get_user_id()
    if error:
        return error
    
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    
    if not account:
        return jsonify({'error': 'Cuenta no encontrada'}), 404
    
    old_balance = account.current_balance
    account.current_balance = account.initial_balance
    account.updated_at = db.func.now()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'account_name': account.name,
        'previous_balance': old_balance,
        'reset_balance': account.initial_balance,
        'currency': account.currency,
        'message': f'Balance reseteado a {account.currency} {account.initial_balance}'
    }), 200