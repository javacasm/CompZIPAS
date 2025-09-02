import pytest
import os
import zipfile
import logging
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime
import tempfile
import shutil
import tkinter as tk
from tkinter import ttk
from zip_comparer_v0_4_5 import load_recent_zips, save_recent_zips, select_zip, compare, create_test_zips_if_not_exist, node_map, RECENT_ZIPS_1, RECENT_ZIPS_2, MAX_RECENT

# Configuración de logging para los tests
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture
def temp_dir():
    """Crea un directorio temporal para los tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def tk_env():
    """Configura un entorno tk con dos Treeview."""
    root = tk.Tk()
    tree1 = ttk.Treeview(root)
    tree2 = ttk.Treeview(root)
    for tree in (tree1, tree2):
        tree.tag_configure('only_zip1', background='lightblue')
        tree.tag_configure('only_zip2', background='lightgreen')
        tree.tag_configure('content_diff', background='yellow')
        tree.tag_configure('date_diff', background='orange')
        tree.tag_configure('same', background='white')
        tree.tag_configure('placeholder', background='gray95', foreground='gray50')
        tree.tag_configure('dir_diff', background='lightcoral')
    yield root, tree1, tree2
    root.destroy()

@pytest.fixture
def clean_globals():
    """Limpia las variables globales antes y después de cada test."""
    global RECENT_ZIPS_1, RECENT_ZIPS_2, node_map
    RECENT_ZIPS_1.clear()
    RECENT_ZIPS_2.clear()
    node_map.clear()
    yield
    RECENT_ZIPS_1.clear()
    RECENT_ZIPS_2.clear()
    node_map.clear()

@pytest.fixture
def create_zip(temp_dir):
    """Función para crear un archivo ZIP de prueba."""
    def _create_zip(filename, files):
        with zipfile.ZipFile(os.path.join(temp_dir, filename), 'w', zipfile.ZIP_DEFLATED) as z:
            for path, content in files.items():
                z.writestr(path, content)
        return os.path.join(temp_dir, filename)
    return _create_zip

def test_load_recent_zips(temp_dir, clean_globals):
    """Prueba la carga de archivos ZIP recientes."""
    recent_zips_file = os.path.join(temp_dir, 'recent_zips.txt')
    with open(recent_zips_file, 'w') as f:
        f.write(f"ZIP1:{os.path.join(temp_dir, 'test1.zip')}\n")
        f.write(f"ZIP2:{os.path.join(temp_dir, 'test2.zip')}\n")
    with patch('os.path.exists', return_value=True):
        load_recent_zips()
    assert RECENT_ZIPS_1 == [os.path.join(temp_dir, 'test1.zip')], "Error al cargar ZIP1 recientes"
    assert RECENT_ZIPS_2 == [os.path.join(temp_dir, 'test2.zip')], "Error al cargar ZIP2 recientes"

def test_load_recent_zips_empty(clean_globals):
    """Prueba la carga cuando recent_zips.txt no existe."""
    with patch('os.path.exists', return_value=False):
        load_recent_zips()
    assert RECENT_ZIPS_1 == [], "RECENT_ZIPS_1 debería estar vacío"
    assert RECENT_ZIPS_2 == [], "RECENT_ZIPS_2 debería estar vacío"

def test_save_recent_zips(temp_dir, clean_globals):
    """Prueba el guardado de archivos ZIP recientes."""
    RECENT_ZIPS_1.append(os.path.join(temp_dir, 'test1.zip'))
    RECENT_ZIPS_2.append(os.path.join(temp_dir, 'test2.zip'))
    save_recent_zips()
    with open('recent_zips.txt', 'r') as f:
        lines = f.readlines()
    assert lines == [f"ZIP1:{os.path.join(temp_dir, 'test1.zip')}\n", f"ZIP2:{os.path.join(temp_dir, 'test2.zip')}\n"], "Error al guardar ZIPs recientes"
    os.remove('recent_zips.txt')

def test_select_zip_no_duplicates(temp_dir, clean_globals):
    """Prueba que select_zip no crea duplicados."""
    path_var = tk.StringVar()
    combo = MagicMock()
    RECENT_ZIPS_1.append(os.path.join(temp_dir, 'test1.zip'))
    with patch('tkinter.filedialog.askopenfilename', return_value=os.path.join(temp_dir, 'test1.zip')):
        with patch('os.path.abspath', return_value=os.path.join(temp_dir, 'test1.zip')):
            select_zip(path_var, combo, RECENT_ZIPS_1)
    assert RECENT_ZIPS_1 == [os.path.join(temp_dir, 'test1.zip')], "No debería haber duplicados en RECENT_ZIPS_1"
    assert len(RECENT_ZIPS_1) == 1, "La longitud debería ser 1"
    combo.configure.assert_called_with(values=[os.path.join(temp_dir, 'test1.zip')])

def test_select_zip_max_recent(temp_dir, clean_globals):
    """Prueba que select_zip respeta el límite de MAX_RECENT."""
    path_var = tk.StringVar()
    combo = MagicMock()
    for i in range(MAX_RECENT):
        RECENT_ZIPS_1.append(f"path_{i}.zip")
    with patch('tkinter.filedialog.askopenfilename', return_value=os.path.join(temp_dir, 'test1.zip')):
        with patch('os.path.abspath', return_value=os.path.join(temp_dir, 'test1.zip')):
            select_zip(path_var, combo, RECENT_ZIPS_1)
    assert len(RECENT_ZIPS_1) == MAX_RECENT, f"Debería haber {MAX_RECENT} elementos"
    assert RECENT_ZIPS_1[0] == os.path.join(temp_dir, 'test1.zip'), "El nuevo ZIP debería estar al inicio"

def test_compare_identical_zips(tk_env, create_zip, clean_globals):
    """Prueba la comparación de dos ZIPs idénticos."""
    root, tree1, tree2 = tk_env
    zip1 = create_zip('test1.zip', {'file.txt': 'Contenido idéntico'})
    zip2 = create_zip('test2.zip', {'file.txt': 'Contenido idéntico'})
    compare(zip1, zip2, tree1, tree2)
    items1 = tree1.get_children()
    items2 = tree2.get_children()
    assert len(items1) == 1, "Debería haber un item en tree1"
    assert len(items2) == 1, "Debería haber un item en tree2"
    assert tree1.item(items1[0])['tags'] == ('same',), "El archivo debería estar etiquetado como 'same'"
    assert tree2.item(items2[0])['tags'] == ('same',), "El archivo debería estar etiquetado como 'same'"
    assert 'file.txt' in node_map, "node_map debería contener file.txt"

def test_compare_different_zips(tk_env, create_zip, clean_globals):
    """Prueba la comparación de ZIPs con diferencias."""
    root, tree1, tree2 = tk_env
    zip1 = create_zip('test1.zip', {'file.txt': 'Contenido ZIP1', 'only_zip1.txt': 'Solo en ZIP1'})
    zip2 = create_zip('test2.zip', {'file.txt': 'Contenido ZIP2', 'only_zip2.txt': 'Solo en ZIP2'})
    compare(zip1, zip2, tree1, tree2)
    items1 = tree1.get_children()
    items2 = tree2.get_children()
    assert len(items1) == 2, "Debería haber 2 items en tree1"
    assert len(items2) == 2, "Debería haber 2 items en tree2"
    for item1, item2 in zip(items1, items2):
        text = tree1.item(item1)['text']
        if text == 'file.txt':
            assert tree1.item(item1)['tags'] == ('content_diff',), "file.txt debería ser 'content_diff' en tree1"
            assert tree2.item(item2)['tags'] == ('content_diff',), "file.txt debería ser 'content_diff' en tree2"
        elif text == 'only_zip1.txt':
            assert tree1.item(item1)['tags'] == ('only_zip1',), "only_zip1.txt debería ser 'only_zip1' en tree1"
            assert tree2.item(item2)['tags'] == ('placeholder',), "only_zip1.txt debería ser 'placeholder' en tree2"
        elif text == 'only_zip2.txt':
            assert tree1.item(item1)['tags'] == ('placeholder',), "only_zip2.txt debería ser 'placeholder' en tree1"
            assert tree2.item(item2)['tags'] == ('only_zip2',), "only_zip2.txt debería ser 'only_zip2' en tree2"

def test_compare_directory_differences(tk_env, create_zip, clean_globals):
    """Prueba la comparación con directorios que tienen diferencias."""
    root, tree1, tree2 = tk_env
    zip1 = create_zip('test1.zip', {'dir/file1.txt': 'Contenido', 'dir/file2.txt': 'Diferente'})
    zip2 = create_zip('test2.zip', {'dir/file1.txt': 'Contenido', 'dir/file3.txt': 'Solo en ZIP2'})
    compare(zip1, zip2, tree1, tree2)
    dir_item1 = tree1.get_children()[0]
    dir_item2 = tree2.get_children()[0]
    assert tree1.item(dir_item1)['tags'] == ('dir_diff',), "El directorio debería ser 'dir_diff' en tree1"
    assert tree2.item(dir_item2)['tags'] == ('dir_diff',), "El directorio debería ser 'dir_diff' en tree2"

def test_create_test_zips(clean_globals):
    """Prueba la creación de ZIPs de prueba."""
    create_test_zips_if_not_exist()
    assert os.path.exists('test1.zip'), "test1.zip debería existir"
    assert os.path.exists('test2.zip'), "test2.zip debería existir"
    with zipfile.ZipFile('test1.zip', 'r') as z1, zipfile.ZipFile('test2.zip', 'r') as z2:
        assert len(z1.namelist()) == 7, "test1.zip debería tener 7 archivos"
        assert len(z2.namelist()) == 7, "test2.zip debería tener 7 archivos"
    os.remove('test1.zip')
    os.remove('test2.zip')

def test_compare_empty_selection(tk_env, clean_globals):
    """Prueba la comparación con selección vacía."""
    root, tree1, tree2 = tk_env
    with patch('tkinter.messagebox.showerror') as mock_showerror:
        compare('', '', tree1, tree2)
        mock_showerror.assert_called_with("Error", "Por favor, seleccione ambos archivos ZIP.")
    assert len(tree1.get_children()) == 0, "tree1 debería estar vacío"
    assert len(tree2.get_children()) == 0, "tree2 debería estar vacío"

def test_logging_info_messages(tk_env, create_zip, clean_globals, caplog):
    """Prueba que los mensajes INFO se emitan correctamente."""
    caplog.set_level(logging.INFO)
    root, tree1, tree2 = tk_env
    zip1 = create_zip('test1.zip', {'file.txt': 'Contenido'})
    zip2 = create_zip('test2.zip', {'file.txt': 'Contenido'})
    compare(zip1, zip2, tree1, tree2)
    expected = [
        f"Iniciando comparación de {zip1} y {zip2}",
        "Encontrados 1 archivos en ZIP1, 1 en ZIP2",
        "Total de miembros únicos: 1"
    ]
    for msg in expected:
        assert msg in caplog.text, f"Mensaje INFO no encontrado: {msg}"