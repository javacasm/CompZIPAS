# Comparador de ZIP - Versión 0.4.1
#
# Descripción:
# Este programa ofrece una interfaz gráfica para comparar dos archivos ZIP, mostrando sus contenidos
# en dos widgets Treeview sincronizados lado a lado. Resalta diferencias en archivos y directorios
# usando colores, con marcadores para archivos faltantes para mantener los árboles alineados. Características:
# - Desplazamiento y selección sincronizados entre árboles (activable/desactivable).
# - Directorios expandibles con sincronización de expansión/contracción.
# - Niveles de logging configurables (DEBUG, INFO, WARNING, ERROR, CRITICAL).
# - Carga automática de archivos ZIP de prueba en modo DEBUG.
# - Creación condicional de archivos ZIP de prueba si no existen.
# - Diferencias codificadas por colores: azul claro para solo ZIP1, verde claro para solo ZIP2, amarillo para diferencias de contenido,
#   naranja para diferencias de fecha, blanco para idénticos, gris claro (texto y fondo) para marcadores, coral claro para directorios con diferencias.
# - Una leyenda con fondos coloreados explica los colores.
# - Selectores de archivos en una línea, encima de los Treeview, usando Combobox con historial de archivos recientes.
#
# Dependencias:
# - Python 3.x
# - tkinter (incluido con la instalación estándar de Python)
# - zipfile, os, logging, datetime, sys (módulos estándar de Python)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import zipfile
import os
import logging
from datetime import datetime
import sys

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Controlador para el nivel de logging en consola
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Variable DEBUG para pruebas
DEBUG = True

# Variable para activar/desactivar sincronización
ENABLE_SYNC = True

# Último tiempo de evento procesado para evitar bucles
LAST_EVENT_TIME = 0

# Listas para almacenar archivos recientes
RECENT_ZIPS_1 = []
RECENT_ZIPS_2 = []
MAX_RECENT = 5

# Mapa para sincronizar nodos entre árboles
node_map = {}  # Ruta completa -> (id_tree1, id_tree2)

def load_recent_zips():
    """Carga los archivos ZIP recientes desde un archivo."""
    global RECENT_ZIPS_1, RECENT_ZIPS_2
    try:
        if os.path.exists('recent_zips.txt'):
            with open('recent_zips.txt', 'r') as f:
                lines = f.readlines()
                RECENT_ZIPS_1 = [line.strip() for line in lines if line.strip().startswith('ZIP1:')]
                RECENT_ZIPS_2 = [line.strip() for line in lines if line.strip().startswith('ZIP2:')]
                RECENT_ZIPS_1 = [path.replace('ZIP1:', '') for path in RECENT_ZIPS_1[:MAX_RECENT]]
                RECENT_ZIPS_2 = [path.replace('ZIP2:', '') for path in RECENT_ZIPS_2[:MAX_RECENT]]
            logger.debug(f"Cargados {len(RECENT_ZIPS_1)} ZIPs recientes para ZIP1, {len(RECENT_ZIPS_2)} para ZIP2")
    except Exception as e:
        logger.error(f"Error al cargar ZIPs recientes: {str(e)}")

def save_recent_zips():
    """Guarda los archivos ZIP recientes en un archivo."""
    try:
        with open('recent_zips.txt', 'w') as f:
            for path in RECENT_ZIPS_1:
                f.write(f"ZIP1:{path}\n")
            for path in RECENT_ZIPS_2:
                f.write(f"ZIP2:{path}\n")
        logger.debug("ZIPs recientes guardados en recent_zips.txt")
    except Exception as e:
        logger.error(f"Error al guardar ZIPs recientes: {str(e)}")

def set_log_level(level):
    """Configura el nivel de logging para la consola."""
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    console_handler.setLevel(levels.get(level, logging.INFO))
    logger.info(f"Nivel de logging configurado a {level}")

