import os
import requests

# Sistema de keywords local como fallback y para mejorar precisión
CATEGORY_KEYWORDS = {
    'expense': {
        'Comida': [
            'pizza', 'hamburguesa', 'comida', 'almuerzo', 'desayuno', 'cena', 'restaurante',
            'comí', 'comer', 'galleta', 'galletas', 'pan', 'panadería', 'supermercado',
            'mercado', 'verduras', 'frutas', 'carne', 'pollo', 'pescado', 'bebida',
            'café', 'té', 'jugo', 'refresco', 'agua', 'cerveza', 'vino', 'bar',
            'snack', 'dulce', 'chocolate', 'helado', 'pastel', 'torta'
        ],
        'Transporte': [
            'uber', 'taxi', 'bus', 'transporte', 'gasolina', 'combustible', 'metro',
            'tren', 'avión', 'vuelo', 'boleto', 'pasaje', 'estacionamiento', 'parqueo',
            'peaje', 'autopista', 'mecánico', 'llanta', 'aceite', 'reparación auto'
        ],
        'Vivienda': [
            'renta', 'alquiler', 'arriendo', 'hipoteca', 'casa', 'apartamento',
            'condominio', 'mantenimiento', 'reparación casa', 'pintura', 'plomero',
            'electricista', 'mueble', 'decoración'
        ],
        'Servicios': [
            'luz', 'agua', 'gas', 'electricidad', 'internet', 'teléfono', 'celular',
            'cable', 'streaming', 'netflix', 'spotify', 'servicio', 'wifi', 'plan'
        ],
        'Salud': [
            'doctor', 'médico', 'medicina', 'farmacia', 'hospital', 'consulta',
            'dentista', 'terapia', 'seguro salud', 'análisis', 'examen', 'vacuna',
            'medicamento', 'pastilla', 'tratamiento'
        ],
        'Entretenimiento': [
            'cine', 'película', 'concierto', 'fiesta', 'bar', 'discoteca', 'club',
            'juego', 'videojuego', 'suscripción', 'hobby', 'deporte', 'gym', 'gimnasio',
            'netflix', 'hbo', 'disney', 'entretenimiento', 'diversión'
        ],
        'Compras': [
            'compré', 'compra', 'comprar', 'tienda', 'shopping', 'mall', 'amazon',
            'online', 'mercadolibre', 'ebay', 'regalo', 'presente', 'ropa nueva'
        ],
        'Educación': [
            'curso', 'clase', 'escuela', 'universidad', 'colegio', 'libro', 'libros',
            'útiles', 'matrícula', 'inscripción', 'maestría', 'certificación',
            'capacitación', 'tutoría'
        ],
        'Ropa': [
            'ropa', 'zapatos', 'camisa', 'pantalón', 'vestido', 'falda', 'chaqueta',
            'abrigo', 'tenis', 'zapatillas', 'calcetines', 'sombrero', 'gorra',
            'bolso', 'cartera', 'accesorio'
        ],
        'Tecnología': [
            'computadora', 'laptop', 'celular', 'teléfono', 'tablet', 'auriculares',
            'mouse', 'teclado', 'monitor', 'cargador', 'cable', 'app', 'aplicación',
            'software', 'licencia', 'antivirus'
        ]
    },
    'income': {
        'Salario': ['salario', 'sueldo', 'nómina', 'pago', 'pagaron', 'cobré', 'quincena'],
        'Freelance': ['freelance', 'proyecto', 'cliente', 'trabajo independiente', 'factura'],
        'Inversiones': ['dividendo', 'interés', 'inversión', 'bolsa', 'acciones', 'crypto'],
        'Venta': ['venta', 'vendí', 'vender'],
        'Regalo': ['regalo', 'regalaron', 'me dieron'],
        'Reembolso': ['reembolso', 'devolución', 'devolvieron']
    }
}

def suggest_category_by_keywords(description, transaction_type='expense'):
    """
    Sistema de keywords para categorización rápida y precisa.
    Útil como fallback si la IA falla.
    """
    if not description:
        return None
        
    description_lower = description.lower()
    keywords_dict = CATEGORY_KEYWORDS.get(transaction_type, {})
    
    # Buscar coincidencias
    matches = []
    for category, keywords in keywords_dict.items():
        for keyword in keywords:
            if keyword in description_lower:
                matches.append((category, len(keyword)))  # Priorizar keywords más largas
                break
    
    # Retornar la categoría con el keyword más largo (más específico)
    if matches:
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[0][0]
    
    return None

