'''
Algoritmo de Hopcroft para minimizar un AFD
'''

from collections import defaultdict, deque

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

def minimizar_afd_hopcroft(afd: AFD) -> AFD:
    """
    Minimiza un AFD usando el algoritmo de Hopcroft
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
    return construir_afd_minimizado(afd, particion)

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
    porcentaje = (reduccion_estados / len(afd_original.estados)) * 100
    
    print(f"Reducción: {reduccion_estados} estados ({porcentaje:.1f}%)")

def probar_minimizacion():
    """Prueba el algoritmo de minimización"""
    casos_prueba = [
        "(a|b)*a",
        "a*b*",
        "(a|b)*abb(a|b)*"
    ]
    
    for caso in casos_prueba:
        print(f"\n{'='*60}")
        print(f"CASO: {caso}")
        print(f"{'='*60}")
        
        # Crear AFN -> AFD
        afn = regexp_a_afn(caso)
        afd = afn_a_afd(afn)
        afd = optimizar_nombres_estados(afd)
        
        print("AFD antes de minimización:")
        mostrar_tabla_transiciones(afd)
        
        # Minimizar
        afd_min = minimizar_afd_hopcroft(afd)
        afd_min = optimizar_nombres_estados(afd_min)
        
        print(f"\nAFD después de minimización:")
        mostrar_tabla_transiciones(afd_min)
        
        # Comparar
        comparar_afd(afd, afd_min)
        
        # Exportar archivos
        nombre_archivo = caso.replace('|', '_or_').replace('*', '_star').replace('(', '').replace(')', '')
        afd_min.exportar_json(f"afd_min_{nombre_archivo}.json")
        afd_min.visualizar(f"afd_min_{nombre_archivo}")
        
        print(f"\nArchivos generados:")
        print(f"- afd_min_{nombre_archivo}.json")
        print(f"- afd_min_{nombre_archivo}.png")

if __name__ == "__main__":
    probar_minimizacion()