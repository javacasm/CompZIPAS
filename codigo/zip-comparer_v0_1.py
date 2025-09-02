import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import zipfile
from datetime import datetime
import os

def main():
    root = tk.Tk()
    root.title("ZIP Comparator")
    root.geometry("800x600")

    zip1_path = tk.StringVar()
    zip2_path = tk.StringVar()

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="ZIP 1:").grid(row=0, column=0, padx=5)
    tk.Entry(frame, textvariable=zip1_path, width=50).grid(row=0, column=1, padx=5)
    tk.Button(frame, text="Select", command=lambda: select_zip(zip1_path)).grid(row=0, column=2, padx=5)

    tk.Label(frame, text="ZIP 2:").grid(row=1, column=0, padx=5)
    tk.Entry(frame, textvariable=zip2_path, width=50).grid(row=1, column=1, padx=5)
    tk.Button(frame, text="Select", command=lambda: select_zip(zip2_path)).grid(row=1, column=2, padx=5)

    tk.Button(frame, text="Compare", command=lambda: compare(zip1_path.get(), zip2_path.get(), tree)).grid(row=2, column=1, pady=10)

    tree_frame = tk.Frame(root)
    tree_frame.pack(fill='both', expand=True)

    columns = ('size1', 'date1', 'size2', 'date2')
    tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
    tree.heading('#0', text='File/Directory')
    tree.heading('size1', text='ZIP1 Size')
    tree.heading('date1', text='ZIP1 Date')
    tree.heading('size2', text='ZIP2 Size')
    tree.heading('date2', text='ZIP2 Date')
    tree.pack(side='left', fill='both', expand=True)

    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scroll.pack(side='right', fill='y')
    tree.configure(yscroll=scroll.set)

    # Configure tags for colors
    tree.tag_configure('only_zip1', background='lightblue')
    tree.tag_configure('only_zip2', background='lightgreen')
    tree.tag_configure('content_diff', background='yellow')
    tree.tag_configure('date_diff', background='orange')
    tree.tag_configure('same', background='white')

    root.mainloop()

def select_zip(path_var):
    path = filedialog.askopenfilename(filetypes=[('ZIP files', '*.zip')])
    if path:
        path_var.set(os.path.abspath(path))

def compare(zip1_file, zip2_file, tree):
    if not zip1_file or not zip2_file:
        messagebox.showerror("Error", "Please select both ZIP files.")
        return

    try:
        with zipfile.ZipFile(zip1_file) as z1, zipfile.ZipFile(zip2_file) as z2:
            namelist1 = z1.namelist()
            namelist2 = z2.namelist()
            all_members = sorted(set(namelist1) | set(namelist2))
            info1 = {name: z1.getinfo(name) for name in namelist1}
            info2 = {name: z2.getinfo(name) for name in namelist2}

            tree.delete(*tree.get_children())

            for full_path in all_members:
                is_dir = full_path.endswith('/')
                parts = full_path.rstrip('/').split('/')
                parent = ''
                current_path = ''

                for i, part in enumerate(parts):
                    if i < len(parts) - 1 or is_dir:
                        current_path = '/'.join(parts[:i+1]) + '/'
                    else:
                        current_path = '/'.join(parts[:i+1])

                    children = tree.get_children(parent)
                    found = None
                    for c in children:
                        if tree.item(c)['text'] == part:
                            found = c
                            break

                    if not found:
                        if i < len(parts) - 1 or is_dir:
                            # Directory
                            iid = tree.insert(parent, 'end', text=part, values=('', '', '', ''))
                        else:
                            # File
                            inf1 = info1.get(full_path)
                            inf2 = info2.get(full_path)
                            size1 = f"{inf1.file_size} bytes" if inf1 else 'Missing'
                            date1 = datetime(*inf1.date_time).strftime('%Y-%m-%d %H:%M:%S') if inf1 else 'Missing'
                            size2 = f"{inf2.file_size} bytes" if inf2 else 'Missing'
                            date2 = datetime(*inf2.date_time).strftime('%Y-%m-%d %H:%M:%S') if inf2 else 'Missing'

                            iid = tree.insert(parent, 'end', text=part, values=(size1, date1, size2, date2))

                            if not inf1:
                                tag = 'only_zip2'
                            elif not inf2:
                                tag = 'only_zip1'
                            elif inf1.file_size != inf2.file_size or inf1.CRC != inf2.CRC:
                                tag = 'content_diff'
                            elif inf1.date_time != inf2.date_time:
                                tag = 'date_diff'
                            else:
                                tag = 'same'

                            tree.item(iid, tags=(tag,))

                        parent = iid
                    else:
                        parent = found
    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    main()