def main():
    root = tk.Tk()
    root.title("Comparador de ZIP con Árboles Sincronizados - v0.4.1")
    root.geometry("1000x600")

    # Variables para los paths de los ZIPs
    zip1_path = tk.StringVar()
    zip2_path = tk.StringVar()

    # Cargar archivos recientes
    load_recent_zips()

    # Frame superior para selección de archivos
    frame = tk.Frame(root)
    frame.pack(pady=5, fill='x')

    # Frame para controles de ZIP 1
    zip1_frame = tk.Frame(frame)
    zip1_frame.pack(side='left', padx=10, fill='x', expand=True)
    tk.Label(zip1_frame, text="Archivo ZIP 1:").pack(side='left', padx=5)
    zip1_combo = ttk.Combobox(zip1_frame, textvariable=zip1_path, width=30, values=RECENT_ZIPS_1)
    zip1_combo.pack(side='left', padx=5)
    tk.Button(zip1_frame, text="Seleccionar", command=lambda: select_zip(zip1_path, zip1_combo, RECENT_ZIPS_1)).pack(side='left', padx=5)

    # Frame para controles de ZIP 2
    zip2_frame = tk.Frame(frame)
    zip2_frame.pack(side='left', padx=10, fill='x', expand=True)
    tk.Label(zip2_frame, text="Archivo ZIP 2:").pack(side='left', padx=5)
    zip2_combo = ttk.Combobox(zip2_frame, textvariable=zip2_path, width=30, values=RECENT_ZIPS_2)
    zip2_combo.pack(side='left', padx=5)
    tk.Button(zip2_frame, text="Seleccionar", command=lambda: select_zip(zip2_path, zip2_combo, RECENT_ZIPS_2)).pack(side='left', padx=5)

    # Frame para controles adicionales
    control_frame = tk.Frame(root)
    control_frame.pack(pady=5)
    tk.Label(control_frame, text="Nivel de Logging:").pack(side='left', padx=5)
    log_level = tk.StringVar(value='INFO')
    tk.OptionMenu(control_frame, log_level, 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 
                  command=lambda lvl: set_log_level(lvl)).pack(side='left', padx=5)
    tk.Button(control_frame, text="Comparar", command=lambda: compare(zip1_path.get(), zip2_path.get(), tree1, tree2)).pack(side='left', padx=10)
    enable_sync_var = tk.BooleanVar(value=ENABLE_SYNC)
    tk.Checkbutton(control_frame, text="Habilitar Sincronización", variable=enable_sync_var, 
                   command=lambda: toggle_sync(enable_sync_var)).pack(side='left', padx=10)

    # Leyenda de colores
    legend_frame = tk.Frame(root)
    legend_frame.pack(pady=5, fill='x')
    tk.Label(legend_frame, text="Leyenda: ", font=('Arial', 10, 'bold')).pack(side='left')
    tk.Label(legend_frame, text="Solo ZIP1", background='lightblue', font=('Arial', 10)).pack(side='left', padx=2)
    tk.Label(legend_frame, text="|", font=('Arial', 10)).pack(side='left')
    tk.Label(legend_frame, text="Solo ZIP2", background='lightgreen', font=('Arial', 10)).pack(side='left', padx=2)
    tk.Label(legend_frame, text="|", font=('Arial', 10)).pack(side='left')
    tk.Label(legend_frame, text="Contenido Diferente", background='yellow', font=('Arial', 10)).pack(side='left', padx=2)
    tk.Label(legend_frame, text="|", font=('Arial', 10)).pack(side='left')
    tk.Label(legend_frame, text="Fecha Diferente", background='orange', font=('Arial', 10)).pack(side='left', padx=2)
    tk.Label(legend_frame, text="|", font=('Arial', 10)).pack(side='left')
    tk.Label(legend_frame, text="Idéntico", background='white', font=('Arial', 10)).pack(side='left', padx=2)
    tk.Label(legend_frame, text="|", font=('Arial', 10)).pack(side='left')
    tk.Label(legend_frame, text="Marcador", background='gray95', foreground='gray50', font=('Arial', 10)).pack(side='left', padx=2)
    tk.Label(legend_frame, text="|", font=('Arial', 10)).pack(side='left')
    tk.Label(legend_frame, text="Directorio con Diferencias", background='lightcoral', font=('Arial', 10)).pack(side='left', padx=2)

    # Frame para los árboles
    tree_frame = tk.Frame(root)
    tree_frame.pack(fill='both', expand=True)

    # Árbol para ZIP 1
    tree1 = ttk.Treeview(tree_frame, columns=('size', 'date'), show='tree headings')
    tree1.heading('#0', text='Archivos ZIP 1')
    tree1.heading('size', text='Tamaño')
    tree1.heading('date', text='Fecha')
    tree1.pack(side='left', fill='both', expand=True)

    # Árbol para ZIP 2
    tree2 = ttk.Treeview(tree_frame, columns=('size', 'date'), show='tree headings')
    tree2.heading('#0', text='Archivos ZIP 2')
    tree2.heading('size', text='Tamaño')
    tree2.heading('date', text='Fecha')
    tree2.pack(side='left', fill='both', expand=True)

    # Scrollbars sincronizados
    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=lambda *args: sync_scroll(tree1, tree2, *args))
    scroll.pack(side='right', fill='y')
    tree1.configure(yscrollcommand=scroll.set)
    tree2.configure(yscrollcommand=scroll.set)

    def toggle_sync(var):
        """Activa o desactiva la sincronización."""
        global ENABLE_SYNC
        ENABLE_SYNC = var.get()
        logger.info(f"Sincronización {'habilitada' if ENABLE_SYNC else 'deshabilitada'}")

    def sync_selection(event):
        """Sincroniza la selección entre árboles, si está habilitada."""
        if not ENABLE_SYNC:
            logger.debug("Sincronización de selección deshabilitada")
            return
        global LAST_EVENT_TIME
        if event.time == LAST_EVENT_TIME:
            logger.debug(f"Omitiendo sync_selection: Tiempo de evento duplicado {event.time}")
            return
        LAST_EVENT_TIME = event.time
        logger.debug(f"Procesando evento sync_selection: {event.time}")

        source_tree = event.widget
        target_tree = tree2 if source_tree == tree1 else tree1
        logger.debug(f"Iniciando sync_selection desde {source_tree} a {target_tree}")

        selected = source_tree.selection()
        if selected:
            selected_path = get_full_path(source_tree, selected[0])
            if selected_path in node_map:
                target_id = node_map[selected_path][1] if source_tree == tree1 else node_map[selected_path][0]
                target_selected = target_tree.selection()
                if target_id not in target_selected:
                    logger.debug(f"Actualizando selección a {target_id} en {target_tree}")
                    target_tree.selection_set(target_id)
                    target_tree.see(target_id)
                    logger.debug(f"Selección sincronizada a item: {target_id}")
                else:
                    logger.debug("No se necesita cambio en la selección")
            else:
                logger.debug(f"Ruta no encontrada en node_map: {selected_path}")
        else:
            logger.debug("Sin selección para sincronizar")
        logger.debug("Completado sync_selection")

    def sync_open(event):
        """Sincroniza la expansión/contracción de nodos entre árboles, si está habilitada."""
        if not ENABLE_SYNC:
            logger.debug("Sincronización de expansión deshabilitada")
            return
        global LAST_EVENT_TIME
        if event.time == LAST_EVENT_TIME:
            logger.debug(f"Omitiendo sync_open: Tiempo de evento duplicado {event.time}")
            return
        LAST_EVENT_TIME = event.time
        logger.debug(f"Procesando evento sync_open: {event.time}")

        source_tree = event.widget
        target_tree = tree2 if source_tree == tree1 else tree1
        logger.debug(f"Iniciando sync_open desde {source_tree} a {target_tree}")
        item = source_tree.focus()
        if item:
            item_path = get_full_path(source_tree, item)
            if item_path in node_map:
                target_id = node_map[item_path][1] if source_tree == tree1 else node_map[item_path][0]
                if source_tree.item(item, 'open'):
                    target_tree.item(target_id, open=True)
                    logger.debug(f"Abierto item: {target_id} en {target_tree}")
                else:
                    target_tree.item(target_id, open=False)
                    logger.debug(f"Cerrado item: {target_id} en {target_tree}")
            else:
                logger.debug(f"Ruta no encontrada en node_map: {item_path}")
        logger.debug("Completado sync_open")

    def get_full_path(tree, item):
        """Obtiene la ruta completa de un item en el árbol."""
        path = []
        current = item
        while current:
            path.append(tree.item(current)['text'])
            current = tree.parent(current)
        return '/'.join(reversed(path))

    # Vincular eventos de selección y expansión
    tree1.bind('<<TreeviewSelect>>', sync_selection)
    tree2.bind('<<TreeviewSelect>>', sync_selection)
    tree1.bind('<<TreeviewOpen>>', sync_open)
    tree2.bind('<<TreeviewOpen>>', sync_open)
    tree1.bind('<<TreeviewClose>>', sync_open)
    tree2.bind('<<TreeviewClose>>', sync_open)

    # Configurar colores para diferencias
    for tree in (tree1, tree2):
        tree.tag_configure('only_zip1', background='lightblue')
        tree.tag_configure('only_zip2', background='lightgreen')
        tree.tag_configure('content_diff', background='yellow')
        tree.tag_configure('date_diff', background='orange')
        tree.tag_configure('same', background='white')
        tree.tag_configure('placeholder', background='gray95', foreground='gray50')
        tree.tag_configure('dir_diff', background='lightcoral')

    # Crear archivos ZIP de prueba si no existen
    create_test_zips_if_not_exist()

    # Establecer los ZIPs de prueba como predeterminados si DEBUG es True
    if DEBUG and os.path.exists('test1.zip') and os.path.exists('test2.zip'):
        zip1_path.set(os.path.abspath('test1.zip'))
        zip2_path.set(os.path.abspath('test2.zip'))
        if 'test1.zip' not in RECENT_ZIPS_1:
            RECENT_ZIPS_1.insert(0, os.path.abspath('test1.zip'))
            if len(RECENT_ZIPS_1) > MAX_RECENT:
                RECENT_ZIPS_1.pop()
            zip1_combo['values'] = RECENT_ZIPS_1
        if 'test2.zip' not in RECENT_ZIPS_2:
            RECENT_ZIPS_2.insert(0, os.path.abspath('test2.zip'))
            if len(RECENT_ZIPS_2) > MAX_RECENT:
                RECENT_ZIPS_2.pop()
            zip2_combo['values'] = RECENT_ZIPS_2
        save_recent_zips()
        logger.info("Modo DEBUG: Cargados automáticamente test1.zip y test2.zip")

    root.mainloop()

