from dotenv import load_dotenv
import os
import json
from typing import List, Dict
from pathlib import Path

# =========================
# Configuración
# =========================

load_dotenv()

PROYECTO = os.getenv('PROYECTO', 'Sin nombre')
VERSION = os.getenv('VERSION', '1.0')

ARCHIVO_TAREAS = 'tareas.json'


# =========================
# Persistencia
# =========================

def cargar_tareas() -> List[Dict]:
    """Carga las tareas desde un archivo JSON."""
    
    if not Path(ARCHIVO_TAREAS).exists():
        return []

    try:
        with open(ARCHIVO_TAREAS, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)

    except json.JSONDecodeError:
        print('⚠ Error leyendo tareas.json. Se iniciará vacío.')
        return []


def guardar_tareas(tareas: List[Dict]) -> None:
    """Guarda las tareas en un archivo JSON."""

    with open(ARCHIVO_TAREAS, 'w', encoding='utf-8') as archivo:
        json.dump(tareas, archivo, indent=4, ensure_ascii=False)


# =========================
# Estado global
# =========================

tareas = cargar_tareas()


# =========================
# Funciones principales
# =========================

def generar_id() -> int:
    """Genera un ID único incremental."""
    
    if not tareas:
        return 1

    return max(t['id'] for t in tareas) + 1


def agregar_tarea(descripcion: str) -> Dict:
    """Agrega una nueva tarea."""

    descripcion = descripcion.strip()

    if not descripcion:
        raise ValueError('La descripción no puede estar vacía.')

    nueva_tarea = {
        'id': generar_id(),
        'descripcion': descripcion,
        'completada': False
    }

    tareas.append(nueva_tarea)
    guardar_tareas(tareas)

    return nueva_tarea


def listar_tareas() -> List[Dict]:
    """Retorna todas las tareas."""
    
    return tareas


def completar_tarea(id_tarea: int) -> Dict:
    """Marca una tarea como completada."""

    for tarea in tareas:
        if tarea['id'] == id_tarea:
            tarea['completada'] = True
            guardar_tareas(tareas)
            return tarea

    raise ValueError(f'Tarea {id_tarea} no encontrada')


def eliminar_tarea(id_tarea: int) -> Dict:
    """Elimina una tarea por ID."""

    for tarea in tareas:
        if tarea['id'] == id_tarea:
            tareas.remove(tarea)
            guardar_tareas(tareas)
            return tarea

    raise ValueError(f'Tarea {id_tarea} no encontrada')


# =========================
# Utilidades
# =========================

def mostrar_tareas() -> None:
    """Imprime las tareas en consola."""

    if not tareas:
        print('No hay tareas registradas.')
        return

    print('\nLista de tareas:\n')

    for tarea in tareas:
        estado = '✓' if tarea['completada'] else '○'
        print(f"{estado} [{tarea['id']}] {tarea['descripcion']}")


# =========================
# Programa principal
# =========================

if __name__ == '__main__':

    print(f'\nProyecto: {PROYECTO} v{VERSION}')

    try:
        agregar_tarea('Configurar entorno de desarrollo')
        agregar_tarea('Crear repositorio en GitHub')
        agregar_tarea('Hacer primer commit')

        completar_tarea(1)

        mostrar_tareas()

    except ValueError as error:
        print(f'❌ Error: {error}')