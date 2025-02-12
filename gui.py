# gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog, messagebox
from manager import TaskManager

def priority_as_text(prio: int) -> str:
    """
    Convierte el valor numérico (1,2,3) en texto (Alta, Mitjana, Baixa).
    """
    if prio == 1:
        return "Alta"
    elif prio == 2:
        return "Media"
    else:
        return "Baja"

class TaskManagerGUI:
    """
    Interfaz gráfica Tkinter que usa un TaskManager para gestionar tareas.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Tareas - Prioridad numérica o texto")

        # Estilo opcional
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        # Barra de menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exportar Tareas a CSV", command=self.exportar_csv_gui)
        file_menu.add_command(label="Importar Tareas desde CSV", command=self.importar_csv_gui)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Opciones", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        # Instancia de la lógica
        self.task_manager = TaskManager(filename="tasks.json")

        # Marco principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # --------------------------------------------------------------------
        # IZQUIERDA: Treeview para listar tareas
        # --------------------------------------------------------------------
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(0, 10))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        columns = ("nombre", "prioridad", "categoria", "descripcion")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("prioridad", text="Prioridad")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("descripcion", text="Descripción")

        self.tree.column("nombre", width=120, anchor="center")
        self.tree.column("prioridad", width=80, anchor="center")
        self.tree.column("categoria", width=100, anchor="center")
        self.tree.column("descripcion", width=200, anchor="w")

        self.tree.grid(row=0, column=0, sticky="nsew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configuración de tags para colorear filas
        self.tree.tag_configure("Alta", background="#ffcccc")      # rojizo
        self.tree.tag_configure("Media", background="#fff2cc")   # amarillento
        self.tree.tag_configure("Baja", background="#ccffcc")     # verdoso

        # --------------------------------------------------------------------
        # DERECHA: Controles
        # --------------------------------------------------------------------
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=1, sticky="nsew")

        # --- Nueva Tarea ---
        task_frame = ttk.LabelFrame(controls_frame, text="Nueva Tarea", padding="10")
        task_frame.grid(row=0, column=0, sticky="ew", pady=5)

        ttk.Label(task_frame, text="Nombre:").grid(row=0, column=0, sticky="e", pady=2)
        self.entry_nombre = ttk.Entry(task_frame)
        self.entry_nombre.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(task_frame, text="Descripción:").grid(row=1, column=0, sticky="e", pady=2)
        self.entry_descripcion = ttk.Entry(task_frame)
        self.entry_descripcion.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(task_frame, text="Prioridad (alta/media/baja o 1/2/3):").grid(row=2, column=0, sticky="e", pady=2)
        self.entry_prioritat = ttk.Entry(task_frame)
        self.entry_prioritat.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(task_frame, text="Categoría:").grid(row=3, column=0, sticky="e", pady=2)
        self.entry_categoria = ttk.Entry(task_frame)
        self.entry_categoria.grid(row=3, column=1, sticky="ew", pady=2)

        task_frame.columnconfigure(1, weight=1)

        self.btn_agregar = ttk.Button(task_frame, text="Agregar Tarea", command=self.agregar_tarea_gui)
        self.btn_agregar.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

        # --- Acciones ---
        actions_frame = ttk.LabelFrame(controls_frame, text="Acciones", padding="10")
        actions_frame.grid(row=1, column=0, sticky="ew", pady=5)

        self.btn_eliminar = ttk.Button(actions_frame, text="Eliminar Tarea", command=self.eliminar_tarea_gui)
        self.btn_eliminar.grid(row=0, column=0, sticky="ew", pady=2)

        self.btn_deshacer = ttk.Button(actions_frame, text="Deshacer (Undo)", command=self.deshacer_accion_gui)
        self.btn_deshacer.grid(row=1, column=0, sticky="ew", pady=2)

        self.btn_rehacer = ttk.Button(actions_frame, text="Rehacer (Redo)", command=self.rehacer_accion_gui)
        self.btn_rehacer.grid(row=2, column=0, sticky="ew", pady=2)

        self.btn_refrescar = ttk.Button(actions_frame, text="Refrescar Lista", command=self.actualizar_tree)
        self.btn_refrescar.grid(row=3, column=0, sticky="ew", pady=2)

        actions_frame.columnconfigure(0, weight=1)

        # --- Filtro de Categoría ---
        filter_frame = ttk.LabelFrame(controls_frame, text="Filtrar Tareas por Categoría", padding="10")
        filter_frame.grid(row=2, column=0, sticky="ew", pady=5)

        ttk.Label(filter_frame, text="Categoría:").grid(row=0, column=0, sticky="e", pady=2)
        self.entry_filtro = ttk.Entry(filter_frame)
        self.entry_filtro.grid(row=0, column=1, sticky="ew", pady=2)

        self.btn_filtrar = ttk.Button(filter_frame, text="Filtrar", command=self.filtrar_categoria_gui)
        self.btn_filtrar.grid(row=1, column=0, sticky="ew", pady=2)

        self.btn_mostrar_todas = ttk.Button(filter_frame, text="Mostrar Todas", command=self.mostrar_todas_gui)
        self.btn_mostrar_todas.grid(row=1, column=1, sticky="ew", pady=2)

        filter_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(0, weight=1)

        # Al iniciar, refresca la tabla
        self.actualizar_tree()

    # --------------------------------------------------------------------
    # Funciones de la GUI
    # --------------------------------------------------------------------
    def show_about(self):
        messagebox.showinfo(
            "Acerca de - Gestor de Tareas",
            (
                "📝 GESTOR DE TAREAS\n"
                "Aplicación diseñada para la gestión eficiente de tareas,\n"
                "permitiendo organizar y priorizar actividades de manera intuitiva.\n\n"
                "📌 Características principales:\n"
                "✅ Gestión de tareas con prioridad numérica o textual.\n"
                "✅ Interfaz intuitiva con soporte para deshacer/rehacer cambios.\n"
                "✅ Filtrado de tareas por categoría para una mejor organización.\n"
                "✅ Persistencia automática en archivo JSON.\n"
                "✅ Código optimizado con estructuras de datos eficientes.\n\n"
                "🔹 Versión: 1.0.0\n"
                "🔹 Autor: Pau\n"
                "🔹 Contacto: pau@example.com\n"
                "🔹 Licencia: MIT\n\n"
                "📢 ¡Gracias por usar nuestro gestor de tareas!"
            )
        )

    def exportar_csv_gui(self):
        """Exporta tareas a un archivo CSV llamado 'tareas.csv' sin cuadro de diálogo."""
        filename = "tareas.csv"  # Nombre fijo del archivo

        if self.task_manager.exportar_csv():  # Ya no necesita pasar filename
            messagebox.showinfo("Exportación Exitosa", f"Tareas exportadas correctamente a:\n{filename}")
        else:
            messagebox.showerror("Error", "No se pudo exportar las tareas.")

    def importar_csv_gui(self):
        """Abre un cuadro de diálogo para importar tareas desde un archivo CSV."""
        filename = filedialog.askopenfilename(
            filetypes=[("Archivo CSV", "*.csv")],
            title="Importar Tareas desde CSV"
        )

        if not filename:
            return  # Usuario canceló la selección

        if self.task_manager.importar_csv(filename):
            messagebox.showinfo("Importación Exitosa", f"Tareas importadas correctamente desde:\n{filename}")
            self.actualizar_tree()  # Refrescar la lista en la GUI
        else:
            messagebox.showerror("Error", "No se pudo importar las tareas.")
    def agregar_tarea_gui(self):
        nombre = self.entry_nombre.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        prioridad = self.entry_prioritat.get().strip()
        categoria = self.entry_categoria.get().strip()

        if not nombre:
            messagebox.showerror("Error", "El campo 'Nombre' es obligatorio.")
            return

        # Si el usuario escribe "1", "2", "3", lo convertimos a int para que
        # en tasks.py lo reconozca como número.
        # Si escribe algo distinto, se mantendrá como string:
        #   "alta", "mitjana", "baixa" -> Ok
        #   cualquier otra -> fallback a 3
        if prioridad in ["1", "2", "3"]:
            prioridad = int(prioridad)  # lo convertimos a entero

        if not categoria:
            categoria = "General"

        self.task_manager.afegir_tasca(nombre, descripcion, prioridad, categoria)
        messagebox.showinfo("Info", f"Tarea '{nombre}' agregada correctamente.")

        # Limpiar los campos
        self.entry_nombre.delete(0, tk.END)
        self.entry_descripcion.delete(0, tk.END)
        self.entry_prioritat.delete(0, tk.END)
        self.entry_categoria.delete(0, tk.END)

        self.actualizar_tree()

    def eliminar_tarea_gui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona una tarea para eliminar.")
            return

        item = selected[0]
        values = self.tree.item(item, "values")
        nombre = values[0]

        resultado = self.task_manager.eliminar_tasca(nombre)
        if resultado:
            messagebox.showinfo("Info", f"Tarea '{nombre}' eliminada.")
        else:
            messagebox.showwarning("Atención", f"No se encontró la tarea '{nombre}'.")

        self.actualizar_tree()

    def deshacer_accion_gui(self):
        resultado = self.task_manager.desfer_accio()
        if resultado is None:
            messagebox.showinfo("Info", "No hay acciones para deshacer.")
        else:
            accion, nombre_tarea = resultado
            if accion == "desfer-afegir":
                messagebox.showinfo("Info", f"Se ha deshecho la adición de la tarea '{nombre_tarea}'.")
            elif accion == "desfer-eliminar":
                messagebox.showinfo("Info", f"Se ha deshecho la eliminación de la tarea '{nombre_tarea}'.")
        self.actualizar_tree()

    def rehacer_accion_gui(self):
        resultado = self.task_manager.refer_accio()
        if resultado is None:
            messagebox.showinfo("Info", "No hay acciones para rehacer.")
        else:
            accion, nombre_tarea = resultado
            if accion == "refer-afegir":
                messagebox.showinfo("Info", f"Se ha rehecho la adición de la tarea '{nombre_tarea}'.")
            elif accion == "refer-eliminar":
                messagebox.showinfo("Info", f"Se ha rehecho la eliminación de la tarea '{nombre_tarea}'.")
        self.actualizar_tree()

    def actualizar_tree(self):
        """Refresca el Treeview con la lista de tareas, coloreando según la prioridad."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        tareas = self.task_manager.llistar_tasques_ordenades()
        for t in tareas:
            # Pasamos de int (1,2,3) a texto (Alta, Mitjana, Baixa)
            p_text = priority_as_text(t.prioritat)

            self.tree.insert(
                "",
                tk.END,
                values=(t.nom, p_text, t.categoria, t.descripcio),
                tags=(p_text,)  # usaremos la tag para colorear
            )

    def filtrar_categoria_gui(self):
        cat = self.entry_filtro.get().strip()
        if not cat:
            messagebox.showwarning("Atención", "Introduce una categoría para filtrar.")
            return

        filtradas = self.task_manager.filtrar_per_categoria(cat)
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not filtradas:
            messagebox.showinfo("Info", f"No hay tareas con la categoría '{cat}'.")
            return

        for t in filtradas:
            p_text = priority_as_text(t.prioritat)
            self.tree.insert(
                "",
                tk.END,
                values=(t.nom, p_text, t.categoria, t.descripcio),
                tags=(p_text,)
            )

    def mostrar_todas_gui(self):
        self.entry_filtro.delete(0, tk.END)
        self.actualizar_tree()
