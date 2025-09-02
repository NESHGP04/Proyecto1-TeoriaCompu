class FragmentoAFN:
    """
    Representa un fragmento de AFN con estado inicial y final
    Usado en la construcción de Thompson
    """
    def __init__(self, afn: AFN, inicial: int, final: int):
        self.afn = afn
        self.inicial = inicial
        self.final = final

def construir_afn_thompson(postfix: str) -> AFN:
    """
    Construye un AFN a partir de una expresión regular en postfix
    usando el algoritmo de Thompson
    """
    pila = []
    
    for simbolo in postfix:
        if simbolo not in ['.', '|', '*', '+']:
            # Símbolo básico
            fragment = crear_fragmento_basico(simbolo)
            pila.append(fragment)
            
        elif simbolo == '.':
            # Concatenación
            if len(pila) >= 2:
                frag2 = pila.pop()
                frag1 = pila.pop()
                fragment = concatenar_fragmentos(frag1, frag2)
                pila.append(fragment)
                
        elif simbolo == '|':
            # Unión
            if len(pila) >= 2:
                frag2 = pila.pop()
                frag1 = pila.pop()
                fragment = unir_fragmentos(frag1, frag2)
                pila.append(fragment)
                
        elif simbolo == '*':
            # Clausura de Kleene
            if len(pila) >= 1:
                frag = pila.pop()
                fragment = clausura_kleene(frag)
                pila.append(fragment)
                
        elif simbolo == '+':
            # Clausura positiva (a+ = aa*)
            if len(pila) >= 1:
                frag = pila.pop()
                fragment = clausura_positiva(frag)
                pila.append(fragment)
    
    if pila:
        fragmento_final = pila[0]
        # Marcar el estado final como de aceptación
        fragmento_final.afn.establecer_aceptacion(fragmento_final.final)
        fragmento_final.afn.establecer_inicial(fragmento_final.inicial)
        return fragmento_final.afn
    
    # AFN vacío
    return AFN()

def crear_fragmento_basico(simbolo: str) -> FragmentoAFN:
    """Crea un fragmento AFN para un símbolo básico"""
    afn = AFN()
    inicial = afn.agregar_estado()
    final = afn.agregar_estado()
    
    afn.agregar_transicion(inicial, simbolo, final)
    
    return FragmentoAFN(afn, inicial, final)

def concatenar_fragmentos(frag1: FragmentoAFN, frag2: FragmentoAFN) -> FragmentoAFN:
    """Concatena dos fragmentos AFN"""
    # Combinar los AFN
    afn_resultado = combinar_afn(frag1.afn, frag2.afn)
    
    # Conectar el estado final de frag1 con el inicial de frag2 usando epsilon
    offset = len(frag1.afn.estados)
    afn_resultado.agregar_transicion(frag1.final, EPSILON, frag2.inicial + offset)
    
    return FragmentoAFN(afn_resultado, frag1.inicial, frag2.final + offset)

def unir_fragmentos(frag1: FragmentoAFN, frag2: FragmentoAFN) -> FragmentoAFN:
    """Une dos fragmentos AFN con el operador |"""
    afn_resultado = AFN()
    
    # Nuevo estado inicial
    nuevo_inicial = afn_resultado.agregar_estado()
    
    # Combinar fragmentos con offset
    offset1 = 1  # Offset para frag1
    offset2 = offset1 + len(frag1.afn.estados)  # Offset para frag2
    
    # Copiar estados y transiciones de frag1
    copiar_fragmento(afn_resultado, frag1.afn, offset1)
    
    # Copiar estados y transiciones de frag2
    copiar_fragmento(afn_resultado, frag2.afn, offset2)
    
    # Nuevo estado final
    nuevo_final = afn_resultado.agregar_estado()
    
    # Conectar nuevo inicial con los iniciales de los fragmentos
    afn_resultado.agregar_transicion(nuevo_inicial, EPSILON, frag1.inicial + offset1)
    afn_resultado.agregar_transicion(nuevo_inicial, EPSILON, frag2.inicial + offset2)
    
    # Conectar los finales con el nuevo final
    afn_resultado.agregar_transicion(frag1.final + offset1, EPSILON, nuevo_final)
    afn_resultado.agregar_transicion(frag2.final + offset2, EPSILON, nuevo_final)
    
    return FragmentoAFN(afn_resultado, nuevo_inicial, nuevo_final)

