"""
Rutas para gestión del chat con IA
"""
from flask import Blueprint, request, jsonify
import time

# rapidfuzz es opcional (pesado para PythonAnywhere)
try:
    from rapidfuzz import process, fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False
    print("[WARNING] rapidfuzz no está instalado - Funcionalidad de búsqueda difusa deshabilitada")

from models import db, User, ChatMessage, Transaction, Account, Category
from datetime import datetime
from utils.jwt_utils import get_user_id_from_header, AuthError
from services.ai_service import ai_service
from services.ai_service_improved import ImprovedAIService
from utils.backup_utils import create_balance_backup, restore_balance_backup, get_available_backups
from decimal import Decimal

# Inicializar servicio de IA mejorado
improved_ai = ImprovedAIService()

chat_bp = Blueprint('chat', __name__)

def simple_fuzzy_match(query, choices):
    """
    Búsqueda difusa simple cuando rapidfuzz no está disponible
    Retorna: (mejor_match, score) o (None, 0)
    """
    if not choices:
        return (None, 0)
    
    query_lower = query.lower()
    best_match = None
    best_score = 0
    
    for choice in choices:
        choice_lower = choice.lower()
        
        # Coincidencia exacta
        if choice_lower == query_lower:
            return (choice, 100)
        
        # Contiene la query
        if query_lower in choice_lower:
            score = 80
            if best_score < score:
                best_score = score
                best_match = choice
        
        # Query contiene el choice
        elif choice_lower in query_lower:
            score = 70
            if best_score < score:
                best_score = score
                best_match = choice
    
    return (best_match, best_score)

def find_best_match(query, choices):
    """
    Encuentra la mejor coincidencia usando rapidfuzz si está disponible,
    o fallback simple si no lo está
    """
    if HAS_RAPIDFUZZ:
        match = process.extractOne(query, choices, scorer=fuzz.WRatio)
        return match if match else (None, 0)
    else:
        return simple_fuzzy_match(query, choices)

def get_user_id():
    """Obtener ID del usuario actual desde JWT"""
    try:
        return get_user_id_from_header(), None
    except AuthError as err:
        return None, ({'error': str(err)}, 401)

def get_user():
    """Obtener objeto User actual"""
    user_id, error = get_user_id()
    if error:
        return None, error
    
    user = User.query.get(user_id)
    if not user:
        return None, ({'error': 'Usuario no encontrado'}, 404)
    
    return user, None

def get_user():
    """Obtener objeto User actual"""
    user_id, error = get_user_id()
    if error:
        return None, error
    
    user = User.query.get(user_id)
    if not user:
        return None, ({'error': 'Usuario no encontrado'}, 404)
    
    return user, None

@chat_bp.route('/init', methods=['POST'])
def init_chat():
    """
    Inicializar chat - Preguntar moneda si es la primera vez
    """
    user, error = get_user()
    if error:
        return error
    
    # Si ya se inicializó, devolver estado actual
    if user.chat_initialized:
        return jsonify({
            'initialized': True,
            'preferred_currency': user.preferred_currency,
            'message': f'Chat ya inicializado con moneda: {user.preferred_currency}'
        }), 200
    
    # Primera inicialización - Preguntar moneda
    init_message = """👋 **¡Bienvenido a OrdenC - Tu Asistente Financiero Inteligente!**

🎯 **¿Qué puedo hacer por ti?**

Soy tu asistente personal que entiende lenguaje natural. Puedes hablar conmigo como lo harías con un amigo:

💰 **Registrar tus finanzas fácilmente:**
• Solo escribe: *"Gasté 50.000 en supermercado"* → ¡Y listo! Yo registro el gasto
• *"Me pagaron 800.000 del trabajo"* → Registra tu ingreso automáticamente
• *"Pagué 35.000 de pizza anoche"* → Incluso con fechas pasadas

📊 **Consultar tu situación financiera:**
• *"¿Cuánto llevo gastado este mes?"* → Te doy el total al instante
• *"Muéstrame mi balance"* → Ves todas tus cuentas
• *"¿En qué categoría gasto más?"* → Análisis detallado

💡 **Recibir consejos personalizados:**
• *"Dame consejos para ahorrar"* → Recomendaciones según tus gastos
• *"Ayúdame a crear un presupuesto"* → Planificación inteligente

🏦 **Gestionar tus cuentas:**
• *"Crea una cuenta llamada Ahorros"* → Nueva cuenta al instante
• *"Transfiere 100.000 de Efectivo a Banco"* → Transferencias rápidas

---

⚙️ **Para comenzar, necesito configurar tu moneda preferida.**

Escribe una de estas opciones:
💵 **USD** - Dólar Estadounidense
💶 **EUR** - Euro  
🇨🇴 **COP** - Peso Colombiano
🇲🇽 **MXN** - Peso Mexicano
🇦🇷 **ARS** - Peso Argentino

📝 **Ejemplos:** "USD", "Mi moneda es COP", "Quiero usar pesos mexicanos"

Una vez configurada, ¡solo habla conmigo naturalmente! 🚀"""
    
    # Guardar mensaje de sistema
    system_message = ChatMessage(
        user_id=user.id,
        role='assistant',
        content=init_message,
        message_metadata={'type': 'initialization', 'ai_service': 'system'}
    )
    
    db.session.add(system_message)
    db.session.commit()
    
    return jsonify({
        'initialized': False,
        'message': init_message,
        'message_id': system_message.id
    }), 200

@chat_bp.route('/set-currency', methods=['POST'])
def set_currency():
    """
    Establecer la moneda preferida del usuario
    """
    user, error = get_user()
    if error:
        return error
    
    data = request.get_json()
    currency = data.get('currency', '').upper().strip()
    
    # Validar moneda
    valid_currencies = ['USD', 'EUR', 'COP', 'MXN', 'ARS', 'PEN', 'CLP', 'BRL']
    
    if currency not in valid_currencies:
        return jsonify({
            'error': f'Moneda no válida. Opciones: {", ".join(valid_currencies)}'
        }), 400
    
    # Actualizar moneda del usuario
    user.preferred_currency = currency
    user.chat_initialized = True
    
    # Actualizar moneda de todas sus cuentas
    accounts = Account.query.filter_by(user_id=user.id, is_active=True).all()
    for account in accounts:
        account.currency = currency
    
    db.session.commit()
    
    # Guardar confirmación en chat
    confirmation_message = ChatMessage(
        user_id=user.id,
        role='assistant',
        content=f"""✅ **¡Perfecto! Moneda configurada: {currency}**

Todas tus transacciones estarán en {currency}. Ahora puedo ayudarte con:

💰 **Registrar Transacciones**
• "Gasté 50.000 en supermercado"
• "Me pagaron 800.000 del trabajo"
• "Pagué 35.000 de pizza anoche"

📊 **Consultar Finanzas**
• "¿Cuánto llevo gastado este mes?"
• "Muéstrame mi balance"
• "¿Cuál es mi cuenta con más dinero?"

💡 **Consejos y Análisis**
• "Dame consejos para ahorrar"
• "¿En qué categoría gasto más?"
• "Ayúdame a crear un presupuesto"

🏦 **Gestionar Cuentas**
• "Crea una cuenta llamada Ahorros"
• "Transfiere 100.000 de Efectivo a Banco"

¿Qué necesitas hacer primero? 😊""",
        message_metadata={'type': 'currency_set', 'ai_service': 'system', 'currency': currency}
    )
    
    db.session.add(confirmation_message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'currency': currency,
        'message': f'Moneda establecida a {currency}',
        'confirmation_id': confirmation_message.id
    }), 200

@chat_bp.route('/messages', methods=['GET'])
def get_messages():
    """Obtener historial de mensajes"""
    user_id, error = get_user_id()
    if error:
        return error
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    messages = ChatMessage.query.filter_by(user_id=user_id).order_by(
        ChatMessage.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'messages': [{
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'metadata': m.message_metadata,
            'created_at': m.created_at.isoformat()
        } for m in reversed(messages.items)],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': messages.total,
            'pages': messages.pages
        }
    }), 200

@chat_bp.route('/clear', methods=['POST'])
def clear_chat():
    """Limpiar historial de chat"""
    user_id, error = get_user_id()
    if error:
        return error
    
    try:
        # Eliminar todos los mensajes del usuario
        ChatMessage.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Historial de chat limpiado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error limpiando historial: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'No se pudo limpiar el historial',
            'details': str(e)
        }), 500

