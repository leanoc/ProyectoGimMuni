# Estándares de Programación (Python)

Estas reglas dictan el estándar de calidad y seguridad para todo el código nuevo o modificado en este proyecto. Cualquier agente o desarrollador que intervenga en el código debe respetarlas estrictamente.

## 1. Tipado Estricto (Type Hinting)
- Todas las funciones y métodos nuevos deben incluir *Type Hints* tanto para sus argumentos como para su valor de retorno.
- **Ejemplo**: `def validar_usuario(dni: str, edad: int) -> bool:`
- Esto garantiza que el código sea auto-documentado y prevenga errores de tipo (TypeErrors).

## 2. Estilo y Formateo Consistente (PEP-8)
- El código debe respetar el estándar PEP-8 de Python (espaciado, nombres de variables en `snake_case`, constantes en `UPPER_CASE`, clases en `PascalCase`).
- Evitar funciones monolíticas; dividir el código en módulos y funciones pequeñas que hagan una sola cosa bien (Single Responsibility Principle).

## 3. Manejo de Errores Específico (No silenciar errores)
- **ESTRICTAMENTE PROHIBIDO**: Usar bloques `except Exception:` genéricos.
- Siempre se deben capturar excepciones precisas y predecibles (ej. `except sqlite3.IntegrityError:`, `except ValueError:`).
- Manejar el error adecuadamente (ej. loguear, retornar un estado de error, revertir un cambio en base de datos).

## 4. Documentación Obligatoria (Docstrings)
- Toda función, clase o módulo que incluya lógica de negocio debe tener un docstring claro (estilo Google o estándar) en la primera línea.
- Debe explicar: Qué hace la función, qué recibe (Args) y qué devuelve (Returns).

## 5. Testing Emparejado
- Por cada función nueva de lógica de negocio o consulta a la base de datos (por ejemplo, agregada a `operations.py`), se debe escribir o actualizar una prueba unitaria correspondiente en la suite de testing (ej. `test_gym.py`).
- El código no se considera completo si carece de pruebas que validen sus escenarios exitosos y de error.

## 6. Seguridad y Configuración Limpia
- Ninguna contraseña, ruta absoluta quemada (hardcodeada), ni configuración crítica debe ser subida al código fuente.
- Las constantes de entorno deben mantenerse aisladas (como en `config.py`) y referenciadas desde el código.
- Usar consultas parametrizadas (Prepared Statements con `?`) para TODAS las operaciones SQL, con el fin de evitar inyecciones SQL.