def clausura_kleene(frag: FragmentoAFN) -> FragmentoAFN:
    """Aplica clausura de Kleene (a*)"""
    afn_resultado = AFN()
    
    # Nuevo estado inicial/final
    nuevo_inicial = afn_resultado.agregar_estado()
    nuevo_final = afn_resultado.agregar_estado()
    
    # Copiar el fragmento original
    offset = 1
    copiar_fragmento(afn_resultado, frag.afn, offset)
    
    # Conexiones para a*:
    # 1. Inicial -> Final (cadena vacía)
    afn_resultado.agregar_transicion(nuevo_inicial, EPSILON, nuevo_final)
    
    # 2. Inicial -> Inicial del fragmento
    afn_resultado.agregar_transicion(nuevo_inicial, EPSILON, frag.inicial + offset)
    
    # 3. Final del fragmento -> Final nuevo
    afn_resultado.agregar_transicion(frag.final + offset, EPSILON, nuevo_final)
    
    # 4. Final del fragmento -> Inicial del fragmento (bucle)
    afn_resultado.agregar_transicion(frag.final + offset, EPSILON, frag.inicial + offset)
    
    return FragmentoAFN(afn_resultado, nuevo_inicial, nuevo_final)

def clausura_positiva(frag: FragmentoAFN) -> FragmentoAFN:
    """Aplica clausura positiva (a+ = aa*)"""
    afn_resultado = AFN()
    
    # Nuevo estado final
    nuevo_final = afn_resultado.agregar_estado()
    
    # Copiar el fragmento original
    offset = 1
    copiar_fragmento(afn_resultado, frag.afn, offset)
    
    # Conexiones para a+:
    # 1. Final del fragmento -> Final nuevo
    afn_resultado.agregar_transicion(frag.final + offset, EPSILON, nuevo_final)
    
    # 2. Final del fragmento -> Inicial del fragmento (bucle)
    afn_resultado.agregar_transicion(frag.final + offset, EPSILON, frag.inicial + offset)
    
    return FragmentoAFN(afn_resultado, frag.inicial + offset, nuevo_final)

def copiar_fragmento(afn_destino: AFN, afn_origen: AFN, offset: int):
    """Copia estados y transiciones de un AFN a otro con offset"""
    # Crear estados con offset
    for _ in range(len(afn_origen.estados)):
        afn_destino.agregar_estado()
    
    # Copiar transiciones con offset
    for t in afn_origen.transiciones:
        afn_destino.agregar_transicion(t.origen + offset, t.simbolo, t.destino + offset)

def combinar_afn(afn1: AFN, afn2: AFN) -> AFN:
    """Combina dos AFN en uno solo"""
    afn_resultado = AFN()
    
    # Copiar primer AFN
    copiar_fragmento(afn_resultado, afn1, 0)
    
    # Copiar segundo AFN con offset
    offset = len(afn1.estados)
    copiar_fragmento(afn_resultado, afn2, offset)
    
    return afn_resultado

def regexp_a_afn(regexp: str) -> AFN:
    """Función principal: convierte regexp a AFN"""
    print(f"Convirtiendo regexp: {regexp}")
    
    # Paso 1: Convertir a postfix
    postfix = shunting_yard(regexp)
    print(f"Postfix: {postfix}")
    
    # Paso 2: Construir AFN con Thompson
    afn = construir_afn_thompson(postfix)
    
    return afn

# Función de prueba
def probar_thompson():
    """Prueba el algoritmo de Thompson"""
    casos_prueba = [
        "a",
        "a|b",
        "a*",
        "(a|b)*",
        "ab"
    ]
    
    for caso in casos_prueba:
        print(f"\n=== Caso: {caso} ===")
        afn = regexp_a_afn(caso)
        
        # Exportar a JSON
        afn.exportar_json(f"afn_{caso.replace('|', '_or_').replace('*', '_star').replace('(', '').replace(')', '')}.json")
        
        # Visualizar
        afn.visualizar(f"afn_{caso.replace('|', '_or_').replace('*', '_star').replace('(', '').replace(')', '')}")
        
        print(f"AFN creado con {len(afn.estados)} estados")
        print(f"Alfabeto: {afn.alfabeto}")
        print(f"Estados de aceptación: {afn.estados_aceptacion}")

if __name__ == "__main__":
    # Primero necesitamos importar las funciones anteriores
    probar_thompson()