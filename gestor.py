from dotenv import load_dotenv
import os

load_dotenv()

PROYECTO = os.getenv('PROYECTO', 'Sin nombre')
VERSION  = os.getenv('VERSION', '1.0')

tareas = []

def agregar_tarea(descripcion):
    '''Agrega una tarea nueva a la lista'''
    tareas.append({'id': len(tareas) + 1, 'descripcion': descripcion, 'completada': False})
    return tareas[-1]

def listar_tareas():
    '''Retorna todas las tareas registradas'''
    return tareas

def completar_tarea(id_tarea):
    '''Marca una tarea como completada'''
    for tarea in tareas:
        if tarea['id'] == id_tarea:
            tarea['completada'] = True
            return tarea
    raise ValueError(f'Tarea {id_tarea} no encontrada')

if __name__ == '__main__':
    print(f'Proyecto: {PROYECTO} v{VERSION}')
    agregar_tarea('Configurar entorno de desarrollo')
    agregar_tarea('Crear repositorio en GitHub')
    agregar_tarea('Hacer primer commit')
    completar_tarea(1)
    for t in listar_tareas():
        estado = '✓' if t['completada'] else '○'
        print(f"{estado} [{t['id']}] {t['descripcion']}")
