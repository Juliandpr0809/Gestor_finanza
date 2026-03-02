"""
Servicio de IA para chat financiero usando Groq API
"""
import os
import requests
from datetime import datetime
from models import db, Transaction, Category, Account

# Coincidencia difusa opcional para tolerar typos/variantes
try:
    from rapidfuzz import fuzz, process
except ImportError:
    fuzz = None
    process = None

class AIService:
    """Servicio para interactuar con Groq API"""
    
    def __init__(self):
        # Intentar GROQ_API_KEY primero, luego GROK_API_KEY (alias)
        self.api_key = os.environ.get('GROQ_API_KEY') or os.environ.get('GROK_API_KEY')
        self.api_base = os.environ.get('GROQ_API_BASE', 'https://api.groq.com/openai/v1')
        self.model = os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile')  # Modelo activo 2026
        self.enabled = bool(self.api_key)
        
        # OPTIMIZACIÓN: Modo agresivo (reduce 90% llamadas API)
        self.ai_mode = os.environ.get('AI_MODE', 'optimized')  # optimized, full, disabled
        self.response_cache = {}  # Cache de respuestas comunes
        self.api_calls_count = 0  # Contador de llamadas (solo estadística)
        
        if not self.enabled:
            print("[WARNING] No GROQ_API_KEY o GROK_API_KEY found in environment")
        
        print(f"[AI SERVICE] Mode: {self.ai_mode}, Enabled: {self.enabled}")
    
    def get_user_context(self, user_id):
        """Obtiene contexto financiero del usuario CON MONEDA"""
        try:
            # Obtener usuario para saber su moneda
            from models import User
            user = User.query.get(user_id)
            currency = user.preferred_currency if user else 'USD'
            
            # Resumen de cuentas con detalles
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            print(f"DEBUG: Found {len(accounts)} accounts for user {user_id} with currency {currency}")
            
            total_balance = sum(a.current_balance for a in accounts)
            print(f"DEBUG: Total balance: {total_balance} {currency}")
            
            accounts_info = [{
                'name': a.name,
                'type': a.account_type,
                'balance': f'{currency} {a.current_balance:,.2f}',
                'balance_raw': a.current_balance,
                'currency': a.currency
            } for a in accounts]
            
            # Resumen de transacciones recientes con detalles
            recent_txs = Transaction.query.filter_by(user_id=user_id).order_by(
                Transaction.transaction_date.desc()
            ).limit(10).all()
            
            print(f"DEBUG: Found {len(recent_txs)} recent transactions")
            
            recent_txs_info = [{
                'date': t.transaction_date.strftime('%Y-%m-%d'),
                'description': t.description,
                'amount': f'{currency} {abs(t.amount):,.2f}',
                'type': t.transaction_type,
                'category': t.category.name if t.category else 'Sin categoría',
                'account': t.account.name if t.account else 'Cuenta desconocida'
            } for t in recent_txs]
            
            # Gastos por categoría
            categories_summary = db.session.query(
                Category.name,
                db.func.sum(Transaction.amount).label('total')
            ).join(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense'
            ).group_by(Category.name).all()
            
            # Todas las categorías disponibles
            all_categories = Category.query.filter_by(user_id=user_id).all()
            categories_list = [{'name': c.name, 'icon': c.icon} for c in all_categories]
            
            # 📊 ESTADÍSTICAS DEL MES ACTUAL
            from datetime import datetime, date
            from sqlalchemy import extract
            
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Gastos del mes
            month_expenses = db.session.query(
                db.func.sum(Transaction.amount)
            ).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                extract('month', Transaction.transaction_date) == current_month,
                extract('year', Transaction.transaction_date) == current_year
            ).scalar() or 0
            
            # Ingresos del mes
            month_income = db.session.query(
                db.func.sum(Transaction.amount)
            ).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'income',
                extract('month', Transaction.transaction_date) == current_month,
                extract('year', Transaction.transaction_date) == current_year
            ).scalar() or 0
            
            # Gastos por categoría del mes
            month_categories = db.session.query(
                Category.name,
                db.func.sum(Transaction.amount).label('total')
            ).join(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                extract('month', Transaction.transaction_date) == current_month,
                extract('year', Transaction.transaction_date) == current_year
            ).group_by(Category.name).order_by(db.func.sum(Transaction.amount).desc()).all()
            
            # 📊 CONTEO DE TRANSACCIONES DEL MES (para análisis)
            month_tx_count = db.session.query(
                db.func.count(Transaction.id)
            ).filter(
                Transaction.user_id == user_id,
                extract('month', Transaction.transaction_date) == current_month,
                extract('year', Transaction.transaction_date) == current_year
            ).scalar() or 0
            
            # Promedio de gasto por transacción
            avg_transaction = (abs(month_expenses) / month_tx_count) if month_tx_count > 0 else 0
            
            context = {
                'currency': currency,  # AGREGADO: Moneda del usuario
                'total_balance': f'{currency} {total_balance:,.2f}',
                'total_balance_raw': total_balance,
                'accounts_count': len(accounts),
                'accounts': accounts_info,
                'recent_transactions_count': len(recent_txs),
                'recent_transactions': recent_txs_info,
                'categories': [{'name': c[0], 'total': f'{currency} {float(c[1]):,.2f}'} for c in categories_summary],
                'available_categories': categories_list,
                # 📊 NUEVO: Estadísticas del mes
                'month_expenses': f'{currency} {abs(month_expenses):,.2f}',
                'month_expenses_raw': abs(month_expenses),
                'month_income': f'{currency} {abs(month_income):,.2f}',
                'month_income_raw': abs(month_income),
                'month_net': f'{currency} {(month_income - abs(month_expenses)):,.2f}',
                'month_net_raw': (month_income - abs(month_expenses)),
                'month_categories': [{'name': c[0], 'total': f'{currency} {abs(float(c[1])):,.2f}', 'total_raw': abs(float(c[1]))} for c in month_categories],
                # 📊 Análisis adicional
                'month_tx_count': month_tx_count,
                'avg_transaction': f'{currency} {avg_transaction:,.2f}',
                'savings_rate': f'{((month_income - abs(month_expenses)) / month_income * 100):.1f}%' if month_income > 0 else '0%',
            }
            
            print(f"DEBUG: Context created with balance {context['total_balance']}")
            return context
        except Exception as e:
            print(f"ERROR in get_user_context: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def get_cached_response(self, message_lower):
        """Retorna respuesta cacheada para preguntas comunes (ahorra API calls)"""
        common_responses = {
            'hola': '👋 ¡Hola! ¿En qué puedo ayudarte con tus finanzas?',
            'ayuda': '💡 Puedo ayudarte a registrar gastos, ingresos, ver tu balance y más. ¿Qué necesitas?',
            'help': '💡 Puedo ayudarte a registrar gastos, ingresos, ver tu balance y más. ¿Qué necesitas?',
            'gracias': '😊 ¡De nada! ¿Necesitas algo más?',
            'adios': '👋 ¡Hasta luego! Que tengas un buen día.',
            'bye': '👋 ¡Hasta luego! Que tengas un buen día.',
        }
        
        for key, response in common_responses.items():
            if key in message_lower:
                return response
        
        return None
    
    def chat(self, user_id, message, conversation_history=None):
        """
        Envía mensaje a Groq y obtiene respuesta
        
        Args:
            user_id: ID del usuario
            message: Mensaje del usuario
            conversation_history: Lista de mensajes previos [{role, content}]
        
        Returns:
            str: Respuesta del asistente
        """
        if not self.enabled:
            return "⚠️ Servicio de IA no configurado. Configure GROQ_API_KEY en .env"
        
        try:
            # Obtener contexto financiero
            context = self.get_user_context(user_id)
            
            print(f"DEBUG: Context received: accounts={context.get('accounts_count', 0)}, balance={context.get('total_balance', 'N/A')}")
            
            # Construir información de cuentas
            accounts_list = context.get('accounts', [])
            if accounts_list:
                accounts_text = '\n'.join([
                    f"  • {a['name']} ({a['type']}): {a['balance']} {a['currency']}" 
                    for a in accounts_list
                ])
            else:
                accounts_text = '  • Sin cuentas registradas'
            
            # Construir información de transacciones recientes
            recent_txs_list = context.get('recent_transactions', [])
            if recent_txs_list:
                recent_txs_text = '\n'.join([
                    f"  • {t['date']}: {t['description']} - {t['amount']} - {t['account']} ({t['category']})" 
                    for t in recent_txs_list[:5]
                ])
            else:
                recent_txs_text = '  • Sin transacciones registradas'
            
            # Construir prompt del sistema con los datos reales
            currency = context.get('currency', 'USD')
            
            # Construir resumen de gastos del mes por categoría
            month_categories_list = context.get('month_categories', [])
            if month_categories_list:
                month_categories_text = '\n'.join([
                    f"  • {c['name']}: {c['total']}" 
                    for c in month_categories_list[:5]  # Top 5 categorías
                ])
            else:
                month_categories_text = '  • Sin gastos registrados este mes'
            
            system_prompt = f"""Eres un asistente financiero experto en español. Ayudas a los usuarios a gestionar sus finanzas personales.

⚠️ **INFORMACIÓN CRÍTICA - MONEDA DEL USUARIO: {currency}**
TODOS LOS MONTOS ESTÁN EN {currency}. SIEMPRE INCLUYE LA MONEDA {currency} EN TUS RESPUESTAS.

📊 CONTEXTO FINANCIERO DEL USUARIO:

Balance Total: {context.get('total_balance', f'{currency} 0.00')}
Número de Cuentas: {context.get('accounts_count', 0)}
Moneda: {currency}

🏦 CUENTAS DISPONIBLES:
{accounts_text}

📊 ESTADÍSTICAS DEL MES ACTUAL:
  💸 Total Gastado: {context.get('month_expenses', f'{currency} 0.00')}
  💰 Total Ingresado: {context.get('month_income', f'{currency} 0.00')}
  📈 Balance Mensual: {context.get('month_net', f'{currency} 0.00')}
  📊 Número de Transacciones: {context.get('month_tx_count', 0)}
  📊 Gasto Promedio por Transacción: {context.get('avg_transaction', f'{currency} 0.00')}
  💹 Tasa de Ahorro del Mes: {context.get('savings_rate', '0%')}

📊 GASTOS POR CATEGORÍA (MES ACTUAL):
{month_categories_text}

📋 ÚLTIMAS TRANSACCIONES:
{recent_txs_text}

💡 INSTRUCCIONES IMPORTANTES:
1. SIEMPRE incluye la moneda "{currency}" en TODOS los montos que menciones
2. SIEMPRE usa los datos reales del contexto anterior en tus respuestas
3. Si el usuario pregunta por su balance, usa el Balance Total mostrado arriba y SIEMPRE añade la moneda
4. Si el usuario pregunta por sus cuentas, menciona las cuentas listadas arriba con sus montos EN {currency}
5. Si el usuario pregunta por transacciones, usa las transacciones mostradas arriba (todas EN {currency})
6. **Si el usuario pregunta "cuánto gasté este mes" o similar, usa el "Total Gastado" de ESTADÍSTICAS DEL MES**
7. **Si pregunta por categorías del mes, usa "GASTOS POR CATEGORÍA (MES ACTUAL)"**
8. **Si pregunta balance del mes, usa "Balance Mensual" (ingresos - gastos del mes)**
9. Responde en español de forma clara y concisa
10. Usa formato de números con separadores de miles: {currency} 1,234.56
11. Usa emojis relevantes (💰 📊 💳 📈 📉 💡 ⚠️ ✅ 🏦)
12. NUNCA uses "$" sin la moneda - siempre escribe el código de moneda ({currency})

🎯 **ANÁLISIS PROFUNDO - SIEMPRE QUE SEA CONSULTA:**
Cuando el usuario pregunta sobre gastos, ingresos o balance, NO solo des el número. ANALIZA:

📊 **Para consultas de gastos del mes:**
- Monto total gastado (de ESTADÍSTICAS DEL MES)
- Desglose por categorías (muestra las TOP 3-5 de GASTOS POR CATEGORÍA)
- Porcentaje de cada categoría sobre el total
- Identifica la categoría con más gasto
- Análisis: ¿Es razonable? ¿Dónde hay oportunidad de ahorro?
- Compara con ingresos: ¿Gasta más o menos de lo que ingresa?

📈 **Para consultas de balance:**
- Balance total actual
- Balance mensual (ingresos vs gastos del mes)
- Salud financiera: ¿Positivo o negativo?
- Tendencia: ¿Está ahorrando o gastando más de lo que ingresa?
- Consejos específicos basados en los datos

💰 **Para consultas de categorías:**
- Lista completa de GASTOS POR CATEGORÍA (MES ACTUAL)
- Identifica las TOP 3 categorías de mayor gasto
- Calcula porcentaje de cada una
- Análisis: ¿Cuál categoría podría optimizarse?
- Sugerencias concretas para reducir gastos

🏦 **Para consultas de cuentas:**
- Lista todas las cuentas con sus balances
- Identifica cuál tiene más/menos dinero
- Sugiere distribución óptima si aplica
- Recomienda si necesita crear más cuentas

⚠️ **IMPORTANTE - SÉ ANALÍTICO, NO SOLO INFORMATIVO:**
- NO digas solo "has gastado X" - EXPLICA qué significa ese gasto
- NO listes categorías sin análisis - INTERPRETA los patrones
- NO des números secos - CONTEXTUALIZA con porcentajes y comparaciones
- SIEMPRE termina con un consejo o insight útil
- USA DATOS REALES del contexto, NUNCA inventes números

📝 **EJEMPLO DE RESPUESTA ANALÍTICA CORRECTA:**
Usuario: "cuánto gasté este mes"

❌ RESPUESTA MALA (no hagas esto):
"Has gastado COP 62,000.00 este mes."

✅ RESPUESTA BUENA (haz esto):
"📊 **Análisis de tus gastos este mes:**

Has gastado **COP 62,000.00** en enero, con un total de 2 transacciones registradas:

💸 **Desglose por categoría:**
• Otros Gastos: COP 50,000.00 (80.6%)
• Ropa: COP 12,000.00 (19.4%)

📈 **Balance mensual:**
• Ingresos: COP 0.00
• Gastos: COP 62,000.00
• Balance: COP -62,000.00 ⚠️

💡 **Insights:**
- Tu categoría con mayor gasto es "Otros Gastos" (80.6%)
- Aún no has registrado ingresos este mes
- Tasa de ahorro: 0% (necesitas registrar ingresos)

🎯 **Recomendaciones:**
1. Registra tus ingresos para tener un panorama completo
2. Considera categorizar mejor tus gastos para análisis más precisos
3. Si estos son todos tus gastos, estás dentro de un control razonable"

📌 **REGLA FINAL:** Cada respuesta debe incluir:
1. Monto principal con moneda
2. Contexto (transacciones, categorías, porcentajes)
3. Comparación o análisis
4. Insight o conclusión
5. Consejo o recomendación accionable

� **CAPACIDADES DEL SISTEMA - LO QUE SÍ PUEDES HACER:**

✅ **CREAR CUENTAS:**
El sistema PUEDE crear cuentas automáticamente con comandos como:
- "crea una cuenta de efectivo llamada Bolsillo con saldo de 1000"
- "crear cuenta de tarjeta llamada Visa con 50000"
- "nueva cuenta de ahorro llamada Emergencias con 100000"

✅ **CREAR TRANSACCIONES:**
El sistema CREA transacciones REALES automáticamente cuando el usuario dice:
- "compré 25000 en mercado"
- "me gasté 2300 en agua"
- "me ingresaron 120000 de mi salario"
- "registra un gasto de 15000 en transporte"

✅ **MODIFICAR BALANCE:**
El sistema PUEDE cambiar el balance de cuentas:
- "cambiar balance de Nequi a 50000"
- "ajustar saldo de Efectivo en 10000"

✅ **RENOMBRAR CUENTAS:**
El sistema PUEDE renombrar cuentas DIRECTAMENTE:
- "cambia el nombre de mi cuenta 2 para que se llame Bolsillo"
- "renombrar cuenta Nequi a MiTarjeta"  
- "modificar nombre de cuenta efectivo a Billetera"
NO digas que hay que crear nueva cuenta y transferir - ¡RENOMBRA DIRECTAMENTE!

✅ **BORRAR/EDITAR TRANSACCIONES:**
El sistema PUEDE borrar y editar transacciones:
- "borrar la última transacción"
- "editar la transacción de 2300"

✅ **RESETEAR BALANCE:**
El sistema PUEDE resetear balances:
- "resetear balance de Nequi"
- "volver balance inicial"

⚠️ **LO QUE NO PUEDES HACER (pero el sistema SÍ):**
- NO digas "no es posible crear cuentas" - ¡SÍ ES POSIBLE!
- NO digas "no puedo renombrar cuentas" - ¡SÍ SE PUEDE RENOMBRAR DIRECTAMENTE!
- NO digas "hay que crear nueva cuenta y transferir" - ¡USA EL COMANDO DE RENOMBRAR!
- NO digas "debes hacerlo en la aplicación" - TODO se hace aquí

🚫 **NUNCA RESPONDAS SOBRE COMANDOS DESTRUCTIVOS SIN CONFIRMACIÓN:**
Si el usuario pide:
- "elimina todas las transacciones" / "elimina todas" / "borrar todo"
- "dejar cuentas en 0" / "poner cuentas en 0"
- "resetear balance"

🚨 **NO INVENTES QUE LO HICISTE** - Di SOLAMENTE:
"⚠️ Esa acción requiere confirmación explícita. Por favor, escribe exactamente lo que necesitas que haga."

❌ **NUNCA digas:**
- "¡Entendido! Todas las transacciones han sido eliminadas."
- "Todas las cuentas han sido reseteadas a COP 0.00."
- "He eliminado todas las transacciones."

✅ **DI SIEMPRE:**
- "Esa acción destructiva requiere confirmación. ¿Qué necesitas específicamente?"
- "No puedo ejecutar comandos destructivos sin confirmación explícita."

🗣️ **CUANDO EL USUARIO PREGUNTA SI PUEDES HACER ALGO:**
- Si pregunta "¿puedes crear una cuenta?" → Responde: "¡Sí! Solo dime el nombre, tipo y saldo"
- Si pregunta "¿puedes cambiar el nombre?" → Responde: "¡Claro! Dime qué cuenta y el nuevo nombre"
- Si pregunta "¿puedes renombrar?" → Responde: "¡Por supuesto! Indícame la cuenta y el nuevo nombre"
- Si pregunta "¿puedes cambiar el balance?" → Responde: "¡Claro! Indícame la cuenta y el nuevo saldo"
- Si pregunta "¿puedes borrar una transacción?" → Responde: "¡Sí! ¿Cuál transacción?"

✅ Cuando el usuario pregunta algo (sin crear transacción), proporciona análisis y consejos basados en los datos REALES, SIEMPRE incluyendo {currency}.

📌 REGLA ORO: Cada vez que menciones un número de dinero, escribe así: "{currency} NÚMERO"
Ejemplo correcto: "Tu balance es {currency} 1,234.56"
Ejemplo INCORRECTO: "Tu balance es $1,234.56" o "Tu balance es 1,234.56"

Proporciona análisis y consejos útiles basados en los datos REALES mostrados arriba."""

            print(f"DEBUG: System prompt created, length: {len(system_prompt)}")
            
            # Construir mensajes
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Agregar historial si existe
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Últimos 10 mensajes
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": message})
            
            # Llamar a Groq API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"Error API ({response.status_code}): {response.text}"
                return f"⚠️ {error_msg}"
                
        except requests.exceptions.Timeout:
            return "⚠️ Tiempo de espera agotado. Intenta de nuevo."
        except requests.exceptions.RequestException as e:
            return f"⚠️ Error de conexión: {str(e)}"
        except Exception as e:
            return f"⚠️ Error inesperado: {str(e)}"
    
    def detect_command_with_ai(self, user_id, message):
        """
        Usa IA para detectar comandos - VERSIÓN SIMPLIFICADA
        Si falla, retorna None para que caiga al fallback de regex
        """
        if not self.enabled:
            return None
        
        try:
            # Obtener cuentas del usuario
            from models import User
            user = User.query.get(user_id)
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            
            accounts_list = ", ".join([f"{a.name} (ID: {i+1})" for i, a in enumerate(accounts)])
            
            # PROMPT MÁS SIMPLE Y SEGURO
            prompt = f"""Eres un clasificador de intenciones. El usuario escribió: "{message}"

Cuentas disponibles: {accounts_list}

Clasifica SOLO con una de estas palabras:
- "rename" si dice renombra/cambiar nombre de cuenta
- "create_account" si dice crea/nueva cuenta
- "set_balance" si dice cambiar/ajustar balance/saldo
- "income" si dice ingresó/me dieron/cobré
- "expense" si dice gasté/compré/pagué
- "chat" para todo lo demás

Responde SOLO UNA palabra, sin explicación."""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,  # Temperature más baja para respuestas consistentes
                "max_tokens": 20  # Solo necesita una palabra
            }
            
            print(f"DEBUG: Sending to Groq API: model={self.model}, prompt_len={len(prompt)}")
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10  # Timeout más corto
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip().lower()
                
                print(f"DEBUG: Groq response: '{content}'")
                
                if not content:
                    print(f"WARNING: Groq returned empty response")
                    return None
                
                # Parsear respuesta simple (una palabra)
                if 'rename' in content:
                    return {'command': 'rename_account', 'params': {}}
                elif 'create_account' in content:
                    return {'command': 'create_account', 'params': {}}
                elif 'set_balance' in content:
                    return {'command': 'set_balance', 'params': {}}
                elif 'income' in content:
                    return {'command': 'create_transaction', 'params': {'transaction_type': 'income'}}
                elif 'expense' in content:
                    return {'command': 'create_transaction', 'params': {'transaction_type': 'expense'}}
                else:
                    return None
            else:
                print(f"ERROR: Groq API returned {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"ERROR: Groq API timeout")
            return None
        except Exception as e:
            print(f"ERROR in detect_command_with_ai: {e}")
            return None
    
    def analyze_spending(self, user_id, period='month'):
        """Analiza patrones de gasto del usuario"""
        if not self.enabled:
            return "Servicio de IA no configurado"
        
        try:
            context = self.get_user_context(user_id)
            total_balance = context.get('total_balance', 0)
            
            prompt = f"""Analiza los siguientes datos financieros y proporciona insights:

Balance: {total_balance}
Categorías de gasto: {context.get('categories', [])}

Proporciona:
1. Patrón principal de gastos
2. Recomendación de ahorro
3. Área de mejora

Sé conciso y práctico."""

            messages = [
                {"role": "system", "content": "Eres un analista financiero experto."},
                {"role": "user", "content": prompt}
            ]
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.5,
                "max_tokens": 400
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error al analizar: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def detect_local_first(self, message, user_id=None):
        """
        OPTIMIZACIÓN AGRESIVA: Detecta transacciones localmente PRIMERO
        Solo llama a la IA si la detección local falla completamente
        Reduce ~90% de llamadas a la API
        """
        # 1. Primero intentar detección local completa
        local_result = self.detect_transaction_intent(message)
        
        if local_result:
            print("[OPTIMIZATION] ✅ Detected locally (no API call)")
            return local_result
        
        # 2. Si falla, verificar cache para respuestas comunes
        cache_key = message.lower().strip()
        if cache_key in self.response_cache:
            print("[OPTIMIZATION] ✅ Response from cache (no API call)")
            return self.response_cache[cache_key]
        
        # 3. Solo si modo permite IA y es necesario, llamar API
        if self.ai_mode == 'disabled':
            print("[OPTIMIZATION] ⚠️ AI disabled, using local only")
            return None
        
        if self.ai_mode == 'optimized':
            # En modo optimizado, solo llamar IA para casos complejos
            # Si no tiene números Y no tiene palabras clave claras, probablemente no es transacción
            import re
            has_number = bool(re.search(r'\d+', message.lower()))
            expense_words = ['gast', 'compr', 'pagué', 'pague']
            income_words = ['recib', 'ingres', 'llegó', 'llego']
            has_clear_intent = any(w in message.lower() for w in expense_words + income_words)
            
            if not has_number and not has_clear_intent:
                print("[OPTIMIZATION] ⚠️ No clear transaction pattern, skipping AI")
                return None
        
        print("[OPTIMIZATION] ⚡ Calling AI API (fallback for complex case)")
        self.api_calls_count += 1
        return None  # Dejamos que el flujo normal llame a la IA
    
    def detect_transaction_intent(self, message):
        """
        Detecta si el mensaje del usuario contiene intención de crear transacciones
        MEJORADO: Detección ultra inteligente con múltiples variaciones
        Detecta MÚLTIPLES transacciones en un solo mensaje
        
        Returns:
            dict: {'has_intent': bool, 'transaction_parts': list, ...} o None
        """
        # PALABRAS CLAVE EXPANDIDAS RADICALMENTE
        keywords_create = [
            'registra', 'agrega', 'crea', 'anota', 'guarda', 'añade', 
            'registrar', 'crear', 'agregar', 'anotar', 'guardar',
            'registro', 'cree', 'graba', 'grabar', 'apunta', 'apuntar',
            'anotame', 'registrame', 'guardame', 'ponle', 'agregale',
        ]
        
        # GASTOS / EGRESOS - Palabras que indican SALIDA de dinero
        keywords_expense = [
            # Verbos directos
            'gast', 'compré', 'compre', 'compr', 'compra', 'comprado',
            'comí', 'comi', 'me comí', 'me comi',
            'pagué', 'pague', 'pagado', 'pago', 'pagar',
            'retiré', 'retire', 'retiro', 'saqué', 'saque', 'saco',
            'transferí', 'transferencia', 'enviado', 'envié', 'envio',
            'debit', 'débito', 'debitaron', 'debitado',
            'cancelé', 'cancelada', 'cancel',
            'consumí', 'consumi', 'consumo', 'consumida',
            'invertí', 'invert', 'inversión', 'invertida',
            'aboné', 'abone', 'abonado',
            'perdí', 'pierdo', 'perdida',
            'pasé', 'pase', 'paso', 'pasó',  # "Le pasé dinero"
            'di', 'dí', 'dio', 'dado',  # "Le di dinero"
            'presté', 'preste', 'prestado',  # "Le presté dinero"
            # Expresiones comunes
            'se fue', 'salió', 'salio', 'salida',
            'me cobraron', 'me cobro', 'me cobr',
            'me debitaron', 'me debit',
            'me quitaron', 'me quit',
            'me costó', 'me costo',
            'pago de', 'compra de', 'gasto en', 'retiro de',
            'cuota', 'suscripción', 'mensualidad', 'comisión', 'multa', 'recargo', 'interés',
        ]
        
        # INGRESOS - Palabras que indican ENTRADA de dinero
        keywords_income = [
            # Verbos directos
            'ingres', 'ingresa', 'ingresó',
            'recibí', 'recibe', 'recibido', 'recib',
            'cobré', 'cobre', 'cobrado', 'cobr',
            'pagó', 'pago', 'consignó', 'consigno', 'transferido',
            'ganancia', 'gané', 'gano', 'ganador',
            'depositaron', 'depósito', 'deposito', 'depos',
            'acreditaron', 'acreditada', 'crédito', 'acredit',
            'vendí', 'vendi', 'vendida', 'venta',
            'pagaron', 'pagada', 'pagado',
            'reembolso', 'reembolsaron', 'reembolsa',
            'devolvieron', 'devuelto', 'devolución',
            'facturación', 'facturé',
            'generé', 'generada', 'generado',
            'regalaron', 'regalo', 'regal',  # regalos/dádivas
            # Expresiones comunes con "me"
            'me llegó', 'me llego', 'me llegaron',
            'me depositaron', 'me depos',
            'me acreditaron', 'me acredit',
            'me pagaron', 'me pagó', 'me pago', 'me pagar',
            'me dieron', 'me regalo',
            # Sustantivos de ingreso
            'salario', 'sueldo', 'nómina', 'propina',
            'comisión', 'bono', 'premio', 'ganancia',
            'venta', 'devolución', 'reembolso',
        ]
        
        message_lower = message.lower()
        
        # FILTRAR PREGUNTAS Y COMANDOS QUE NO SON TRANSACCIONES
        # Si es una pregunta o consulta, NO es transacción
        question_patterns = [
            r'^(que|qué|cual|cuál|como|cómo|donde|dónde|cuando|cuándo|quien|quién|por\s*que|por\s*qué)',
            r'(dime|cuales|cuentame|explica|muestra|ver|consulta|puedes|puedo|cuanto|cuánto)',
            r'(funciones|capacidades|que\s+haces|que\s+sabes|ayuda|help)',
            r'(agregala|agrégala|ponla|guardala|anótala|registrala)\s+(a|en)\s+(transacciones|transacción)',  # "agregala a transacciones"
        ]
        
        import re
        for pattern in question_patterns:
            if re.search(pattern, message_lower):
                return None  # Es una pregunta/comando vago, no una transacción
        
        # Si menciona "cambiar nombre", "renombrar", "modificar nombre" NO es transacción
        if any(word in message_lower for word in ['cambiar nombre', 'renombrar', 'modificar nombre', 'editar nombre', 'cambia el nombre', 'cambiar cuenta']):
            return None
        
        # MEJORADO: Detectar si "pasa" es GASTO (transferencia de dinero) o EDICIÓN (mover transacción)
        # "Le pasé 200k" = GASTO (transferencia)
        # "Pasa esta transacción a otra cuenta" = EDICIÓN
        has_pasa_word = any(word in message_lower for word in ['cambia', 'mueve', 'pasa', 'traslada'])
        
        if has_pasa_word:
            # Si dice "le pasé", "di", "presté" con monto = es GASTO (transferencia/pago)
            is_money_transfer = any(phrase in message_lower for phrase in [
                'le pas', 'le di', 'le prest', 'le envi', 'le transfer',
                'a mi ', 'para el ', 'para la ', 'para pagar',
                'arriendo', 'alquiler', 'renta',  # Contexto de pago
            ]) and bool(re.search(r'\d+', message_lower))
            
            # Si NO es transferencia de dinero Y NO tiene palabras de futuro = es comando de edición
            if not is_money_transfer and not any(w in message_lower for w in ['gastaré', 'gastará', 'pagaré', 'regalaré']):
                return None
        
        # Verificar si hay intención de crear
        has_create_intent = any(keyword in message_lower for keyword in keywords_create)
        has_expense = any(keyword in message_lower for keyword in keywords_expense)
        has_income = any(keyword in message_lower for keyword in keywords_income)
        
        # También detectar frases comunes sin palabra clave explícita
        implicit_patterns = [
            r'\d+[.,\d]*\s+(en|de|para|por)\s+\w+',  # "25000 en mercado"
            r'\d+[.,\d]*\s+a\s+\d+[.,\d]*\s+cada',  # "3 fritos a 5k cada"
            r'(me|te|le)\s+(gast|compr|pag|recib|ingres)',  # "me gasté"
            r'(me\s+com[ií]|com[ií])\s+\d+',
            r'\d+[.,\d]*\s+(cop|usd|pesos|dolares|€)',  # "25000 pesos"
        ]
        
        has_implicit = any(re.search(pattern, message_lower) for pattern in implicit_patterns)
        
        # Debe tener al menos UN número para ser transacción NORMAL
        # EXCEPTO: casos específicos sin número que son claramente transacciones
        has_number = bool(re.search(r'\d+', message_lower))
        
        # ⚠️ REGLA CRÍTICA: Para CREAR transacción debe tener número
        # Sin número = NO es transacción válida para crear
        if not has_number:
            return None
        
        # Debe tener al menos una palabra clave de transacción
        if not (has_create_intent or has_expense or has_income or has_implicit):
            return None
        
        # SEPARACIÓN INTELIGENTE DE MÚLTIPLES TRANSACCIONES
        import re
        
        # Primero: NO separar por "," o puntos de miles - eso rompe montos
        # Solo separar si hay VARIAS frases distintas (líneas, "y", "además", etc)
        
        # Separar por saltos de línea primero
        parts = re.split(r'\n+', message)
        parts = [p.strip() for p in parts if p.strip()]
        
        # Si solo una línea, chequear si hay múltiples con "y", "además", "también"
        if len(parts) == 1:
            # Solo separar si hay CLARAMENTE múltiples frases con separadores fuertes
            multi_separators = [' y ', ' además ', ' también ', '; ', ' luego ']
            has_multi_separator = any(sep in message_lower for sep in multi_separators)
            
            if has_multi_separator:
                # Separar solo por esos separadores, NO por números
                for sep in [' y ', ' además ', ' también ', '; ', ' luego ']:
                    if sep in message_lower:
                        parts = [p.strip() for p in re.split(re.escape(sep), message) if p.strip()]
                        break
        
        # Filtrar partes válidas (que tengan números y longitud mínima)
        transaction_parts = []
        for p in parts:
            p_stripped = p.strip()
            # Debe tener al menos un número y más de 5 caracteres para ser válida
            if re.search(r'\d+', p_stripped) and len(p_stripped) > 5:
                transaction_parts.append(p_stripped)
        
        # Si no hay partes válidas, usar el mensaje completo
        if not transaction_parts:
            transaction_parts = [message]
        
        # Determinar si hay REALMENTE múltiples transacciones
        # Solo si hay 2+ partes AND cada una tiene números
        multiple = len(transaction_parts) > 1 and all(re.search(r'\d+', p) for p in transaction_parts)
        
        # Determinar tipo predominante CON PRIORIDAD A GASTOS
        tx_type = 'expense'  # Default a gasto
        
        # Buscar palabras claras de GASTO
        clear_expense_words = ['compr', 'gast', 'comí', 'comi', 'saque', 'retire', 'pagué', 'pague', 'pagado', 'debit', 'cancelé', 'cancel', 'me cobr', 'pasé', 'pase', 'di', 'dí', 'presté']
        clear_income_words = ['recibí', 'recibe', 'cobré', 'cobre', 'ingres', 'ganancia', 'salario', 'sueldo', 'depósito', 'deposito', 'devolución', 'vendí', 'vendi', 'me pagó', 'me pago', 'me pagaron', 'consignó', 'consigno']
        
        clear_expense = any(word in message_lower for word in clear_expense_words)
        clear_income = any(word in message_lower for word in clear_income_words)
        
        # Detectar contexto con pronombre pasivo "me" para ingresos
        has_passive_me_income = 'me' in message_lower and any(word in message_lower for word in ['llegó', 'llego', 'depositaron', 'depos', 'acreditaron', 'acredit', 'pagaron', 'pagó', 'pago', 'dieron', 'regalo', 'consignó', 'consigno'])

        # Si explícitamente dice "me pagó/me pagaron", forzar ingreso
        if any(phrase in message_lower for phrase in ['me pagó', 'me pago', 'me pagaron', 'me consignó', 'me consigno']):
            clear_income = True
            clear_expense = False
        
        if clear_expense:
            tx_type = 'expense'
        elif has_passive_me_income and clear_income:
            tx_type = 'income'
        elif clear_income and not clear_expense:
            tx_type = 'income'
        elif has_income and not has_expense:
            tx_type = 'income'
        
        return {
            'has_intent': True,
            'transaction_type': tx_type,
            'original_message': message,
            'multiple_transactions': multiple,
            'transaction_parts': transaction_parts
        }
    
        return {
            'has_intent': True,
            'transaction_type': tx_type,
            'original_message': message,
            'multiple_transactions': multiple,
            'transaction_parts': transaction_parts
        }

    def parse_date_natural(self, text):
        """Parsea fechas naturales (ayer, antier, el 5...)"""
        import re
        from datetime import datetime, timedelta
        
        text = text.lower()
        today = datetime.now()
        
        if 'ayer' in text:
            return (today - timedelta(days=1)).strftime('%Y-%m-%d')
        if 'antier' in text or 'anteayer' in text:
            return (today - timedelta(days=2)).strftime('%Y-%m-%d')
        if 'semana pasada' in text:
            return (today - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Patrones numéricos: "el 5", "el dia 10", "5 de enero"
        # Simplemente asumimos el mes actual si solo dice el día
        match = re.search(r'\b(?:el\s+)?(?:dia\s+)?(\d{1,2})\b', text)
        if match:
            day = int(match.group(1))
            # Si el día es mayor al día de hoy, probablemente se refiere al mes pasado
            # O si explícitamente dice mes pasado
            if day > today.day or 'pasado' in text:
                # Restar un mes aprox (logic simple)
                target_date = today.replace(day=1) - timedelta(days=1)
                try:
                    return target_date.replace(day=day).strftime('%Y-%m-%d')
                except ValueError: 
                    # Si el mes pasado tiene menos días (ej: 31 feb no existe), usar ultimo dia
                    return target_date.strftime('%Y-%m-%d')
            try:
                return today.replace(day=day).strftime('%Y-%m-%d')
            except ValueError:
                pass
                
        return today.strftime('%Y-%m-%d')

    def convert_currency(self, amount, text, user_currency):
        """Detecta moneda en texto y convierte si es necesario"""
        import re
        text = text.upper()
        
        # Tasas de cambio APROXIMADAS (fijas por simplicidad, idealmente API externa)
        # Base: USD
        rates = {
            'USD': 1.0,
            'EUR': 0.92,
            'COP': 4150.0,
            'MXN': 17.50,
            'ARS': 1050.0,
            'CLP': 950.0,
            'BRL': 5.0,
            'PEN': 3.75
        }
        
        # Detectar moneda en texto
        detected_curr = None
        for curr in rates.keys():
            if curr in text and curr != user_currency:
                detected_curr = curr
                break
        
        if not detected_curr:
            return amount # No conversión necesaria
            
        # Convertir: (Monto / TasaOrigen) * TasaDestino
        if detected_curr in rates and user_currency in rates:
            amount_in_usd = amount / rates[detected_curr]
            amount_final = amount_in_usd * rates[user_currency]
            print(f"[AI] Converting {amount} {detected_curr} -> {amount_final} {user_currency}")
            return round(amount_final, 2)
            
        return amount

    def _extract_transaction_simple(self, user_id, message):
        """
        Extracción simple de transacciones sin IA usando regex
        Funciona cuando la API de IA no está disponible
        """
        import re
        
        msg_lower = message.lower()
        
        # GASTOS - Lista completa de palabras de egreso
        expense_words = [
            'gast', 'compré', 'compre', 'compr', 'compra',
            'pagué', 'pague', 'pagado', 'pago', 'pagar',
            'retiré', 'retire', 'retiro', 'saqué', 'saque', 'saco',
            'debit', 'débito', 'debitaron',
            'cancelé', 'cancel', 'cancelada',
            'consumí', 'consumi', 'consumo',
            'invertí', 'invert', 'inversión',
            'perdí', 'pierdo',
            'se fue', 'salió', 'salio',
            'me cobraron', 'me cobr',
            'me debitaron', 'me debit',
            'me quitaron', 'me quit',
            'me costó', 'me costo',
            'pago de', 'compra de', 'gasto en',
            'cuota', 'suscripción', 'mensualidad', 'comisión', 'multa', 'recargo',
        ]
        
        # INGRESOS - Lista completa de palabras de entrada
        income_words = [
            'ingres', 'ingresa', 'ingresó',
            'recibí', 'recibe', 'recibido', 'recib',
            'cobré', 'cobre', 'cobrado', 'cobr',
            'ganancia', 'gané', 'gano', 'ganador',
            'depositaron', 'depósito', 'deposito', 'depos',
            'acreditaron', 'acredit', 'crédito',
            'vendí', 'vendi', 'venta',
            'pagaron', 'pagada',
            'reembolso', 'reembolsa',
            'devolvieron', 'devolución',
            'me llegó', 'me llego',
            'me depositaron', 'me depos',
            'me acreditaron', 'me acredit',
            'me pagaron', 'me pagar',
            'me dieron', 'me regalo',
            'salario', 'sueldo', 'nómina', 'propina',
            'bono', 'premio',
        ]
        
        # Prioridad: Si hay CLARO verbo de gasto, es gasto
        transaction_type = 'expense'  # Default a gasto
        
        # Chequear presencia de palabras
        has_expense = any(word in msg_lower for word in expense_words)
        has_income = any(word in msg_lower for word in income_words)
        
        # LÓGICA CORRECTA:
        # 1. Si tiene palabra de gasto clara (compr, gast) => es gasto
        # 2. Si tiene palabra de ingreso clara sin gasto => es ingreso
        # 3. Si tiene ambas => analizar pronombres
        
        clear_expense = any(word in msg_lower for word in ['compr', 'gast', 'saque', 'retire', 'pagué', 'pague', 'pagado'])
        clear_income = any(word in msg_lower for word in ['ingres', 'recibí', 'recibe', 'cobré', 'cobre', 'salario', 'sueldo', 'ganancia', 'depósito', 'deposito', 'devolución'])
        
        # Detectar contexto con pronombres
        has_passive_me = 'me' in msg_lower and any(word in msg_lower for word in ['llegó', 'llego', 'depositaron', 'depos', 'acreditaron', 'acredit', 'pagaron', 'dieron', 'regalo', 'cobraron', 'cobr'])
        
        if clear_expense:
            transaction_type = 'expense'
        elif has_passive_me and clear_income:
            transaction_type = 'income'
        elif clear_income and not clear_expense:
            transaction_type = 'income'
        elif has_income and not has_expense:
            transaction_type = 'income'
        elif not has_income and not has_expense:
            # CONTEXTO: Si no hay verbos claros, revisar mensaje anterior
            # Ej: "Y 20 en leche"
            is_continuation = any(w in msg_lower for w in ['y', 'tambien', 'también', 'además', 'ademas', 'otro'])
            
            if previous_message and (is_continuation or len(message.split()) < 5):
                # Analizar el mensaje previo recursivamente para ver qué fue
                prev_tx = self._extract_transaction_simple(user_id, previous_message)
                if prev_tx:
                    transaction_type = prev_tx['transaction_type']
                    print(f"[AI] Context inference: Inherited {transaction_type} from previous message")

        if not transaction_type:
            transaction_type = 'expense' # Default final
        
        if clear_expense:
            transaction_type = 'expense'
        elif clear_income and not clear_expense:
            transaction_type = 'income'
        elif has_income and not has_expense:
            transaction_type = 'income'
        
        # Extraer monto (soporta puntos y comas como separadores)
        # Buscar patrones como: 25.000, 25,000, 2.300, 120000
        amount_patterns = [
            r'(\d{1,3}(?:[.,]\d{3})+)',  # 25.000 o 25,000
            r'(\d+[.,]\d{2,3})',          # 2.300 o 2,30
            r'(\d+)',                     # 25000
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, message)
            if match:
                amount_str = match.group(1).replace('.', '').replace(',', '')
                try:
                    amount = float(amount_str)
                    break
                except:
                    continue
        
        if not amount:
            return None
        
        # Extraer descripción
        # Buscar texto después de "en" o antes del monto
        description = None
        desc_patterns = [
            r'(?:en|de|para)\s+([a-záéíóúñ\s]+?)(?:\s+\d|$)',
            r'(?:gast[éeó]|compr[éeó]|pagu[éeó])\s+\d+[.,\d]*\s+(?:en|de|para)?\s*([a-záéíóúñ\s]+)',
            r'(?:ingres[oó]|recib[íió]|cobr[éeó])\s+\d+[.,\d]*\s+(?:de|por)?\s*([a-záéíóúñ\s]+)',
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                description = match.group(1).strip()
                break
        
        if not description:
            # Intentar extraer palabras después del monto
            words = msg_lower.split()
            # Buscar palabras significativas (no números ni palabras comunes)
            for i, word in enumerate(words):
                if re.search(r'\d', word):
                    if i + 1 < len(words):
                        desc_words = []
                        for j in range(i + 1, len(words)):
                            if words[j] not in ['en', 'de', 'para', 'con', 'mi', 'la', 'el']:
                                desc_words.append(words[j])
                        if desc_words:
                            description = ' '.join(desc_words[:3])  # Max 3 palabras
                            break
        
        if not description:
            description = "Transacción"
        
        if not description:
            description = "Transacción"
        
        # 4. AMBIGÜEDAD: Filtrar "3 manzanas"
        # Si el monto es bajo (<10) y NO tiene moneda explícita NI palabras clave fuertes
        # y la descripción parece objeto contable
        has_currency_symbol = any(s in msg_lower for s in ['$', 'usd', 'eur', 'cop', 'pesos'])
        strong_keyword = any(k in msg_lower for k in ['gast', 'compr', 'pagu', 'cost'])
        
        if amount < 10 and not has_currency_symbol and not strong_keyword:
            # Si parece conteo de objetos (palabra plural siguiente)
            # Ej: "3 manzanas", "2 panes"
            # Esto es un heurístico simple
            return None

        # 5. CONVERSION MONEDA
        # Obtener moneda del usuario
        from models import User
        user = User.query.get(user_id)
        current_curr = user.preferred_currency if user else 'USD'
        amount = self.convert_currency(amount, message, current_curr)
            
        # 6. FECHA NATURAL
        tx_date = self.parse_date_natural(message)
        
        # Buscar cuenta mencionada
        from models import User
        user = User.query.get(user_id)
        accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
        
        # Buscar cuenta mencionada (Exacta o Fuzzy)
        account_name = None
        
        # 1. Búsqueda Exacta (Prioridad máxima)
        for acc in accounts:
            if acc.name.lower() in msg_lower:
                account_name = acc.name
                break
        
        # 2. Búsqueda Difusa (Si no hay exacta)
        if not account_name and fuzz and process:
            import string
            # Limpiar puntuación para mejorar matching
            msg_clean = message.translate(str.maketrans('', '', string.punctuation)).lower()
            words = msg_clean.split()
            
            # Generar n-grams del mensaje (1 a 4 palabras)
            # Esto permite encontrar "banco bogota" en "mi banco de bogota"
            ngrams = []
            max_n = 4
            for n in range(1, max_n + 1):
                for i in range(len(words) - n + 1):
                    ngrams.append(" ".join(words[i:i+n]))
            
            if ngrams:
                best_score = 0
                best_acc = None
                
                for acc in accounts:
                    # Normalizar nombre cuenta
                    acc_name_clean = acc.name.translate(str.maketrans('', '', string.punctuation)).lower()
                    
                    # Buscar la mejor coincidencia de ESTA cuenta en los n-grams
                    match = process.extractOne(acc_name_clean, ngrams, scorer=fuzz.ratio)
                    
                    if match and match[1] > best_score:
                        best_score = match[1]
                        best_acc = acc.name
                
                # Umbral de confianza (85/100)
                if best_score >= 82: # Un poco más tolerante que 85
                    account_name = best_acc
                    print(f"[AI] Fuzzy match account: '{account_name}' (Score: {best_score})")
        
        return {
            'description': description.title(),
            'amount': amount,
            'transaction_type': transaction_type,
            'category': None,
            'account': account_name,
            'date': tx_date
        }
    
    def extract_transaction_from_text(self, user_id, message, previous_message=None):
        """
        Usa IA para extraer información de transacción del texto del usuario
        Si IA no está disponible, usa extracción basada en regex
        
        Returns:
            dict: Datos de la transacción extraídos
        """
        # Si IA no está disponible, usar extracción simple
        if not self.enabled:
            return self._extract_transaction_simple(user_id, message, previous_message)
        
        try:
            # Obtener usuario para saber su moneda
            from models import User
            user = User.query.get(user_id)
            currency = user.preferred_currency if user else 'USD'
            
            # Obtener cuentas y categorías del usuario
            accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
            categories = Category.query.filter_by(user_id=user_id).all()
            
            accounts_list = ', '.join([f"{a.name} ({a.account_type})" for a in accounts])
            expense_categories = ', '.join([c.name for c in categories if c.category_type == 'expense'])
            income_categories = ', '.join([c.name for c in categories if c.category_type == 'income'])
            
            prompt = f"""Analiza el siguiente mensaje y extrae información de transacción en formato JSON.

IMPORTANTE: La moneda del usuario es: {currency}
TODOS los montos deben interpretarse como {currency} a menos que el usuario especifique otra cosa.

Mensaje del usuario: "{message}"

Cuentas disponibles: {accounts_list}
Categorías de gasto: {expense_categories}
Categorías de ingreso: {income_categories}

Responde SOLO con un objeto JSON con esta estructura exacta (sin markdown, sin ```json):
{{
    "description": "descripción de la transacción (REQUERIDO)",
    "amount": número (solo número, sin símbolo ${currency}, REQUERIDO),
    "transaction_type": "expense" o "income",
    "category": "nombre de categoría válida o null si no está claro",
    "account": "nombre de cuenta válida o null si no se especifica",
    "date": "YYYY-MM-DD" (usa hoy: {datetime.now().strftime('%Y-%m-%d')})
}}

IMPORTANTE: 
- Si no mencionan cuenta específica, pon null
- Si la categoría no es clara, intenta inferir de la descripción o pon null
- description y amount son OBLIGATORIOS
- Si no puedes extraer description o amount, retorna null para TODO"""

            messages = [
                {"role": "user", "content": prompt}
            ]
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 200
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                content = content.replace('```json', '').replace('```', '').strip()
                
                print(f"DEBUG extract_transaction: AI response: {content[:200]}")
                
                # Limpiar respuesta (eliminar ```json si existe)
                content = content.replace('```json', '').replace('```', '').strip()
                
                # Parsear JSON
                import json
                try:
                    transaction_data = json.loads(content)
                    print(f"DEBUG extract_transaction: Parsed data: {transaction_data}")
                    return transaction_data
                except json.JSONDecodeError as e:
                    print(f"ERROR extract_transaction: Failed to parse JSON: {content[:300]}")
                    print(f"ERROR: {e}")
                    return self._extract_transaction_simple(user_id, message)
            else:
                print(f"ERROR extract_transaction: API returned {response.status_code}")
                return self._extract_transaction_simple(user_id, message)
                
        except Exception as e:
            print(f"Error extracting transaction with AI: {e}")
            # Intentar extracción simple como respaldo
            return self._extract_transaction_simple(user_id, message)
    
    def get_transaction_advice(self, description, amount, currency):
        """
        Genera un consejo personalizado basado en la transacción
        
        Args:
            description: Descripción de la transacción
            amount: Monto (negativo para gastos, positivo para ingresos)
            currency: Moneda
            
        Returns:
            str: Consejo personalizado
        """
        if not self.enabled:
            return None
        
        try:
            transaction_type = "gasto" if amount < 0 else "ingreso"
            abs_amount = abs(amount)
            amount_formatted = f"{currency} {abs_amount:,.2f}"
            
            prompt = f"""Genera un consejo corto y práctico (1-2 oraciones) sobre este {transaction_type}:
- Descripción: {description}
- Monto: {amount_formatted}

El consejo debe ser útil, específico y motivador. Ej:
- Para un gasto en comida: "Considera hacer una lista de compras para evitar gastos innecesarios"
- Para un gasto en transporte: "Usa opciones de transporte compartido para reducir costos"
- Para un ingreso: "Considera ahorrar una parte de este ingreso para emergencias"

Responde SOLO con el consejo, sin explicaciones adicionales."""
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 100
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                advice = result['choices'][0]['message']['content'].strip()
                return advice
            else:
                return None
                
        except Exception as e:
            print(f"Error generating transaction advice: {e}")
            return None
    
    def detect_control_command(self, message):
        """
        Detecta comandos de control de cuenta en el mensaje del usuario
        MEJORADO: Detección inteligente con múltiples variaciones y tolerancia a errores
        Retorna: {'type': 'comando', 'action': 'tipo_accion', 'params': {...}}
        """
        msg_lower = message.lower()
        
        # Función auxiliar para buscar patrones flexibles
        def contains_pattern(text, patterns, fuzzy_threshold=82):
            """Busca patrones con substring, regex o coincidencia difusa (si está disponible)."""
            import re
            string_patterns = []

            for pattern in patterns:
                if isinstance(pattern, str):
                    if pattern in text:
                        return True
                    string_patterns.append(pattern)
                else:  # es regex
                    if re.search(pattern, text):
                        return True

            # Coincidencia difusa para tolerar typos o variantes
            if fuzz and process and string_patterns:
                match = process.extractOne(text, string_patterns, scorer=fuzz.partial_ratio)
                if match and match[1] >= fuzzy_threshold:
                    return True

            return False
        
        
        # 4. Eliminar cuenta específica (PRIORIDAD ALTA)
        # Patrón: "elimina la cuenta nequi", "borrar cuenta de ahorros", "eliminar mi cuenta nequi"
        import re
        delete_account_match = re.search(r'(?:elimina(?:r)?|borra(?:r)?)\s+(?:(?:la|las|el|los|mi|mis|tu|tus|su|sus|una|unas)\s+)?cuenta\s+(?:de\s+)?(.+)', msg_lower)
        if delete_account_match:
            account_name = delete_account_match.group(1).strip()
            # Limpiar puntuación final si existe
            account_name = account_name.rstrip('.,;?!')
            return {
                'type': 'control_command',
                'action': 'delete_account',
                'account_name': account_name,
                'raw_message': message
            }

        # Comando: Crear cuenta (MUY AMPLIADO)
        create_account_patterns = [
            'crear cuenta', 'crea cuenta', 'crea una cuenta', 'crear una cuenta',
            'nueva cuenta', 'agregar cuenta', 'añadir cuenta', 'agrega cuenta',
            'quiero crear', 'necesito crear', 'puedo crear', 'como creo',
            'abrir cuenta', 'abre cuenta', 'registrar cuenta', 'registra cuenta',
            'dame cuenta', 'hazme cuenta', 'haz cuenta', 'crea la cuenta',
            'crear.*cuenta', 'cuenta nueva', 'cuenta de', 'cuenta llamada',
            'quiero.*cuenta', 'necesito.*cuenta', 'agregar.*cuenta',
            r'cre[aeo]\s+\w*\s*cuenta',  # crea/creo cuenta
            r'cuenta\s+(nueva|de|llamada)',  # cuenta nueva/de/llamada
        ]
        
        if contains_pattern(msg_lower, create_account_patterns):
            import re
            # Extraer nombre de la cuenta - MEJORADO
            name_patterns = [
                # "crea una cuenta de efectivo que se llame bolsillo"
                r'(?:se\s+)?llame?\s+([a-záéíóúñ\d\s]+?)(?:\s+(?:con|y|de|que|tenga|saldo)|\s*$)',
                # "cuenta llamada bolsillo"
                r'(?:cuenta|tarjeta|efectivo|ahorro|banco)\s+llamada?\s+([a-záéíóúñ\d\s]+?)(?:\s+(?:con|y|de|que|tenga|saldo)|\s*$)',
                # "cuenta de efectivo bolsillo"
                r'cuenta\s+de\s+(?:efectivo|tarjeta|ahorro|credito|banco)\s+([a-záéíóúñ\d\s]+?)(?:\s+(?:con|y|de|que|tenga|saldo)|\s*$)',
                # "crea cuenta bolsillo"
                r'(?:crea|crear|nueva|agregar)\s+(?:una\s+)?cuenta\s+([a-záéíóúñ\d\s]+?)(?:\s+(?:con|y|de|que|tenga|saldo)|\s*$)',
                # Último intento: buscar después de tipo de cuenta
                r'(?:efectivo|tarjeta|ahorro|credito|banco)\s+([a-záéíóúñ\d\s]+?)(?:\s+(?:con|y|de|que|tenga|saldo)|\s*$)',
            ]
            
            account_name = None
            for pattern in name_patterns:
                match = re.search(pattern, msg_lower)
                if match:
                    name_candidate = match.group(1).strip()
                    # Filtrar palabras comunes que no son nombres
                    filter_words = ['que', 'con', 'de', 'saldo', 'tenga', 'este', 'en', 'y', 'se', 'la', 'el']
                    words = name_candidate.split()
                    words = [w for w in words if w not in filter_words]
                    if words:
                        account_name = ' '.join(words)
                        break
            
            # Si no se encontró nombre, intentar detectar después de "llame"
            if not account_name:
                match = re.search(r'llame?\s+([a-záéíóúñ\d]+)', msg_lower)
                if match:
                    account_name = match.group(1).strip()
            
            # Extraer tipo de cuenta
            account_type = 'checking'  # Por defecto
            if 'tarjeta' in msg_lower or 'credito' in msg_lower or 'crédito' in msg_lower:
                account_type = 'credit_card'
            elif 'efectivo' in msg_lower or 'cash' in msg_lower:
                account_type = 'cash'
            elif 'ahorro' in msg_lower or 'savings' in msg_lower:
                account_type = 'savings'
            
            # Extraer balance inicial
            amounts = re.findall(r'(\d+[.,]?\d*)\s*(?:mil|k|pesos|cop|usd|€|$)?', msg_lower)
            initial_balance = 0
            if amounts:
                amount_str = amounts[0].replace(',', '').replace('.', '')
                try:
                    initial_balance = float(amount_str)
                except:
                    initial_balance = 0
            
            return {
                'type': 'control_command',
                'action': 'create_account',
                'account_name': account_name,
                'account_type': account_type,
                'initial_balance': initial_balance,
                'raw_message': message
            }
        
        # Comando: Cambiar balance (MUY AMPLIADO)
        balance_patterns = [
            'cambiar balance', 'cambia balance', 'cambiar el balance', 'cambiar saldo',
            'set balance', 'establecer balance', 'balance a', 'ajustar balance',
            'modificar balance', 'actualizar balance', 'poner balance', 'pon balance',
            'balance en', 'saldo en', 'saldo a', 'ajustar saldo', 'modificar saldo',
            'quiero.*balance', 'necesito.*balance', 'mi balance.*sea',
            r'balance\s+(a|en|de)\s+\d',  # balance a/en/de [número]
            r'(cambiar|modificar|ajustar|poner)\s+\w*\s*(balance|saldo)',
        ]
        
        if contains_pattern(msg_lower, balance_patterns):
            # Intentar extraer la cantidad
            import re
            amounts = re.findall(r'(\d+[.,]?\d*)\s*(cop|usd|€|$)?', msg_lower)
            if amounts:
                amount_str = amounts[0][0].replace(',', '.')
                try:
                    amount = float(amount_str)
                    return {
                        'type': 'control_command',
                        'action': 'set_balance',
                        'amount': amount,
                        'raw_message': message
                    }
                except:
                    pass
        


        # Comando: Eliminar TODAS las transacciones (DESTRUCTIVO - REQUIERE CONFIRMACIÓN)
        delete_all_patterns = [
            'eliminar todas las transacciones', 'borrar todas las transacciones',
            'elimina todas las transacciones', 'borra todas las transacciones',
            'delete all transactions', 'eliminar todo', 'borrar todo',
            'elimina todas', 'borra todas', 'eliminar todas', 'borrar todas',
            r'(eliminar|borrar|delete)\s+(todas?|todo)\s+(las?\s+)?(transacci|registro)',
            r'(eliminar|borrar|delete)\s+(todas?|todo)(?:\s+mis)?\s*$',  # "elimina todas", "borra todo"
        ]
        
        if contains_pattern(msg_lower, delete_all_patterns):
            return {
                'type': 'control_command',
                'action': 'delete_all_transactions',
                'raw_message': message
            }
        
        # Comando: Borrar/Eliminar transacción INDIVIDUAL (después de verificar que no es "todas")
        delete_keywords = ['borrar', 'borra', 'eliminar', 'elimina', 'delete', 'quitar', 'quita']
        
        # Detectar si pide "última" transacción (esto lo hace más flexible)
        last_words = ['última', 'ultimo', 'ultima', 'últimas', 'ultimos', 'ultimas', 'último', 'last', 'reciente']
        is_last = any(word in msg_lower for word in last_words)
        has_transaccion_word = 'transacci' in msg_lower or 'registro' in msg_lower
        has_delete_keyword = any(kw in msg_lower for kw in delete_keywords)
        
        # Permite eliminación si tiene verbo delete Y (transacción O última)
        # O simplemente si tiene verbo delete + "último" sin necesidad de mencionar transacción
        if has_delete_keyword and (has_transaccion_word or is_last):
            import re
            # Buscar números que podrían ser IDs o montos
            numbers = re.findall(r'\d+', msg_lower)
            
            return {
                'type': 'control_command',
                'action': 'delete_transaction',
                'identifiers': numbers if numbers else ['last'],
                'raw_message': message
            }
        
        # Comando: Renombrar cuenta (NUEVO)
        rename_patterns = [
            'renombrar', 'cambiar nombre', 'cambia nombre', 'modificar nombre',
            'editar nombre', 'cambiar el nombre', 'modifica el nombre',
            'ponerle nombre', 'cambiar.*nombre', 'renombrar.*cuenta',
            'que se llame', 'se llame', 'se llamara', 'se llamará', 'llamala', 'llámala', 'llamara', 'llamará',
            'cambia la que se llama', 'cambies el nombre', 'cambies nombre',
            r'(cambiar|modificar|editar|renombrar|cambies)\s+\w*\s*nombre',
            r'renombrar\s+cuenta',
            r'cuenta\s+\w+\s+a\s+',
            r'cambia\s+la\s+que\s+se\s+llama',
            r'que\s+se\s+llame\s+[a-záéíóúñ\s]+',
            r'que\s+se\s+llam[aeo]\s+[a-záéíóúñ\s]+',
            r'se\s+llam[aá]r?\s+[a-záéíóúñ\s]+',
        ]
        
        if contains_pattern(msg_lower, rename_patterns):
            import re
            # Extraer nuevo nombre - MEJORADO con prioridad correcta
            name_patterns = [
                # Prioridad 1: Después de "llame/llamará/llamara"
                r'(?:se\s+)?llam[aeoárá]+\s+([a-záéíóúñ\d]+(?:\s+[a-záéíóúñ\d]+){0,3})(?:\s*$|[.,])',
                # Prioridad 2: Después de "para que se llame"
                r'para\s+que\s+se\s+llam[ae]\s+([a-záéíóúñ\d]+(?:\s+[a-záéíóúñ\d]+){0,3})(?:\s*$|[.,])',
                # Prioridad 3: Después de "nombre a" (específico para "cambies el nombre a X")
                r'nombre\s+(?:a|por)\s+([a-záéíóúñ\d]+(?:\s+[a-záéíóúñ\d]+){0,3})(?:\s*$|[.,])',
                # Prioridad 4: Después de "nombre" (pero antes del final)
                r'nombre\s+(?:es|sea)?(?:\s+)?([a-záéíóúñ\d]+(?:\s+[a-záéíóúñ\d]+){0,3})(?:\s*$|[.,])',
                # Prioridad 5: Después de "a" pattern que cubra "a aliexpress."
                # El problema era que el punto no estaba considerado en el boundary final
                r'\s+a\s+([a-záéíóúñ\d]+(?:\s+[a-záéíóúñ\d]+){0,3})(?:\s*[.,]?\s*$)',
            ]
            
            new_name = None
            for pattern in name_patterns:
                match = re.search(pattern, msg_lower)
                if match:
                    candidate = match.group(1).strip()
                    # Filtrar palabras que claramente no son nombres de cuenta
                    stop_words = ['cuenta', 'numero', 'número', 'para', 'que', 'se', 'el', 'la', 'mi', 'nombre', 'de']
                    words = candidate.split()
                    filtered = [w for w in words if w not in stop_words]
                    if filtered:
                        new_name = ' '.join(filtered)
                        break
            
            # Extraer identificador de cuenta (número o nombre)
            account_id = None
            if 'cuenta' in msg_lower:
                # Buscar "cuenta 2", "cuenta nequi", "mi cuenta 2", "cuenta numero 4", "cuenta número cuatro"
                # Soporte para palabras de números
                num_words = 'uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez'
                match = re.search(r'cuenta\s+(?:n[uú]mero\s+)?((\d+|' + num_words + r'|[a-záéíóúñ\s]+?))(?:\s+para|\s+que|\s+a\s|$)', msg_lower)
                if match:
                    account_id = match.group(1).strip()

            # Fallback: "la que se llama X" o "se llama X"
            if not account_id:
                match = re.search(r'que\s+se\s+llama\s+([a-záéíóúñ\s]+?)(?:\s|$)', msg_lower)
                if match:
                    account_id = match.group(1).strip()
            if not account_id:
                match = re.search(r'se\s+llama\s+([a-záéíóúñ\s]+?)(?:\s|$)', msg_lower)
                if match:
                    account_id = match.group(1).strip()
            
            # Normalizar account_id si es palabra "cuatro" -> "4"
            if account_id:
                 word_to_num = {
                     'uno': '1', 'dos': '2', 'tres': '3', 'cuatro': '4', 'cinco': '5',
                     'seis': '6', 'siete': '7', 'ocho': '8', 'nueve': '9', 'diez': '10'
                 }
                 if account_id in word_to_num:
                     account_id = word_to_num[account_id]
            
            return {
                'type': 'control_command',
                'action': 'rename_account',
                'account_id': account_id,
                'new_name': new_name,
                'raw_message': message
            }
        
        # Comando: Editar transacción (MUY AMPLIADO)
        edit_patterns = [
            'editar', 'edit', 'modificar', 'cambiar descripción', 'change description',
            'actualizar', 'corregir', 'arreglar', 'cambiar monto', 'cambiar cantidad',
            'editar transacción', 'modificar transacción', 'cambiar transacción',
            r'(editar|modificar|cambiar|actualizar|corregir)\s+\w*\s*(transacci|registro)',
            r'(corrige|cambia|modifica)\s+(la|el)\s+(anterior|ultima|última|esa)',
        ]
        
        if contains_pattern(msg_lower, edit_patterns):
            # Verificar si se refiere a transacción
            keywords = ['transacci', 'registro', 'descripción', 'monto', 'anterior', 'ultima', 'última', 'esa', 'la']
            if any(k in msg_lower for k in keywords):
                # Intentar extraer ID si existe
                import re
                numbers = re.findall(r'\d+', msg_lower)
                # Si hay números grandes (>1000) probablemente es monto, no ID
                ids = [n for n in numbers if int(n) < 10000]
                
                return {
                    'type': 'control_command',
                    'action': 'edit_transaction',
                    'target': ids[0] if ids else 'last',
                    'raw_message': message
                }
        
        # Comando: Resetear/Restablecer balance (MÁS RESTRICTIVO - REQUIERE CONFIRMACIÓN EXPLÍCITA)
        # NOTA: Este es un comando muy peligroso, solo detectar si es CLARAMENTE intencional
        reset_patterns = [
            'resetear balance', 'resetear saldo', 'reset balance', 'reset saldo',
            'restaurar balance inicial', 'restaurar saldo inicial',
            r'(reset|resetear)\s+(balance|saldo|todo)',  # Forma más explícita
        ]
        
        if contains_pattern(msg_lower, reset_patterns):
            # SAFEGUARD: Requiere que la palabra "reset" o "resetear" esté explícitamente
            # Palabras sueltas como "inicial", "restaurar" ya no son suficientes
            has_explicit_reset = any(word in msg_lower for word in ['reset', 'resetear', 'resetea'])
            
            if has_explicit_reset:
                return {
                    'type': 'control_command',
                    'action': 'reset_balance',
                    'raw_message': message
                }
        
        # Comando: Restaurar balance desde backup (MÁS SEGURO - BUSCA "RESTAURAR" SIN "INICIAL")
        # Esto es más seguro porque solo se dispara con "restaurar balance"
        restore_patterns = [
            'restaurar balance', 'restaurar saldo', 'restore balance',
            'volver atrás', 'deshacer cambios', 'recuperar balance',
            r'(restaurar|recuperar)\s+(balance|saldo)',
        ]
        
        if contains_pattern(msg_lower, restore_patterns):
            # Asegurarse de que NO sea "restaurar balance inicial" (eso es reset)
            if 'inicial' not in msg_lower:
                return {
                    'type': 'control_command',
                    'action': 'restore_balance',
                    'raw_message': message
                }
        
        # Comando: Poner cuentas en 0 (DESTRUCTIVO - REQUIERE CONFIRMACIÓN)
        zero_accounts_patterns = [
            'dejar cuentas en 0', 'poner cuentas en 0', 'cuentas en 0',
            'resetear cuentas a 0', 'llevar cuentas a 0',
            r'(dejar|poner|resetear|llevar)\s+(mis\s+)?cuentas?\s+(a|en)\s+0',
            r'cuentas?\s+(a|en)\s+0',
        ]
        
        if contains_pattern(msg_lower, zero_accounts_patterns):
            return {
                'type': 'control_command',
                'action': 'zero_accounts',
                'raw_message': message
            }
        
        return None

    def clean_user_input(self, message):
        """
        🧹 LIMPIEZA BRUTAL DE ENTRADA
        - Remover emojis
        - Remover texto pegado (múltiples líneas de respuestas anteriores)
        - Normalizar espacios
        - Detectar intención real del usuario
        """
        import re
        
        original = message
        
        # 1️⃣ REMOVER EMOJIS Y SÍMBOLOS ESPECIALES VISUALES
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # Emojis
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"  
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # Variante de emoji
            "\u3030"
            "]+"
        )
        text = emoji_pattern.sub('', message).strip()
        
        # 2️⃣ REMOVER "<XXXX" tags (si hay parsing HTML accidental)
        text = re.sub(r'<[^>]+>', '', text)
        
        # 3️⃣ REMOVER LÍNEAS QUE PARECEN RESPUESTAS ANTERIORES PEGADAS
        # Detectar patrones como "✅ **Gasto registrado**", "🍟 **Gasto...", "❌ No pude..."
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Líneas técnicas de respuestas anteriores que deben descartarse siempre
            metadata_prefixes = [
                '- **monto:', '- **cuenta:', '- **descripción:', '- **descripcion:',
                '- **gasto:', '- **ingreso:', '- **nuevo balance:', '- **anterior:',
                'monto:', 'cuenta:', 'descripción:', 'descripcion:', 'balance:',
                '📊 **balance', '⚠️ **nota:', '💡 **recuerda', '🔄 **balance'
            ]
            lower_line = line_stripped.lower()
            if any(lower_line.startswith(prefix) for prefix in metadata_prefixes):
                continue

            # Si la línea se ve como una respuesta del sistema (comienza con símbolos de respuesta)
            # Y NO es la línea principal del usuario, ignorarla
            is_response_line = any([
                line_stripped.startswith('✅'),
                line_stripped.startswith('❌'),
                line_stripped.startswith('⚠️'),
                line_stripped.startswith('📊'),
                line_stripped.startswith('🍟'),
                line_stripped.startswith('💡'),
                line_stripped.startswith('📝'),
                line_stripped.startswith('🔄'),
                line_stripped.startswith('💰'),
                line_stripped.startswith('📈'),
                line_stripped.startswith('📉'),
                line_stripped.startswith('✨'),
                # Patrones de código de respuesta
                re.match(r'^Gasto registrado|^Ingreso registrado|^Balance actualizado|^Transacción', line_stripped),
                re.match(r'^\*\*', line_stripped),  # **Bold text** de respuestas
            ])

            # Si la línea contiene una intención clara del usuario, conservarla
            has_user_action_words = any(token in lower_line for token in [
                'aplica', 'aplíca', 'hazlo', 'registra', 'guarda', 'agrega', 'crea',
                'cambia', 'modifica', 'edita', 'corrige', 'ajusta', 'cancela', 'no',
                'dale', 'ok', 'si', 'sí'
            ])
            
            # Si es respuesta del sistema, ignorar (aunque tenga números)
            if is_response_line and not has_user_action_words:
                continue
            
            cleaned_lines.append(line_stripped)
        
        # Reconstruir: quedarse con líneas que tengan contenido nuevo
        text = ' '.join(cleaned_lines).strip()
        
        # 4️⃣ SI QUEDA VACÍO, REGRESAR ORIGINAL (fue solo símbolos)
        if not text or text.isspace():
            # Buscar al menos el primer número o palabra significativa
            match = re.search(r'COP\s*[\d,.]+|USD\s*[\d,.]+|EUR\s*[\d,.]+|\d+|\w+', original)
            if match:
                text = match.group().strip()
            else:
                text = original.strip()
        
        # 5️⃣ NORMALIZAR ESPACIOS Y PUNTUACIÓN
        text = re.sub(r'\s+', ' ', text)  # Múltiples espacios → uno
        text = re.sub(r'\s+([.,!?])', r'\1', text)  # Espacio antes de puntuación
        
        return text.strip()

    def detect_action_intent(self, message):
        """
        ⚡ DETECCIÓN DE INTENCIÓN DE APLICACIÓN/EJECUCIÓN
        Detecta palabras que significan "aplica la última transacción"
        
        Returns:
            str: Tipo de acción ('apply', 'edit', None)
        """
        message_lower = message.lower().strip()
        
        # ❌ RECHAZO (primero para evitar falsos positivos)
        reject_keywords = [
            'cancela', 'cancel', 'no', 'desecha', 'borr',
            'elimina', 'olvida', 'olvídalo', 'olvide',
            'atrás', 'atras', 'volver', 'no me',
        ]

        for keyword in reject_keywords:
            if keyword in message_lower:
                return 'reject'

        # 🔧 PALABRAS CLAVE DE EDICIÓN (antes de apply)
        edit_keywords = [
            'cambiar', 'cambia', 'cámbiale', 'cambiale', 'modifica', 'edita', 'actualiza',
            'corrige', 'ajusta', 'arregla', 'modifica nombre', 'cambiar monto',
            'cambiar descripción', 'cambiar descripcion', 'cambiar cuenta', 'cambiar categoria',
        ]

        for keyword in edit_keywords:
            if keyword in message_lower:
                return 'edit'

        # 🎯 PALABRAS CLAVE DE APLICACIÓN/EJECUCIÓN (sin confirmaciones ambiguas)
        apply_keywords = [
            'aplícalo', 'aplica', 'aplico', 'aplicala', 'aplicalo',
            'hazlo', 'haz lo', 'hazlo pue', 'hazlo pues', 'haz', 'hezblo', 'hazo',
            'registralo', 'registrala', 'registra',
            'guardalo', 'guardala', 'guarda',
            'agrega', 'agregalo', 'agregala', 'agregalo',
            'confirmalo', 'confirma', 'confirmalo',
            'crealo', 'crea',
            'ejecuta', 'ejecutalo',
            'dale pa', 'vamos',
            'ándale', 'andale',
        ]
        
        for keyword in apply_keywords:
            if keyword in message_lower:
                return 'apply'
        
        return None

    def detect_confirmation_words(self, message):
        """
        ✅ DETECCIÓN AGRESIVA DE CONFIRMACIÓN
        Simple affirmations that mean "YES, apply it"
        """
        message_lower = message.lower().strip()

        # Negaciones primero
        if any(neg in message_lower for neg in [' no ', 'no ', ' no', 'cancel', 'cancela', 'olvida']):
            return False
        
        # Si el mensaje tiene menos de 15 caracteres y contiene confirmación, es confirmación
        if len(message_lower) < 15:
            simple_confirmations = [
                'sí', 'si', 'ok', 'dale', 'listo', 'ya', 'bien',
                'sipi', 'yes', 'ándale', 'andale', 'okey', 'okei',
                'confirmo', 'acepto', 'aprobado', 'vai', 'vamo', 'claro',
            ]
            
            for conf in simple_confirmations:
                if conf == message_lower or message_lower.startswith(conf):
                    return True
        
        # Patterns más largos pero claros
        patterns = [
            r'^(sí|si)[\s.,!]*$',
            r'^está bien',
            r'^está\s+bien',
            r'^pues bien',
            r'^ok[\s.,!]*$',
            r'^dale[\s.,!]*$',
            r'^listo[\s.,!]*$',
            r'^confirmo[\s.,!]*$',
            r'^acepto[\s.,!]*$',
            r'^claro[\s.,!]*$',
            r'^ok(\s+ok)+[\s.,!]*$',
            r'^(sí|si)\s*(está\s+)?bien',
            r'^está\s+bien,?\s*(sí|si)$',
        ]
        
        import re
        for pattern in patterns:
            if re.match(pattern, message_lower):
                return True
        
        return False

    def extract_pending_transaction(self, messages_history):
        """
        🔍 EXTRAE TRANSACCIÓN SIMULADA DE HISTORIAL
        Busca en los últimos mensajes del asistente si hay una transacción simulada
        
        Returns:
            dict: {monto, cuenta, descripción, tipo} o None
        """
        import re
        
        # Buscar en los últimos 3 mensajes del asistente
        for msg in reversed(messages_history[-3:]):
            if msg.get('role') != 'assistant':
                continue
            
            content = msg.get('content', '')
            
            # Buscar patrones de transacción simulada
            # Patrón: "Monto: COP/USD/EUR XXXXX" o similar
            monto_match = re.search(
                r'(?:Monto|MONTO|Amount):\s*(?:COP|USD|EUR|MXN|ARS)?\s*([\d,.]+)',
                content,
                re.IGNORECASE
            )
            
            if not monto_match:
                continue
            
            # Extraer monto limpio
            monto_str = monto_match.group(1).replace(',', '').replace('.', ',')
            monto_str = monto_str.replace(',', '.')
            monto = float(monto_str) if '.' in monto_str else float(monto_str.replace(',', ''))
            
            # Extraer cuenta
            cuenta_match = re.search(
                r'(?:Cuenta|CUENTA):\s*([^\n.]+)',
                content,
                re.IGNORECASE
            )
            cuenta = cuenta_match.group(1).strip() if cuenta_match else None
            
            # Extraer descripción
            desc_match = re.search(
                r'(?:Descripción|DESCRIPCIÓN|Description):\s*([^\n.]+)',
                content,
                re.IGNORECASE
            )
            descripcion = desc_match.group(1).strip() if desc_match else 'Transacción'
            
            # Detectar tipo (gasto o ingreso)
            is_expense = 'gasto' in content.lower() or 'compró' in content.lower()
            tx_type = 'expense' if is_expense else 'income'
            
            if monto and cuenta:
                return {
                    'monto': monto,
                    'cuenta': cuenta,
                    'descripcion': descripcion,
                    'tipo': tx_type,
                    'original_message': content
                }
        
        return None


# Instancia global del servicio
ai_service = AIService()

