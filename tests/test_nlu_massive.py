"""
🧠 TEST BRUTAL DEL NLU AVANZADO
Pruebas masivas de expresiones reales de usuarios, jerga local, typos, emojis, etc.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.ai_service import ai_service

# COLORES
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def test_action_intent():
    print(f"\n{BLUE}{'='*80}")
    print(f"🎯 TEST 1: DETECCIÓN DE INTENCIÓN DE ACCIÓN")
    print(f"{'='*80}{RESET}\n")
    
    test_cases = {
        'apply': [
            'aplícalo', 'aplica', 'aplicalo', 'aolicalo', 'hazlo', 'haz',
            'hezblo', 'registralo', 'registra', 'guardalo', 'guarda',
            'agrega', 'agregalo', 'crealo', 'crea', 'ejecuta',
            'dale', 'dale pa', 'vamos', 'listo', 'ya', 'ándale',
            'órale', 'está bien', 'bueno', 'ok', 'okey', 'sí', 'si',
            'sipi', 'yes', 'claro', 'confirmo', 'acepto',
        ],
        'edit': [
            'cambiar', 'cambia', 'cambiale', 'modifica', 'edita',
            'actualiza', 'corrige', 'ajusta', 'arregla',
            'cambiar monto', 'cambiar descripción',
        ],
        'reject': [
            'cancela', 'no', 'nope', 'nah', 'borr', 'borra',
            'elimina', 'olvida', 'olvídalo', 'atrás', 'volver',
        ],
    }
    
    results = {'apply': 0, 'edit': 0, 'reject': 0, 'errors': 0}
    
    for expected_action, messages in test_cases.items():
        print(f"{BOLD}{expected_action.upper()}{RESET}")
        for msg in messages[:10]:  # Mostrar primeros 10
            result = ai_service.detect_action_intent(msg)
            if result == expected_action:
                print(f"  {GREEN}✓{RESET} '{msg}' → {expected_action}")
                results[expected_action] += 1
            else:
                print(f"  {RED}✗{RESET} '{msg}' → {result}")
                results['errors'] += 1
        print()
    
    total = sum(v for k, v in results.items() if k != 'errors')
    print(f"{BOLD}RESUMEN: {GREEN}{total} exitosas, {RED}{results['errors']} errores{RESET}")


def test_confirmation_words():
    print(f"\n{BLUE}{'='*80}")
    print(f"✅ TEST 2: DETECCIÓN DE CONFIRMACIONES SIMPLES")
    print(f"{'='*80}{RESET}\n")
    
    confirmations = [
        'sí', 'si', 'ok', 'dale', 'listo', 'ya', 'bien',
        'está bien', 'confirmo', 'yes', 'claro', 'sipi',
    ]
    
    print(f"{GREEN}Confirmaciones esperadas:{RESET}")
    success = 0
    for conf in confirmations:
        result = ai_service.detect_confirmation_words(conf)
        if result:
            print(f"  {GREEN}✓{RESET} '{conf}'")
            success += 1
        else:
            print(f"  {RED}✗{RESET} '{conf}'")
    
    print(f"\n{BOLD}RESUMEN: {GREEN}{success}/{len(confirmations)} detectadas{RESET}")


def test_clean_input():
    print(f"\n{BLUE}{'='*80}")
    print(f"🧹 TEST 3: LIMPIEZA DE ENTRADA DEL USUARIO")
    print(f"{'='*80}{RESET}\n")
    
    test_cases = [
        ("✅ **Gasto registrado**\n🍟 Monto: COP 15,000\nAplícalo", "Aplícalo"),
        ("❌ No pude identificar\n📊 Balance: COP 1,200,000\nRegistra mi gasto", "Registra"),
        ("Gasté 25000 en mercado 🛒", "Gasté 25000"),
        ("📈 Análisis:\n✅ Transacción exitosa\nHazlo", "Hazlo"),
    ]
    
    success = 0
    for dirty, expected in test_cases:
        result = ai_service.clean_user_input(dirty)
        is_similar = expected.lower() in result.lower()
        
        if is_similar:
            print(f"{GREEN}✓{RESET} Limpieza correcta")
            print(f"   Entrada (70 chars): '{dirty[:70]}...'")
            print(f"   Resultado: '{result}'")
            success += 1
        else:
            print(f"{RED}✗{RESET} Limpieza fallida")
            print(f"   Resultado: '{result}'")
        print()
    
    print(f"{BOLD}RESUMEN: {GREEN}{success}/{len(test_cases)} exitosas{RESET}")


def test_combined_scenarios():
    print(f"\n{BLUE}{'='*80}")
    print(f"🎭 TEST 4: ESCENARIOS COMBINADOS (REALISTAS)")
    print(f"{'='*80}{RESET}\n")
    
    scenarios = [
        {
            'name': 'Usuario copia-pega respuesta completa y dice aplícalo',
            'input': """✅ **Gasto registrado**
