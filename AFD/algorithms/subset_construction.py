from collections import defaultdict, deque
from typing import Set
from AFD.algorithms.thompson import regexp_a_afn
from models.automata import AFD, AFN, EPSILON

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

def completar_afd(afd: AFD, mostrar_detalles: bool = True) -> AFD:
    """
    Completa un AFD agregando un estado trampa/muerto y todas las transiciones faltantes
    
    Args:
        afd: El AFD a completar
        mostrar_detalles: Si mostrar información detallada del proceso
    
    Returns:
        AFD completo con estado trampa si es necesario
    """
    
    # Verificar si ya está completo
    transiciones_existentes = {}
    for t in afd.transiciones:
        if t.origen not in transiciones_existentes:
            transiciones_existentes[t.origen] = set()
        transiciones_existentes[t.origen].add(t.simbolo)
    
    # Verificar qué transiciones faltan
    transiciones_faltantes = []
    
    for estado in afd.estados.keys():
        for simbolo in afd.alfabeto:
            if (estado not in transiciones_existentes or 
                simbolo not in transiciones_existentes[estado]):
                transiciones_faltantes.append((estado, simbolo))
    
    if not transiciones_faltantes:
        if mostrar_detalles:
            print("   ✅ AFD ya está completo (no necesita estado trampa)")
        return afd
    
    if mostrar_detalles:
        print(f"   ⚠️  Faltan {len(transiciones_faltantes)} transiciones")
        print("   🔧 Agregando estado trampa...")
    
    # Crear estado trampa/muerto (siempre NO de aceptación)
    estado_trampa = afd.agregar_estado(es_aceptacion=False)
    
    if mostrar_detalles:
        print(f"   💀 Estado trampa creado: q{estado_trampa}")
    
    # Agregar transiciones faltantes hacia el estado trampa
    for estado, simbolo in transiciones_faltantes:
        afd.agregar_transicion(estado, simbolo, estado_trampa)
        if mostrar_detalles:
            print(f"     q{estado} --{simbolo}--> q{estado_trampa}")
    
    # IMPORTANTE: El estado trampa debe tener transiciones a sí mismo 
    # para TODOS los símbolos del alfabeto (característica del estado trampa)
    for simbolo in afd.alfabeto:
        afd.agregar_transicion(estado_trampa, simbolo, estado_trampa)
        if mostrar_detalles:
            print(f"     q{estado_trampa} --{simbolo}--> q{estado_trampa} (bucle trampa)")
    
    if mostrar_detalles:
        print(f"   ✅ AFD completado con {len(afd.estados)} estados")
        print(f"      Estado trampa q{estado_trampa}: rechaza todas las cadenas que llegan a él")
    
    return afd

def es_afd_completo(afd: AFD) -> bool:
    """
    Verifica si un AFD está completo (tiene transición para cada estado y símbolo)
    """
    for estado in afd.estados.keys():
        for simbolo in afd.alfabeto:
            # Buscar si existe transición para este estado y símbolo
            encontrada = False
            for transicion in afd.transiciones:
                if transicion.origen == estado and transicion.simbolo == simbolo:
                    encontrada = True
                    break
            
            if not encontrada:
                return False
    
    return True

def mostrar_tabla_transiciones_completa(afd: AFD):
    """Muestra la tabla de transiciones completa del AFD"""
    print("\n=== Tabla de Transiciones AFD Completa ===")
    
    if not es_afd_completo(afd):
        print("⚠️ ADVERTENCIA: Este AFD no está completo!")
    
    # Crear tabla de transiciones
    tabla = defaultdict(dict)
    for transicion in afd.transiciones:
        tabla[transicion.origen][transicion.simbolo] = transicion.destino
    
    # Encabezado
    simbolos_ordenados = sorted(afd.alfabeto)
    encabezado = f"{'Estado':<10} |"
    for simbolo in simbolos_ordenados:
        encabezado += f" {simbolo:<8} |"
    print(encabezado)
    print("-" * len(encabezado))
    
    # Filas de estados
    for estado in sorted(afd.estados.keys()):
        # Marcadores para diferentes tipos de estados
        marcador = ""
        if estado == afd.estado_inicial:
            marcador += "→"
        if estado in afd.estados_aceptacion:
            marcador += "*"
        
        # Detectar estado trampa (no de aceptación y todas las transiciones van a sí mismo)
        es_trampa = (estado not in afd.estados_aceptacion and 
                    all(tabla[estado].get(s) == estado for s in simbolos_ordenados))
        if es_trampa and estado != afd.estado_inicial:
            marcador += "💀"
        
        fila = f"{marcador}q{estado:<8} |"
        
        for simbolo in simbolos_ordenados:
            destino = tabla[estado].get(simbolo, "ERROR")
            if destino != "ERROR":
                destino = f"q{destino}"
            fila += f" {destino:<8} |"
        
        print(fila)
    
    print(f"\nLeyenda:")
    print(f"→ = Estado inicial")
    print(f"* = Estado de aceptación")
    print(f"💀 = Estado trampa/muerto")
    print(f"ERROR = Transición faltante (no debería ocurrir en AFD completo)")

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