def suggest_category_with_ai(description, transaction_type='expense', language='es', available_categories=None):
    """
    Usa IA de Groq para sugerir una categoría basada en la descripción.
    Incluye sistema de keywords como fallback mejorado.
    
    Args:
        description: Descripción de la transacción
        transaction_type: 'expense' o 'income'
        language: Idioma ('es', 'en', 'fr', 'de', 'pt', 'it')
        available_categories: Lista de nombres de categorías existentes (opcional)
    
    Returns:
        dict con 'category', 'confidence', y 'ai_suggested'
    """
    
    if not description or len(description.strip()) < 3:
        return {'category': None, 'confidence': 0, 'ai_suggested': False}
    
    # PRIMERO: Intentar con keywords locales (más rápido y preciso para casos comunes)
    keyword_match = suggest_category_by_keywords(description, transaction_type)
    if keyword_match:
        # Verificar que la categoría exists en las disponibles
        if available_categories and keyword_match in available_categories:
            return {
                'category': keyword_match,
                'confidence': 0.95,
                'ai_suggested': False,  # Es keyword, no IA
                'method': 'keywords'
            }
    
    # SEGUNDO: Si no hay match de keywords, usar IA
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        # Sin IA disponible, retornar keyword match si existe o None
        if keyword_match:
            return {'category': keyword_match, 'confidence': 0.8, 'ai_suggested': False, 'method': 'keywords_fallback'}
        return {'category': None, 'confidence': 0, 'ai_suggested': False}
    
    # Definir categorías base si no se proveen
    if not available_categories:
        if transaction_type == 'expense':
            available_categories = [
                'Comida', 'Transporte', 'Vivienda', 'Servicios', 'Salud', 
                'Entretenimiento', 'Compras', 'Educación', 'Ropa', 
                'Hogar', 'Tecnología', 'Viajes', 'Mascotas', 'Otros Gastos'
            ]
        else:
            available_categories = [
                'Salario', 'Freelance', 'Inversiones', 'Venta', 
                'Regalo', 'Reembolso', 'Otros Ingresos'
            ]
            
    cats_str = ", ".join(available_categories)
    
    # Prompt MEJORADO con ejemplos y contexto
    language_prompts = {
        'es': f'''Clasifica esta transacción en UNA categoría.

Transacción: "{description}"
Tipo: {transaction_type}

Categorías disponibles: {cats_str}

Ejemplos:
- "compré una pizza" → Comida
- "pagué el uber" → Transporte
- "compré una galleta" → Comida
- "netflix" → Entretenimiento
- "gasolina" → Transporte
- "corte de pelo" → Otros Gastos

Responde SOLO con el nombre EXACTO de la categoría (sin explicación).''',
        
        'en': f'''Classify this transaction into ONE category.

Transaction: "{description}"
Type: {transaction_type}

Available categories: {cats_str}

Examples:
- "bought a pizza" → Comida
- "paid for uber" → Transporte
- "bought cookies" → Comida
- "netflix subscription" → Entretenimiento

Respond ONLY with the EXACT category name (no explanation).'''
    }
    
    prompt = language_prompts.get(language, language_prompts['es'])
    
    try:
        # Llamar a la API de Groq
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.3-70b-versatile',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 30,
                'temperature': 0.1  # Baja temperatura para respuestas consistentes
            },
            timeout=10
        )
        
        if response.status_code != 200:
            # Fallback a keywords
            if keyword_match:
                return {'category': keyword_match, 'confidence': 0.8, 'ai_suggested': False, 'method': 'keywords_after_ai_fail'}
            return {'category': None, 'confidence': 0, 'ai_suggested': False}
        
        data = response.json()
        category = data['choices'][0]['message']['content'].strip()
        
        # Limpiar respuesta
        category = category.replace('"', '').replace("'", '').replace('.', '').strip()
        
        # Buscar coincidencia exacta o difusa
        matched_category = None
        
        # 1. Búsqueda exacta (case insensitive)
        for cat in available_categories:
            if cat.lower() == category.lower():
                matched_category = cat
                break
        
        # 2. Si no hay exacta, buscar contención
        if not matched_category:
            for cat in available_categories:
                if cat.lower() in category.lower() or category.lower() in cat.lower():
                    matched_category = cat
                    break
        
        if matched_category:
            return {
                'category': matched_category,
                'confidence': 0.9,
                'ai_suggested': True,
                'method': 'ai'
            }
        
        # Fallback final: keywords o "Otros"
        if keyword_match and keyword_match in available_categories:
            return {'category': keyword_match, 'confidence': 0.75, 'ai_suggested': False, 'method': 'keywords_fallback'}
        
        # Último recurso: "Otros"  
        if available_categories:
            otros_variants = ['Otros', 'Otros Gastos', 'Otros Ingresos', 'Other']
            for variant in otros_variants:
                if variant in available_categories:
                    return {'category': variant, 'confidence': 0.5, 'ai_suggested': True, 'method': 'ai_fallback_otros'}
            return {'category': available_categories[0], 'confidence': 0.3, 'ai_suggested': True, 'method': 'ai_fallback_first'}
        else:
            return {'category': category, 'confidence': 0.7, 'ai_suggested': True, 'method': 'ai_raw'}
    
    except Exception as e:
        print(f"Error IA Groq: {e}")
        # Fallback a keywords
        if keyword_match:
            return {'category': keyword_match, 'confidence': 0.8, 'ai_suggested': False, 'method': 'keywords_after_exception'}
        return {'category': None, 'confidence': 0, 'ai_suggested': False}
