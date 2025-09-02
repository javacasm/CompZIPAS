# CompZIPAS: Comparador de ZIP con Árboles Sincronizados

**Versión**: 0.4.6  
**Última actualización**: 2 de septiembre de 2025

## Objetivo

El **Comparador de ZIP con Árboles Sincronizados** es una herramienta gráfica desarrollada en Python que permite comparar visualmente el contenido de dos archivos ZIP. Muestra los archivos y directorios de ambos ZIPs en dos widgets `Treeview` sincronizados lado a lado, resaltando diferencias mediante colores. Su objetivo es facilitar la identificación de diferencias en contenido, fechas, archivos exclusivos de cada ZIP y directorios con diferencias, con una interfaz intuitiva y funcional.

## Utilidad

Esta herramienta es útil para:

- **Desarrolladores y testers**: Comparar versiones de proyectos empaquetados en ZIP, identificando cambios en archivos o estructuras.
- **Gestión de backups**: Verificar diferencias entre copias de seguridad comprimidas.
- **Análisis de datos comprimidos**: Inspeccionar el contenido de ZIPs para detectar archivos faltantes, modificados o con fechas diferentes.
- **Automatización de revisiones**: Usar el modo `DEBUG` para pruebas automáticas con ZIPs generados.

Características clave:

- **Sincronización**: Desplazamiento, selección y expansión de directorios sincronizados entre los dos `Treeview` (activable/desactivable).
- **Diferencias visuales**: Colores para indicar archivos exclusivos (azul claro para ZIP1, verde claro para ZIP2), diferencias en contenido (amarillo), diferencias en fechas (naranja), archivos idénticos (blanco), marcadores de archivos faltantes (gris claro) y directorios con diferencias (coral claro).
- **Historial de archivos**: Combobox con hasta 5 archivos ZIP recientes, sin duplicados, guardados en `recent_zips.txt`.
- **Logging configurable**: Niveles de logging ajustables (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) para depuración.
- **Modo de prueba**: Carga automática de ZIPs de prueba (`test1.zip` y `test2.zip`) en modo `DEBUG`, con estructuras complejas para pruebas.

## Requisitos

- **Python**: 3.x
- **Módulos**:
    - `tkinter` (incluido en la instalación estándar de Python).
    - `zipfile`, `os`, `logging`, `datetime`, `sys` (módulos estándar de Python).
- **Sistema operativo**: Compatible con Windows, macOS y Linux (donde `tkinter` esté disponible).
- **Archivos ZIP de prueba** (opcional): Generados automáticamente en modo `DEBUG` si no existen.

## Instalación

1. Clona o descarga el repositorio:
    
    ```bash
    git clone https://github.com/javacasm/CompZIPAS
    cd CompZIPAS
    ```
    
2. Asegúrate de tener Python 3.x instalado:
    
    ```bash
    python --version
    ```
    
3. No se requieren dependencias externas, ya que usa módulos estándar de Python.

## Uso

1. **Ejecutar el programa**:
    
    ```bash
    python zip_comparator.py
    ```
    
2. **Interfaz gráfica**:
    
    - **Selección de archivos ZIP**:
        - Usa los `Combobox` en la parte superior para seleccionar archivos ZIP recientes o haz clic en "Seleccionar" para abrir un explorador de archivos.
        - Los últimos 5 ZIPs seleccionados se guardan en `recent_zips.txt` (sin duplicados).
    - **Nivel de logging**:
        - Selecciona un nivel (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) desde el menú desplegable.
        - Con `INFO`, verás mensajes como el número de archivos en cada ZIP y el total de miembros únicos.
        - Con `ERROR`, solo se muestran errores críticos.
    - **Sincronización**:
        - Activa/desactiva la sincronización de desplazamiento, selección y expansión de directorios con el `Checkbutton` "Habilitar Sincronización".
    - **Comparación**:
        - Haz clic en "Comparar" para analizar los ZIPs seleccionados.
        - Los `Treeview` muestran los contenidos con colores según las diferencias:
            - **Azul claro**: Archivo solo en ZIP1.
            - **Verde claro**: Archivo solo en ZIP2.
            - **Amarillo**: Contenido diferente.
            - **Naranja**: Fechas diferentes.
            - **Blanco**: Archivos idénticos.
            - **Gris claro (texto y fondo)**: Marcador para archivos faltantes.
            - **Coral claro**: Directorios con diferencias.
        - Expande/contrae directorios haciendo clic en el triángulo o el nombre; la acción se sincroniza en el otro árbol si está habilitada.
    - **Leyenda**: Una barra en la interfaz explica los colores usados.
