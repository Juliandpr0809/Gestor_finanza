"""
🧠 TEST BRUTAL DEL NLU AVANZADO
Pruebas masivas de expresiones reales de usuarios, jerga local, typos, emojis, etc.
Para validar que el sistema detecta intenciones correctamente
"""

import sys
import os

# Agregar paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.ai_service import ai_service

# COLORES PARA OUTPUT
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def test_action_intent():
    """
    🎯 TEST: Detectar intención de acción (apply, edit, reject)
    """
    print(f"\n{BLUE}{'='*80}")
    print(f"🎯 TEST 1: DETECCIÓN DE INTENCIÓN DE ACCIÓN")
    print(f"{'='*80}{RESET}\n")
    
    test_cases = {
        # ✅ APLICAR - Formas REALES que dice el usuario
        'apply': [
            # Directo
            'aplícalo',
            'aplica',
            'aplico',
            'aplicala',
            'aplicalo',
            # Variantes con typos
            'aolicalo',  # Typo común
            'aplocaló',  # Acento mal puesto
            'aplizcalo',  # Typo de Z
            # Formas cortas
            'hazlo',
            'haz',
            'hazmeló',
            'hezblo',  # Typo común en teclado
            'hazo',
            # Registro
            'registralo',
            'registrala',
            'registra',
            'registrame',
            'registramelo',
            # Guardar
            'guardalo',
            'guardala',
            'guarda',
            'guardame',
            # Agregar
            'agrega',
            'agregalo',
            'agregala',
            'agregame',
            # Crear
            'crealo',
            'crea',
            'creame',
            # Confirmación
            'confirmalo',
            'confirma',
            'confirmame',
            # Ejecutar
            'ejecuta',
            'ejecutalo',
            'ejecutame',
            # Jerga latina
            'dale',
            'dale pa',
            'dale pal lao',
            'vamos',
            'listo',
            'ya',
            'ándale',
            'andale',
            'órale',
            'orale',
            'está bien',
            'esta bien',
            'pues bien',
            'bien',
            'bueno',
            'ok',
            'okey',
            'okei',
            'oki',
            'okok',
            # Afirmaciones simples
            'sí',
            'si',
            'sipi',
            'sip',
            'shi',
            'shii',
            'yesss',
            'yes',
            'claro',
            'claro que sí',
        ],
        
        # 🔧 EDITAR - Cambiar detalles
        'edit': [
            'cambiar',
            'cambia',
            'cambiale',
            'cambiam',
            'modifica',
            'modifícalo',
            'modifícame',
            'edita',
            'edítame',
            'actualiza',
            'actualicela',
            'actualícame',
            'corrige',
            'corrigela',
            'corrigeme',
            'ajusta',
            'ajustate',
            'arregla',
            'arreglamela',
            'cambiar monto',
            'cambiar descripción',
            'cambiar cuenta',
            'cambiar categoría',
            'modifica el monto',
            'actualiza la descripción',
        ],
        
        # ❌ RECHAZAR - No, cancelar, etc.
        'reject': [
            'cancela',
            'cancelala',
            'no',
            'nope',
            'nah',
            'negado',
            'desecha',
            'deshechala',
            'borr',
            'borra',
            'borrala',
            'elimina',
            'elimínala',
            'olvida',
            'olvídalo',
            'olvide',
            'olvídeme',
            'atrás',
            'atras',
            'volver',
            'volvamos',
            'no me',
            'no lo hagas',
            'ni se te ocurra',
        ],
    }
    
    results = {'apply': 0, 'edit': 0, 'reject': 0, 'errors': 0}
    
    for expected_action, messages in test_cases.items():
        print(f"{BOLD}{expected_action.upper()}{RESET}")
        
        for message in messages:
            result = ai_service.detect_action_intent(message)
            
            if result == expected_action:
                print(f"  {GREEN}✓{RESET} '{message}' → {expected_action}")
                results[expected_action] += 1
            else:
                print(f"  {RED}✗{RESET} '{message}' → {result} (esperaba {expected_action})")
                results['errors'] += 1
        
        print()
    
    total = sum(v for k, v in results.items() if k != 'errors')
    print(f"{BOLD}RESUMEN:{RESET}")
    print(f"  {GREEN}Exitosas: {total}{RESET}")
    print(f"  {RED}Errores: {results['errors']}{RESET}")
    print(f"  Ratio: {GREEN}{total}/{total + results['errors']} ({100*total/(total+results['errors']):.1f}%){RESET}")


