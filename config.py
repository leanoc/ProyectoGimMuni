# config.py
"""
Configuración Global y Parámetros del Sistema
Gimnasio Municipal - Versión 3.0.0
"""

# Metadatos del Sistema e Institución
APP_TITLE = "Sistema de Inscripción y Sorteo - Gimnasio Municipal"
APP_VERSION = "3.0.0"
APP_DEVELOPER = "L. M. OCARIZ ARRIETA"
INSTITUTION_NAME = "Gimnasio Municipal"

# Reglas de Negocio Generales
MINIMUM_AGE = 16  # Edad mínima por defecto para postulantes

# Criterios de Selección Admitidos
CRITERION_SORTEO = "Sorteo"
CRITERION_ORDEN_LLEGADA = "Orden de llegada"
AVAILABLE_CRITERIA = [CRITERION_SORTEO, CRITERION_ORDEN_LLEGADA]

# Estados de Inscripción (Valores de la base de datos)
STATUS_ESPERA = 0      # Postulante en Lista de Espera
STATUS_ADMITIDO = 1    # Postulante Titular Admitido

# Parámetros de Ventana GUI
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 740
WINDOW_MIN_WIDTH = 1050
WINDOW_MIN_HEIGHT = 680