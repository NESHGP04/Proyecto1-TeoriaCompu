from collections import defaultdict, deque

def epsilon_clausura(afn: AFN, estados: Set[int]) -> Set[int]:
    """
    Calcula la ε-clausura de un conjunto de estados
    """
    clausura = set(estados)
    pila = list(estados)
    
    while pila:
        estado_actual = pila.pop()
        
        # Buscar todas las transiciones epsilon desde este estado
        for transicion in afn.transiciones:
            if (transicion.origen == estado_actual and 
                transicion.simbolo == EPSILON and
                transicion.destino not in clausura):
                
                clausura.add(transicion.destino)
                pila.append(transicion.destino)
    
    return clausura

def mover(afn: AFN, estados: Set[int], simbolo: str) -> Set[int]:
    """
    Calcula el conjunto de estados alcanzables desde 'estados' con 'simbolo'
    """
    resultado = set()
    
    for estado in estados:
        for transicion in afn.transiciones:
            if (transicion.origen == estado and 
                transicion.simbolo == simbolo):
                resultado.add(transicion.destino)
    
    return resultado

def afn_a_afd(afn: AFN) -> AFD:
    """
    Convierte un AFN a AFD usando el algoritmo de Construcción de Subconjuntos
    """
    afd = AFD()
    
    # Conjunto inicial: ε-clausura del estado inicial del AFN
    conjunto_inicial = epsilon_clausura(afn, {afn.estado_inicial})
    
    # Mapeo de conjuntos de estados AFN -> estado AFD
    conjunto_a_estado = {}
    estados_procesados = set()
    cola = deque()
    
    # Crear estado inicial del AFD
    estado_inicial_afd = afd.agregar_estado()
    afd.establecer_inicial(estado_inicial_afd)
    conjunto_a_estado[frozenset(conjunto_inicial)] = estado_inicial_afd
    cola.append(conjunto_inicial)
    
    # Verificar si el estado inicial es de aceptación
    if conjunto_inicial.intersection(afn.estados_aceptacion):
        afd.establecer_aceptacion(estado_inicial_afd)
    
    print(f"Estado inicial AFD {estado_inicial_afd}: {conjunto_inicial}")
    
    while cola:
        conjunto_actual = cola.popleft()
        conjunto_frozen = frozenset(conjunto_actual)
        
        if conjunto_frozen in estados_procesados:
            continue
            
        estados_procesados.add(conjunto_frozen)
        estado_afd_actual = conjunto_a_estado[conjunto_frozen]
        
        # Para cada símbolo del alfabeto
        for simbolo in afn.alfabeto:
            # Calcular el conjunto destino
            conjunto_mover = mover(afn, conjunto_actual, simbolo)
            if not conjunto_mover:
                continue
                
            conjunto_destino = epsilon_clausura(afn, conjunto_mover)
            conjunto_destino_frozen = frozenset(conjunto_destino)
            
            # Si es un conjunto nuevo, crear nuevo estado
            if conjunto_destino_frozen not in conjunto_a_estado:
                nuevo_estado = afd.agregar_estado()
                conjunto_a_estado[conjunto_destino_frozen] = nuevo_estado
                
                # Verificar si es estado de aceptación
                if conjunto_destino.intersection(afn.estados_aceptacion):
                    afd.establecer_aceptacion(nuevo_estado)
                
                cola.append(conjunto_destino)
                print(f"Nuevo estado AFD {nuevo_estado}: {conjunto_destino}")
            
            # Agregar transición
            estado_destino = conjunto_a_estado[conjunto_destino_frozen]
            afd.agregar_transicion(estado_afd_actual, simbolo, estado_destino)
            
            print(f"Transición: {estado_afd_actual} --{simbolo}--> {estado_destino}")
    
    return afd