def process_control_command(user, user_id, control_command, original_message):
    """
    Procesa comandos de control del usuario para modificar balance/transacciones
    Requiere confirmación explícita del usuario
    """
    action = control_command['action']
    currency = user.preferred_currency
    
    try:
        if action == 'create_account':
            # Crear nueva cuenta
            account_name = control_command.get('account_name')
            account_type = control_command.get('account_type', 'checking')
            initial_balance = control_command.get('initial_balance', 0)
            
            if not account_name:
                return """❌ No pude identificar el nombre de la cuenta.

Por favor, especifica el nombre. Ejemplo:
*"Crear cuenta llamada Nequi con saldo de 234000"*"""
            
            # Verificar si ya existe
            existing = Account.query.filter_by(user_id=user_id, name=account_name.title()).first()
            if existing:
                return f"""⚠️ Ya tienes una cuenta llamada **{account_name.title()}**

Balance actual: {currency} {existing.current_balance:,.2f}

¿Deseas usar otro nombre?"""
            
            # Crear la cuenta
            new_account = Account(
                user_id=user_id,
                name=account_name.title(),
                account_type=account_type,
                currency=currency,
                initial_balance=initial_balance,
                current_balance=initial_balance
            )
            
            db.session.add(new_account)
            db.session.commit()
            
            type_names = {
                'checking': 'Cuenta Corriente',
                'savings': 'Cuenta de Ahorros',
                'credit_card': 'Tarjeta de Crédito',
                'cash': 'Efectivo'
            }
            
            return f"""✅ **Cuenta creada exitosamente**

📋 **Detalles:**
- **Nombre:** {new_account.name}
- **Tipo:** {type_names.get(account_type, account_type)}
- **Balance inicial:** {currency} {initial_balance:,.2f}
- **Moneda:** {currency}

🎉 Ya puedes registrar transacciones en esta cuenta!

Ejemplo: *"Gasté 50 en gasolina con mi {new_account.name}"*"""
        
        elif action == 'rename_account':
            # Renombrar cuenta
            account_id = control_command.get('account_id')
            new_name = control_command.get('new_name')
            msg_lower = original_message.lower() if original_message else ''
            
            if not new_name:
                return """❌ No pude identificar el nuevo nombre.

Por favor, especifica el nuevo nombre. Ejemplo:
*"Cambiar nombre de cuenta 2 para que se llame Bolsillo"*"""
            
            # Buscar la cuenta
            account = None
            
            # Si es número, buscar por posición
            if account_id and account_id.isdigit():
                accounts = Account.query.filter_by(user_id=user_id, is_active=True).order_by(Account.id).all()
                idx = int(account_id) - 1
                if 0 <= idx < len(accounts):
                    account = accounts[idx]
            else:
                # Buscar por nombre
                if account_id:
                    account = Account.query.filter(
                        Account.user_id == user_id,
                        Account.is_active == True,
                        Account.name.ilike(f'%{account_id}%')
                    ).first()

            # Fallback: detectar por coincidencia de nombre en el mensaje (aunque no diga "cuenta")
            if not account:
                accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
                for acc in accounts:
                    if acc.name.lower() in msg_lower:
                        account = acc
                        break

            # Fallback adicional: si menciona "efectivo" o "cash", elegir primera cuenta de efectivo
            if not account and 'efectivo' in msg_lower:
                account = Account.query.filter_by(user_id=user_id, is_active=True, account_type='cash').first()
            
            if not account:
                accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
                accounts_list = '\n'.join([f"{i+1}. {a.name} ({a.account_type})" for i, a in enumerate(accounts)])
                return f"""❌ No pude encontrar la cuenta especificada.

**Tus cuentas:**
{accounts_list}

Ejemplo: *"Cambiar nombre de cuenta 2 para que se llame Bolsillo"*"""
            
            # Guardar nombre anterior
            old_name = account.name
            
            # Actualizar nombre
            account.name = new_name.title()
            db.session.commit()
            
            return f"""✅ **Cuenta renombrada exitosamente**

📋 **Cambio realizado:**
- **Nombre anterior:** {old_name}
- **Nuevo nombre:** {account.name}
- **Tipo:** {account.account_type}
- **Balance actual:** {currency} {account.current_balance:,.2f}

🎉 Ahora puedes usar el nuevo nombre en tus transacciones!"""
        
        elif action == 'set_balance':
            amount = control_command['amount']
            
            # Obtener la primera cuenta (o todas si el mensaje especifica)
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            
            if not accounts:
                return "❌ No tienes cuentas configuradas para modificar."
            
            if len(accounts) == 1:
                account = accounts[0]
                # Solicitar confirmación
                return f"""⚠️ **CONFIRMACIÓN REQUERIDA**

Estás a punto de cambiar el balance de **{account.name}**:
- **Balance actual:** {currency} {account.current_balance:,.2f}
- **Nuevo balance:** {currency} {amount:,.2f}
- **Diferencia:** {currency} {amount - account.current_balance:,.2f}

**¿Estás seguro? Escribe "CONFIRMAR" para aplicar este cambio.**"""
            else:
                # Múltiples cuentas: mostrar cuáles se modificarían
                account_list = ", ".join([f"{a.name} ({currency} {a.current_balance:,.2f})" for a in accounts])
                return f"""⚠️ **CONFIRMACIÓN REQUERIDA - MÚLTIPLES CUENTAS**

Tienes {len(accounts)} cuentas:
{chr(10).join([f"- {a.name}: {currency} {a.current_balance:,.2f}" for a in accounts])}

¿En cuál cuenta deseas cambiar el balance a {currency} {amount:,.2f}?

Escribe el nombre de la cuenta exactamente como aparece arriba."""
        
        elif action == 'delete_transaction':
            identifiers = control_command.get('identifiers', [])
            
            # Buscar transacción por ID o descripción
            transactions = Transaction.query.filter_by(user_id=user_id).all()
            
            if not transactions:
                return "❌ No tienes transacciones para eliminar."
            
            # Si pidió "última" sin número específico, eliminarla directamente
            if identifiers == ['last'] or any(x in str(identifiers).lower() for x in ['ultima', 'last']):
                last_transaction = transactions[-1] if transactions else None
                if last_transaction:
                    account = last_transaction.account
                    # Revertir el balance: hacer lo opuesto a lo que se hizo cuando se creó
                    if last_transaction.transaction_type == 'expense':
                        account.current_balance += last_transaction.amount  # Fue gasto → suma de vuelta
                    else:  # income
                        account.current_balance -= last_transaction.amount  # Fue ingreso → resta
                    account.updated_at = db.func.now()
                    db.session.delete(last_transaction)
                    db.session.commit()
                    return f"""✅ **TRANSACCIÓN ELIMINADA**

Se eliminó la transacción:
- **ID:** {last_transaction.id}
- **Monto:** {currency} {last_transaction.amount:,.2f}
- **Descripción:** {last_transaction.description}
- **Fecha:** {last_transaction.transaction_date.strftime('%d/%m/%Y %H:%M')}

El balance ha sido actualizado: {currency} {account.current_balance:,.2f}"""
                else:
                    return "❌ No hay transacciones para eliminar."
            
            # Si tiene números específicos, mostrar las opciones
            recent = transactions[-5:] if len(transactions) > 5 else transactions
            
            txn_list = "\n".join([
                f"- ID {t.id}: {currency} {t.amount:,.2f} - {t.description}"
                for t in recent
            ])
            
            return f"""⚠️ **ELIMINAR TRANSACCIÓN**

Tus últimas transacciones:
{txn_list}

¿Cuál transacción deseas eliminar? Proporciona el ID (número).

Ejemplo: "Eliminar transacción 45"

⚠️ Esto no se puede deshacer fácilmente."""
        
        elif action == 'edit_transaction':
            target = control_command.get('target')
            raw_msg = control_command.get('raw_message', '').lower()
            
            # Identificar transacción
            transaction = None
            if target == 'last' or not target:
                transaction = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.id.desc()).first()
            elif str(target).isdigit():
                transaction = Transaction.query.filter_by(user_id=user_id, id=int(target)).first()
            
            if not transaction:
                return "❌ No encontré ninguna transacción para editar."
            
            # Detectar qué cambiar (Monto o Descripción)
            changes = []
            
            # Monto
            import re
            detected_amount = None

            def parse_money_from_text(text):
                text = (text or '').lower()

                def parse_number(num_str):
                    val = (num_str or '').replace(' ', '')
                    if '.' in val and ',' in val:
                        val = val.replace('.', '').replace(',', '.')
                    elif val.count('.') > 1:
                        val = val.replace('.', '')
                    elif val.count(',') > 1:
                        val = val.replace(',', '')
                    else:
                        val = val.replace(',', '.')
                    try:
                        return float(val)
                    except Exception:
                        return None

                # 1) Con escala (millon/mil/k)
                scaled_patterns = [
                    r'(\d+(?:[.,]\d+)?)\s*(millon(?:es)?|mill[oó]n|mil|k)\b',
                    r'(\d+(?:[.,]\d+)?)(millon(?:es)?|mill[oó]n|mil|k)\b'
                ]
                for pattern in scaled_patterns:
                    match = re.search(pattern, text)
                    if match:
                        base = parse_number(match.group(1))
                        if base is not None:
                            scale = match.group(2)
                            if scale in ['millon', 'millón', 'millones']:
                                return base * 1_000_000
                            if scale in ['mil', 'k']:
                                return base * 1_000
                            return base

                # 2) Miles con separadores
                grouped = re.search(r'(\d{1,3}(?:[.,]\d{3})+)', text)
                if grouped:
                    return float(grouped.group(1).replace('.', '').replace(',', ''))

                # 3) Número simple
                simple = re.search(r'(\d+(?:[.,]\d+)?)', text)
                if simple:
                    return parse_number(simple.group(1))

                return None

            # Priorizar segmentos típicos de edición de monto
            amount_scopes = []
            scope_patterns = [
                r'(?:monto|cantidad|valor)\s*(?:a|en|de)?\s*([^\n]+)$',
                r'(?:editar|edita|cambiar|cambia|modificar|modifica)\s+[^\n]*?\s+a\s+([^\n]+)$',
            ]

            for pattern in scope_patterns:
                match = re.search(pattern, raw_msg)
                if match:
                    amount_scopes.append(match.group(1))

            amount_scopes.append(raw_msg)

            for scope in amount_scopes:
                parsed_amount = parse_money_from_text(scope)
                if parsed_amount and parsed_amount > 0:
                    detected_amount = parsed_amount
                    break
            
            if detected_amount:
                old_amount = transaction.amount
                transaction.amount = detected_amount
                # Actualizar balance de cuenta
                account = Account.query.get(transaction.account_id)
                diff = detected_amount - old_amount
                if transaction.transaction_type == 'expense':
                    account.current_balance -= diff # Si gasto aumenta, balance baja
                else:
                    account.current_balance += diff
                changes.append(f"Monto: {currency} {old_amount} → {currency} {detected_amount}")
            
            # Descripción (si hay texto entre comillas o después de "a")
            new_desc = None
            desc_match = re.search(r'descripción\s+(?:a|es)\s+([a-zA-Z0-9\s]+)', raw_msg)
            if not desc_match:
                 # Si no es monto, asumir que el resto es descripción? No, muy arriesgado.
                 pass
            else:
                 new_desc = desc_match.group(1).strip()
                 transaction.description = new_desc.title()
                 changes.append(f"Descripción actualizada a: {new_desc.title()}")
            
            if not changes:
                 return f"""📝 **EDITAR TRANSACCIÓN #{transaction.id}**
                 
                 Encontré la transacción: {currency} {transaction.amount} - {transaction.description}
                 
                 Pero no entendí qué quieres cambiar. Prueba:
                 • "Cambiar monto a 50000"
                 • "Cambiar descripción a Taxi" """
            
            transaction.updated_at = datetime.utcnow()
            db.session.commit()
            
            return f"""✅ **Transacción Actualizada**
            
            {chr(10).join(changes)}
            
            **Balance actualizado:** {currency} {transaction.account.current_balance:,.2f}"""
        
        elif action == 'reset_balance':
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            
            if not accounts:
                return "❌ No tienes cuentas para resetear."
            
            account_list = "\n".join([
                f"- {a.name}: Balance actual {currency} {a.current_balance:,.2f} → Inicial {currency} {a.initial_balance:,.2f}"
                for a in accounts
            ])
            
            return f"""⚠️ **CONFIRMACIÓN REQUERIDA - RESETEAR BALANCES**

Se resetearán los siguientes balances a sus valores iniciales:
{account_list}

¿Estás seguro? **Escribe "CONFIRMAR" para aplicar este cambio.**

⚠️ Esta acción afectará TODAS tus cuentas.
✨ Se creará un backup automático para poder restaurar después."""
        
        elif action == 'restore_balance':
            # Mostrar backups disponibles
            backups = get_available_backups(user_id)
            
            if not backups:
                return "❌ No hay backups disponibles para restaurar."
            
            backup_list = "\n".join([
                f"- ID {b['id']}: {b['type']} ({b['created_at'][:10]})" + 
                (f" - {b['reason']}" if b['reason'] else "")
                for b in backups[:3]  # Mostrar solo los 3 más recientes
            ])
            
            return f"""📋 **BACKUPS DISPONIBLES**

{backup_list}

¿Deseas restaurar el backup más reciente? **Escribe "CONFIRMAR" para restaurar.**

⚠️ Esto revertirá tus balances al estado anterior."""
        
        elif action == 'delete_all_transactions':
            # Contar transacciones
            tx_count = Transaction.query.filter_by(user_id=user_id).count()
            
            if tx_count == 0:
                return "❌ No tienes transacciones para eliminar."
            
            return f"""⚠️ **CONFIRMACIÓN REQUERIDA - ELIMINAR TODAS LAS TRANSACCIONES**

Estás a punto de eliminar **{tx_count} transacciones**.

🚨 **Esta acción es IRREVERSIBLE y NO se puede deshacer.**

¿Estás seguro? **Escribe "CONFIRMAR" para eliminar todas las transacciones.**

✨ Se creará un backup automático antes de eliminar."""
        
        elif action == 'zero_accounts':
            # Listar cuentas
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            
            if not accounts:
                return "❌ No tienes cuentas para modificar."
            
            account_list = "\n".join([
                f"- {a.name}: Balance actual {currency} {a.current_balance:,.2f} → {currency} 0.00"
                for a in accounts
            ])
            
            return f"""⚠️ **CONFIRMACIÓN REQUERIDA - PONER CUENTAS EN 0**
            
            Estás a punto de poner TODAS tus cuentas en {currency} 0.00:
            
            {account_list}
            
            🚨 **Esta acción modificará los balances de {len(accounts)} cuentas.**
            
            ¿Estás seguro? **Escribe "CONFIRMAR" para poner todas las cuentas en 0.**
            
            ✨ Se creará un backup automático antes del cambio."""
        
        elif action == 'recalculate_balances':
            # Recalcular saldos basado en historial
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            
            if not accounts:
                return "❌ No tienes cuentas para recalcular."
                
            return f"""⚠️ **CONFIRMACIÓN REQUERIDA - RECALCULAR SALDOS**
            
            Voy a revisar todas tus transacciones y recalcular el saldo de tus {len(accounts)} cuentas para asegurar que coincidan perfectamente.
            
            Esto corregirá cualquier error de sincronización.
            
            ¿Estás seguro? **Escribe "CONFIRMAR" para recalcular.**"""

        elif action == 'delete_account':
            account_name = control_command.get('account_name')
            if not account_name:
                return "❌ No entendí qué cuenta quieres eliminar."

            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            account_names = [a.name for a in accounts]
            
            # Buscar cuenta (fuzzy match)
            match = find_best_match(account_name, account_names)
            
            target_account = None
            if match and match[1] >= 70:
                target_name = match[0]
                target_account = next((a for a in accounts if a.name == target_name), None)
            
            if not target_account:
                return f"❌ No encontré ninguna cuenta llamada '{account_name}'."
            
            return f"""⚠️ **CONFIRMACIÓN REQUERIDA - ELIMINAR CUENTA**
            
            Estás a punto de eliminar la cuenta **{target_account.name}**.
            
            🚨 **Esta acción eliminará la cuenta y TODAS sus transacciones asociadas.**
            
            ¿Estás seguro? **Escribe "CONFIRMAR" para eliminar la cuenta permanently.**"""
        
        else:
            return "❌ Comando no reconocido."
    
    except Exception as e:
        return f"❌ Error procesando comando: {str(e)}"