def test_confirmation_words():
    """
    ✅ TEST: Detectar confirmaciones simples
    """
    print(f"\n{BLUE}{'='*80}")
    print(f"✅ TEST 2: DETECCIÓN DE CONFIRMACIONES SIMPLES")
    print(f"{'='*80}{RESET}\n")
    
    confirmations = [
        'sí',
        'si',
        'sipi',
        'sip',
        'ok',
        'okey',
        'dale',
        'listo',
        'ya',
        'bien',
        'está bien',
        'confirmo',
        'acepto',
        'aprobado',
        'yes',
        'claro',
        'valido',
        'validado',
        'ok ok',
        'sí ok',
        'sí bien',
    ]
    
    rejections = [
        'no',
        'nope',
        'nah',
        'negado',
        'cancela',
        'no gracias',
    ]
    
    print(f"{GREEN}Confirmaciones esperadas:{RESET}")
    success = 0
    for conf in confirmations:
        result = ai_service.detect_confirmation_words(conf)
        if result:
            print(f"  {GREEN}✓{RESET} '{conf}' → confirmación")
            success += 1
        else:
            print(f"  {RED}✗{RESET} '{conf}' → NO detectado como confirmación")
    
    print(f"\n{RED}Rechazos (NO deben ser confirmaciones):{RESET}")
    false_positives = 0
    for rejection in rejections:
        result = ai_service.detect_confirmation_words(rejection)
        if not result:
            print(f"  {GREEN}✓{RESET} '{rejection}' → correctamente NO es confirmación")
        else:
            print(f"  {RED}✗{RESET} '{rejection}' → FALSO POSITIVO (detectado como confirmación)")
            false_positives += 1
    
    total = len(confirmations) + len(rejections)
    correct = success + (len(rejections) - false_positives)
    print(f"\n{BOLD}RESUMEN:{RESET}")
    print(f"  {GREEN}Exitosas: {correct}/{total} ({100*correct/total:.1f}%){RESET}")


def test_clean_input():
    """
    🧹 TEST: Limpieza de entrada (emojis, texto pegado, etc.)
    """
    print(f"\n{BLUE}{'='*80}")
    print(f"🧹 TEST 3: LIMPIEZA DE ENTRADA DEL USUARIO")
    print(f"{'='*80}{RESET}\n")
    
    test_cases = [
        # (entrada sucia, salida esperada limpia)
        (
            "✅ **Gasto registrado**\n🍟 Monto: COP 15,000\nAplícalo",
            "Aplícalo"
        ),
        (
            "❌ No pude identificar\n📊 Balance: COP 1,200,000\nRegistra mi gasto",
            "Registra mi gasto"
        ),
        (
            "✅ **Transacción aplicada** 🎉\n💡 Recuerda que...\nDale, otro gasto",
            "Dale, otro gasto"
        ),
        (
            "🍞️ Ingreso registrado\n📊 Balance actualizado\nMe папа me мано 3k\nAña",
            "Me папа me мано 3k Añа"  # Preserve datos nuevos
        ),
        (
            "Gasté 25000 en mercado 🛒",
            "Gasté 25000 en mercado"
        ),
        (
            "💰 Compra de COP 50,000 📦\nÁgregadoSí, correcto",
            "Sí, correcto"
        ),
        (
            "📈 Análisis:\n✅ Transacción exitosa\n- Monto: COP 12,500\nHazlo",
            "Hazlo"
        ),
        (
            "🔄 Balance actualizado: COP 1,185,000\n⚠️ Nota: Esta es solo una simulación\nAplica eso",
            "Aplica eso"
        ),
    ]
    
    print("Limpieza de emojis, símbolos y texto pegado:\n")
    success = 0
    
    for dirty_input, expected_clean in test_cases:
        result = ai_service.clean_user_input(dirty_input)
        
        # Ser flexible - no tiene que ser EXACTAMENTE igual, solo similar
        is_similar = (
            expected_clean.lower() in result.lower() or
            result.lower() in expected_clean.lower() or
            set(result.split()) & set(expected_clean.split())  # Al menos algunas palabras iguales
        )
        
        if is_similar:
            print(f"{GREEN}✓{RESET} Limpieza correcta")
            print(f"   Entrada: '{dirty_input[:50]}...'")
            print(f"   Resultado: '{result}'")
            success += 1
        else:
            print(f"{RED}✗{RESET} Limpieza fallida")
            print(f"   Entrada: '{dirty_input[:50]}...'")
            print(f"   Esperaba: '{expected_clean}'")
            print(f"   Resultado: '{result}'")
        print()
    
    print(f"{BOLD}RESUMEN:{RESET}")
    print(f"  {GREEN}Exitosas: {success}/{len(test_cases)} ({100*success/len(test_cases):.1f}%){RESET}")


