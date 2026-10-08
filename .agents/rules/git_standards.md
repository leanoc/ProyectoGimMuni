# Estándares de Git y Control de Versiones

Para mantener un historial limpio, trazable y profesional, todo el trabajo en este repositorio debe adherirse a las siguientes convenciones modernas de Git:

## 1. Convención de Nombres de Ramas (Branching)
Las ramas deben crearse a partir de `main` o `develop` y deben seguir esta nomenclatura descriptiva:
- `feature/<nombre-descriptivo>`: Para nuevas características o funcionalidades (ej. `feature/sistema-de-sorteo`).
- `bugfix/<nombre-descriptivo>`: Para solución de errores (ej. `bugfix/error-validacion-dni`).
- `hotfix/<nombre-descriptivo>`: Para parches urgentes en producción.
- `refactor/<nombre-descriptivo>`: Para reescritura de código que no añade ni quita funcionalidades.
- `docs/<nombre-descriptivo>`: Para tareas exclusivamente de documentación.

## 2. Conventional Commits (Mensajes de Commit)
Los mensajes de commit deben seguir la especificación de *Conventional Commits*:
- **Formato general**: `<tipo>[ámbito opcional]: <descripción breve>`
- **Tipos permitidos**:
  - `feat:`: Una nueva característica.
  - `fix:`: Solución de un bug.
  - `refactor:`: Cambio de código que no arregla un bug ni añade una feature.
  - `style:`: Cambios de formato que no afectan la lógica (espacios, comas, etc.).
  - `test:`: Añadir o corregir pruebas.
  - `docs:`: Cambios en el README u otra documentación.
  - `chore:`: Actualizaciones de dependencias, scripts de build, configuraciones.
- **Cuerpo del mensaje**: Los commits que cambien lógica importante deben incluir un cuerpo detallado explicando *qué* cambió y *por qué* (evitar solo decir *cómo*).

## 3. Frecuencia y Tamaño de Commits (Atomic Commits)
- Los commits deben ser atómicos: cada commit debe representar un único cambio lógico o una unidad de trabajo completa que no rompa el sistema.
- Evitar hacer un solo commit masivo al final del día. Comitear frecuentemente.

## 4. Semantic Versioning (SemVer)
- Utilizar *Tags* y nomenclatura de versiones formales (ej. `v1.0.0`) para marcar hitos de entregas o pases a producción.
  - Mayor (`1.x.x`): Cambios incompatibles / rediseños grandes.
  - Menor (`x.1.x`): Nuevas funcionalidades retrocompatibles.
  - Parche (`x.x.1`): Corrección de errores.

## 5. Flujo de Trabajo (Git Flow simplificado)
- La rama `main` siempre debe estar en un estado funcional y estable.
- El trabajo pesado y los experimentos deben hacerse en ramas secundarias y unificarse mediante un *Merge* ordenado o *Pull Request*.
