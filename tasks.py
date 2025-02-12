# tasks.py

PRIORITAT_MAP = {
    "alta": 1,
    "media": 2,
    "baja": 3
}

class Task:
    """
    Representa una tarea que puede recibir la prioridad:
    - como entero (1,2,3)
    - o como texto ("alta","mitjana","baixa")
    """
    def __init__(self, nom, descripcio, prioritat, categoria=None):
        self.nom = nom
        self.descripcio = descripcio

        # Si es int (1, 2, 3), se usa tal cual. Si no, se interpreta como texto.
        if isinstance(prioritat, int):
            if prioritat in [1, 2, 3]:
                self.prioritat = prioritat
            else:
                self.prioritat = 3  # por defecto, baja
        else:
            # si es texto ("alta","mitjana","baixa" o "1"...) -> se fuerza a minúsculas
            prio_str = str(prioritat).lower()
            self.prioritat = PRIORITAT_MAP.get(prio_str, 3)

        self.categoria = categoria if categoria else "General"

    def __repr__(self):
        return (
            f"Task(nom='{self.nom}', "
            f"prioritat={self.prioritat}, "
            f"desc='{self.descripcio}', "
            f"cat='{self.categoria}')"
        )

    def __lt__(self, other):
        """Define cómo comparar tareas en el heap. Se ordenan por prioridad."""
        return self.prioritat < other.prioritat