def process_confirmation(user, user_id, last_control_action, confirmation_message):
    """
    Procesa la confirmación explícita del usuario para ejecutar comandos
    """
    msg_lower = confirmation_message.lower()
    currency = user.preferred_currency
    
    if 'confirmar' not in msg_lower:
        return None  # No es confirmación
    
    try:
        if last_control_action and last_control_action.get('action') == 'delete_account':
            account_name = last_control_action.get('account_name')
            
            # Re-buscar cuenta (para seguridad)
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            account_names = [a.name for a in accounts]
            match = find_best_match(account_name, account_names)
            
            target_account = None
            if match and match[1] >= 70:
                target_name = match[0]
                target_account = next((a for a in accounts if a.name == target_name), None)
            
            if not target_account:
                return "❌ No pude encontrar la cuenta para eliminar. Intenta de nuevo."
            
            # Eliminar transacciones (cascade debería hacerlo, pero por seguridad)
            Transaction.query.filter_by(account_id=target_account.id).delete()
            
            # Eliminar cuenta
            db.session.delete(target_account)
            db.session.commit()
            
            return f"""✅ **Cuenta Eliminada**
            
            La cuenta **{target_account.name}** y sus transacciones han sido eliminadas correctamente.
            
            🗑️ Se liberó el espacio y se actualizaron tus reportes."""

        elif last_control_action and last_control_action.get('action') == 'set_balance':
            amount = last_control_action['amount']
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            
            if len(accounts) == 1:
                account = accounts[0]
                old_balance = account.current_balance
                account.current_balance = amount
                account.updated_at = datetime.utcnow()
                db.session.commit()
                
                return f"""✅ **Balance actualizado correctamente**

- **Cuenta:** {account.name}
- **Balance anterior:** {currency} {old_balance:,.2f}
- **Balance nuevo:** {currency} {amount:,.2f}
- **Cambio:** {currency} {amount - old_balance:,.2f}

✨ Tu cuenta ha sido actualizada."""
            else:
                return "⚠️ Necesito que especifiques en cuál cuenta cambiar el balance."
        
        elif last_control_action and last_control_action.get('action') == 'reset_balance':
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            
            # Crear backup ANTES de cambiar (pero continuar si falla)
            try:
                backup = create_balance_backup(user_id, backup_type='reset', reason='Reset manual por usuario')
            except Exception as e:
                print(f"[WARNING] Backup failed, continuing without backup: {e}")
                backup = False
            
            for account in accounts:
                account.current_balance = account.initial_balance
                account.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            account_list = "\n".join([
                f"- {a.name}: {currency} {a.current_balance:,.2f}"
                for a in accounts
            ])
            
            restore_hint = "\n\n💾 **Guardar para restaurar:** Si necesitas volver a los balances anteriores, puedes escribir \"restaurar balance\" para recuperarlos." if backup else ""
            
            return f"""✅ **Balances reseteados a valores iniciales**

{account_list}

✨ Todos tus balances han sido restaurados a su valor inicial.{restore_hint}"""
        
        elif last_control_action and last_control_action.get('action') == 'restore_balance':
            # Restaurar desde el backup más reciente
            result = restore_balance_backup(user_id)
            
            if result['success']:
                accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
                account_list = "\n".join([
                    f"- {a.name}: {currency} {a.current_balance:,.2f}"
                    for a in accounts
                ])
                
                return f"""✅ **Balances Restaurados**

Se restauraron {result['restored_accounts']} cuentas desde el backup:

{account_list}

✨ Tus balances han vuelto a su estado anterior."""
            else:
                return f"""❌ No se pudo restaurar: {result['message']}"""
        
        elif last_control_action and last_control_action.get('action') == 'delete_all_transactions':
            # Crear backup ANTES de eliminar (pero continuar si falla)
            try:
                backup = create_balance_backup(user_id, backup_type='delete_all', reason='Eliminar todas las transacciones')
            except Exception as e:
                print(f"[WARNING] Backup failed, continuing without backup: {e}")
                backup = False
            
            # Eliminar todas las transacciones
            # Primero contamos cuántas hay para el reporte
            tx_count = Transaction.query.filter_by(user_id=user_id).count()
            
            Transaction.query.filter_by(user_id=user_id).delete()
            
            # Resetear balances de cuentas a sus valores iniciales
            # Esto asegura que las cuentas queden "limpias" de historia
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            for account in accounts:
                account.current_balance = account.initial_balance
                account.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            restore_hint = "\n\n💾 **Para deshacer:** Si necesitas recuperar las transacciones, escribe \"restaurar balance\" para volver al estado anterior." if backup else ""
            
            return f"""✅ **Transacciones Eliminadas**

🗑️ Se eliminaron **{tx_count} transacciones**.

📊 **Balance Total:** {currency} {sum(a.current_balance for a in Account.query.filter_by(user_id=user_id, is_active=True).all()):,.2f}

✨ Todos los balances han sido actualizados.{restore_hint}"""
        
        elif last_control_action and last_control_action.get('action') == 'zero_accounts':
            # Crear backup ANTES de cambiar (pero continuar si falla)
            try:
                backup = create_balance_backup(user_id, backup_type='zero', reason='Poner cuentas en 0')
            except Exception as e:
                print(f"[WARNING] Backup failed, continuing without backup: {e}")
                backup = False
            
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            
            for account in accounts:
                account.current_balance = Decimal('0.00')
                account.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            account_list = "\n".join([
                f"- {a.name}: {currency} 0.00"
                for a in accounts
            ])
            
            restore_hint = "\n\n💾 **Para deshacer:** Si necesitas recuperar los balances anteriores, escribe \"restaurar balance\" para restaurarlos." if backup else ""
            
            return f"""✅ **Cuentas en 0**

{account_list}

📊 **Balance Total:** {currency} 0.00

✨ Todas tus cuentas han sido puestas en {currency} 0.00.{restore_hint}"""
        
        elif last_control_action and last_control_action.get('action') == 'recalculate_balances':
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            changes = []
            
            for account in accounts:
                # 1. Empezar con balance inicial
                calculated_balance = account.initial_balance if account.initial_balance else 0.0
                
                # 2. Sumar transacciones
                transactions = Transaction.query.filter_by(account_id=account.id).all()
                income = sum(t.amount for t in transactions if t.transaction_type == 'income')
                expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
                
                calculated_balance += (income - expense)
                
                # 3. Verificar diferencia
                current = account.current_balance
                if abs(float(current) - float(calculated_balance)) > 0.01:
                    changes.append(f"- {account.name}: {currency} {current:,.2f} → {currency} {calculated_balance:,.2f}")
                    account.current_balance = float(calculated_balance)
                    account.updated_at = datetime.utcnow()
            
            if changes:
                db.session.commit()
                change_list = "\n".join(changes)
                return f"""✅ **Saldos Recalculados y Corregidos**
                
                Se encontraron y corrigieron discrepancias en las siguientes cuentas:
                
                {change_list}
                
                ✨ Ahora tus saldos coinciden perfectamente con tu historial de transacciones."""
            else:
                return f"""✅ **Todo en orden**
                
                Revisé todas tus cuentas y transacciones. ¡Tus saldos ya están perfectamente sincronizados!
                
                No fue necesario realizar cambios."""
        
        else:
            return None
    
    except Exception as e:
        return f"❌ Error procesando confirmación: {str(e)}"