def afn_a_afd_completo(afn: AFN, completar: bool = True, mostrar_detalles: bool = True) -> AFD:
    """
    Convierte un AFN a AFD usando construcción de subconjuntos y opcionalmente lo completa
    
    Args:
        afn: El AFN a convertir
        completar: Si completar el AFD con estados trampa
        mostrar_detalles: Si mostrar información detallada del proceso
    
    Returns:
        AFD completo (con estado trampa si es necesario)
    """
    if mostrar_detalles:
        print("🔄 Iniciando conversión AFN → AFD...")
    
    # Paso 1: Conversión normal AFN → AFD
    afd = afn_a_afd(afn)
    afd = optimizar_nombres_estados(afd)
    
    if mostrar_detalles:
        print(f"✅ AFD básico creado:")
        print(f"   - Estados: {len(afd.estados)}")
        print(f"   - Transiciones: {len(afd.transiciones)}")
        print(f"   - Alfabeto: {sorted(afd.alfabeto)}")
        print(f"   - Completo: {'Sí' if es_afd_completo(afd) else 'No'}")
    
    # Mostrar tabla antes de completar
    if mostrar_detalles:
        print(f"\n📊 AFD antes de completar:")
        mostrar_tabla_transiciones(afd)
    
    # Paso 2: Completar AFD si se solicita
    if completar:
        afd = completar_afd(afd, mostrar_detalles)
        
        if mostrar_detalles:
            print(f"\n📊 AFD después de completar:")
            mostrar_tabla_transiciones_completa(afd)
            
            # Verificación final
            if es_afd_completo(afd):
                print(f"✅ Verificación: AFD está completamente definido")
            else:
                print(f"❌ ERROR: AFD aún no está completo")
    
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
    """Muestra la tabla de transiciones del AFD (puede estar incompleta)"""
    print("\n=== Tabla de Transiciones AFD ===")
    
    # Crear tabla de transiciones
    tabla = defaultdict(dict)
    for transicion in afd.transiciones:
        tabla[transicion.origen][transicion.simbolo] = transicion.destino
    
    # Encabezado
    simbolos_ordenados = sorted(afd.alfabeto)
    print(f"{'Estado':<10} | {' | '.join(f'{s:<8}' for s in simbolos_ordenados)}")
    print("-" * (12 + len(simbolos_ordenados) * 11))
    
    # Filas
    for estado in sorted(afd.estados.keys()):
        marcador = ""
        if estado in afd.estados_aceptacion:
            marcador += "*"
        if estado == afd.estado_inicial:
            marcador += "→"
        
        fila = f"{marcador}q{estado:<8} | "
        for simbolo in simbolos_ordenados:
            destino = tabla[estado].get(simbolo, "---")
            if destino != "---":
                destino = f"q{destino}"
            fila += f"{destino:<8} | "
        print(fila)
    
    print(f"\nLeyenda: → = inicial, * = aceptación, --- = transición faltante")

def probar_afd_completo():
    """Prueba la construcción de AFD completo con estados trampa"""
    casos_prueba = [
        "a|b",        # Simple alternación
        "a*",         # Kleene simple
        "(a|b)*a",    # Expresión más compleja
        "ab*c"        # Concatenación con Kleene
    ]
    
    for caso in casos_prueba:
        print(f"\n{'='*70}")
        print(f"CASO: {caso}")
        print(f"{'='*70}")
        
        # Crear AFN
        from .thompson import regexp_a_afn
        afn = regexp_a_afn(caso)
        
        print(f"AFN generado:")
        print(f"- Estados: {len(afn.estados)}")
        print(f"- Alfabeto: {sorted(afn.alfabeto)}")
        
        # Convertir a AFD completo
        print(f"\n--- Conversión AFN → AFD ---")
        afd_completo = afn_a_afd_completo(afn, completar=True)
        
        # Exportar
        nombre = caso.replace('|', '_or_').replace('*', '_star').replace('(', '').replace(')', '')
        afd_completo.exportar_json(f"afd_completo_{nombre}.json")
        afd_completo.visualizar(f"afd_completo_{nombre}")
        
        print(f"\n✅ AFD completo generado:")
        print(f"   - Estados: {len(afd_completo.estados)}")
        print(f"   - Archivo: afd_completo_{nombre}.json/png")
        print(f"   - Completo: {'Sí' if es_afd_completo(afd_completo) else 'No'}")
        
        # Probar algunas cadenas para verificar
        cadenas_test = ["", "a", "b", "aa", "ab", "ba", "bb", "abc"]
        print(f"\n🧪 Probando cadenas:")
        for cadena in cadenas_test[:6]:  # Solo primeras 6
            try:
                es_aceptada, secuencia = afd_completo.simular(cadena)
                resultado = "✅" if es_aceptada else "❌"
                estados_str = ' → '.join(f'q{e}' for e in secuencia)
                print(f"   '{cadena:>3}' → {resultado} (estados: {estados_str})")
            except Exception as e:
                print(f"   '{cadena:>3}' → ERROR: {e}")

def probar_construccion_subconjuntos():
    """Prueba la construcción de subconjuntos básica"""
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
        
        # Convertir a AFD (sin completar)
        print(f"\nConvirtiendo AFN a AFD (básico)...")
        afd = afn_a_afd(afn)
        afd = optimizar_nombres_estados(afd)
        
        print(f"\nAFD resultante:")
        print(f"- Estados: {len(afd.estados)}")
        print(f"- Estado inicial: {afd.estado_inicial}")
        print(f"- Estados de aceptación: {sorted(afd.estados_aceptacion)}")
        print(f"- Completo: {'Sí' if es_afd_completo(afd) else 'No'}")
        
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
    print("🧪 Ejecutando pruebas de construcción de subconjuntos...\n")
    probar_afd_completo()