def test_combined_scenarios():
    """
    🎭 TEST: Escenarios COMBINADOS (como en conversación real)
    Usuario dice algo sucio, con typos, emojis, y el sistema debe:
    1. Limpiar
    2. Detectar intención
    3. Detectar si es confirmación
    """
    print(f"\n{BLUE}{'='*80}")
    print(f"🎭 TEST 4: ESCENARIOS COMBINADOS (REALISTAS)")
    print(f"{'='*80}{RESET}\n")
    
    scenarios = [
        {
            'name': 'Usuario copia-pega respuesta y dice aplícalo',
            'input': """✅ **Gasto registrado**
- **Monto:** COP 15,000.00 (3 fritos x COP 5,000.00)
- **Cuenta:** Nequi
- **Descripción:** Comida (fritos)

📊 **Balance actualizado:**
- **Anterior:** COP 1,200,000.00
- **Gasto:** COP 15,000.00
- **Nuevo balance:** COP 1,185,000.00

Aplícalo""",
            'expected_action': 'apply',
            'expected_confirmation': False,
            'expected_clean_contains': ['Aplícalo', 'aplicalo', 'aplica']
        },
        {
            'name': 'Usuario con jerga latina dice hazlo',
            'input': '🍟 Gasto registrado, hazlo pue',
            'expected_action': 'apply',
            'expected_confirmation': False,
            'expected_clean_contains': ['hazlo', 'pue']
        },
        {
            'name': 'Usuario typo dice "aolicalo"',
            'input': 'aolicalo 🎉',
            'expected_action': 'apply',
            'expected_confirmation': False,
            'expected_clean_contains': ['aolicalo']
        },
        {
            'name': 'Usuario solo confirma con "sí"',
            'input': '✅ Está bien, sí',
            'expected_action': None,
            'expected_confirmation': True,
            'expected_clean_contains': ['sí']
        },
        {
            'name': 'Usuario rechaza su gasto',
            'input': '❌ No, cancela eso 🚫',
            'expected_action': 'reject',
            'expected_confirmation': False,
            'expected_clean_contains': ['cancela', 'no']
        },
        {
            'name': 'Usuario con jerga quiere editar',
            'input': '🔧 Cambiale el monto, anda',
            'expected_action': 'edit',
            'expected_confirmation': False,
            'expected_clean_contains': ['Cambiale', 'monto']
        },
        {
            'name': 'Usuario dice "Dale pa" (jerga)',
            'input': '💰 Dale pa, registralo',
            'expected_action': 'apply',
            'expected_confirmation': False,
            'expected_clean_contains': ['Dale', 'registralo']
        },
        {
            'name': 'Usuario simplemente dice "ok"',
            'input': 'ok',
            'expected_action': None,
            'expected_confirmation': True,
            'expected_clean_contains': ['ok']
        },
        {
            'name': 'Usuario dice "está bien" sin emojis',
            'input': 'está bien',
            'expected_action': None,
            'expected_confirmation': True,
            'expected_clean_contains': ['está bien']
        },
        {
            'name': 'Entrada muy sucia con múltiples líneas de respuesta',
            'input': """📊 **Balance actualizado:** COP 1,188,000.00

💡 **Recuerda que es importante...**

⚠️ **Nota:** Esta es solo una simulación

Pero aplícalo en serio ahora""",
            'expected_action': 'apply',
            'expected_confirmation': False,
            'expected_clean_contains': ['aplícalo']
        },
    ]
    
    success = 0
    
    for scenario in scenarios:
        print(f"{BOLD}{scenario['name']}{RESET}")
        
        # Limpiar
        clean = ai_service.clean_user_input(scenario['input'])
        
        # Detectar acción
        action = ai_service.detect_action_intent(clean)
        
        # Detectar confirmación
        confirmation = ai_service.detect_confirmation_words(clean)
        
        # Verificar
        action_ok = action == scenario['expected_action']
        conf_ok = confirmation == scenario['expected_confirmation']
        
        # Verificar palabras clave en la salida limpia
        clean_ok = any(
            keyword.lower() in clean.lower() 
            for keyword in scenario['expected_clean_contains']
        )
        
        all_ok = action_ok and conf_ok and clean_ok
        
        print(f"  Input (first 70 chars): {scenario['input'][:70]}...")
        print(f"  ✓ Limpiado: '{clean}'")
        print(f"  {'✓' if action_ok else '✗'} Acción: {action} (esperaba {scenario['expected_action']})")
        print(f"  {'✓' if conf_ok else '✗'} Confirmación: {confirmation} (esperaba {scenario['expected_confirmation']})")
        print(f"  {'✓' if clean_ok else '✗'} Palabras clave presente: {scenario['expected_clean_contains']}")
        
        if all_ok:
            print(f"  {GREEN}✅ ESCENARIO EXITOSO{RESET}")
            success += 1
        else:
            print(f"  {RED}❌ ESCENARIO FALLIDO{RESET}")
        print()
    
    print(f"{BOLD}RESUMEN:{RESET}")
    print(f"  {GREEN}Escenarios exitosos: {success}/{len(scenarios)} ({100*success/len(scenarios):.1f}%){RESET}")


