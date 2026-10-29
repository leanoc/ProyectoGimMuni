### *Planes de Desarrollo v1*



1. *Exportar resultados a PDF / Excel*
2. *Fecha límite de inscripción*
3. *Notificación por e-mail al sorteado*
4. 



*Agregados Complejos*

1. *Login con roles (Administrador / Visitante)*
2. *Importación masiva de inscriptos desde CSV*
3. *Historial de sorteos anteriores*


Plan de Ciberseguridad y Protección de Datos para la App Municipal


1. Seguridad de la Base de Datos (Técnico)

• Cifrado en reposo con SQLCipher: Reemplazar el motor estándar de SQLite por SQLCipher. Esto aplica un cifrado de grado militar (AES-256) al archivo de la base de datos, impidiendo que alguien copie el archivo en un pendrive y lea los datos fuera de la aplicación.
• Resguardo seguro de credenciales (Hashing): Las contraseñas de los usuarios municipales no se guardarán en texto plano. Se utilizarán algoritmos de encriptación irreversible (como bcrypt o PBKDF2 mediante la librería hashlib de Python) para proteger el acceso al sistema.
• Principio de menor privilegio: Restringir las funciones críticas dentro del código de Python. Por ejemplo, solo un usuario con rol de "Administrador" podrá eliminar registros o exportar listados masivos.

2. Control de Acceso a la Aplicación (Funcional)

• Pantalla de autenticación obligatoria (Login): La aplicación no se ejecutará de forma directa; requerirá un usuario y contraseña válidos para iniciar sesión cada vez que se abra.
• Cierre de sesión por inactividad: Si el operador municipal deja la aplicación abierta y se desatiende de la computadora, el sistema cerrará la sesión de la app automáticamente tras unos minutos de inactividad.

3. Entorno Operativo y Seguridad Física (Municipalidad)

• Usuarios de Windows individuales: La computadora municipal debe tener cuentas de usuario protegidas por contraseña para cada empleado. Se debe evitar categóricamente el uso de una única "cuenta genérica" compartida.
• Bloqueo automático de pantalla: Configurar el sistema operativo de la computadora para bloquear la pantalla tras un máximo de 3 minutos de inactividad, evitando miradas indiscretas si el operador se levanta de su puesto.
• Ubicación física del equipo: La computadora donde resida la base de datos debe estar en un área de acceso restringido al público general (detrás de un mostrador o en una oficina interna).

4. Gestión de Backups y Exportaciones (Políticas)

• Cifrado de copias de seguridad: Dado que el sistema funciona sin internet, los respaldos manuales (en discos externos o pendrives) deben realizarse utilizando herramientas que cifren el contenedor del backup con una contraseña robusta.
• Custodia física de los respaldos: Los dispositivos físicos utilizados para los backups semanales o mensuales deben ser almacenados bajo llave en la oficina del responsable del área.
• Trazabilidad de exportaciones: Si el sistema permite exportar datos a formatos como Excel o CSV para trabajar las planillas, estas acciones deben quedar registradas en un historial (log) interno para saber qué usuario descargó la información.

5. Cumplimiento Legal (Marco Normativo)

• Alineación con la Ley de Protección de Datos Personales: El tratamiento manual y digital de campos sensibles (DNI, localidad, dirección, fecha de nacimiento) se estructurará bajo los principios de confidencialidad y seguridad que exigen las normativas de protección de datos vigentes para organismos públicos.



6. acerca de
7. exportar info bd, casillas selección
8. mail al inscripto y a los confimados