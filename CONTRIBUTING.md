# Contribuir a FinanceFlow

¡Gracias por tu interés en contribuir a FinanceFlow! 🎉

## 📋 Código de Conducta

Este proyecto se adhiere a un Código de Conducta. Al participar, se espera que mantengas este código. Por favor reporta comportamientos inaceptables.

## 🤔 ¿Cómo puedo contribuir?

### Reportar Bugs

Antes de crear un reporte de bug:
- Verifica que el bug no haya sido reportado antes
- Asegúrate de estar usando la última versión
- Recopila información sobre el bug (pasos para reproducir, logs, etc.)

**Formato del reporte:**
```
**Descripción del bug**
Descripción clara y concisa del bug.

**Pasos para reproducir**
1. Ve a '...'
2. Haz clic en '...'
3. Desplázate hasta '...'
4. Ver error

**Comportamiento esperado**
Descripción de lo que esperabas que sucediera.

**Capturas de pantalla**
Si aplica, añade capturas de pantalla.

**Entorno:**
- OS: [ej. Windows 11]
- Navegador: [ej. Chrome 120]
- Versión de Python: [ej. 3.11]
```

### Sugerir Mejoras

Las sugerencias de mejoras son bienvenidas. Antes de sugerir:
- Verifica que no exista ya una sugerencia similar
- Proporciona un caso de uso claro

### Pull Requests

1. **Fork el proyecto**
2. **Crea tu rama** (`git checkout -b feature/AmazingFeature`)
3. **Sigue las guías de estilo**
4. **Escribe tests** para tu código
5. **Commit tus cambios** siguiendo las convenciones
6. **Push a la rama** (`git push origin feature/AmazingFeature`)
7. **Abre un Pull Request**

## 📝 Guías de Estilo

### Git Commit Messages

Usa los siguientes prefijos:
- `Add:` Para nuevas funcionalidades
- `Fix:` Para corrección de bugs
- `Update:` Para actualizaciones de código existente
- `Refactor:` Para refactorización de código
- `Docs:` Para cambios en documentación
- `Test:` Para añadir o actualizar tests
- `Style:` Para cambios de formato
- `Chore:` Para tareas de mantenimiento

**Ejemplo:**
```
Add: endpoint para exportar transacciones a CSV

- Implementa nuevo endpoint /api/transactions/export
- Añade validación de parámetros de fecha
- Incluye tests unitarios
```

### Estilo de Código Python

- Sigue [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Usa `black` para formateo automático
- Usa `flake8` para linting
- Documenta funciones con docstrings
- Máximo 88 caracteres por línea (black default)

**Ejemplo:**
```python
def calculate_balance(account_id: int, start_date: datetime) -> float:
    """
    Calcula el balance de una cuenta desde una fecha específica.
    
    Args:
        account_id: ID de la cuenta
        start_date: Fecha inicial para el cálculo
        
    Returns:
        Balance calculado como float
        
    Raises:
        ValueError: Si la cuenta no existe
    """
    # Implementación
    pass
```

### Estilo de Código JavaScript

- Usa ES6+ features
- 2 espacios para indentación
- Usa `const` y `let`, evita `var`
- Nombres de variables en camelCase
- Nombres de clases en PascalCase

### Tests

- Escribe tests para nuevo código
- Mantén cobertura > 80%
- Usa nombres descriptivos para tests
- Organiza tests con arrange-act-assert

```python
def test_user_can_create_transaction():
    # Arrange
    user = create_test_user()
    account = create_test_account(user)
    
    # Act
    transaction = create_transaction(account, amount=100)
    
    # Assert
    assert transaction.amount == 100
    assert transaction.account_id == account.id
```

## 🏗️ Estructura de Ramas

- `main` - Producción estable
- `develop` - Desarrollo activo
- `feature/*` - Nuevas funcionalidades
- `fix/*` - Correcciones de bugs
- `hotfix/*` - Correcciones urgentes

## ✅ Checklist del Pull Request

Antes de enviar tu PR, verifica:

- [ ] El código sigue las guías de estilo
- [ ] Has añadido tests que prueban tu cambio
- [ ] Todos los tests pasan (`pytest`)
- [ ] Has actualizado la documentación si es necesario
- [ ] El commit sigue las convenciones
- [ ] Has probado en diferentes navegadores (si aplica)
- [ ] No hay warnings de linter
- [ ] Has actualizado CHANGELOG.md (si aplica)

## 🔄 Proceso de Review

1. Al menos un maintainer debe aprobar el PR
2. Todos los tests de CI deben pasar
3. La cobertura de código no debe disminuir
4. Los comentarios del review deben ser resueltos

## 📚 Recursos

- [Documentación del Proyecto](docs/)
- [Guía de API](docs/API.md)
- [Arquitectura del Backend](docs/BACKEND_STRUCTURE.md)
- [Setup de Desarrollo](docs/SETUP.md)

## ❓ Preguntas

Si tienes preguntas, puedes:
- Abrir un issue con la etiqueta `question`
- Contactar a los maintainers

## 🎉 Reconocimientos

Los contribuidores serán añadidos al archivo CONTRIBUTORS.md

---

¡Gracias por contribuir a FinanceFlow! 💰✨