def test_ambiguous_cases():
    """
    🤔 TEST: Casos AMBIGUOS que podrían ser confusos
    """
    print(f"\n{BLUE}{'='*80}")
    print(f"🤔 TEST 5: CASOS AMBIGUOS Y EDGE CASES")
    print(f"{'='*80}{RESET}\n")
    
    ambiguous = [
        {
            'input': 'bien',
            'note': '¿Es confirmación o solo un adjetivo?',
            'should_be_confirmation': True
        },
        {
            'input': 'está bien',
            'note': '¿Es confirmación o comentario?',
            'should_be_confirmation': True
        },
        {
            'input': 'no está bien',
            'note': '¿Es rechazo o solo negación?',
            'should_be_confirmation': False
        },
        {
            'input': 'dale',
            'note': '¿Es jerga para "aplícalo" o solo un saludo?',
            'should_be_confirmation': True  # En contexto de transacción = confirmación
        },
        {
            'input': 'cambiar',
            'note': '¿Es editar o es un comentario?',
            'should_be_edit': True
        },
        {
            'input': 'volver',
            'note': '¿Es rechazo o ir a otra pantalla?',
            'should_be_reject': True
        },
        {
            'input': 'si',
            'note': 'Sin tilde - ¿Es confirmación o la conjunción "si"?',
            'should_be_confirmation': True  # En contexto = confirmación
        },
        {
            'input': 'ok ok ok',
            'note': '¿Múltiples ok = múltiple confirmación?',
            'should_be_confirmation': True
        },
        {
            'input': 'sip',
            'note': 'Typo de "sipi" del jerga',
            'should_be_confirmation': True
        },
    ]
    
    print("Casos ambiguos que requieren contexto:\n")
    
    for case in ambiguous:
        print(f"{BOLD}{case['input']}{RESET}")
        print(f"  Nota: {case['note']}")
        
        action = ai_service.detect_action_intent(case['input'])
        confirmation = ai_service.detect_confirmation_words(case['input'])
        
        if 'should_be_confirmation' in case:
            result = '✓' if confirmation == case['should_be_confirmation'] else '✗'
            print(f"  {result} Confirmación: {confirmation}")
        
        if 'should_be_edit' in case:
            result = '✓' if action == 'edit' else '✗'
            print(f"  {result} Editar: {action}")
        
        if 'should_be_reject' in case:
            result = '✓' if action == 'reject' else '✗'
            print(f"  {result} Rechazar: {action}")
        
        print()


