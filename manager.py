# manager.py
import csv
import heapq
import json
import os
from tasks import Task, PRIORITAT_MAP

class TaskManager:
    """
    Gestiona las tareas con:
    - Cola de prioridad (min-heap)
    - Pilas de deshacer/rehacer
    - Persistencia en un archivo JSON
    """
    def __init__(self, filename="tasks.json"):
        self.filename = filename

        # Estructura de datos principal: min-heap
        # Cada elemento será una tupla: (prioridad, counter, Task)
        self.heap_tasques = []

        # Pilas para deshacer y rehacer
        self.undo_stack = []
        self.redo_stack = []

        # Contador incremental para desempatar cuando hay misma prioridad
        self._counter = 0

        # Al crear el gestor, cargamos los datos si existe el archivo
        self.load_data()
    # --------------------------------------------------
    # EXPORTAR TAREAS A CSV
    # --------------------------------------------------

    def exportar_csv(self):
        """Exporta todas las tareas a un archivo CSV en la carpeta Descargas del usuario."""
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "tareas.csv")

        try:
            with open(downloads_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Nombre", "Descripción", "Prioridad", "Categoría"])  # Cabecera

                if not self.heap_tasques:
                    print(f"No hay tareas, se generó un CSV vacío en: {downloads_path}")
                    return True

                for _, _, tarea in self.heap_tasques:
                    writer.writerow([tarea.nom, tarea.descripcio, tarea.prioritat, tarea.categoria])

            print(f"Tareas exportadas correctamente en: {downloads_path}")
            return True

        except Exception as e:
            print(f"Error al exportar CSV: {e}")
            return False
    # --------------------------------------------------
    # IMPORTAR TAREAS DESDE CSV
    # --------------------------------------------------

    def importar_csv(self, filepath="tareas.csv"):
        """Importa tareas desde un archivo CSV y borra todas las tareas existentes antes de importar."""
        try:
            with open(filepath, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                header = next(reader, None)  # Leer la cabecera para ignorarla

                if header != ["Nombre", "Descripción", "Prioridad", "Categoría"]:
                    print("Formato de archivo CSV incorrecto. Asegúrate de que tenga la cabecera correcta.")
                    return False

                # Borrar todas las tareas actuales antes de importar
                self.heap_tasques.clear()

                for row in reader:
                    if len(row) == 4:
                        nombre, descripcion, prioridad, categoria = row

                        # Convertimos prioridad a entero
                        try:
                            prioridad = int(prioridad)  # Asegurar que sea un número
                        except ValueError:
                            prioridad = 3  # Si hay un error, establecer prioridad "baja"

                        nueva_tarea = Task(nombre, descripcion, prioridad, categoria)
                        heapq.heappush(self.heap_tasques, (nueva_tarea.prioritat, self._counter, nueva_tarea))
                        self._counter += 1

                print(f"Tareas importadas correctamente desde {filepath}")
                return True

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {filepath}.")
            return False
        except Exception as e:
            print(f"Error al importar CSV: {e}")
            return False

    # --------------------------------------------------
    # PERSISTENCIA
    # --------------------------------------------------
    def load_data(self):
        """
        Carga las tareas desde un archivo JSON (si existe).
        Sin forzar a str(...) la prioridad, para que
        si es un número en JSON, se mantenga como entero.
        """
        if not os.path.exists(self.filename):
            return  # Si no existe el archivo, no hacemos nada

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Si el archivo está vacío o corrupto, no cargamos nada
            return

        # data debe ser una lista de diccionarios
        for item in data:
            nom = item.get("nom")
            desc = item.get("descripcio", "")
            # Obtenemos la prioridad tal cual (int o str).
            prior = item.get("prioritat", 3)  # por defecto 3 (baja)
            cat = item.get("categoria", "General")

            # Creamos la Task (el constructor maneja prioridad como texto o numérico)
            tasca = Task(nom, desc, prior, cat)

            # Insertamos en el heap con un contador incremental para desempatar
            heapq.heappush(self.heap_tasques, (tasca.prioritat, self._counter, tasca))
            self._counter += 1

    def save_data(self):
        """
        Guarda las tareas en formato JSON.
        """
        # Obtenemos la lista de tareas en orden de prioridad
        tasques = self.llistar_tasques_ordenades()

        # Convertimos cada tarea a diccionario
        data = []
        for t in tasques:
            data.append({
                "nom": t.nom,
                "descripcio": t.descripcio,
                "prioritat": t.prioritat,
                "categoria": t.categoria
            })

        # Escribimos en el archivo JSON
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # --------------------------------------------------
    # MÉTODOS PRINCIPALES
    # --------------------------------------------------
    def afegir_tasca(self, nom, descripcio, prioritat, categoria):
        """
        Agrega una nueva tarea al heap y registra la acción en undo_stack.
        """
        tasca = Task(nom, descripcio, prioritat, categoria)
        # Insertamos en el heap la tupla (prioridad, _counter, task)
        heapq.heappush(self.heap_tasques, (tasca.prioritat, self._counter, tasca))
        self._counter += 1

        self.undo_stack.append(("afegir", tasca))
        self.redo_stack.clear()
        self.save_data()

    def eliminar_tasca(self, nom):
        """
        Elimina solo la tarea cuyo nombre sea 'nom' (sin borrar otras con la misma prioridad).
        """
        tasques_restantes = []
        tasca_eliminada = None

        # Filtramos solo la tarea específica sin eliminar otras con la misma prioridad
        for prio, cnt, t in self.heap_tasques:
            if t.nom == nom and not tasca_eliminada:
                tasca_eliminada = t  # Eliminamos solo una vez la tarea con ese nombre
            else:
                tasques_restantes.append((prio, cnt, t))

        if tasca_eliminada:
            # Limpiamos el heap y lo reconstruimos solo con las tareas restantes
            self.heap_tasques.clear()
            for prio, cnt, t in tasques_restantes:
                heapq.heappush(self.heap_tasques, (prio, cnt, t))

            # Guardar la acción en undo_stack
            self.undo_stack.append(("eliminar", tasca_eliminada))
            self.redo_stack.clear()
            self.save_data()
            return True

        return False  # Si no se encontró la tarea

    def llistar_tasques_ordenades(self):
        """
        Retorna una lista de tareas ordenadas por prioridad (sin modificar el heap).
        """
        if not self.heap_tasques:
            return []

        copia = list(self.heap_tasques)
        tasques_ordenades = []
        while copia:
            prio, cnt, t = heapq.heappop(copia)
            tasques_ordenades.append(t)
        return tasques_ordenades

    # --------------------------------------------------
    # DESHACER / REHACER
    # --------------------------------------------------
    def desfer_accio(self):
        """
        Deshace la última acción (agregar o eliminar).
        """
        if not self.undo_stack:
            return None

        accio, tasca = self.undo_stack.pop()
        if accio == "afegir":
            # Eliminamos la tarea del heap
            self._eliminar_directe(tasca)
            self.redo_stack.append(("afegir", tasca))
            self.save_data()
            return ("desfer-afegir", tasca.nom)
        elif accio == "eliminar":
            # Volvemos a agregar la tarea
            self._afegir_directe(tasca)
            self.redo_stack.append(("eliminar", tasca))
            self.save_data()
            return ("desfer-eliminar", tasca.nom)

    def refer_accio(self):
        """
        Rehace la última acción deshecha.
        """
        if not self.redo_stack:
            return None

        accio, tasca = self.redo_stack.pop()
        if accio == "afegir":
            self._afegir_directe(tasca)
            self.undo_stack.append(("afegir", tasca))
            self.save_data()
            return ("refer-afegir", tasca.nom)
        elif accio == "eliminar":
            self._eliminar_directe(tasca)
            self.undo_stack.append(("eliminar", tasca))
            self.save_data()
            return ("refer-eliminar", tasca.nom)

    # --------------------------------------------------
    # MÉTODOS AUXILIARES
    # --------------------------------------------------
    def _afegir_directe(self, tasca):
        """
        Inserta la tarea en el heap sin registrar la acción en undo_stack.
        (Se utiliza al deshacer y rehacer.)
        """
        heapq.heappush(self.heap_tasques, (tasca.prioritat, self._counter, tasca))
        self._counter += 1

    def _eliminar_directe(self, tasca):
        """
        Elimina solo UNA tarea del heap sin afectar a otras con la misma prioridad.
        """
        temp = []
        eliminada = False  # Para asegurarnos de que solo eliminamos una vez

        while self.heap_tasques:
            prio, cnt, t = heapq.heappop(self.heap_tasques)
            if t.nom == tasca.nom and not eliminada:
                eliminada = True  # Marcamos que eliminamos la tarea
            else:
                temp.append((prio, cnt, t))

        # Reconstruimos el heap con las tareas restantes
        for prio, cnt, t in temp:
            heapq.heappush(self.heap_tasques, (prio, cnt, t))

    # --------------------------------------------------
    # FILTRADO POR CATEGORÍA
    # --------------------------------------------------
    def filtrar_per_categoria(self, categoria):
        """
        Retorna las tareas que coincidan con la categoría (en orden de prioridad).
        """
        tasques = self.llistar_tasques_ordenades()
        return [t for t in tasques if t.categoria.lower() == categoria.lower()]