def optimizar_nombres_estados(afd: AFD) -> AFD:
    """
    Renombra los estados del AFD para que sean consecutivos desde 0
    """
    afd_optimizado = AFD()
    mapeo_estados = {}
    
    # Crear mapeo de nombres antiguos a nuevos
    estados_ordenados = sorted(afd.estados.keys())
    for i, estado_viejo in enumerate(estados_ordenados):
        mapeo_estados[estado_viejo] = i
        es_aceptacion = estado_viejo in afd.estados_aceptacion
        afd_optimizado.agregar_estado(es_aceptacion)
    
    # Establecer estado inicial
    nuevo_inicial = mapeo_estados[afd.estado_inicial]
    afd_optimizado.establecer_inicial(nuevo_inicial)
    
    # Copiar transiciones con nuevos nombres
    for transicion in afd.transiciones:
        nuevo_origen = mapeo_estados[transicion.origen]
        nuevo_destino = mapeo_estados[transicion.destino]
        afd_optimizado.agregar_transicion(nuevo_origen, transicion.simbolo, nuevo_destino)
    
    return afd_optimizado

def mostrar_tabla_transiciones(afd: AFD):
    """Muestra la tabla de transiciones del AFD"""
    print("\n=== Tabla de Transiciones AFD ===")
    
    # Crear tabla de transiciones
    tabla = defaultdict(dict)
    for transicion in afd.transiciones:
        tabla[transicion.origen][transicion.simbolo] = transicion.destino
    
    # Encabezado
    simbolos_ordenados = sorted(afd.alfabeto)
    print(f"{'Estado':<8} | {' | '.join(f'{s:<8}' for s in simbolos_ordenados)}")
    print("-" * (10 + len(simbolos_ordenados) * 11))
    
    # Filas
    for estado in sorted(afd.estados.keys()):
        marcador = "*" if estado in afd.estados_aceptacion else " "
        marcador += "→" if estado == afd.estado_inicial else " "
        
        fila = f"{marcador}q{estado:<5} | "
        for simbolo in simbolos_ordenados:
            destino = tabla[estado].get(simbolo, "-")
            if destino != "-":
                destino = f"q{destino}"
            fila += f"{destino:<8} | "
        print(fila)

def probar_construccion_subconjuntos():
    """Prueba la construcción de subconjuntos"""
    casos_prueba = [
        "a",
        "a|b",
        "(a|b)*a",
        "a*b*"
    ]
    
    for caso in casos_prueba:
        print(f"\n{'='*50}")
        print(f"CASO: {caso}")
        print(f"{'='*50}")
        
        # Crear AFN
        afn = regexp_a_afn(caso)
        print(f"\nAFN creado:")
        print(f"- Estados: {len(afn.estados)}")
        print(f"- Alfabeto: {sorted(afn.alfabeto)}")
        print(f"- Estado inicial: {afn.estado_inicial}")
        print(f"- Estados de aceptación: {sorted(afn.estados_aceptacion)}")
        
        # Convertir a AFD
        print(f"\nConvirtiendo AFN a AFD...")
        afd = afn_a_afd(afn)
        afd = optimizar_nombres_estados(afd)
        
        print(f"\nAFD resultante:")
        print(f"- Estados: {len(afd.estados)}")
        print(f"- Estado inicial: {afd.estado_inicial}")
        print(f"- Estados de aceptación: {sorted(afd.estados_aceptacion)}")
        
        # Mostrar tabla de transiciones
        mostrar_tabla_transiciones(afd)
        
        # Exportar archivos
        nombre_archivo = caso.replace('|', '_or_').replace('*', '_star').replace('(', '').replace(')', '')
        afd.exportar_json(f"afd_{nombre_archivo}.json")
        afd.visualizar(f"afd_{nombre_archivo}")
        
        print(f"\nArchivos generados:")
        print(f"- afd_{nombre_archivo}.json")
        print(f"- afd_{nombre_archivo}.png")

if __name__ == "__main__":
    probar_construccion_subconjuntos()