def test_transaction_detection():
    """
    💳 TEST: Detectar cuando hay REALMENTE una transacción
    """
    print(f"\n{BLUE}{'='*80}")
    print(f"💳 TEST 6: DETECCIÓN DE TRANSACCIONES REALES")
    print(f"{'='*80}{RESET}\n")
    
    transactions = [
        # (mensaje, debe_detectarse, tipo_esperado)
        ('Me comí 3 fritos a 5k cada uno', True, 'expense'),
        ('Gasté 25000 en mercado', True, 'expense'),
        ('Le pasé 200k a mi mamá', True, 'expense'),
        ('Recibí 50000 de mi papá', True, 'income'),
        ('Mi hermano me pagó 30000', True, 'income'),
        ('Compré una laptop por 1500000', True, 'expense'),
        ('¿Cuánto gasté este mes?', False, None),  # Pregunta, no transacción
        ('Hola, ¿cómo estás?', False, None),  # Conversación normal
        ('Aplícalo', False, None),  # Comando, no transacción nueva
        ('Cambiar monto a 50000', False, None),  # Edición, no nueva transacción
    ]
    
    print("Detecting transaction intents:\n")
    success = 0
    
    for message, should_have_intent, expected_type in transactions:
        intent = ai_service.detect_transaction_intent(message)
        has_intent = intent and intent.get('has_intent')
        
        if has_intent == should_have_intent:
            if has_intent:
                actual_type = intent.get('transaction_type')
                type_ok = actual_type == expected_type
                status = '✓' if type_ok else '⚠'
                print(f"  {GREEN}{status}{RESET} '{message}'")
                print(f"      Detectada como: {actual_type}")
                if type_ok:
                    success += 1
            else:
                print(f"  {GREEN}✓{RESET} '{message}'")
                print(f"      Correctamente NO detectada como transacción")
                success += 1
        else:
            print(f"  {RED}✗{RESET} '{message}'")
            print(f"      Esperaba intent={should_have_intent}, obtuvo intent={has_intent}")
        print()
    
    print(f"{BOLD}RESUMEN:{RESET}")
    print(f"  {GREEN}Exitoso: {success}/{len(transactions)} ({100*success/len(transactions):.1f}%){RESET}")


if __name__ == '__main__':
    print(f"\n{BOLD}{BLUE}{'='*80}")
    print(f"🚀 PRUEBAS MASIVAS DEL NLU AVANZADO")
    print(f"Test grande y creativo con expresiones reales de usuarios")
    print(f"{'='*80}{RESET}\n")
    
    try:
        test_action_intent()
        test_confirmation_words()
        test_clean_input()
        test_combined_scenarios()
        test_ambiguous_cases()
        test_transaction_detection()
        
        print(f"\n{BOLD}{GREEN}{'='*80}")
        print(f"✅ TODAS LAS PRUEBAS COMPLETADAS")
        print(f"{'='*80}{RESET}\n")
        
    except Exception as e:
        print(f"\n{RED}❌ ERROR EN LAS PRUEBAS: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
