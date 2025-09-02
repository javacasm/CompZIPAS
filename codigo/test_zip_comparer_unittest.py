import unittest
import os
import zipfile
import logging
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime
import tempfile
import shutil
from zip_comparer_v0_4_5 import load_recent_zips, save_recent_zips, select_zip, compare, create_test_zips_if_not_exist, node_map, RECENT_ZIPS_1, RECENT_ZIPS_2, MAX_RECENT
import tkinter as tk
from tkinter import ttk

# Configuración de logging para los tests
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestZipComparator(unittest.TestCase):
    def setUp(self):
        """Configura el entorno para cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_zip1 = os.path.join(self.temp_dir, 'test1.zip')
        self.test_zip2 = os.path.join(self.temp_dir, 'test2.zip')
        self.recent_zips_file = os.path.join(self.temp_dir, 'recent_zips.txt')
        self.root = tk.Tk()
        self.tree1 = ttk.Treeview(self.root)
        self.tree2 = ttk.Treeview(self.root)
        # Configurar etiquetas de color
        for tree in (self.tree1, self.tree2):
            tree.tag_configure('only_zip1', background='lightblue')
            tree.tag_configure('only_zip2', background='lightgreen')
            tree.tag_configure('content_diff', background='yellow')
            tree.tag_configure('date_diff', background='orange')
            tree.tag_configure('same', background='white')
            tree.tag_configure('placeholder', background='gray95', foreground='gray50')
            tree.tag_configure('dir_diff', background='lightcoral')
        # Limpiar listas globales
        global RECENT_ZIPS_1, RECENT_ZIPS_2, node_map
        RECENT_ZIPS_1.clear()
        RECENT_ZIPS_2.clear()
        node_map.clear()

    def tearDown(self):
        """Limpia el entorno después de cada test."""
        self.root.destroy()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_zip(self, filename, files):
        """Crea un archivo ZIP de prueba."""
        with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as z:
            for path, content in files.items():
                z.writestr(path, content)

    def test_load_recent_zips(self):
        """Prueba la carga de archivos ZIP recientes desde recent_zips.txt."""
        # Crear un archivo recent_zips.txt simulado
        with open(self.recent_zips_file, 'w') as f:
            f.write(f"ZIP1:{self.test_zip1}\n")
            f.write(f"ZIP2:{self.test_zip2}\n")
        # Simular os.path.exists
        with patch('os.path.exists', return_value=True):
            load_recent_zips()
        self.assertEqual(RECENT_ZIPS_1, [self.test_zip1], "Error al cargar ZIP1 recientes")
        self.assertEqual(RECENT_ZIPS_2, [self.test_zip2], "Error al cargar ZIP2 recientes")

    def test_load_recent_zips_empty(self):
        """Prueba la carga cuando recent_zips.txt no existe."""
        with patch('os.path.exists', return_value=False):
            load_recent_zips()
        self.assertEqual(RECENT_ZIPS_1, [], "RECENT_ZIPS_1 debería estar vacío")
        self.assertEqual(RECENT_ZIPS_2, [], "RECENT_ZIPS_2 debería estar vacío")

    def test_save_recent_zips(self):
        """Prueba el guardado de archivos ZIP recientes."""
        RECENT_ZIPS_1.append(self.test_zip1)
        RECENT_ZIPS_2.append(self.test_zip2)
        save_recent_zips()
        with open('recent_zips.txt', 'r') as f:
            lines = f.readlines()
        self.assertEqual(lines, [f"ZIP1:{self.test_zip1}\n", f"ZIP2:{self.test_zip2}\n"], "Error al guardar ZIPs recientes")
        os.remove('recent_zips.txt')

    def test_select_zip_no_duplicates(self):
        """Prueba que select_zip no crea duplicados en la lista de recientes."""
        path_var = tk.StringVar()
        combo = MagicMock()
        RECENT_ZIPS_1.append(self.test_zip1)
        with patch('tkinter.filedialog.askopenfilename', return_value=self.test_zip1):
            with patch('os.path.abspath', return_value=self.test_zip1):
                select_zip(path_var, combo, RECENT_ZIPS_1)
        self.assertEqual(RECENT_ZIPS_1, [self.test_zip1], "No debería haber duplicados en RECENT_ZIPS_1")
        self.assertEqual(len(RECENT_ZIPS_1), 1, "La longitud debería ser 1")
        combo.configure.assert_called_with(values=[self.test_zip1])

    def test_select_zip_max_recent(self):
        """Prueba que select_zip respeta el límite de MAX_RECENT."""
        path_var = tk.StringVar()
        combo = MagicMock()
        for i in range(MAX_RECENT + 1):
            RECENT_ZIPS_1.append(f"path_{i}.zip")
        with patch('tkinter.filedialog.askopenfilename', return_value=self.test_zip1):
            with patch('os.path.abspath', return_value=self.test_zip1):
                select_zip(path_var, combo, RECENT_ZIPS_1)
        self.assertEqual(len(RECENT_ZIPS_1), MAX_RECENT, f"Debería haber {MAX_RECENT} elementos")
        self.assertEqual(RECENT_ZIPS_1[0], self.test_zip1, "El nuevo ZIP debería estar al inicio")

    def test_compare_identical_zips(self):
        """Prueba la comparación de dos ZIPs idénticos."""
        files = {'file.txt': 'Contenido idéntico'}
        self.create_test_zip(self.test_zip1, files)
        self.create_test_zip(self.test_zip2, files)
        compare(self.test_zip1, self.test_zip2, self.tree1, self.tree2)
        items1 = self.tree1.get_children()
        items2 = self.tree2.get_children()
        self.assertEqual(len(items1), 1, "Debería haber un item en tree1")
        self.assertEqual(len(items2), 1, "Debería haber un item en tree2")
        self.assertEqual(self.tree1.item(items1[0])['tags'], ('same',), "El archivo debería estar etiquetado como 'same'")
        self.assertEqual(self.tree2.item(items2[0])['tags'], ('same',), "El archivo debería estar etiquetado como 'same'")
        self.assertIn('file.txt', node_map, "node_map debería contener file.txt")

    def test_compare_different_zips(self):
        """Prueba la comparación de ZIPs con diferencias."""
        zip1_files = {'file.txt': 'Contenido ZIP1', 'only_zip1.txt': 'Solo en ZIP1'}
        zip2_files = {'file.txt': 'Contenido ZIP2', 'only_zip2.txt': 'Solo en ZIP2'}
        self.create_test_zip(self.test_zip1, zip1_files)
        self.create_test_zip(self.test_zip2, zip2_files)
        compare(self.test_zip1, self.test_zip2, self.tree1, self.tree2)
        items1 = self.tree1.get_children()
        items2 = self.tree2.get_children()
        self.assertEqual(len(items1), 2, "Debería haber 2 items en tree1")
        self.assertEqual(len(items2), 2, "Debería haber 2 items en tree2")
        for item1, item2 in zip(items1, items2):
            text = self.tree1.item(item1)['text']
            if text == 'file.txt':
                self.assertEqual(self.tree1.item(item1)['tags'], ('content_diff',), "file.txt debería ser 'content_diff' en tree1")
                self.assertEqual(self.tree2.item(item2)['tags'], ('content_diff',), "file.txt debería ser 'content_diff' en tree2")
            elif text == 'only_zip1.txt':
                self.assertEqual(self.tree1.item(item1)['tags'], ('only_zip1',), "only_zip1.txt debería ser 'only_zip1' en tree1")
                self.assertEqual(self.tree2.item(item2)['tags'], ('placeholder',), "only_zip1.txt debería ser 'placeholder' en tree2")
            elif text == 'only_zip2.txt':
                self.assertEqual(self.tree1.item(item1)['tags'], ('placeholder',), "only_zip2.txt debería ser 'placeholder' en tree1")
                self.assertEqual(self.tree2.item(item2)['tags'], ('only_zip2',), "only_zip2.txt debería ser 'only_zip2' en tree2")

    def test_compare_directory_differences(self):
        """Prueba la comparación con directorios que tienen diferencias."""
        zip1_files = {'dir/file1.txt': 'Contenido', 'dir/file2.txt': 'Diferente'}
        zip2_files = {'dir/file1.txt': 'Contenido', 'dir/file3.txt': 'Solo en ZIP2'}
        self.create_test_zip(self.test_zip1, zip1_files)
        self.create_test_zip(self.test_zip2, zip2_files)
        compare(self.test_zip1, self.test_zip2, self.tree1, self.tree2)
        dir_item1 = self.tree1.get_children()[0]
        dir_item2 = self.tree2.get_children()[0]
        self.assertEqual(self.tree1.item(dir_item1)['tags'], ('dir_diff',), "El directorio debería ser 'dir_diff' en tree1")
        self.assertEqual(self.tree2.item(dir_item2)['tags'], ('dir_diff',), "El directorio debería ser 'dir_diff' en tree2")

    def test_create_test_zips(self):
        """Prueba la creación de ZIPs de prueba."""
        create_test_zips_if_not_exist()
        self.assertTrue(os.path.exists('test1.zip'), "test1.zip debería existir")
        self.assertTrue(os.path.exists('test2.zip'), "test2.zip debería existir")
        with zipfile.ZipFile('test1.zip', 'r') as z1, zipfile.ZipFile('test2.zip', 'r') as z2:
            self.assertEqual(len(z1.namelist()), 7, "test1.zip debería tener 7 archivos")
            self.assertEqual(len(z2.namelist()), 7, "test2.zip debería tener 7 archivos")
        os.remove('test1.zip')
        os.remove('test2.zip')

    def test_compare_empty_selection(self):
        """Prueba la comparación con selección vacía."""
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            compare('', '', self.tree1, self.tree2)
            mock_showerror.assert_called_with("Error", "Por favor, seleccione ambos archivos ZIP.")
        self.assertEqual(len(self.tree1.get_children()), 0, "tree1 debería estar vacío")
        self.assertEqual(len(self.tree2.get_children()), 0, "tree2 debería estar vacío")

    def test_logging_info_messages(self):
        """Prueba que los mensajes INFO se emitan correctamente."""
        zip1_files = {'file.txt': 'Contenido'}
        zip2_files = {'file.txt': 'Contenido'}
        self.create_test_zip(self.test_zip1, zip1_files)
        self.create_test_zip(self.test_zip2, zip2_files)
        log_capture = []
        def capture_log(record):
            log_capture.append(record.getMessage())
        logger.handlers = []  # Limpiar manejadores
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.emit = capture_log
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        compare(self.test_zip1, self.test_zip2, self.tree1, self.tree2)
        expected = [
            f"Iniciando comparación de {self.test_zip1} y {self.test_zip2}",
            "Encontrados 1 archivos en ZIP1, 1 en ZIP2",
            "Total de miembros únicos: 1"
        ]
        for msg in expected:
            self.assertIn(msg, log_capture, f"Mensaje INFO no encontrado: {msg}")

if __name__ == '__main__':
    unittest.main()