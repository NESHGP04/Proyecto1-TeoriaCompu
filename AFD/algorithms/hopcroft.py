'''
Algoritmo de Hopcroft para minimizar un AFD - Versión mejorada con eliminación de estados muertos
'''

from collections import defaultdict, deque
from typing import List, Optional, Set
from .subset_construction import afn_a_afd, mostrar_tabla_transiciones, optimizar_nombres_estados
from .thompson import regexp_a_afn
from models.automata import AFD

class Particion:
    """Representa una partición de estados para el algoritmo de Hopcroft"""
    def __init__(self):
        self.grupos = []
        self.estado_a_grupo = {}
    
    def agregar_grupo(self, estados: Set[int]) -> int:
        """Agrega un nuevo grupo y retorna su índice"""
        grupo_id = len(self.grupos)
        self.grupos.append(set(estados))
        
        for estado in estados:
            self.estado_a_grupo[estado] = grupo_id
        
        return grupo_id
    
    def obtener_grupo(self, estado: int) -> int:
        """Obtiene el grupo al que pertenece un estado"""
        return self.estado_a_grupo.get(estado, -1)
    
    def dividir_grupo(self, grupo_id: int, nuevos_grupos: List[Set[int]]):
        """Divide un grupo en varios grupos nuevos"""
        # Remover el grupo original
        for estado in self.grupos[grupo_id]:
            del self.estado_a_grupo[estado]
        
        # Agregar los nuevos grupos
        for nuevo_grupo in nuevos_grupos:
            if nuevo_grupo:  # Solo si no está vacío
                self.agregar_grupo(nuevo_grupo)
    
    def __len__(self):
        return len(self.grupos)
    
    def __iter__(self):
        return iter(self.grupos)

def eliminar_estados_muertos(afd: AFD, mostrar_detalles: bool = True) -> AFD:
    """
    Elimina estados muertos (estados no de aceptación que no pueden alcanzar estados de aceptación)
    
    Args:
        afd: El AFD del cual eliminar estados muertos
        mostrar_detalles: Si mostrar información del proceso
    
    Returns:
        AFD sin estados muertos
    """
    if mostrar_detalles:
        print("🗑️  Eliminando estados muertos...")
    
    # Paso 1: Encontrar todos los estados que pueden alcanzar estados de aceptación
    estados_vivos = set(afd.estados_aceptacion)  # Los estados de aceptación están vivos
    
    # BFS inverso: desde estados de aceptación hacia atrás
    cambios = True
    while cambios:
        cambios = False
        nuevos_vivos = set(estados_vivos)
        
        # Para cada transición, si el destino está vivo, el origen también
        for transicion in afd.transiciones:
            if transicion.destino in estados_vivos and transicion.origen not in estados_vivos:
                nuevos_vivos.add(transicion.origen)
                cambios = True
        
        estados_vivos = nuevos_vivos
    
    # Paso 2: Identificar estados muertos
    todos_los_estados = set(afd.estados.keys())
    estados_muertos = todos_los_estados - estados_vivos
    
    if mostrar_detalles:
        print(f"   Estados vivos: {sorted(estados_vivos)}")
        print(f"   Estados muertos: {sorted(estados_muertos)}")
    
    # Paso 3: Si no hay estados muertos, retornar el AFD original
    if not estados_muertos:
        if mostrar_detalles:
            print("   ✅ No hay estados muertos que eliminar")
        return afd
    
    # Paso 4: Crear nuevo AFD sin estados muertos
    afd_sin_muertos = AFD()
    mapeo_estados = {}
    
    # Crear estados vivos en el nuevo AFD
    for estado_viejo in sorted(estados_vivos):
        es_aceptacion = estado_viejo in afd.estados_aceptacion
        estado_nuevo = afd_sin_muertos.agregar_estado(es_aceptacion)
        mapeo_estados[estado_viejo] = estado_nuevo
        
        if mostrar_detalles:
            tipo = " (aceptación)" if es_aceptacion else ""
            print(f"   q{estado_viejo} -> q{estado_nuevo}{tipo}")
    
    # Establecer estado inicial (solo si está vivo)
    if afd.estado_inicial in estados_vivos:
        nuevo_inicial = mapeo_estados[afd.estado_inicial]
        afd_sin_muertos.establecer_inicial(nuevo_inicial)
    else:
        # Caso especial: si el estado inicial está muerto, el autómata no acepta nada
        if mostrar_detalles:
            print("   ⚠️  Estado inicial está muerto - autómata no acepta nada")
        # Crear un estado inicial que no acepta nada
        estado_inicial_nuevo = afd_sin_muertos.agregar_estado(es_aceptacion=False)
        afd_sin_muertos.establecer_inicial(estado_inicial_nuevo)
    
    # Agregar transiciones entre estados vivos
    transiciones_agregadas = set()
    for transicion in afd.transiciones:
        if (transicion.origen in estados_vivos and 
            transicion.destino in estados_vivos):
            
            origen_nuevo = mapeo_estados[transicion.origen]
            destino_nuevo = mapeo_estados[transicion.destino]
            
            # Evitar transiciones duplicadas
            clave_transicion = (origen_nuevo, transicion.simbolo, destino_nuevo)
            if clave_transicion not in transiciones_agregadas:
                afd_sin_muertos.agregar_transicion(origen_nuevo, transicion.simbolo, destino_nuevo)
                transiciones_agregadas.add(clave_transicion)
    
    if mostrar_detalles:
        print(f"   ✅ Eliminados {len(estados_muertos)} estados muertos")
        print(f"   AFD resultante: {len(afd_sin_muertos.estados)} estados")
    
    return afd_sin_muertos

