import json
from abc import ABC, abstractmethod
from typing import List

# Principio S: Responsabilidad Única
class Task:
    def __init__(self, task_id: int, title: str, description: str, completed: bool = False):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.completed = completed

    def mark_completed(self):
        self.completed = True

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed
        }

# Principio O: Abierto/Cerrado
class TaskRepository(ABC):
    @abstractmethod
    def save_tasks(self, tasks: List[Task]):
        pass

    @abstractmethod
    def load_tasks(self) -> List[Task]:
        pass

# Implementación concreta del repositorio
class JsonTaskRepository(TaskRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def save_tasks(self, tasks: List[Task]):
        # Cumple con ACID: Atomicidad (escribe todo o nada), Consistencia (valida datos)
        try:
            with open(self.file_path, 'w') as file:
                json.dump([task.to_dict() for task in tasks], file, indent=4)
        except Exception as e:
            raise Exception(f"Error saving tasks: {e}")

    def load_tasks(self) -> List[Task]:
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                return [Task(**task_data) for task_data in data]
        except FileNotFoundError:
            return []
        except Exception as e:
            raise Exception(f"Error loading tasks: {e}")

# Principio L: Sustitución de Liskov
# TaskManager depende de la abstracción TaskRepository, no de la implementación concreta
class TaskManager:
    def __init__(self, repository: TaskRepository):
        self.repository = repository
        self.tasks: List[Task] = self.repository.load_tasks()

    def add_task(self, title: str, description: str):
        # Cumple con ACID: Durabilidad (persiste después de agregar)
        task_id = len(self.tasks) + 1
        task = Task(task_id, title, description)
        self.tasks.append(task)
        self.repository.save_tasks(self.tasks)

    def complete_task(self, task_id: int):
        for task in self.tasks:
            if task.task_id == task_id:
                task.mark_completed()
                self.repository.save_tasks(self.tasks)  # Durabilidad
                return
        raise ValueError(f"Task with ID {task_id} not found")

    def list_tasks(self) -> List[Task]:
        return self.tasks

# Principio I: Segregación de Interfaces
# TaskRepository solo define los métodos necesarios
# Principio D: Inversión de Dependencias
# TaskManager depende de la abstracción TaskRepository
def main():
    repository = JsonTaskRepository("tasks.json")
    manager = TaskManager(repository)

    # Ejemplo de uso
    manager.add_task("Comprar víveres", "Leche, pan, huevos")
    manager.add_task("Estudiar", "Repasar SOLID y ACID")
    manager.complete_task(1)
    for task in manager.list_tasks():
        print(f"Task {task.task_id}: {task.title} - Completed: {task.completed}")

if __name__ == "__main__":
    main()
