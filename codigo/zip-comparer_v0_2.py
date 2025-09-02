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
    root.title("ZIP Comparator with Synced Trees")
    root.geometry("1000x600")

    # Variables para los paths de los ZIPs
    zip1_path = tk.StringVar()
    zip2_path = tk.StringVar()

    # Frame superior para selección de archivos y nivel de log
    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="ZIP 1:").grid(row=0, column=0, padx=5)
    tk.Entry(frame, textvariable=zip1_path, width=50).grid(row=0, column=1, padx=5)
    tk.Button(frame, text="Select", command=lambda: select_zip(zip1_path)).grid(row=0, column=2, padx=5)

    tk.Label(frame, text="ZIP 2:").grid(row=1, column=0, padx=5)
    tk.Entry(frame, textvariable=zip2_path, width=50).grid(row=1, column=1, padx=5)
    tk.Button(frame, text="Select", command=lambda: select_zip(zip2_path)).grid(row=1, column=2, padx=5)

    tk.Label(frame, text="Log Level:").grid(row=2, column=0, padx=5)
    log_level = tk.StringVar(value='INFO')
    tk.OptionMenu(frame, log_level, 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 
                  command=lambda lvl: set_log_level(lvl)).grid(row=2, column=1, sticky='w', padx=5)

    tk.Button(frame, text="Compare", command=lambda: compare(zip1_path.get(), zip2_path.get(), tree1, tree2)).grid(row=2, column=1, pady=10)

    # Frame para los árboles
    tree_frame = tk.Frame(root)
    tree_frame.pack(fill='both', expand=True)

    # Árbol para ZIP 1
    tree1 = ttk.Treeview(tree_frame, columns=('size', 'date'), show='tree headings')
    tree1.heading('#0', text='ZIP 1 Files')
    tree1.heading('size', text='Size')
    tree1.heading('date', text='Date')
    tree1.pack(side='left', fill='both', expand=True)

    # Árbol para ZIP 2
    tree2 = ttk.Treeview(tree_frame, columns=('size', 'date'), show='tree headings')
    tree2.heading('#0', text='ZIP 2 Files')
    tree2.heading('size', text='Size')
    tree2.heading('date', text='Date')
    tree2.pack(side='left', fill='both', expand=True)

    # Scrollbars sincronizados
    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=lambda *args: sync_scroll(tree1, tree2, *args))
    scroll.pack(side='right', fill='y')
    tree1.configure(yscrollcommand=scroll.set)
    tree2.configure(yscrollcommand=scroll.set)

    def sync_selection(event):
        """Sincroniza la selección entre árboles, evitando bucles."""
        global SYNCING
        if SYNCING:
            logger.debug("Skipping sync_selection due to active SYNCING")
            return
        SYNCING = True
        source_tree = event.widget
        target_tree = tree2 if source_tree == tree1 else tree1
        logger.debug(f"Starting sync_selection from {source_tree} to {target_tree}")
        
        # Desvincular evento del árbol objetivo
        target_tree.unbind('<<TreeviewSelect>>')
        selected = source_tree.selection()
        if selected:
            target_tree.selection_set(selected)
            target_tree.see(selected[0])
            logger.debug(f"Synchronized selection to item: {selected[0]}")
        else:
            logger.debug("No selection to synchronize")
        # Volver a vincular evento
        target_tree.bind('<<TreeviewSelect>>', sync_selection)
        logger.debug(f"Rebound <<TreeviewSelect>> to {target_tree}")
        SYNCING = False
        logger.debug("Completed sync_selection")

    def sync_open(event):
        """Sincroniza la expansión/contracción de nodos entre árboles."""
        global SYNCING
        if SYNCING:
            logger.debug("Skipping sync_open due to active SYNCING")
            return
        SYNCING = True
        source_tree = event.widget
        target_tree = tree2 if source_tree == tree1 else tree1
        logger.debug(f"Starting sync_open from {source_tree} to {target_tree}")
        item = source_tree.focus()
        if item:
            if source_tree.item(item, 'open'):
                target_tree.item(item, open=True)
                logger.debug(f"Opened item: {item} in {target_tree}")
            else:
                target_tree.item(item, open=False)
                logger.debug(f"Closed item: {item} in {target_tree}")
        SYNCING = False
        logger.debug("Completed sync_open")

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
        tree.tag_configure('placeholder', background='gray95')

    # Crear archivos ZIP de prueba si no existen
    create_test_zips_if_not_exist()

    # Establecer los ZIPs de prueba como predeterminados si DEBUG es True
    if DEBUG and os.path.exists('test1.zip') and os.path.exists('test2.zip'):
        zip1_path.set(os.path.abspath('test1.zip'))
        zip2_path.set(os.path.abspath('test2.zip'))
        logger.info("DEBUG mode: Automatically loaded test1.zip and test2.zip")

    root.mainloop()

