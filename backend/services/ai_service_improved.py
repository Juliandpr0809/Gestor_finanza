"""
MEJORA 1: Sistema de IA mejorado con Function Calling y Structured Outputs
Reemplaza el método actual de keywords por detección inteligente con IA
"""
import os
import json
import requests
from datetime import datetime

class ImprovedAIService:
    """Servicio mejorado con function calling y structured outputs"""
    
    def __init__(self):
        self.api_key = os.environ.get('GROQ_API_KEY') or os.environ.get('GROK_API_KEY')
        self.api_base = os.environ.get('GROQ_API_BASE', 'https://api.groq.com/openai/v1')
        self.model = 'llama-3.3-70b-versatile'
        self.enabled = bool(self.api_key)
    
    def get_compact_context(self, user_id):
        """
        Contexto COMPACTO - Solo los datos más relevantes
        La clave es ser específico pero breve
        """
        from models import db, Account, Transaction, Category
        from datetime import datetime
        from sqlalchemy import extract
        
        # Usuario y moneda
        from models import User
        user = User.query.get(user_id)
        currency = user.preferred_currency if user else 'USD'
        
        # Cuentas con saldo
        accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
        accounts_data = [
            {
                'id': a.id,
                'name': a.name,
                'type': a.account_type,
                'balance': float(a.current_balance),
                'currency': a.currency
            }
            for a in accounts
        ]
        
        # Estadísticas del mes
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        month_expenses = db.session.query(
            db.func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'expense',
            extract('month', Transaction.transaction_date) == current_month,
            extract('year', Transaction.transaction_date) == current_year
        ).scalar() or 0
        
        month_income = db.session.query(
            db.func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'income',
            extract('month', Transaction.transaction_date) == current_month,
            extract('year', Transaction.transaction_date) == current_year
        ).scalar() or 0
        
        # Top 3 categorías del mes
        top_categories = db.session.query(
            Category.name,
            db.func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'expense',
            extract('month', Transaction.transaction_date) == current_month,
            extract('year', Transaction.transaction_date) == current_year
        ).group_by(Category.name).order_by(
            db.func.sum(Transaction.amount).desc()
        ).limit(3).all()
        
        return {
            'currency': currency,
            'accounts': accounts_data,
            'total_balance': sum(a['balance'] for a in accounts_data),
            'month_stats': {
                'expenses': abs(float(month_expenses)),
                'income': abs(float(month_income)),
                'balance': float(month_income) - abs(float(month_expenses))
            },
            'top_spending_categories': [
                {'name': c[0], 'amount': abs(float(c[1]))} 
                for c in top_categories
            ]
        }
    
    def chat_with_function_calling(self, user_id, message, conversation_history=None):
        """
        ESTRATEGIA 1: Function Calling (RECOMENDADO)
        Deja que el modelo decida qué acción ejecutar
        """
        context = self.get_compact_context(user_id)
        
        #  PROMPT COMPACTO Y DIRECTO
        system_prompt = f"""Eres un asistente financiero en español. Ayudas a gestionar las finanzas del usuario.

CONTEXTO DEL USUARIO (Moneda: {context['currency']}):
• Balance total: {context['currency']} {context['total_balance']:,.2f}
• Cuentas: {len(context['accounts'])}
{chr(10).join(f"  - {a['name']}: {a['currency']} {a['balance']:,.2f}" for a in context['accounts'])}

ESTADÍSTICAS DEL MES:
• Gastado: {context['currency']} {context['month_stats']['expenses']:,.2f}
• Ingresado: {context['currency']} {context['month_stats']['income']:,.2f}
• Balance mensual: {context['currency']} {context['month_stats']['balance']:,.2f}

INSTRUCCIONES:
1. Entiende la INTENCIÓN del usuario, no solo las palabras exactas
2. Si pide crear transacción → usa create_transaction
3. Si pregunta sobre finanzas → usa get_financial_summary
4. Si pide crear cuenta → usa create_account
5. SIEMPRE incluye la moneda {context['currency']} en los montos
6. Sé conversacional y natural
7. Si algo no está claro, pregunta amablemente"""

        # Definir funciones disponibles (compatibles con OpenAI format)
        functions = [
            {
                "name": "create_transaction",
                "description": "Crea una nueva transacción (gasto o ingreso) cuando el usuario menciona que gastó, compró, pagó, recibió dinero, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "Monto de la transacción (siempre positivo)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción de la transacción (ej: 'Compra en supermercado', 'Salario mensual')"
                        },
                        "transaction_type": {
                            "type": "string",
                            "enum": ["expense", "income"],
                            "description": "Tipo: 'expense' para gastos, 'income' para ingresos"
                        },
                        "account_name": {
                            "type": "string",
                            "description": "Nombre de la cuenta a usar (si no se especifica, usar la primera disponible)"
                        },
                        "category_hint": {
                            "type": "string",
                            "description": "Pista sobre la categoría (ej: 'comida', 'transporte', 'salario')"
                        }
                    },
                    "required": ["amount", "description", "transaction_type"]
                }
            },
            {
                "name": "get_financial_summary",
                "description": "Obtiene un resumen financiero detallado cuando el usuario pregunta por su balance, gastos, ingresos, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["month", "all_time"],
                            "description": "Período a consultar: 'month' para el mes actual, 'all_time' para todo el historial"
                        },
                        "include_categories": {
                            "type": "boolean",
                            "description": "Si incluir desglose por categorías"
                        }
                    },
                    "required": ["period"]
                }
            },
            {
                "name": "create_account",
                "description": "Crea una nueva cuenta bancaria o de efectivo",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre de la cuenta"
                        },
                        "account_type": {
                            "type": "string",
                            "enum": ["checking", "savings", "credit", "cash"],
                            "description": "Tipo de cuenta"
                        },
                        "initial_balance": {
                            "type": "number",
                            "description": "Saldo inicial (opcional, por defecto 0)"
                        }
                    },
                    "required": ["name", "account_type"]
                }
            }
        ]
        
        # Construir historial de mensajes
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Solo últimos 6 mensajes
        
        messages.append({"role": "user", "content": message})
        
        try:
            # Llamada a Groq con function calling
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': messages,
                'functions': functions,
                'function_call': 'auto',  # Deja que el modelo decida
                'temperature': 0.7,
                'max_tokens': 800
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    'type': 'error',
                    'message': f"Error de API: {response.text}"
                }
            
            result = response.json()
            choice = result['choices'][0]
            
            #  PROCESAR RESPUESTA
            if 'function_call' in choice['message']:
                # El modelo quiere ejecutar una función
                function_call = choice['message']['function_call']
                function_name = function_call['name']
                function_args = json.loads(function_call['arguments'])
                
                return {
                    'type': 'function_call',
                    'function': function_name,
                    'arguments': function_args,
                    'requires_confirmation': True,  #  AQUÍ ENTRA LA MEJORA 2
                    'original_message': message
                }
            else:
                # Respuesta normal del asistente
                return {
                    'type': 'text',
                    'message': choice['message']['content'],
                    'requires_confirmation': False
                }
        
        except Exception as e:
            return {
                'type': 'error',
                'message': f"Error al procesar: {str(e)}"
            }
    
    def chat_with_json_mode(self, user_id, message):
        """
        ESTRATEGIA 2: JSON Mode (alternativa más simple)
        Fuerza al modelo a responder siempre en JSON estructurado
        """
        context = self.get_compact_context(user_id)
        
        system_prompt = f"""Eres un asistente financiero. SIEMPRE responde en formato JSON válido.

Contexto del usuario (Moneda: {context['currency']}):
- Balance: {context['currency']} {context['total_balance']:,.2f}
- Cuentas: {', '.join(a['name'] for a in context['accounts'])}
- Gastos del mes: {context['currency']} {context['month_stats']['expenses']:,.2f}

FORMATO DE RESPUESTA:
{{
  "intent": "query|create_transaction|create_account|help",
  "confidence": 0.0-1.0,
  "data": {{
    // Para create_transaction:
    "amount": 1000,
    "description": "Compra en supermercado",
    "type": "expense",
    "account": "Efectivo",
    // Para query:
    "question_type": "balance|expenses|income|categories"
  }},
  "response_text": "Mensaje al usuario en lenguaje natural",
  "requires_confirmation": true/false
}}

Interpreta la INTENCIÓN del usuario, no las palabras exactas. Ejemplos:
- "gasté 50 en pan" → create_transaction
- "cuánto tengo" → query (balance)
- "créame una cuenta" → create_account"""

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                'response_format': {'type': 'json_object'},  # Fuerza JSON
                'temperature': 0.5,
                'max_tokens': 500
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return json.loads(content)  # Ya es JSON estructurado
            else:
                return {
                    'intent': 'error',
                    'response_text': f"Error de API: {response.text}",
                    'requires_confirmation': False
                }
        
        except Exception as e:
            return {
                'intent': 'error',
                'response_text': f"Error: {str(e)}",
                'requires_confirmation': False
            }
    
    def chat_with_improved_prompt(self, user_id, message, conversation_history=None):
        """
        ESTRATEGIA 3: Prompt Engineering Mejorado (sin cambiar el código actual)
        Optimiza el prompt existente para mejor comprensión
        """
        context = self.get_compact_context(user_id)
        
        # Prompt optimizado - MÁS CORTO pero MÁS EFECTIVO
        system_prompt = f"""Eres un asistente financiero en español que entiende lenguaje natural. Usuario usa moneda: {context['currency']}.

CONTEXTO ACTUAL:
• Balance: {context['currency']} {context['total_balance']:,.2f} en {len(context['accounts'])} cuenta(s)
• Gastos mes: {context['currency']} {context['month_stats']['expenses']:,.2f}
• Ingresos mes: {context['currency']} {context['month_stats']['income']:,.2f}

CUENTAS DISPONIBLES:
{chr(10).join(f'• {a["name"]}: {a["currency"]} {a["balance"]:,.2f}' for a in context['accounts'])}

CAPACIDADES:
1. CREAR TRANSACCIONES: Si el usuario dice algo como "gasté X", "compré Y", "me pagaron Z" → Genera una transacción

2. CONSULTAR FINANZAS: Si pregunta "cuánto tengo", "cuánto gasté", "mi balance" → Responde con los datos del contexto

3. GESTIONAR CUENTAS: Si pide "crear cuenta", "nueva cuenta" → Ayuda a crear

REGLAS DE INTERPRETACIÓN:
• "gasté/compré/pagué" = GASTO (expense)
• "me pagaron/recibí/ingresó" = INGRESO (income)
• Números sin contexto → Preguntar si es gasto o ingreso
• Si no menciona cuenta → Usar la primera disponible
• SIEMPRE incluir moneda {context['currency']} en respuestas

FORMATO DE RESPUESTA para transacciones:
Si detectas que quiere crear una transacción, responde:

"He registrado tu [gasto/ingreso] de {context['currency']} [MONTO] en [DESCRIPCIÓN] a tu cuenta [NOMBRE_CUENTA].

¿Deseas confirmar y aplicar esta transacción?"

Luego espera confirmación del usuario ("sí", "dale", "confirmo", etc.)

SÉ NATURAL Y CONVERSACIONAL. No uses lenguaje robótico."""

        # Construir mensajes
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history[-8:])
        
        messages.append({"role": "user", "content": message})
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 600,
                'top_p': 0.9
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"⚠️ Error de API: {response.text}"
        
        except Exception as e:
            return f"⚠️ Error: {str(e)}"


# Crear instancia global
improved_ai_service = ImprovedAIService()
