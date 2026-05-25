"""
Aplicación profesional de gestión de tareas.

Características:
- Persistencia en JSON
- Tipado estático
- Dataclasses
- Logging
- Manejo robusto de errores
- Prioridades
- Fechas de creación/completado
- Búsquedas y filtros
- Estadísticas
- Arquitectura limpia
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from dotenv import load_dotenv
from enum import Enum
from pathlib import Path
from typing import List, Optional
import json
import logging
import os


# =========================================================
# CONFIGURACIÓN
# =========================================================

load_dotenv()

PROYECTO = os.getenv("PROYECTO", "Task Manager")
VERSION = os.getenv("VERSION", "2.0.0")

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "tareas.json"
LOG_FILE = BASE_DIR / "app.log"


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)


# =========================================================
# ENUMS
# =========================================================

class Prioridad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


# =========================================================
# EXCEPCIONES PERSONALIZADAS
# =========================================================

class TareaError(Exception):
    """Excepción base para tareas."""


class TareaNoEncontradaError(TareaError):
    """Se lanza cuando no existe una tarea."""


class ValidacionError(TareaError):
    """Se lanza cuando los datos son inválidos."""


# =========================================================
# MODELO
# =========================================================

@dataclass
class Tarea:
    id: int
    descripcion: str
    prioridad: Prioridad
    completada: bool = False
    fecha_creacion: str = ""
    fecha_completado: Optional[str] = None

    def completar(self) -> None:
        self.completada = True
        self.fecha_completado = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Tarea":
        return Tarea(
            id=data["id"],
            descripcion=data["descripcion"],
            prioridad=Prioridad(data["prioridad"]),
            completada=data.get("completada", False),
            fecha_creacion=data.get("fecha_creacion", ""),
            fecha_completado=data.get("fecha_completado")
        )


# =========================================================
# REPOSITORIO
# =========================================================

class RepositorioTareas:

    def __init__(self, archivo: Path):
        self.archivo = archivo

    def cargar(self) -> List[Tarea]:

        if not self.archivo.exists():
            return []

        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                data = json.load(f)

            return [Tarea.from_dict(item) for item in data]

        except json.JSONDecodeError as e:
            logging.error(f"JSON corrupto: {e}")
            return []

        except Exception as e:
            logging.error(f"Error cargando tareas: {e}")
            return []

    def guardar(self, tareas: List[Tarea]) -> None:

        try:
            with open(self.archivo, "w", encoding="utf-8") as f:
                json.dump(
                    [t.to_dict() for t in tareas],
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:
            logging.error(f"Error guardando tareas: {e}")
            raise


# =========================================================
# SERVICIO
# =========================================================

class GestorTareas:

    def __init__(self, repositorio: RepositorioTareas):
        self.repo = repositorio
        self.tareas = self.repo.cargar()

    # -----------------------------------------------------

    def _generar_id(self) -> int:

        if not self.tareas:
            return 1

        return max(t.id for t in self.tareas) + 1

    # -----------------------------------------------------

    def agregar_tarea(
        self,
        descripcion: str,
        prioridad: Prioridad = Prioridad.MEDIA
    ) -> Tarea:

        descripcion = descripcion.strip()

        if not descripcion:
            raise ValidacionError(
                "La descripción no puede estar vacía."
            )

        tarea = Tarea(
            id=self._generar_id(),
            descripcion=descripcion,
            prioridad=prioridad,
            fecha_creacion=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        self.tareas.append(tarea)
        self.repo.guardar(self.tareas)

        logging.info(f"Tarea agregada: {tarea.descripcion}")

        return tarea

    # -----------------------------------------------------

    def listar_tareas(self) -> List[Tarea]:
        return self.tareas

    # -----------------------------------------------------

    def buscar_por_id(self, tarea_id: int) -> Tarea:

        for tarea in self.tareas:
            if tarea.id == tarea_id:
                return tarea

        raise TareaNoEncontradaError(
            f"Tarea {tarea_id} no encontrada."
        )

    # -----------------------------------------------------

    def completar_tarea(self, tarea_id: int) -> Tarea:

        tarea = self.buscar_por_id(tarea_id)

        tarea.completar()

        self.repo.guardar(self.tareas)

        logging.info(f"Tarea completada: {tarea.descripcion}")

        return tarea

    # -----------------------------------------------------

    def eliminar_tarea(self, tarea_id: int) -> Tarea:

        tarea = self.buscar_por_id(tarea_id)

        self.tareas.remove(tarea)

        self.repo.guardar(self.tareas)

        logging.info(f"Tarea eliminada: {tarea.descripcion}")

        return tarea

    # -----------------------------------------------------

    def filtrar_completadas(self) -> List[Tarea]:

        return [
            t for t in self.tareas
            if t.completada
        ]

    # -----------------------------------------------------

    def filtrar_pendientes(self) -> List[Tarea]:

        return [
            t for t in self.tareas
            if not t.completada
        ]

    # -----------------------------------------------------

    def buscar_por_prioridad(
        self,
        prioridad: Prioridad
    ) -> List[Tarea]:

        return [
            t for t in self.tareas
            if t.prioridad == prioridad
        ]

    # -----------------------------------------------------

    def obtener_estadisticas(self) -> dict:

        total = len(self.tareas)

        completadas = len(
            self.filtrar_completadas()
        )

        pendientes = len(
            self.filtrar_pendientes()
        )

        return {
            "total": total,
            "completadas": completadas,
            "pendientes": pendientes
        }


# =========================================================
# UI
# =========================================================

def imprimir_tareas(tareas: List[Tarea]) -> None:

    if not tareas:
        print("\nNo hay tareas.\n")
        return

    print("\n================ TAREAS ================\n")

    for tarea in tareas:

        estado = "✓" if tarea.completada else "○"

        print(
            f"{estado} "
            f"[{tarea.id}] "
            f"{tarea.descripcion}"
        )

        print(f"   Prioridad : {tarea.prioridad.value}")
        print(f"   Creada    : {tarea.fecha_creacion}")

        if tarea.fecha_completado:
            print(
                f"   Completada: "
                f"{tarea.fecha_completado}"
            )

        print()


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print(f"\n{PROYECTO} v{VERSION}")

    repo = RepositorioTareas(DATA_FILE)

    gestor = GestorTareas(repo)

    try:

        if not gestor.listar_tareas():

            gestor.agregar_tarea(
                "Configurar entorno",
                Prioridad.ALTA
            )

            gestor.agregar_tarea(
                "Crear repositorio GitHub",
                Prioridad.MEDIA
            )

            gestor.agregar_tarea(
                "Hacer primer commit",
                Prioridad.ALTA
            )

            gestor.completar_tarea(1)

        imprimir_tareas(
            gestor.listar_tareas()
        )

        stats = gestor.obtener_estadisticas()

        print("============= ESTADÍSTICAS =============\n")

        print(f"Total       : {stats['total']}")
        print(f"Completadas : {stats['completadas']}")
        print(f"Pendientes  : {stats['pendientes']}")

        print()

    except TareaError as e:

        logging.error(str(e))

        print(f"\n❌ Error: {e}\n")

    except Exception as e:

        logging.exception("Error inesperado")

        print(f"\n🔥 Error inesperado: {e}\n")


# =========================================================

if __name__ == "__main__":
    main()