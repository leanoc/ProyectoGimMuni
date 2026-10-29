# Historial de cambios

## [3.1.0] - 2026-10-23

### Agregado
- Sección «Acerca de...» con el contexto educativo del CFP N.º 402 de Berisso.
- Exportación de columnas seleccionadas de una o más tablas completas a archivos CSV separados.
- Correos de recepción de inscripción y de confirmación al obtener una vacante titular, incluso por promoción desde lista de espera.
- Configuración SMTP mediante variables de entorno, sin credenciales guardadas en el código.

### Documentación
- Se actualizaron el README y el manual operativo con las nuevas funciones, la configuración SMTP y el resguardo de los datos exportados.

### Compatibilidad
- El envío de correos es complementario: un fallo SMTP no revierte inscripciones, adjudicaciones ni promociones.