def es_estado_trampa(afd: AFD, estado: int) -> bool:
    """
    Verifica si un estado es un estado trampa:
    - No es de aceptación
    - Todas sus transiciones van a sí mismo
    """
    if estado in afd.estados_aceptacion:
        return False
    
    # Verificar que todas las transiciones desde este estado van a sí mismo
    for simbolo in afd.alfabeto:
        encontrada_transicion = False
        for transicion in afd.transiciones:
            if transicion.origen == estado and transicion.simbolo == simbolo:
                if transicion.destino != estado:
                    return False  # Una transición no va a sí mismo
                encontrada_transicion = True
                break
        
        if not encontrada_transicion:
            return False  # Falta una transición
    
    return True

def minimizar_afd_hopcroft(afd: AFD) -> AFD:
    """
    Minimiza un AFD usando el algoritmo de Hopcroft y elimina estados muertos
    """
    print("Iniciando minimización con algoritmo de Hopcroft...")
    
    # Paso 1: Crear partición inicial
    # Separar estados de aceptación y no aceptación
    estados_aceptacion = set(afd.estados_aceptacion)
    estados_no_aceptacion = set(afd.estados.keys()) - estados_aceptacion
    
    particion = Particion()
    
    if estados_no_aceptacion:
        particion.agregar_grupo(estados_no_aceptacion)
        print(f"Grupo 0 (no aceptación): {estados_no_aceptacion}")
    
    if estados_aceptacion:
        particion.agregar_grupo(estados_aceptacion)
        print(f"Grupo {len(particion)-1} (aceptación): {estados_aceptacion}")
    
    # Paso 2: Refinar particiones iterativamente
    cambios = True
    iteracion = 0
    
    while cambios:
        cambios = False
        iteracion += 1
        print(f"\n--- Iteración {iteracion} ---")
        
        # Para cada grupo actual
        grupos_actuales = list(particion.grupos)
        
        for grupo_id, grupo in enumerate(grupos_actuales):
            if not grupo:  # Grupo vacío
                continue
                
            print(f"Analizando grupo {grupo_id}: {grupo}")
            
            # Para cada símbolo del alfabeto
            for simbolo in sorted(afd.alfabeto):
                # Crear subgrupos basados en a dónde van con este símbolo
                subgrupos = defaultdict(set)
                
                for estado in grupo:
                    # Encontrar el grupo destino para este estado con este símbolo
                    estado_destino = obtener_destino(afd, estado, simbolo)
                    if estado_destino is not None:
                        grupo_destino = particion.obtener_grupo(estado_destino)
                        subgrupos[grupo_destino].add(estado)
                    else:
                        # Estados sin transición para este símbolo van a un grupo especial
                        subgrupos[-1].add(estado)
                
                # Si se formaron múltiples subgrupos, dividir
                if len(subgrupos) > 1:
                    nuevos_grupos = list(subgrupos.values())
                    print(f"  Dividiendo por símbolo '{simbolo}': {list(subgrupos.keys())}")
                    
                    # Remover el grupo original de la partición actual
                    particion.grupos[grupo_id] = set()
                    
                    # Agregar los nuevos subgrupos
                    for nuevo_grupo in nuevos_grupos:
                        if nuevo_grupo:
                            nuevo_id = particion.agregar_grupo(nuevo_grupo)
                            print(f"    Nuevo grupo {nuevo_id}: {nuevo_grupo}")
                    
                    cambios = True
                    break  # Procesar siguiente grupo
    
    print(f"\nMinimización completada en {iteracion} iteraciones")
    print(f"Grupos finales: {len(particion)}")
    
    # Paso 3: Construir AFD minimizado
    afd_minimizado = construir_afd_minimizado(afd, particion)
    
    # Paso 4: Eliminar estados muertos
    print(f"\n--- Eliminación de estados muertos ---")
    afd_sin_muertos = eliminar_estados_muertos(afd_minimizado, mostrar_detalles=True)
    
    # Paso 5: Renumerar estados para orden lógico
    afd_final = renumerar_afd_logico(afd_sin_muertos)
    
    return afd_final