def select_zip(path_var, combo, recent_list):
    """Selecciona un archivo ZIP y actualiza la lista de recientes."""
    path = filedialog.askopenfilename(filetypes=[('Archivos ZIP', '*.zip')])
    if path:
        path = os.path.abspath(path)
        path_var.set(path)
        if path not in recent_list:
            recent_list.insert(0, path)
            if len(recent_list) > MAX_RECENT:
                recent_list.pop()
            combo['values'] = recent_list
            save_recent_zips()
        logger.info(f"Archivo ZIP seleccionado: {path}")

def sync_scroll(tree1, tree2, *args):
    """Sincroniza el desplazamiento de ambos árboles."""
    tree1.yview(*args)
    tree2.yview(*args)
    return 'break'

def compare(zip1_file, zip2_file, tree1, tree2):
    """Compara dos archivos ZIP y muestra diferencias en los árboles."""
    if not zip1_file or not zip2_file:
        messagebox.showerror("Error", "Por favor, seleccione ambos archivos ZIP.")
        logger.error("Falta selección de archivo ZIP")
        return

    logger.info(f"Iniciando comparación de {zip1_file} y {zip2_file}")

    try:
        with zipfile.ZipFile(zip1_file) as z1, zipfile.ZipFile(zip2_file) as z2:
            namelist1 = z1.namelist()
            namelist2 = z2.namelist()
            all_members = sorted(set(namelist1) | set(namelist2))
            info1 = {name: z1.getinfo(name) for name in namelist1}
            info2 = {name: z2.getinfo(name) for name in namelist2}

            logger.debug(f"Encontrados {len(namelist1)} archivos en ZIP1, {len(namelist2)} en ZIP2")
            logger.debug(f"Total de miembros únicos: {len(all_members)}")

            # Limpiar árboles y mapa de nodos
            tree1.delete(*tree1.get_children())
            tree2.delete(*tree2.get_children())
            global node_map
            node_map.clear()

            # Estructura para almacenar nodos
            parent_map1 = {'': ''}
            parent_map2 = {'': ''}
            dir_tags = {}  # Mapa para rastrear etiquetas de directorios

            for full_path in all_members:
                is_dir = full_path.endswith('/')
                parts = full_path.rstrip('/').split('/')
                parent1 = parent2 = ''
                current_path = ''

                for i, part in enumerate(parts):
                    if i < len(parts) - 1 or is_dir:
                        current_path = '/'.join(parts[:i+1]) + '/'
                    else:
                        current_path = '/'.join(parts[:i+1])

                    # Árbol 1
                    children1 = tree1.get_children(parent1)
                    found1 = None
                    for c in children1:
                        if tree1.item(c)['text'] == part:
                            found1 = c
                            break

                    # Árbol 2
                    children2 = tree2.get_children(parent2)
                    found2 = None
                    for c in children2:
                        if tree2.item(c)['text'] == part:
                            found2 = c
                            break

                    inf1 = info1.get(full_path)
                    inf2 = info2.get(full_path)

                    if i < len(parts) - 1 or is_dir:
                        # Directorio
                        if not found1:
                            found1 = tree1.insert(parent1, 'end', text=part, values=('', ''), open=False)
                            parent_map1[current_path] = found1
                        if not found2:
                            found2 = tree2.insert(parent2, 'end', text=part, values=('', ''), open=False)
                            parent_map2[current_path] = found2
                    else:
                        # Archivo
                        size1 = f"{inf1.file_size} bytes" if inf1 else ''
                        date1 = datetime(*inf1.date_time).strftime('%Y-%m-%d %H:%M:%S') if inf1 else ''
                        size2 = f"{inf2.file_size} bytes" if inf2 else ''
                        date2 = datetime(*inf2.date_time).strftime('%Y-%m-%d %H:%M:%S') if inf2 else ''

                        tag = 'same'
                        if not inf1:
                            tag = 'only_zip2'
                            found1 = tree1.insert(parent1, 'end', text=part, values=(size1, date1), tags=('placeholder',))
                            found2 = tree2.insert(parent2, 'end', text=part, values=(size2, date2), tags=(tag,))
                        elif not inf2:
                            tag = 'only_zip1'
                            found1 = tree1.insert(parent1, 'end', text=part, values=(size1, date1), tags=(tag,))
                            found2 = tree2.insert(parent2, 'end', text=part, values=(size2, date2), tags=('placeholder',))
                        else:
                            if inf1.file_size != inf2.file_size or inf1.CRC != inf2.CRC:
                                tag = 'content_diff'
                            elif inf1.date_time != inf2.date_time:
                                tag = 'date_diff'
                            found1 = tree1.insert(parent1, 'end', text=part, values=(size1, date1), tags=(tag,))
                            found2 = tree2.insert(parent2, 'end', text=part, values=(size2, date2), tags=(tag,))

                        # Actualizar etiquetas de directorios padre
                        for j in range(i, -1, -1):
                            dir_path = '/'.join(parts[:j]) + '/' if j > 0 else ''
                            if dir_path in parent_map1:
                                dir_tags.setdefault(dir_path, set()).add(tag)
                        logger.debug(f"Archivo procesado: {full_path}, Etiqueta: {tag}")

                    parent1 = parent_map1.get(current_path, found1)
                    parent2 = parent_map2.get(current_path, found2)

                    # Mapear nodos para sincronización
                    node_map[current_path] = (found1, found2)

            # Aplicar etiquetas a directorios según contenido
            for dir_path, tags in dir_tags.items():
                tag = 'same'
                if 'only_zip1' in tags or 'only_zip2' in tags or 'content_diff' in tags or 'date_diff' in tags:
                    tag = 'dir_diff'
                if dir_path in parent_map1:
                    tree1.item(parent_map1[dir_path], tags=(tag,))
                    tree2.item(parent_map2[dir_path], tags=(tag,))
                logger.debug(f"Directorio {dir_path} etiquetado como {tag}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        logger.error(f"Error durante la comparación: {str(e)}")

def create_test_zips_if_not_exist():
    """Crea archivos ZIP de prueba solo si no existen."""
    if os.path.exists('test1.zip') and os.path.exists('test2.zip'):
        logger.info("Los archivos ZIP de prueba ya existen: test1.zip, test2.zip. Omitiendo creación.")
        return

    logger.info("Creando archivos ZIP de prueba")
    try:
        # ZIP 1
        if not os.path.exists('test1.zip'):
            with zipfile.ZipFile('test1.zip', 'w', zipfile.ZIP_DEFLATED) as z1:
                z1.writestr('project/docs/readme.txt', 'README para ZIP1')
                z1.writestr('project/docs/install.txt', 'Guía de instalación v1')
                z1.writestr('project/src/main.py', 'print("Hola desde ZIP1")')
                z1.writestr('project/src/utils/helper.py', 'def helper(): pass')
                z1.writestr('project/tests/test_main.py', 'assert True')
                z1.writestr('data/images/icon.png', b'\x89PNG\r\nfakeimage')
                z1.writestr('data/config.json', '{"version": "1.0"}')
                logger.debug("Creado test1.zip con 7 archivos")

        # ZIP 2
        if not os.path.exists('test2.zip'):
            with zipfile.ZipFile('test2.zip', 'w', zipfile.ZIP_DEFLATED) as z2:
                z2.writestr('project/docs/readme.txt', 'README para ZIP2 (actualizado)')
                z2.writestr('project/docs/install.txt', 'Guía de instalación v1')  # Mismo contenido
                z2.writestr('project/src/main.py', 'print("Hola desde ZIP2")')  # Contenido diferente
                z2.writestr('project/src/utils/extra.py', 'def extra(): pass')  # Nuevo archivo
                z2.writestr('project/tests/test_extra.py', 'assert False')  # Nuevo archivo
                z2.writestr('data/images/icon.png', b'\x89PNG\r\nfakeimage')  # Mismo contenido
                z2.writestr('data/config.json', '{"version": "1.1"}')  # Contenido diferente
                logger.debug("Creado test2.zip con 7 archivos")
        
        logger.info("Archivos ZIP de prueba creados exitosamente: test1.zip, test2.zip")
    except Exception as e:
        logger.error(f"Error al crear ZIPs de prueba: {str(e)}")

if __name__ == "__main__":
    main()