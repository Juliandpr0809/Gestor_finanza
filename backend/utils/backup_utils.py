"""
Utilidades para backup y restauración de balances de cuentas
"""
from models import db, Account, AccountBalanceBackup
from datetime import datetime

def create_balance_backup(user_id, backup_type='manual', reason=None):
    """
    Crea un backup del estado actual de todas las cuentas del usuario
    
    Args:
        user_id: ID del usuario
        backup_type: Tipo de backup ('reset', 'manual_edit', 'delete_transaction', etc)
        reason: Razón opcional para el backup
    
    Returns:
        AccountBalanceBackup object o None si hay error
    """
    try:
        accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
        
        if not accounts:
            return None
        
        # Guardar snapshot de balances
        backup_data = {
            str(account.id): {
                'name': account.name,
                'balance': float(account.current_balance),
                'currency': account.currency
            }
            for account in accounts
        }
        
        backup = AccountBalanceBackup(
            user_id=user_id,
            backup_type=backup_type,
            backup_data=backup_data,
            reason=reason
        )
        
        db.session.add(backup)
        db.session.commit()
        
        print(f"[BACKUP] Created backup {backup.id} for user {user_id}: {backup_type}")
        return backup
    
    except Exception as e:
        print(f"[ERROR] Failed to create balance backup: {e}")
        return None


def restore_balance_backup(user_id, backup_id=None):
    """
    Restaura los balances desde un backup
    
    Args:
        user_id: ID del usuario
        backup_id: ID del backup a restaurar (si None, usa el más reciente)
    
    Returns:
        dict con resultado: {'success': bool, 'message': str, 'restored_accounts': int}
    """
    try:
        if backup_id:
            backup = AccountBalanceBackup.query.filter_by(
                id=backup_id, user_id=user_id
            ).first()
        else:
            # Usar el más reciente que no haya sido restaurado
            backup = AccountBalanceBackup.query.filter_by(
                user_id=user_id, restored_at=None
            ).order_by(AccountBalanceBackup.created_at.desc()).first()
        
        if not backup:
            return {
                'success': False,
                'message': 'No hay backup disponible para restaurar'
            }
        
        # Restaurar balances
        restored_count = 0
        for account_id_str, account_data in backup.backup_data.items():
            account_id = int(account_id_str)
            account = Account.query.filter_by(
                id=account_id, user_id=user_id
            ).first()
            
            if account:
                account.current_balance = account_data['balance']
                account.updated_at = datetime.utcnow()
                restored_count += 1
        
        # Marcar backup como restaurado
        backup.restored_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"[RESTORE] Restored {restored_count} accounts from backup {backup.id}")
        
        return {
            'success': True,
            'message': f'Se restauraron {restored_count} cuentas correctamente',
            'restored_accounts': restored_count,
            'backup_id': backup.id,
            'backup_reason': backup.reason
        }
    
    except Exception as e:
        print(f"[ERROR] Failed to restore balance backup: {e}")
        return {
            'success': False,
            'message': f'Error al restaurar: {str(e)}'
        }


def get_available_backups(user_id):
    """
    Obtiene lista de backups disponibles para un usuario
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Lista de backups (máximo 5 más recientes)
    """
    try:
        backups = AccountBalanceBackup.query.filter_by(
            user_id=user_id
        ).order_by(
            AccountBalanceBackup.created_at.desc()
        ).limit(5).all()
        
        return [
            {
                'id': b.id,
                'type': b.backup_type,
                'reason': b.reason,
                'created_at': b.created_at.isoformat(),
                'restored': b.restored_at is not None
            }
            for b in backups
        ]
    
    except Exception as e:
        print(f"[ERROR] Failed to get backups: {e}")
        return []