def obtener_destino(afd: AFD, estado: int, simbolo: str) -> Optional[int]:
    """Obtiene el estado destino para una transición dada"""
    for transicion in afd.transiciones:
        if transicion.origen == estado and transicion.simbolo == simbolo:
            return transicion.destino
    return None

def construir_afd_minimizado(afd_original: AFD, particion: Particion) -> AFD:
    """Construye el AFD minimizado a partir de la partición final"""
    afd_min = AFD()
    
    # Crear estados en el AFD minimizado (uno por grupo)
    grupo_a_estado = {}
    for grupo_id, grupo in enumerate(particion.grupos):
        if grupo:  # Solo grupos no vacíos
            es_aceptacion = bool(grupo.intersection(afd_original.estados_aceptacion))
            estado_min = afd_min.agregar_estado(es_aceptacion)
            grupo_a_estado[grupo_id] = estado_min
            
            print(f"Grupo {grupo_id} -> Estado {estado_min} {'(aceptación)' if es_aceptacion else ''}")
    
    # Establecer estado inicial
    grupo_inicial = particion.obtener_grupo(afd_original.estado_inicial)
    if grupo_inicial in grupo_a_estado:
        afd_min.establecer_inicial(grupo_a_estado[grupo_inicial])
    
    # Crear transiciones
    transiciones_agregadas = set()
    
    for transicion in afd_original.transiciones:
        grupo_origen = particion.obtener_grupo(transicion.origen)
        grupo_destino = particion.obtener_grupo(transicion.destino)
        
        if grupo_origen in grupo_a_estado and grupo_destino in grupo_a_estado:
            estado_origen = grupo_a_estado[grupo_origen]
            estado_destino = grupo_a_estado[grupo_destino]
            
            # Evitar transiciones duplicadas
            transicion_key = (estado_origen, transicion.simbolo, estado_destino)
            if transicion_key not in transiciones_agregadas:
                afd_min.agregar_transicion(estado_origen, transicion.simbolo, estado_destino)
                transiciones_agregadas.add(transicion_key)
    
    return afd_min