@chat_bp.route('/send', methods=['POST'])
def send_message():
    """
    Enviar mensaje al chat
    - Si es solicitud de moneda, procesar
    - Si detecta transacción, CREAR REAL
    - Si pide simulación, NO CREAR
    """
    user, error = get_user()
    if error:
        return error
    
    user_id = user.id
    
    # Si el chat no está inicializado, procesar la respuesta de moneda
    if not user.chat_initialized:
        data = request.get_json()
        content = data.get('content', '').upper().strip()
        
        # Guardar mensaje del usuario
        user_message = ChatMessage(
            user_id=user_id,
            role='user',
            content=data.get('content'),
            message_metadata=data.get('metadata')
        )
        db.session.add(user_message)
        db.session.commit()
        
        # Extraer moneda del mensaje
        valid_currencies = ['USD', 'EUR', 'COP', 'MXN', 'ARS', 'PEN', 'CLP', 'BRL']
        detected_currency = None
        
        for curr in valid_currencies:
            if curr in content:
                detected_currency = curr
                break
        
        if detected_currency:
            # Establecer la moneda
            user.preferred_currency = detected_currency
            user.chat_initialized = True
            
            # Actualizar moneda de todas sus cuentas
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            for account in accounts:
                account.currency = detected_currency
            
            db.session.commit()
            
            ai_response = f"""✅ **Moneda establecida: {detected_currency}**

Perfecto, ahora todas tus transacciones estarán en {detected_currency}.

💡 Puedes:
• Registrar transacciones: *"Gasté 50 en comida"*
• Ver tus cuentas: *"¿Cuál es mi balance?"*
• Obtener consejos de ahorro: *"Dame recomendaciones"*
• Cualquier otra pregunta sobre tu finanzas

¿Qué necesitas hacer? 🤔"""
        else:
            # Pedir aclaración
            ai_response = """❌ No entendí la moneda.

Por favor, escribe una de estas opciones:
• **USD** - Dólar Estadounidense
• **EUR** - Euro
• **COP** - Peso Colombiano
• **MXN** - Peso Mexicano
• **ARS** - Peso Argentino

Ejemplo: *"USD"*"""
        
        assistant_message = ChatMessage(
            user_id=user_id,
            role='assistant',
            content=ai_response,
            message_metadata={'type': 'currency_request', 'ai_service': 'system'}
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        return jsonify({
            'user_message': {
                'id': user_message.id,
                'role': 'user',
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat()
            },
            'assistant_message': {
                'id': assistant_message.id,
                'role': 'assistant',
                'content': assistant_message.content,
                'created_at': assistant_message.created_at.isoformat()
            }
        }), 201
    
    # Chat ya inicializado - procesar normalmente
    t_start = time.time()
    times = {}
    
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': 'Contenido del mensaje vacío'}), 400
    
    # 🧹 LIMPIAR ENTRADA BRUTAL: Remover emojis, texto pegado, etc.
    user_input_raw = data['content']
    t_input_start = time.time()
    user_input_clean = ai_service.clean_user_input(user_input_raw)
    times['input_cleaning'] = time.time() - t_input_start
    
    # Guardar mensaje ORIGINAL (lo que escribió el usuario)
    user_message = ChatMessage(
        user_id=user_id,
        role='user',
        content=user_input_raw,  # Guardar original para auditoría
        message_metadata=data.get('metadata')
    )
    
    t_db_save = time.time()
    db.session.add(user_message)
    db.session.commit()
    times['db_save_user_message'] = time.time() - t_db_save
    
    # Obtener historial de conversación
    t_history = time.time()
    recent_messages = ChatMessage.query.filter_by(user_id=user_id).order_by(
        ChatMessage.created_at.desc()
    ).limit(15).all()
    
    conversation_history = [
        {'role': m.role, 'content': m.content} 
        for m in reversed(recent_messages)
    ]
    times['fetch_history'] = time.time() - t_history
    
    # ⚡ DETECTAR SI USUARIO QUIERE APLICAR UNA TRANSACCIÓN PREVIA SIMULADA
    # Precedencia: 1) Palabras explícitas de acción, 2) Confirmación simple, 3) Lógica normal
    t_detect = time.time()
    action_intent = ai_service.detect_action_intent(user_input_clean)
    is_confirmation = ai_service.detect_confirmation_words(user_input_clean)
    times['detect_intent'] = time.time() - t_detect
    
    print(f"DEBUG: action_intent={action_intent}, is_confirmation={is_confirmation}")
    print(f"DEBUG: user_input_clean='{user_input_clean}'")
    
    # Si detecta "aplícalo", "hazlo", etc. → intentar extraer última transacción simulada
    if action_intent == 'apply' or (is_confirmation and action_intent != 'edit'):
        print(f"DEBUG: Attempting to apply/confirm pending transaction...")
        t_pending = time.time()
        pending_tx = ai_service.extract_pending_transaction(conversation_history)
        times['extract_pending'] = time.time() - t_pending
        
        if pending_tx:
            print(f"DEBUG: Found pending transaction to apply: {pending_tx}")
            
            # Procesar la transacción extraída
            account_name = pending_tx.get('cuenta')
            monto = pending_tx.get('monto')
            descripcion = pending_tx.get('descripcion')
            tx_type = pending_tx.get('tipo', 'expense')
            
            # Buscar cuenta por nombre fuzzy match
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            account = None
            
            if accounts:
                account_names = [a.name for a in accounts]
                # Búsqueda fuzzy del nombre
                from rapidfuzz import process as rfuzz_process, fuzz
                best_match = rfuzz_process.extractOne(
                    account_name, 
                    account_names, 
                    scorer=fuzz.WRatio
                )
                
                if best_match and best_match[1] >= 60:
                    account = next(a for a in accounts if a.name == best_match[0])
                else:
                    account = accounts[0]  # Usar primera cuenta por defecto
            
            if account:
                # Buscar o crear categoría
                category = Category.query.filter(
                    Category.user_id == user_id,
                    Category.category_type == tx_type
                ).first()
                
                if category:
                    try:
                        # Crear TRANSACCIÓN REAL
                        sign = -1 if tx_type == 'expense' else 1
                        new_transaction = Transaction(
                            user_id=user_id,
                            account_id=account.id,
                            category_id=category.id,
                            amount=monto * sign,
                            description=descripcion,
                            transaction_type=tx_type,
                            transaction_date=datetime.utcnow()
                        )
                        
                        # Actualizar balance
                        if tx_type == 'expense':
                            account.current_balance -= monto
                        else:
                            account.current_balance += monto
                        
                        account.updated_at = datetime.utcnow()
                        
                        t_tx_create = time.time()
                        db.session.add(new_transaction)
                        db.session.commit()
                        times['create_transaction'] = time.time() - t_tx_create
                        
                        currency = user.preferred_currency
                        
                        # Calcular timing total
                        total_time = time.time() - t_start
                        timing_info = f"\n\n⏱️ **TIMING DE PROCESAMIENTO:**\n"
                        timing_info += f"• Limpieza de entrada: {times.get('input_cleaning', 0)*1000:.1f}ms\n"
                        timing_info += f"• Guardar mensaje: {times.get('db_save_user_message', 0)*1000:.1f}ms\n"
                        timing_info += f"• Obtener historial: {times.get('fetch_history', 0)*1000:.1f}ms\n"
                        timing_info += f"• Detectar intención: {times.get('detect_intent', 0)*1000:.1f}ms\n"
                        timing_info += f"• Extraer pending: {times.get('extract_pending', 0)*1000:.1f}ms\n"
                        timing_info += f"• Crear transacción: {times.get('create_transaction', 0)*1000:.1f}ms\n"
                        timing_info += f"**⏲️ TOTAL: {total_time*1000:.1f}ms**"
                        
                        ai_response = f"""✅ **¡TRANSACCIÓN APLICADA!**
- **Monto:** {currency} {monto:,.2f}
- **Cuenta:** {account.name}
- **Descripción:** {descripcion}
- **Tipo:** {'Gasto' if tx_type == 'expense' else 'Ingreso'}

🔄 **Balance actualizado:** {currency} {account.current_balance:,.2f}

¡Transacción registrada exitosamente! 🎉{timing_info}"""
                        
                        assistant_message = ChatMessage(
                            user_id=user_id,
                            role='assistant',
                            content=ai_response,
                            message_metadata={'type': 'transaction_applied', 'action': 'auto_apply'}
                        )
                        db.session.add(assistant_message)
                        db.session.commit()
                        
                        return jsonify({
                            'user_message': {
                                'id': user_message.id,
                                'role': 'user',
                                'content': user_message.content,
                                'created_at': user_message.created_at.isoformat()
                            },
                            'assistant_message': {
                                'id': assistant_message.id,
                                'role': 'assistant',
                                'content': assistant_message.content,
                                'created_at': assistant_message.created_at.isoformat()
                            }
                        }), 201
                    except Exception as e:
                        print(f"Error applying transaction: {e}")
                        ai_response = f"❌ Error al aplicar transacción: {str(e)}"
                        
                        assistant_message = ChatMessage(
                            user_id=user_id,
                            role='assistant',
                            content=ai_response,
                            message_metadata={'type': 'transaction_apply_error'}
                        )
                        db.session.add(assistant_message)
                        db.session.commit()
                        
                        return jsonify({
                            'user_message': {
                                'id': user_message.id,
                                'role': 'user',
                                'content': user_message.content,
                                'created_at': user_message.created_at.isoformat()
                            },
                            'assistant_message': {
                                'id': assistant_message.id,
                                'role': 'assistant',
                                'content': assistant_message.content,
                                'created_at': assistant_message.created_at.isoformat()
                            }
                        }), 201
        
        # Si se detectó "aplica" pero NO hay transacción simulada, avisar
        elif action_intent == 'apply':
            print(f"DEBUG: User said 'apply' but no pending transaction found")
            ai_response = """❌ **No hay transacción pendiente para aplicar**

No encontré una transacción simulada anterior. Prueba:
• Describir una transacción primero: "Gaste 50k en pasajes para Nu"
• Luego aplicarla: "Aplícalo" o "Aplica esa transacción"

También puedes usar:
• "Registra una transacción" + descripción
• "Crea un gasto de 50k en pasajes"
"""
            
            assistant_message = ChatMessage(
                user_id=user_id,
                role='assistant',
                content=ai_response,
                message_metadata={'type': 'no_pending_transaction'}
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            return jsonify({
                'user_message': {
                    'id': user_message.id,
                    'role': 'user',
                    'content': user_message.content,
                    'created_at': user_message.created_at.isoformat()
                },
                'assistant_message': {
                    'id': assistant_message.id,
                    'role': 'assistant',
                    'content': assistant_message.content,
                    'created_at': assistant_message.created_at.isoformat()
                }
            }), 201
    
    # Detectar si el usuario quiere SIMULAR (no crear real)
    simulate_keywords = ['simula', 'ejemplo', 'simulación', 'muestra ejemplo', 'como sería', 'cómo quedaría']
    wants_simulation = any(keyword in user_input_clean.lower() for keyword in simulate_keywords)
    
    # ============================================================================
    # NUEVA IA MEJORADA: Function Calling para detectar transacciones
    # ============================================================================
    print(f"DEBUG CHAT: Using ImprovedAIService with function calling...")
    
    try:
        # Procesar con IA mejorada (function calling)
        ai_response_improved = improved_ai.chat_with_function_calling(
            user_message=user_input_clean,
            user_id=user_id,
            conversation_history=conversation_history
        )
        
        print(f"DEBUG: AI Response: {ai_response_improved}")
        
        # Si la IA detectó una función a ejecutar
        if ai_response_improved['type'] == 'function_call':
            function_name = ai_response_improved['function']
            arguments = ai_response_improved['arguments']
            requires_confirmation = ai_response_improved.get('requires_confirmation', True)
            response_text = ai_response_improved.get('response_text', '')
            
            print(f"DEBUG: Function={function_name}, Requires Confirmation={requires_confirmation}")
            
            # FUNCIÓN: create_transaction
            if function_name == 'create_transaction':
                # Buscar cuenta (fuzzy matching)
                account_name = arguments.get('account_name', '')
                accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
                
                account = None
                if accounts:
                    account_names = [a.name for a in accounts]
                    best_match, score = find_best_match(account_name, account_names)
                    
                    if best_match and score >= 60:
                        account = next((a for a in accounts if a.name == best_match), None)
                    
                    # Si no encontró, usar primera cuenta
                    if not account:
                        account = accounts[0]
                
                if not account:
                    ai_response = "❌ No tienes cuentas configuradas. Crea una cuenta primero."
                    
                    assistant_message = ChatMessage(
                        user_id=user_id,
                        role='assistant',
                        content=ai_response,
                        message_metadata={'type': 'error', 'ai_service': 'improved_ai'}
                    )
                    db.session.add(assistant_message)
                    db.session.commit()
                    
                    return jsonify({
                        'user_message': {
                            'id': user_message.id,
                            'role': 'user',
                            'content': user_message.content,
                            'created_at': user_message.created_at.isoformat()
                        },
                        'assistant_message': {
                            'id': assistant_message.id,
                            'role': 'assistant',
                            'content': assistant_message.content,
                            'created_at': assistant_message.created_at.isoformat()
                        }
                    }), 201
                
                # Buscar categoría (fuzzy matching)
                category_name = arguments.get('category', '')
                tx_type = arguments.get('type', 'expense')
                
                categories = Category.query.filter_by(
                    user_id=user_id,
                    category_type=tx_type
                ).all()
                
                category = None
                if categories and category_name:
                    cat_names = [c.name for c in categories]
                    best_cat_match, cat_score = find_best_match(category_name, cat_names)
                    
                    if best_cat_match and cat_score >= 60:
                        category = next((c for c in categories if c.name == best_cat_match), None)
                
                # Si no encontró, usar primera categoría del tipo
                if not category and categories:
                    category = categories[0]
                
                # Preparar datos para confirmación
                tx_data = {
                    'amount': abs(arguments['amount']),
                    'type': tx_type,
                    'account': account.name,
                    'account_id': account.id,
                    'category': category.name if category else 'Sin categoría',
                    'category_id': category.id if category else None,
                    'description': arguments.get('description', ''),
                    'date': arguments.get('date', datetime.now().strftime('%d/%m/%Y'))
                }
                
                # Guardar respuesta de la IA
                assistant_message = ChatMessage(
                    user_id=user_id,
                    role='assistant',
                    content=response_text,
                    message_metadata={
                        'type': 'confirmation_required',
                        'ai_service': 'improved_ai',
                        'function': 'create_transaction',
                        'pending_transaction': tx_data
                    }
                )
                db.session.add(assistant_message)
                db.session.commit()
                
                # RETORNAR CON DATOS PARA CONFIRMACIÓN VISUAL
                return jsonify({
                    'user_message': {
                        'id': user_message.id,
                        'role': 'user',
                        'content': user_message.content,
                        'created_at': user_message.created_at.isoformat()
                    },
                    'assistant_message': {
                        'id': assistant_message.id,
                        'role': 'assistant',
                        'content': assistant_message.content,
                        'created_at': assistant_message.created_at.isoformat()
                    },
                    'requires_confirmation': True,
                    'transaction_data': tx_data,
                    'function': 'create_transaction'
                }), 201
            
            # FUNCIÓN: get_financial_summary
            elif function_name == 'get_financial_summary':
                # Aquí iría la lógica de resumen financiero
                # Por ahora dejamos que siga el flujo normal
                pass
            
            # FUNCIÓN: create_account  
            elif function_name == 'create_account':
                # Aquí iría la lógica de crear cuenta
                # Por ahora dejamos que siga el flujo normal
                pass
        
        # Si es respuesta conversacional normal, continuar con flujo normal
        elif ai_response_improved['type'] == 'text':
            # Guardar respuesta y retornar
            assistant_message = ChatMessage(
                user_id=user_id,
                role='assistant',
                content=ai_response_improved['message'],
                message_metadata={'type': 'text', 'ai_service': 'improved_ai'}
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            return jsonify({
                'user_message': {
                    'id': user_message.id,
                    'role': 'user',
                    'content': user_message.content,
                    'created_at': user_message.created_at.isoformat()
                },
                'assistant_message': {
                    'id': assistant_message.id,
                    'role': 'assistant',
                    'content': assistant_message.content,
                    'created_at': assistant_message.created_at.isoformat()
                }
            }), 201
    
    except Exception as e:
        print(f"ERROR en ImprovedAIService: {e}")
        print(f"Cayendo a lógica antigua...")
        # Si falla la nueva IA, continuar con lógica antigua
    
    # FALLBACK: LÓGICA ANTIGUA (si la nueva IA falla)
    print(f"DEBUG CHAT: Detecting command with AI (fallback)...")
    ai_command = None
    
    # Solo intentar detect_command_with_ai si el servicio está realmente disponible
    # Pero como está fallando, lo saltamos y confiamos en el fallback de regex
    if ai_service.enabled and False:  # Temporalmente deshabilitado porque Groq no responde bien
        ai_command = ai_service.detect_command_with_ai(user_id, data['content'])
    
    if ai_command and ai_command.get('command') != 'chat':
        print(f"DEBUG CHAT: AI detected command = {ai_command['command']}, params = {ai_command.get('params')}")
        
        # Convertir comando de IA a control_command del sistema
        command_type = ai_command['command']
        params = ai_command.get('params', {})
        
        if command_type == 'rename_account':
            control_command = {
                'type': 'control_command',
                'action': 'rename_account',
                'account_id': params.get('account_id'),
                'new_name': params.get('new_name'),
                'raw_message': data['content']
            }
            ai_response = process_control_command(user, user_id, control_command, data['content'])
            
            assistant_message = ChatMessage(
                user_id=user_id,
                role='assistant',
                content=ai_response,
                message_metadata={'ai_service': 'ai_command', 'action': 'rename_account'}
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            return jsonify({
                'user_message': {
                    'id': user_message.id,
                    'role': 'user',
                    'content': user_message.content,
                    'created_at': user_message.created_at.isoformat()
                },
                'assistant_message': {
                    'id': assistant_message.id,
                    'role': 'assistant',
                    'content': assistant_message.content,
                    'created_at': assistant_message.created_at.isoformat()
                }
            }), 201
        
        elif command_type == 'create_account':
            control_command = {
                'type': 'control_command',
                'action': 'create_account',
                'account_name': params.get('new_name'),
                'account_type': params.get('account_type', 'checking'),
                'initial_balance': params.get('amount', 0),
                'raw_message': data['content']
            }
            ai_response = process_control_command(user, user_id, control_command, data['content'])
            
            assistant_message = ChatMessage(
                user_id=user_id,
                role='assistant',
                content=ai_response,
                message_metadata={'ai_service': 'ai_command', 'action': 'create_account'}
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            return jsonify({
                'user_message': {
                    'id': user_message.id,
                    'role': 'user',
                    'content': user_message.content,
                    'created_at': user_message.created_at.isoformat()
                },
                'assistant_message': {
                    'id': assistant_message.id,
                    'role': 'assistant',
                    'content': assistant_message.content,
                    'created_at': assistant_message.created_at.isoformat()
                }
            }), 201
        
        elif command_type == 'set_balance':
            control_command = {
                'type': 'control_command',
                'action': 'set_balance',
                'amount': params.get('amount'),
                'account_id': params.get('account_id'),
                'raw_message': data['content']
            }
            ai_response = process_control_command(user, user_id, control_command, data['content'])
            
            assistant_message = ChatMessage(
                user_id=user_id,
                role='assistant',
                content=ai_response,
                message_metadata={'ai_service': 'ai_command', 'action': 'set_balance'}
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            return jsonify({
                'user_message': {
                    'id': user_message.id,
                    'role': 'user',
                    'content': user_message.content,
                    'created_at': user_message.created_at.isoformat()
                },
                'assistant_message': {
                    'id': assistant_message.id,
                    'role': 'assistant',
                    'content': assistant_message.content,
                    'created_at': assistant_message.created_at.isoformat()
                }
            }), 201
        
        elif command_type == 'create_transaction':
            # La IA detectó una transacción, procesarla directamente
            print(f"DEBUG: AI detected transaction with params: {params}")
            
            # Buscar cuenta por ID o nombre
            account = None
            account_id_param = params.get('account_id')
            
            if account_id_param:
                if str(account_id_param).isdigit():
                    # Buscar por posición
                    accounts = Account.query.filter_by(user_id=user_id, is_active=True).order_by(Account.id).all()
                    idx = int(account_id_param) - 1
                    if 0 <= idx < len(accounts):
                        account = accounts[idx]
                else:
                    # Buscar por nombre (fuzzy)
                    account = Account.query.filter(
                        Account.user_id == user_id,
                        Account.is_active == True,
                        Account.name.ilike(f'%{account_id_param}%')
                    ).first()
            
            if not account:
                # Usar primera cuenta disponible
                account = Account.query.filter_by(user_id=user_id, is_active=True).first()
            
            if not account:
                ai_response = "❌ No tienes cuentas configuradas. Crea una primero."
            else:
                # Buscar o crear categoría
                category = Category.query.filter_by(
                    user_id=user_id,
                    category_type='expense'
                ).first()
                
                if not category:
                    ai_response = "❌ No tienes categorías configuradas. Crea una primero."
                else:
                    try:
                        amount = float(params.get('amount', 0))
                        description = params.get('description', 'Compra')
                        
                        # Crear transacción
                        new_transaction = Transaction(
                            user_id=user_id,
                            account_id=account.id,
                            category_id=category.id,
                            amount=abs(amount),  # Siempre positivo
                            description=description.title(),
                            transaction_type='expense',
                            transaction_date=datetime.utcnow()
                        )
                        
                        account.current_balance -= abs(amount)
                        account.updated_at = datetime.utcnow()
                        
                        db.session.add(new_transaction)
                        db.session.commit()
                        
                        currency = user.preferred_currency
                        ai_response = f"""✅ **Transacción registrada**
- **Monto:** {currency} {abs(amount):,.2f}
- **Cuenta:** {account.name}
- **Descripción:** {description.title()}
- **Categoría:** {category.name}

🔄 **Balance actualizado:** {currency} {account.current_balance:,.2f}"""
                    
                    except Exception as e:
                        print(f"Error creating transaction: {e}")
                        ai_response = f"❌ Error al crear transacción: {str(e)}"
            
            assistant_message = ChatMessage(
                user_id=user_id,
                role='assistant',
                content=ai_response,
                message_metadata={'ai_service': 'ai_command', 'action': 'create_transaction'}
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            return jsonify({
                'user_message': {
                    'id': user_message.id,
                    'role': 'user',
                    'content': user_message.content,
                    'created_at': user_message.created_at.isoformat()
                },
                'assistant_message': {
                    'id': assistant_message.id,
                    'role': 'assistant',
                    'content': assistant_message.content,
                    'created_at': assistant_message.created_at.isoformat()
                }
            }), 201
    
    # PRIORIDAD 1: Detectar comandos de control (REGEX LOCAL - MÁS RÁPIDO)
    # Estos comandos se procesan ANTES que transacciones/consultas
    print(f"DEBUG CHAT: Checking for control commands...")
    print(f"DEBUG CHAT: Message content (clean): '{user_input_clean}'")
    control_cmd = ai_service.detect_control_command(user_input_clean)
    print(f"DEBUG CHAT: Control command result: {control_cmd}")
    
    # PRIORIDAD 1.5: Verificar si hay acción pendiente (confirmación)
    last_msg = ChatMessage.query.filter_by(user_id=user_id, role='assistant').order_by(
        ChatMessage.created_at.desc()
    ).first()
    
    last_action_metadata = last_msg.message_metadata if last_msg else {}
    last_control_action = last_action_metadata.get('pending_action')
    
    print(f"DEBUG CHAT: Last message metadata: {last_action_metadata}")
    print(f"DEBUG CHAT: Last control action: {last_control_action}")
    print(f"DEBUG CHAT: User message contains 'confirmar': {'confirmar' in data['content'].lower()}")
    
    # Si hay acción pendiente Y el usuario confirma, procesar confirmación SIN NECESIDAD DE DETECTAR COMANDO
    if last_control_action and 'confirmar' in data['content'].lower():
        print(f"DEBUG CHAT: Processing confirmation for {last_control_action.get('action')}")
        ai_response = process_confirmation(user, user_id, last_control_action, data['content'])
        
        if ai_response:
            assistant_message = ChatMessage(
                user_id=user_id,
                role='assistant',
                content=ai_response,
                message_metadata={'ai_service': 'control_confirmation'}
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            return jsonify({
                'user_message': {
                    'id': user_message.id,
                    'role': 'user',
                    'content': user_message.content,
                    'created_at': user_message.created_at.isoformat()
                },
                'assistant_message': {
                    'id': assistant_message.id,
                    'role': 'assistant',
                    'content': assistant_message.content,
                    'created_at': assistant_message.created_at.isoformat()
                }
            }), 201
    
    if control_cmd and control_cmd.get('type') == 'control_command':
        print(f"DEBUG CHAT: Control command detected: {control_cmd.get('action')}")
        
        # Verificar si requiere confirmación
        action = control_cmd.get('action')
        requires_confirmation = action in [
            'reset_balance', 'delete_all_transactions', 
            'zero_accounts', 'restore_balance', 'set_balance',
            'delete_account'
        ]
        
        # Procesar el comando de control
        ai_response = process_control_command(user, user_id, control_cmd, data['content'])
        
        # Guardar metadata con acción pendiente si requiere confirmación
        metadata = {'ai_service': 'control_command', 'action': action}
        if requires_confirmation and '⚠️' in ai_response:
            # Solo guardar datos esenciales en pending_action (serializable)
            metadata['pending_action'] = {
                'action': control_cmd.get('action'),
                'identifiers': control_cmd.get('identifiers'),
                'amount': control_cmd.get('amount'),
                'account_id': control_cmd.get('account_id')
            }
            print(f"DEBUG CHAT: Saved pending_action in metadata: {metadata['pending_action']}")
        
        assistant_message = ChatMessage(
            user_id=user_id,
            role='assistant',
            content=ai_response,
            message_metadata=metadata
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        return jsonify({
            'user_message': {
                'id': user_message.id,
                'role': 'user',
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat()
            },
            'assistant_message': {
                'id': assistant_message.id,
                'role': 'assistant',
                'content': assistant_message.content,
                'created_at': assistant_message.created_at.isoformat()
            }
        }), 201
    
    # Si no es comando de control, continuar con detección de transacciones
    # OPTIMIZACIÓN: Detectar localmente primero, solo llamar IA si falla
    intent = ai_service.detect_local_first(user_input_clean, user_id)

    print(f"DEBUG CHAT: Intent detected = {intent}, wants_simulation = {wants_simulation}")
    
    # ⚠️ LOGGING: Si NO se detectó intención, informar al usuario POR QUÉ
    if not intent or not intent.get('has_intent'):
        print(f"DEBUG CHAT: ❌ NO transaction intent detected for message: '{data['content']}'")
        print(f"DEBUG CHAT: Reason: Missing transaction keywords or numbers")
        # Continuar con la IA normal (consultas, análisis, etc.)
    
    if intent and intent.get('has_intent') and not wants_simulation:
        # El usuario quiere crear transacciones REALES (pueden ser múltiples)
        print(f"DEBUG CHAT: Intent detected, processing transactions...")
        
        transaction_parts = intent.get('transaction_parts', [data['content']])
        multiple = intent.get('multiple_transactions', False)
        
        print(f"DEBUG CHAT: Found {len(transaction_parts)} transaction parts")
        
        created_transactions = []
        failed_transactions = []
        
        t_main_start = time.time()
        timing_data = {}
        
        # Procesar cada parte del mensaje como una transacción
        for i, part in enumerate(transaction_parts):
            print(f"DEBUG CHAT: Processing part {i+1}/{len(transaction_parts)}: {part}")
            
            t_part_start = time.time()
            
            # Obtener último mensaje del usuario para contexto (si existe)
            last_user_msg = ChatMessage.query.filter_by(user_id=user_id, role='user').order_by(ChatMessage.created_at.desc()).offset(1).first()
            context_msg = last_user_msg.content if last_user_msg else None
            
            t_extract = time.time()
            transaction_data = ai_service.extract_transaction_from_text(user_id, part, context_msg)
            timing_data[f'extract_tx_{i+1}'] = time.time() - t_extract
            print(f"DEBUG CHAT: Extracted data: {transaction_data}")
            
            if not transaction_data:
                print(f"DEBUG CHAT: ❌ Could not extract transaction data from: {part}")
                failed_transactions.append({
                    'text': part, 
                    'reason': f'❌ **No pude interpretar esta transacción**\n\n🤔 El texto "{part[:50]}..." no contiene información clara de:\n• 💵 Monto\n• 🎯 Tipo (gasto/ingreso)\n• 📝 Descripción'
                })
                continue
            
            # ⚠️ VALIDACIÓN CRÍTICA: Verificar campos mínimos ANTES de continuar
            # No intentar procesar si falta monto, tipo de transacción o descripción
            amount = transaction_data.get('amount')
            tx_type = transaction_data.get('transaction_type')
            description = transaction_data.get('description')
            
            if not amount or not tx_type or not description:
                print(f"DEBUG CHAT: ❌ Skipping incomplete transaction: amount={amount}, type={tx_type}, desc={description}")
                
                # Mensaje MUY específico sobre qué falta
                missing_parts = []
                if not amount:
                    missing_parts.append('💵 **Monto** (ej: 200000, 50k, 1500)')
                if not tx_type:
                    missing_parts.append('🎯 **Tipo de transacción** (usa palabras como: "gasté", "compré", "me llegaron", "ingresó")')
                if not description:
                    missing_parts.append('📝 **Descripción** (para qué fue: arriendo, mercado, salario, etc.)')
                
                failed_transactions.append({
                    'text': part, 
                    'reason': f'Falta información:\n' + '\n'.join(missing_parts)
                })
                continue
            
            # Autocompletar información faltante
            if not transaction_data.get('account'):
                first_account = Account.query.filter_by(user_id=user_id, is_active=True).first()
                if first_account:
                    transaction_data['account'] = first_account.name
            
            if not transaction_data.get('category'):
                # Buscar categoría según el tipo de transacción (ya validado que no es None)
                category = Category.query.filter_by(
                    user_id=user_id, 
                    category_type=tx_type
                ).first()
                
                # Si no existe categoría, crear una por defecto
                if not category:
                    print(f"DEBUG: Creating default {tx_type} category for user {user_id}")
                    default_name = 'Otros Ingresos' if tx_type == 'income' else 'Otros'
                    category = Category(
                        user_id=user_id,
                        name=default_name,
                        icon='💰' if tx_type == 'income' else '💸',
                        category_type=tx_type  # Ahora garantizado que no es None
                    )
                    db.session.add(category)
                    db.session.commit()
                
                if category:
                    transaction_data['category'] = category.name
            
                # Si aún no tiene cuenta o categoría, usar los primeros disponibles
            if not transaction_data.get('account'):
                print(f"DEBUG CHAT: ❌ No account found for user {user_id}")
                failed_transactions.append({
                    'text': part, 
                    'reason': '⚠️ **No tienes cuentas configuradas**\n\n👉 Ve a la página de "Cuentas" y crea una primero.\nEjemplo: "Nequi", "Efectivo", "Banco", etc.'
                })
                continue
            
            if not transaction_data.get('category'):
                print(f"DEBUG CHAT: ❌ No category found for user {user_id}, type {tx_type}")
                failed_transactions.append({
                    'text': part, 
                    'reason': f'⚠️ **No tienes categorías de {"gastos" if tx_type == "expense" else "ingresos"}**\n\n👉 Ve a la página de "Transacciones" y crea una categoría primero.'
                })
                continue
            
                # Crear la transacción
            try:
                account = Account.query.filter_by(
                    user_id=user_id,
                    name=transaction_data['account'],
                    is_active=True
                ).first()
                
                category = Category.query.filter_by(
                    user_id=user_id,
                    name=transaction_data['category']
                ).first()
                
                if not account:
                    print(f"DEBUG CHAT: ❌ Account '{transaction_data['account']}' not found")
                    all_accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
                    available = ', '.join([acc.name for acc in all_accounts[:3]])
                    failed_transactions.append({
                        'text': part, 
                        'reason': f"❌ **Cuenta '{transaction_data['account']}' no encontrada**\n\n💳 Tus cuentas disponibles: {available or 'Ninguna'}"
                    })
                    continue
                
                if not category:
                    print(f"DEBUG CHAT: ❌ Category '{transaction_data['category']}' not found")
                    all_categories = Category.query.filter_by(user_id=user_id, category_type=tx_type).all()
                    available = ', '.join([cat.name for cat in all_categories[:3]])
                    failed_transactions.append({
                        'text': part, 
                        'reason': f"❌ **Categoría '{transaction_data['category']}' no encontrada**\n\n📊 Categorías disponibles: {available or 'Ninguna'}"
                    })
                    continue
                
                # Amount siempre positivo en DB, balance se ajusta según tipo
                amount = abs(Decimal(str(transaction_data['amount'])))
                balance_change = -amount if transaction_data['transaction_type'] == 'expense' else amount
                
                new_transaction = Transaction(
                    user_id=user_id,
                    account_id=account.id,
                    category_id=category.id,
                    amount=float(amount),  # Siempre positivo
                    description=transaction_data['description'],
                    transaction_type=transaction_data['transaction_type'],
                    transaction_date=datetime.utcnow()
                )
                
                account.current_balance = float(Decimal(str(account.current_balance)) + balance_change)
                account.updated_at = datetime.utcnow()
                
                db.session.add(new_transaction)
                
                created_transactions.append({
                    'transaction': new_transaction,
                    'account': account,
                    'amount': float(amount),
                    'description': transaction_data['description'],
                    'transaction_type': transaction_data['transaction_type']
                })
                
            except Exception as e:
                print(f"Error creating transaction: {e}")
                import traceback
                traceback.print_exc()
                failed_transactions.append({
                    'text': part, 
                    'reason': f'❌ **Error técnico al crear transacción:**\n{str(e)[:100]}'
                })
        
            # Commit todas las transacciones creadas
        if created_transactions:
            db.session.commit()
            print(f"DEBUG CHAT: ✅ Created {len(created_transactions)} transactions")
            
                # Obtener saldo actualizado
            all_accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            total_balance = sum(float(acc.current_balance) for acc in all_accounts)
            currency_symbol = user.preferred_currency
            
            if multiple and len(created_transactions) > 1:
                    # Respuesta para múltiples transacciones
                ai_response = f"""✅ **{len(created_transactions)} Transacciones registradas**

"""
                for idx, tx in enumerate(created_transactions, 1):
                    tipo = "💰 Ingreso" if tx['transaction_type'] == 'income' else "💸 Gasto"
                    ai_response += f"{idx}. {tipo}: {tx['description']} - {currency_symbol} {abs(tx['amount']):,.2f}\n"
                
                ai_response += f"\n🔄 **Balance actualizado**\n"
                for acc in all_accounts:
                    ai_response += f"- {acc.name}: {currency_symbol} {float(acc.current_balance):,.2f}\n"
                
                ai_response += f"\n**Balance Total:** {currency_symbol} {total_balance:,.2f}"
                
                if failed_transactions:
                    ai_response += f"\n\n⚠️ No se pudieron procesar {len(failed_transactions)} transacciones."
                
                # Agregar timing info
                total_time = time.time() - t_main_start
                ai_response += f"\n\n⏱️ **TIMING:** {total_time*1000:.1f}ms totales"
            
            else:
                    # Respuesta para una sola transacción
                tx = created_transactions[0]
                ai_response = f"""✅ **Transacción registrada**
- **Monto:** {currency_symbol} {abs(tx['amount']):,.2f}
- **Cuenta:** {tx['account'].name}
- **Descripción:** {tx['description']}

🔄 **Balance actualizado:** {currency_symbol} {tx['account'].current_balance:,.2f}"""
                
                # Agregar timing info
                total_time = time.time() - t_main_start
                ai_response += f"\n\n⏱️ **TIMING:** {total_time*1000:.1f}ms totales"
        
        elif failed_transactions:
            # Generar mensaje MUY específico con las razones de fallo
            print(f"DEBUG CHAT: ❌ {len(failed_transactions)} transactions failed")
            
            ai_response = f"""❌ **No se pudo crear la transacción**

🔍 **Razones:**\n"""
            
            for f in failed_transactions[:2]:  # Máximo 2 ejemplos
                ai_response += f"\n{f['reason']}\n"
            
            ai_response += f"""\n✅ **Para registrar correctamente:**

💵 Usa frases como:
• *"Gasté 25000 en mercado"*
• *"Le pasé 200k a mi mamá para el arriendo"*
• *"Me llegaron 50000 de salario"*
• *"Compré una pizza por 35000"*

📄 **Componentes necesarios:**
1️⃣ Monto (200000, 50k, etc.)
2️⃣ Acción (gasté, compré, me llegaron)
3️⃣ Descripción (mercado, arriendo, salario)

🔗 Si aún falla, asegúrate de tener cuentas y categorías creadas primero.
"""
        else:
            # No se detectó intención clara ni se crearon transacciones
            print(f"DEBUG CHAT: ⚠️ No transactions created, no clear reason")
            ai_response = """⚠️ **No entendí qué transacción querrías crear**

👉 **¿Qué quisiste decir?**

Si querías registrar un gasto o ingreso, intenta con frases claras:

💸 **Gastos:**
• "Gasté [monto] en [descripción]"
• "Compré [cosa] por [monto]"
• "Le pasé [monto] para [motivo]"

💰 **Ingresos:**
• "Me llegaron [monto] de [motivo]"
• "Recibí [monto] por [descripción]"
• "Ingresó mi salario de [monto]"

🤔 Si querías hacer otra cosa (consultar, analizar, etc.), ¡inténtalo de nuevo!
"""
        
        # Guardar respuesta del asistente
        assistant_message = ChatMessage(
            user_id=user_id,
            role='assistant',
            content=ai_response,
            message_metadata={'ai_service': 'transaction_detection', 'action': 'auto_transaction'}
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        return jsonify({
            'user_message': {
                'id': user_message.id,
                'role': 'user',
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat()
            },
            'assistant_message': {
                'id': assistant_message.id,
                'role': 'assistant',
                'content': assistant_message.content,
                'created_at': assistant_message.created_at.isoformat()
            }
        }), 201
    else:
        # FALLBACK CRÍTICO: Si detect_local_first falló, intentar ÚLTIMA opción antes de simulación
        # Checar si el mensaje tiene palabras claras de gasto/ingreso
        expense_keywords = ['gast', 'compr', 'comí', 'comi', 'saque', 'retire', 'pagué', 'pague', 'debit', 'cancelé', 'cancel', 'pasé', 'pase', 'presté']
        income_keywords = ['recibí', 'recibe', 'cobré', 'cobre', 'ingres', 'ganancia', 'salario', 'sueldo', 'depósito', 'deposito', 'devolución', 'vendí', 'vendi', 'me pagó', 'me pago', 'me pagaron']
        
        has_expense_word = any(keyword in user_input_clean.lower() for keyword in expense_keywords)
        has_income_word = any(keyword in user_input_clean.lower() for keyword in income_keywords)
        has_number = any(char.isdigit() for char in user_input_clean)
        
        # Si tiene palabras de transacción Y número, intentar crear real antes de simulación
        if (has_expense_word or has_income_word) and has_number:
            print(f"DEBUG CHAT: FALLBACK - Attempting to create real transaction despite no intent detection")
            
            # Intentar extraer transacción
            try:
                transaction_data = ai_service.extract_transaction_from_text(user_id, data['content'], None)
                
                if transaction_data and transaction_data.get('amount') and transaction_data.get('transaction_type') and transaction_data.get('description'):
                    # ✅ Datos válidos - CREAR TRANSACCIÓN REAL
                    print(f"DEBUG CHAT: FALLBACK SUCCESS - Creating real transaction")
                    
                    # MEJORADO: Buscar cuenta mencionada en el mensaje con aliases
                    all_accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
                    if not all_accounts:
                        ai_response = "❌ No tienes cuentas configuradas. Ve a la página de 'Cuentas' y crea una."
                        assistant_message = ChatMessage(user_id=user_id, role='assistant', content=ai_response, message_metadata={'type': 'no_account'})
                        db.session.add(assistant_message)
                        db.session.commit()
                        return jsonify({'user_message': {'id': user_message.id, 'role': 'user', 'content': user_message.content, 'created_at': user_message.created_at.isoformat()}, 'assistant_message': {'id': assistant_message.id, 'role': 'assistant', 'content': assistant_message.content, 'created_at': assistant_message.created_at.isoformat()}}), 201
                    
                    # Alias mapping para reconocer variantes
                    account_aliases = {
                        'nequi': ['nequi', 'neq', 'nqi'],
                        'nu': ['nu', 'banco nu'],
                        'efectivo': ['efectivo', 'cash', 'efecti'],
                        'banco': ['banco', 'ahorros', 'corriente'],
                        'bolsillo': ['bolsillo', 'bolsi'],
                    }
                    
                    # Buscar cuenta por nombre fuzzy match
                    account = None
                    account_names = [a.name for a in all_accounts]
                    
                    # Primero: buscar en el mensaje original patrones claros
                    msg_lower = data['content'].lower()
                    for account_obj in all_accounts:
                        account_name_lower = account_obj.name.lower()
                        # Búsqueda exacta/parcial
                        if account_name_lower in msg_lower or msg_lower in account_name_lower:
                            account = account_obj
                            break
                    
                    # Segundo: buscar usando aliases
                    if not account:
                        for alias_group, aliases in account_aliases.items():
                            if any(alias in msg_lower for alias in aliases):
                                # Buscar cuenta que contenga el alias principal
                                for account_obj in all_accounts:
                                    if alias_group.lower() in account_obj.name.lower():
                                        account = account_obj
                                        break
                                if account:
                                    break
                    
                    # Tercero: fuzzy match con todas las cuentas
                    if not account:
                        from rapidfuzz import process as rfuzz_process, fuzz
                        for account_obj in all_accounts:
                            best_match = rfuzz_process.extractOne(
                                account_obj.name, 
                                [msg_lower], 
                                scorer=fuzz.partial_ratio
                            )
                            if best_match and best_match[1] >= 40:
                                account = account_obj
                                break
                    
                    # Cuarto: Si transaction_data tiene nombre, fuzzy match
                    if not account and transaction_data.get('account'):
                        from rapidfuzz import process as rfuzz_process, fuzz
                        best_match = rfuzz_process.extractOne(
                            transaction_data['account'], 
                            account_names, 
                            scorer=fuzz.WRatio
                        )
                        if best_match and best_match[1] >= 60:
                            account = next(a for a in all_accounts if a.name == best_match[0])
                    
                    # Fallback: usar primera cuenta
                    if not account:
                        account = all_accounts[0]
                    
                    print(f"DEBUG CHAT: Selected account: {account.name} (from all: {[a.name for a in all_accounts]})")
                    
                    category = Category.query.filter_by(user_id=user_id, category_type=transaction_data['transaction_type']).first()
                    if not category:
                        default_name = 'Otros Ingresos' if transaction_data['transaction_type'] == 'income' else 'Otros'
                        category = Category(user_id=user_id, name=default_name, icon='📊', category_type=transaction_data['transaction_type'])
                        db.session.add(category)
                        db.session.commit()
                    
                    # Crear transacción
                    amount = abs(transaction_data['amount'])
                    balance_change = -amount if transaction_data['transaction_type'] == 'expense' else amount
                    new_tx = Transaction(
                        user_id=user_id, account_id=account.id, category_id=category.id,
                        amount=amount, description=transaction_data['description'],
                        transaction_type=transaction_data['transaction_type'],
                        transaction_date=datetime.utcnow()
                    )
                    account.current_balance = float(Decimal(str(account.current_balance)) + balance_change)
                    account.updated_at = datetime.utcnow()
                    db.session.add(new_tx)
                    db.session.commit()
                    
                    currency = user.preferred_currency
                    tipo = "Ingreso" if transaction_data['transaction_type'] == 'income' else "Gasto"
                    ai_response = f"""✅ **Transaccion registrada**
- **Monto:** {currency} {amount:,.2f}
- **Cuenta:** {account.name}
- **Descripcion:** {transaction_data['description']}
- **Tipo:** {tipo}

Balance actualizado: {currency} {account.current_balance:,.2f}"""
                    
                    assistant_message = ChatMessage(user_id=user_id, role='assistant', content=ai_response, message_metadata={'type': 'fallback_transaction_created'})
                    db.session.add(assistant_message)
                    db.session.commit()
                    return jsonify({'user_message': {'id': user_message.id, 'role': 'user', 'content': user_message.content, 'created_at': user_message.created_at.isoformat()}, 'assistant_message': {'id': assistant_message.id, 'role': 'assistant', 'content': assistant_message.content, 'created_at': assistant_message.created_at.isoformat()}}), 201
            except Exception as e:
                print(f"DEBUG CHAT: FALLBACK FAILED - {str(e)}")
                # Continuar a simulación
                pass
        
        # No hay intención de crear transacción.
        # Responder localmente preguntas frecuentes críticas para evitar dependencia de IA externa.
        lower_msg = user_input_clean.lower()
        asks_last_transaction = any(phrase in lower_msg for phrase in [
            'ultima transaccion', 'última transacción', 'ultimo movimiento',
            'último movimiento', 'mi ultima transaccion', 'mi última transacción'
        ])

        if asks_last_transaction:
            last_tx = Transaction.query.filter_by(user_id=user_id).order_by(
                Transaction.transaction_date.desc(), Transaction.id.desc()
            ).first()

            if not last_tx:
                ai_response = "❌ No tienes transacciones registradas todavía."
            else:
                tx_currency = user.preferred_currency
                tx_type_label = 'Ingreso' if last_tx.transaction_type == 'income' else 'Gasto'
                ai_response = f"""📌 **Tu última transacción fue:**
- **Tipo:** {tx_type_label}
- **Monto:** {tx_currency} {last_tx.amount:,.2f}
- **Cuenta:** {last_tx.account.name if last_tx.account else 'N/A'}
- **Descripción:** {last_tx.description}
- **Fecha:** {last_tx.transaction_date.strftime('%d/%m/%Y %H:%M')}"""
        else:
            # La IA maneja: consultas, análisis, consejos, gestión de cuentas, etc.
            print(f"DEBUG CHAT: No transaction intent, using AI for response (Groq)")
            ai_response = ai_service.chat(user_id, data['content'], conversation_history)
        
        # ⚠️ ADVERTENCIA: Si la IA menciona "transacción registrada" pero NO creó nada
        if any(keyword in ai_response.lower() for keyword in ['transacción registrada', 'balance actualizado', 'gasto registrado']):
            print(f"DEBUG CHAT: ⚠️️ AI simulated transaction without creating it!")
            ai_response += "\n\n⚠️ **Nota:** Esta es solo una simulacion. Para crear transacciones reales, usa frases como:\n• *'Gaste 25000 en mercado'*\n• *'Le pase 200k para arriendo'*"
    
    # Guardar respuesta del asistente en la base de datos
    response_metadata = {'ai_service': 'groq', 'processed': True}
    if not intent or not intent.get('has_intent') or wants_simulation:
        response_metadata['no_side_effects'] = True

    assistant_message = ChatMessage(
        user_id=user_id,
        role='assistant',
        content=ai_response,
        message_metadata=response_metadata
    )
    
    db.session.add(assistant_message)
    db.session.commit()
    
    return jsonify({
        'user_message': {
        'id': user_message.id,
        'role': 'user',
        'content': user_message.content,
        'created_at': user_message.created_at.isoformat()
        },
        'assistant_message': {
        'id': assistant_message.id,
        'role': 'assistant',
        'content': assistant_message.content,
        'created_at': assistant_message.created_at.isoformat()
        }
    }), 201


# ==========================================
# CONFIRM TRANSACTION ENDPOINT
# ==========================================

@chat_bp.route('/confirm-transaction', methods=['POST'])
def confirm_transaction():
    """
    Endpoint para confirmar y guardar transacción desde UI de confirmación visual
    Recibe: datos de transacción confirmados por el usuario
    Retorna: success + transaction_id
    """
    user, error = get_user()
    if error:
        return error
    
    user_id = user.id
    data = request.get_json()
    
    try:
        # Validar datos requeridos
        if not data.get('account_id'):
            return jsonify({'success': False, 'error': 'Cuenta no especificada'}), 400
        
        if not data.get('amount'):
            return jsonify({'success': False, 'error': 'Monto no especificado'}), 400
        
        # Buscar cuenta
        account = Account.query.filter_by(
            id=data['account_id'],
            user_id=user_id,
            is_active=True
        ).first()
        
        if not account:
            return jsonify({'success': False, 'error': 'Cuenta no encontrada'}), 404
        
        # Buscar categoría (opcional)
        category = None
        if data.get('category_id'):
            category = Category.query.filter_by(
                id=data['category_id'],
                user_id=user_id
            ).first()
        
        # Determinar tipo de transacción
        tx_type = data.get('type', 'expense')
        amount = float(data['amount'])
        
        # Crear transacción
        new_transaction = Transaction(
            user_id=user_id,
            account_id=account.id,
            category_id=category.id if category else None,
            amount=amount if tx_type == 'income' else -abs(amount),
            description=data.get('description', ''),
            transaction_type=tx_type,
            transaction_date=datetime.utcnow()
        )
        
        # Actualizar balance de cuenta
        if tx_type == 'expense':
            account.current_balance -= abs(amount)
        else:
            account.current_balance += abs(amount)
        
        account.updated_at = datetime.utcnow()
        
        # Guardar en BD
        db.session.add(new_transaction)
        db.session.commit()
        
        # Guardar mensaje de confirmación en el chat
        currency = user.preferred_currency or 'COP'
        confirmation_msg = f"""✅ **¡Transacción guardada!**
- **Monto:** {currency} {abs(amount):,.2f}
- **Cuenta:** {account.name}
- **Categoría:** {category.name if category else 'Sin categoría'}
- **Tipo:** {'Ingreso' if tx_type == 'income' else 'Gasto'}

💰 **Nuevo balance:** {currency} {account.current_balance:,.2f}"""
        
        assistant_message = ChatMessage(
            user_id=user_id,
            role='assistant',
            content=confirmation_msg,
            message_metadata={
                'type': 'transaction_confirmed',
                'transaction_id': new_transaction.id,
                'ai_service': 'improved_ai'
            }
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction_id': new_transaction.id,
            'message': 'Transacción registrada exitosamente',
            'new_balance': float(account.current_balance)
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Valor inválido: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error confirmando transacción: {e}")
        return jsonify({
            'success': False,
            'error': f'Error al guardar transacción: {str(e)}'
        }), 500


# ==========================================
# VOICE CHAT ENDPOINTS
# ==========================================

@chat_bp.route('/voice/process', methods=['POST'])
def voice_process():
    """
    Procesa comando de voz del usuario
    Acepta: audio en base64 o transcripción ya hecha
    Retorna: respuesta en texto y audio
    """
    user, error = get_user()
    if error:
        return error
    
    try:
        import base64
        from pathlib import Path
        import uuid
        
        data = request.get_json(silent=True) or {}
        
        # Opción 1: Transcripción ya hecha (Web Speech API desde frontend)
        if 'transcription' in data and isinstance(data['transcription'], str):
            transcription = data['transcription'].strip()
            if not transcription:
                return jsonify({'error': 'La transcripción está vacía'}), 400
            print("[VOICE] ✅ Using frontend transcription (Web Speech API)")
        
        # Opción 2: Audio para transcribir en backend (Deepgram)
        elif 'audio' in data:
            from services.voice_service import voice_service
            if not voice_service.enabled:
                return jsonify({
                    'error': 'Transcripción de audio no disponible en el servidor',
                    'details': 'Deepgram no está configurado o no está disponible',
                    'hint': 'Usa el envío por transcripción de texto desde frontend'
                }), 503

            # Decodificar audio de base64
            try:
                audio_base64 = data['audio']
                if isinstance(audio_base64, str) and audio_base64.startswith('data:'):
                    # Formato data: URL
                    audio_base64 = audio_base64.split(',')[1]
                audio_data = base64.b64decode(audio_base64)
            except Exception as e:
                print(f"[VOICE] ❌ Error decodificando audio: {e}")
                return jsonify({
                    'error': 'El audio está corrupto o mal formateado',
                    'details': str(e)
                }), 400
            
            # Transcribir directamente con los datos binarios (más eficiente)
            try:
                transcription = voice_service.transcribe(audio_data)
            except Exception as e:
                error_msg = str(e)
                
                # Clasificar tipo de error
                if '401' in error_msg or 'Invalid API Key' in error_msg:
                    print(f"[VOICE] ❌ Auth error: {error_msg}")
                    return jsonify({
                        'error': 'Error de autenticación con Deepgram',
                        'details': 'API Key inválido o expirado',
                        'hint': 'Verifica que DEEPGRAM_API_KEY sea correcto en .env'
                    }), 503
                
                # Errores del cliente (audio inválido, silencio, etc)
                elif any(keyword in error_msg for keyword in ['silencio', 'sin resultados', 'muy corto', 'sin canales', 'lenguaje no detectado', 'confidence']):
                    print(f"[VOICE] ⚠️ Invalid audio: {error_msg}")
                    return jsonify({
                        'error': 'No se pudo reconocer el audio',
                        'details': error_msg,
                        'hint': 'Asegúrate de hablar claramente y en español. El audio puede estar muy bajo, cortado o ser solo ruido.'
                    }), 400
                
                # Otros errores (rate limit, timeout, etc)
                else:
                    print(f"[VOICE] ❌ Deepgram error: {error_msg}")
                    return jsonify({
                        'error': 'Error transcribiendo audio',
                        'details': error_msg,
                        'hint': 'Intenta nuevamente en unos segundos'
                    }), 503
            
            print("[VOICE] ✅ Using backend transcription (Deepgram)")
        
        else:
            return jsonify({
                'error': 'Se requiere "transcription" o "audio"'
            }), 400
        
        # Guardar mensaje del usuario
        user_message = ChatMessage(
            user_id=user.id,
            role='user',
            content=transcription,
            message_metadata={'input_type': 'voice'}
        )
        db.session.add(user_message)
        db.session.commit()
        
        # Procesar con IA (Groq)
        response_text = ai_service.chat(user.id, transcription)
        
        # Guardar respuesta
        assistant_message = ChatMessage(
            user_id=user.id,
            role='assistant',
            content=response_text,
            message_metadata={'input_type': 'voice', 'output_type': 'voice'}
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        # Generar audio de respuesta
        audio_response_data = None
        audio_format = None
        tts_warning = None
        
        try:
            from services.tts_service import tts_service
            
            try:
                audio_path = tts_service.synthesize(response_text)
                
                # Validar que el archivo existe y tiene contenido
                if not audio_path.exists():
                    raise Exception(f"Audio file not created: {audio_path}")
                
                if audio_path.stat().st_size == 0:
                    raise Exception(f"Audio file is empty: {audio_path}")
                
                # Leer audio generado y convertir a base64
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()
                    if len(audio_data) > 0:
                        audio_response_data = base64.b64encode(audio_data).decode('utf-8')
                        audio_format = 'mp3'
                        print(f"[VOICE] ✅ Audio generated: {len(audio_data)} bytes")
                    else:
                        raise Exception("Audio file contains no data")
                        
            except Exception as tts_error:
                tts_error_msg = str(tts_error)
                print(f"[VOICE] ⚠️ TTS error: {tts_error_msg}")
                
                # No fallar completamente, solo advertir
                tts_warning = f"Audio generation failed: {tts_error_msg}"
                # El usuario recibirá la respuesta de texto aunque no tenga audio
                
        except Exception as e:
            print(f"[VOICE] ⚠️ Unexpected TTS error: {e}")
            tts_warning = f"TTS system error: {str(e)}"
        
        print(f"[VOICE] ✅ Response generated for user {user.id}")
        
        # Devolver siempre 200 con respuesta de texto (audio es optional)
        return jsonify({
            'transcription': transcription,
            'response_text': response_text,
            'response_audio': audio_response_data,
            'audio_format': audio_format,
            'tts_warning': tts_warning,
            'user_message_id': user_message.id,
            'assistant_message_id': assistant_message.id
        }), 200
        
    except Exception as e:
        print(f"[VOICE] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error procesando comando de voz',
            'details': str(e)
        }), 500


@chat_bp.route('/voice/test', methods=['GET'])
def voice_test():
    """
    Endpoint de prueba para verificar que los servicios de voz funcionan
    """
    try:
        from services.voice_service import voice_service
        from services.tts_service import tts_service
        
        return jsonify({
            'voice_enabled': voice_service.enabled,
            'tts_enabled': True,
            'message': '✅ Servicios de voz configurados correctamente' if voice_service.enabled else '⚠️ Deepgram no configurado'
        }), 200
        
    except Exception as e:
        return jsonify({
            'voice_enabled': False,
            'tts_enabled': False,
            'error': str(e)
        }), 500