def select_zip(path_var):
    """Selecciona un archivo ZIP."""
    path = filedialog.askopenfilename(filetypes=[('ZIP files', '*.zip')])
    if path:
        path_var.set(os.path.abspath(path))
        logger.info(f"Selected ZIP file: {path}")

def sync_scroll(tree1, tree2, *args):
    """Sincroniza el desplazamiento de ambos árboles."""
    tree1.yview(*arguments)
    tree2.yview(*arguments)
    return 'break'

def compare(zip1_file, zip2_file, tree1, tree2):
    """Compara dos archivos ZIP y muestra diferencias en los árboles."""
    if not zip1_file or not zip2_file:
        messagebox.showerror("Error", "Please select both ZIP files.")
        logger.error("Missing ZIP file selection")
        return

    logger.info(f"Starting comparison of {zip1_file} and {zip2_file}")

    try:
        with zipfile.ZipFile(zip1_file) as z1, zipfile.ZipFile(zip2_file) as z2:
            namelist1 = z1.namelist()
            namelist2 = z2.namelist()
            all_members = sorted(set(namelist1) | set(namelist2))
            info1 = {name: z1.getinfo(name) for name in namelist1}
            info2 = {name: z2.getinfo(name) for name in namelist2}

            logger.debug(f"Found {len(namelist1)} files in ZIP1, {len(namelist2)} files in ZIP2")
            logger.debug(f"Total unique members: {len(all_members)}")

            # Limpiar árboles
            tree1.delete(*tree1.get_children())
            tree2.delete(*tree2.get_children())

            # Estructura para almacenar nodos
            parent_map1 = {'': ''}
            parent_map2 = {'': ''}

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

                        logger.debug(f"Processed file: {full_path}, Tag: {tag}")

                    parent1 = parent_map1.get(current_path, found1)
                    parent2 = parent_map2.get(current_path, found2)

    except Exception as e:
        messagebox.showerror("Error", str(e))
        logger.error(f"Error during comparison: {str(e)}")

def create_test_zips_if_not_exist():
    """Crea archivos ZIP de prueba solo si no existen."""
    if os.path.exists('test1.zip') and os.path.exists('test2.zip'):
        logger.info("Test ZIP files already exist: test1.zip, test2.zip. Skipping creation.")
        return

    logger.info("Creating test ZIP files")
    try:
        # ZIP 1
        if not os.path.exists('test1.zip'):
            with zipfile.ZipFile('test1.zip', 'w', zipfile.ZIP_DEFLATED) as z1:
                z1.writestr('folder1/file1.txt', 'Content of file1 in ZIP1')
                z1.writestr('folder1/file2.txt', 'Content of file2 in ZIP1')
                z1.writestr('folder2/subfolder/file3.txt', 'Content of file3 in ZIP1')
                logger.debug("Created test1.zip with 3 files")

        # ZIP 2
        if not os.path.exists('test2.zip'):
            with zipfile.ZipFile('test2.zip', 'w', zipfile.ZIP_DEFLATED) as z2:
                z2.writestr('folder1/file1.txt', 'Content of file1 in ZIP2 (modified)')
                z2.writestr('folder1/file4.txt', 'Content of file4 in ZIP2')
                z2.writestr('folder2/subfolder/file3.txt', 'Content of file3 in ZIP2')
                logger.debug("Created test2.zip with 3 files")
        
        logger.info("Test ZIP files created successfully: test1.zip, test2.zip")
    except Exception as e:
        logger.error(f"Error creating test ZIPs: {str(e)}")

if __name__ == "__main__":
    main()