def renumerar_afd_logico(afd: AFD) -> AFD:
    """
    Renumera los estados del AFD para que sigan un orden lógico:
    - Estado inicial: 0
    - Estados siguientes: en orden BFS
    - Estados de aceptación al final cuando sea posible
    """
    print("Renumerando estados para orden lógico...")
    
    # BFS desde el estado inicial para encontrar orden lógico
    mapeo = {}
    visitados = set()
    cola = deque([afd.estado_inicial])
    orden_estados = []
    
    # BFS para orden lógico
    while cola:
        estado_actual = cola.popleft()
        if estado_actual not in visitados:
            visitados.add(estado_actual)
            orden_estados.append(estado_actual)
            
            # Encontrar estados destino ordenados por símbolo
            destinos = []
            for t in afd.transiciones:
                if t.origen == estado_actual and t.destino not in visitados:
                    destinos.append((t.simbolo, t.destino))
            
            # Ordenar por símbolo y agregar a la cola
            destinos.sort(key=lambda x: x[0])
            for simbolo, destino in destinos:
                if destino not in cola:
                    cola.append(destino)
    
    # Agregar estados no visitados (si los hay)
    for estado in afd.estados.keys():
        if estado not in visitados:
            orden_estados.append(estado)
    
    # Crear mapeo: estado_antiguo -> estado_nuevo
    for i, estado_antiguo in enumerate(orden_estados):
        mapeo[estado_antiguo] = i
    
    # Crear nuevo AFD con estados renumerados
    afd_nuevo = AFD()
    
    # Crear estados en orden
    for i in range(len(orden_estados)):
        estado_original = orden_estados[i]
        es_aceptacion = estado_original in afd.estados_aceptacion
        afd_nuevo.agregar_estado(es_aceptacion)
    
    # Copiar transiciones con nueva numeración
    for t in afd.transiciones:
        nuevo_origen = mapeo[t.origen]
        nuevo_destino = mapeo[t.destino]
        afd_nuevo.agregar_transicion(nuevo_origen, t.simbolo, nuevo_destino)
    
    # Establecer estado inicial
    nuevo_inicial = mapeo[afd.estado_inicial]
    afd_nuevo.establecer_inicial(nuevo_inicial)
    
    print(f"Estados renumerados: {[f'{old}->{new}' for old, new in mapeo.items()]}")
    
    return afd_nuevo

def comparar_afd(afd_original: AFD, afd_minimizado: AFD):
    """Compara el AFD original con el minimizado"""
    print(f"\n=== Comparación ===")
    print(f"AFD Original:")
    print(f"  - Estados: {len(afd_original.estados)}")
    print(f"  - Transiciones: {len(afd_original.transiciones)}")
    
    print(f"AFD Minimizado:")
    print(f"  - Estados: {len(afd_minimizado.estados)}")
    print(f"  - Transiciones: {len(afd_minimizado.transiciones)}")
    
    reduccion_estados = len(afd_original.estados) - len(afd_minimizado.estados)
    if len(afd_original.estados) > 0:
        porcentaje = (reduccion_estados / len(afd_original.estados)) * 100
        print(f"Reducción: {reduccion_estados} estados ({porcentaje:.1f}%)")
    else:
        print(f"Reducción: {reduccion_estados} estados")

def verificar_orden_logico(afd: AFD) -> bool:
    """Verifica si los estados están en orden lógico"""
    estados_ordenados = sorted(afd.estados.keys())
    
    # Verificar que el estado inicial sea 0
    if afd.estado_inicial != 0:
        print(f"Warning: Estado inicial {afd.estado_inicial} no es 0")
        return False
    
    # Verificar numeración consecutiva
    for i, estado in enumerate(estados_ordenados):
        if estado != i:
            print(f"Warning: Estados no son consecutivos desde 0")
            return False
    
    print("Estados en orden lógico correcto")
    return True

def probar_minimizacion():
    """Prueba el algoritmo de minimización mejorado"""
    casos_prueba = [
        "(a|b)*a",
        "a*b*", 
        "(a|b)*abb(a|b)*",
        "a+",
        "(ab)*"
    ]
    
    for caso in casos_prueba:
        print(f"\n{'='*60}")
        print(f"CASO: {caso}")
        print(f"{'='*60}")
        
        try:
            # Crear AFN -> AFD
            afn = regexp_a_afn(caso)
            afd = afn_a_afd(afn)
            afd = optimizar_nombres_estados(afd)
            
            print("AFD antes de minimización:")
            mostrar_tabla_transiciones(afd)
            
            # Minimizar
            afd_min = minimizar_afd_hopcroft(afd)
            
            print(f"\nAFD después de minimización:")
            mostrar_tabla_transiciones(afd_min)
            
            # Verificar orden
            verificar_orden_logico(afd_min)
            
            # Comparar
            comparar_afd(afd, afd_min)
            
            # Exportar archivos
            nombre_archivo = caso.replace('|', '_or_').replace('*', '_star').replace('+', '_plus').replace('(', '').replace(')', '')
            afd_min.exportar_json(f"afd_min_{nombre_archivo}.json")
            afd_min.visualizar(f"afd_min_{nombre_archivo}")
            
            print(f"\nArchivos generados:")
            print(f"- afd_min_{nombre_archivo}.json")
            print(f"- afd_min_{nombre_archivo}.png")
            
        except Exception as e:
            print(f"Error procesando caso {caso}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    probar_minimizacion()