3. **Modo DEBUG**:
    
    - Activa el modo `DEBUG` (definido como `DEBUG = True` en el código) para cargar automáticamente `test1.zip` y `test2.zip`.
    - Si no existen, se crean con estructuras complejas (directorios anidados, archivos con diferencias en contenido y fechas).
    - Para desactivar, cambia a `DEBUG = False`.
4. **Ejemplo de salida de logging** (nivel `INFO`):
    
    ```
    2025-09-02 10:47:00,000 - INFO - Iniciando comparación de test1.zip y test2.zip
    2025-09-02 10:47:00,010 - INFO - Encontrados 7 archivos en ZIP1, 7 en ZIP2
    2025-09-02 10:47:00,015 - INFO - Total de miembros únicos: 9
    2025-09-02 10:47:00,020 - INFO - Modo DEBUG: Cargados automáticamente test1.zip y test2.zip
    ```
    

## Estructura del Proyecto

- `zip_comparator.py`: Script principal con la lógica del comparador.
- `recent_zips.txt`: Archivo generado para almacenar los últimos 5 ZIPs seleccionados por cada `Treeview`.
- `test1.zip`, `test2.zip`: Archivos ZIP de prueba generados en modo `DEBUG` si no existen.

## Posibles Mejoras

1. **Soporte para otros formatos comprimidos**:
    - Añadir compatibilidad con formatos como `.tar.gz`, `.rar` o `.7z` usando bibliotecas como `tarfile` o `py7zr`.
2. **Comparación de contenido detallada**:
    - Mostrar diferencias específicas en archivos de texto (por ejemplo, usando `difflib` para mostrar líneas modificadas).
3. **Exportación de resultados**:
    - Permitir exportar el informe de diferencias a un archivo (por ejemplo, CSV o HTML).
4. **Interfaz mejorada**:
    - Añadir un panel para mostrar el contenido de archivos seleccionados (por ejemplo, texto o imágenes).
    - Implementar búsqueda de archivos dentro de los `Treeview`.
5. **Rendimiento**:
    - Optimizar la comparación para ZIPs grandes con miles de archivos, usando procesamiento en segundo plano.
6. **Soporte multiplataforma avanzado**:
    - Asegurar compatibilidad total con macOS y Linux, incluyendo temas visuales de `tkinter`.
7. **Internacionalización**:
    - Añadir soporte para otros idiomas además del castellano (por ejemplo, inglés).
8. **Pruebas automatizadas**:
    - Implementar pruebas unitarias con `unittest` para validar la comparación y sincronización.
9. **Configuración personalizable**:
    - Permitir al usuario definir colores personalizados para las diferencias.
    - Añadir un archivo de configuración para ajustes como el número máximo de archivos recientes.

## Contribuciones

Si deseas contribuir:

1. Clona el repositorio.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3. Implementa tus cambios y verifica con los ZIPs de prueba.
4. Envía un pull request con una descripción clara de los cambios.

## Licencia

Este proyecto no tiene una licencia explícita definida. Contacta al autor para más información sobre el uso y distribución.

## Contacto

Para reportar errores, sugerir mejoras o solicitar soporte, crea un _issue_ en el repositorio o contacta al equipo de desarrollo.