- **Monto:** COP 15,000.00 (3 fritos x COP 5,000.00)
- **Cuenta:** Nequi
- **Descripción:** Comida (fritos)
📊 **Balance actualizado:**
Aplícalo""",
            'expected_action': 'apply',
        },
        {
            'name': 'Jerga latina: "hazlo pue"',
            'input': '🍟 Gasto registrado, hazlo pue',
            'expected_action': 'apply',
        },
        {
            'name': 'Usuario solo confirma con "sí"',
            'input': '✅ Está bien, sí',
            'expected_action': None,
        },
        {
            'name': 'Usuario rechaza gasto',
            'input': '❌ No, cancela eso 🚫',
            'expected_action': 'reject',
        },
        {
            'name': 'Usuario quiere editar monto',
            'input': '🔧 Cambiale el monto, anda',
            'expected_action': 'edit',
        },
        {
            'name': 'Jerga: "Dale pa"',
            'input': '💰 Dale pa, registralo',
            'expected_action': 'apply',
        },
    ]
    
    success = 0
    for scenario in scenarios:
        print(f"{BOLD}{scenario['name']}{RESET}")
        clean = ai_service.clean_user_input(scenario['input'])
        action = ai_service.detect_action_intent(clean)
        
        is_ok = action == scenario['expected_action']
        if is_ok:
            print(f"  {GREEN}✓{RESET} Limpiado: '{clean}'")
            print(f"  {GREEN}✓{RESET} Acción: {action}")
            success += 1
        else:
            print(f"  {RED}✗{RESET} Esperaba {scenario['expected_action']}, obtuvo {action}")
        print()
    
    print(f"{BOLD}RESUMEN: {GREEN}{success}/{len(scenarios)} escenarios exitosos{RESET}")


def test_transaction_detection():
    print(f"\n{BLUE}{'='*80}")
    print(f"💳 TEST 5: DETECCIÓN DE TRANSACCIONES REALES")
    print(f"{'='*80}{RESET}\n")
    
    transactions = [
        ('Me comí 3 fritos a 5k cada uno', True, 'expense'),
        ('Gasté 25000 en mercado', True, 'expense'),
        ('Le pasé 200k a mi mamá', True, 'expense'),
        ('Recibí 50000 de mi papá', True, 'income'),
        ('Mi hermano me pagó 30000', True, 'income'),
        ('Compré una laptop por 1500000', True, 'expense'),
        ('¿Cuánto gasté este mes?', False, None),
        ('Hola, ¿cómo estás?', False, None),
        ('Aplícalo', False, None),
        ('Cambiar monto a 50000', False, None),
    ]
    
    success = 0
    for message, should_have_intent, expected_type in transactions:
        intent = ai_service.detect_transaction_intent(message)
        has_intent = bool(intent and intent.get('has_intent'))
        
        if has_intent == should_have_intent:
            actual_type = intent.get('transaction_type') if has_intent else None
            type_ok = actual_type == expected_type
            
            if type_ok:
                print(f"  {GREEN}✓{RESET} '{message}'")
                if has_intent:
                    print(f"     → {actual_type}")
                success += 1
            else:
                print(f"  {RED}⚠{RESET} '{message}'")
                print(f"     Esperaba {expected_type}, obtuvo {actual_type}")
        else:
            print(f"  {RED}✗{RESET} '{message}'")
            print(f"     Esperaba intent={should_have_intent}, obtuvo {has_intent}")
    
    print(f"\n{BOLD}RESUMEN: {GREEN}{success}/{len(transactions)} correctas{RESET}")


def test_edge_cases():
    print(f"\n{BLUE}{'='*80}")
    print(f"🤔 TEST 6: CASOS EDGE Y AMBIGUOS")
    print(f"{'='*80}{RESET}\n")
    
    ambiguous = [
        ('bien', True, 'confirmación simple'),
        ('está bien', True, 'confirmación formal'),
        ('dale', True, 'jerga latina'),
        ('si', True, 'sin tilde'),
        ('ok ok ok', True, 'múltiples confirmaciones'),
        ('no está bien', False, 'negación, no confirmación'),
        ('cambiar monto', 'edit', 'comando de edición'),
        ('volver', 'reject', 'rechazo de acción'),
    ]
    
    success = 0
    for text, expected, desc in ambiguous:
        result_conf = ai_service.detect_confirmation_words(text)
        result_action = ai_service.detect_action_intent(text)
        
        if isinstance(expected, bool):
            is_ok = result_conf == expected
            print(f"  {'✓' if is_ok else '✗'} '{text}' ({desc})")
            print(f"     Confirmación: {result_conf}" + (' ✓' if is_ok else f' (esperaba {expected})'))
        else:
            is_ok = result_action == expected
            print(f"  {'✓' if is_ok else '✗'} '{text}' ({desc})")
            print(f"     Acción: {result_action}" + (' ✓' if is_ok else f' (esperaba {expected})'))
        
        if is_ok:
            success += 1
        print()
    
    print(f"{BOLD}RESUMEN: {GREEN}{success}/{len(ambiguous)} correctas{RESET}")


if __name__ == '__main__':
    print(f"\n{BOLD}{BLUE}{'='*80}")
    print(f"🚀 TEST MASIVO DEL NLU AVANZADO")
    print(f"Expresiones reales, jerga local, typos, emojis")
    print(f"{'='*80}{RESET}\n")
    
    try:
        test_action_intent()
        test_confirmation_words()
        test_clean_input()
        test_combined_scenarios()
        test_transaction_detection()
        test_edge_cases()
        
        print(f"\n{BOLD}{GREEN}{'='*80}")
        print(f"✅ TODAS LAS PRUEBAS COMPLETADAS")
        print(f"{'='*80}{RESET}\n")
        
    except Exception as e:
        print(f"\n{RED}❌ ERROR: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
