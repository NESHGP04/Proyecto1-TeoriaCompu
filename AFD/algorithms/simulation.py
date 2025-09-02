# AFD/simulation.py
from models.automata import AFD
from thompson import regexp_a_afn
from subset_construction import afn_a_afd, optimizar_nombres_estados, mostrar_tabla_transiciones
from hopcroft import minimizar_afd_hopcroft

from typing import Set, Dict, List, Tuple
from itertools import product

def simular_afd_detallado(afd: AFD, cadena: str) -> Tuple[bool, List[Dict]]:
    """
    Simula la ejecución de una cadena en el AFD con información detallada
    Retorna si es aceptada y la secuencia completa de pasos
    """
    estado_actual = afd.estado_inicial
    pasos = []
    
    # Estado inicial
    paso_inicial = {
        'paso': 0,
        'simbolo': None,
        'estado_anterior': None,
        'estado_actual': estado_actual,
        'cadena_restante': cadena,
        'es_aceptacion': estado_actual in afd.estados_aceptacion
    }
    pasos.append(paso_inicial)
    
    # Procesar cada símbolo
    for i, simbolo in enumerate(cadena):
        # Verificar si el símbolo está en el alfabeto
        if simbolo not in afd.alfabeto:
            paso_error = {
                'paso': i + 1,
                'simbolo': simbolo,
                'estado_anterior': estado_actual,
                'estado_actual': None,
                'cadena_restante': cadena[i:],
                'error': f"Símbolo '{simbolo}' no está en el alfabeto {sorted(afd.alfabeto)}",
                'es_aceptacion': False
            }
            pasos.append(paso_error)
            return False, pasos
        
        # Buscar transición
        estado_anterior = estado_actual
        transicion_encontrada = False
        
        for transicion in afd.transiciones:
            if transicion.origen == estado_actual and transicion.simbolo == simbolo:
                estado_actual = transicion.destino
                transicion_encontrada = True
                break
        
        if not transicion_encontrada:
            paso_error = {
                'paso': i + 1,
                'simbolo': simbolo,
                'estado_anterior': estado_anterior,
                'estado_actual': None,
                'cadena_restante': cadena[i:],
                'error': f"No hay transición desde q{estado_anterior} con '{simbolo}'",
                'es_aceptacion': False
            }
            pasos.append(paso_error)
            return False, pasos
        
        # Registrar paso exitoso
        paso = {
            'paso': i + 1,
            'simbolo': simbolo,
            'estado_anterior': estado_anterior,
            'estado_actual': estado_actual,
            'cadena_restante': cadena[i+1:],
            'es_aceptacion': estado_actual in afd.estados_aceptacion
        }
        pasos.append(paso)
    
    # Verificar si el estado final es de aceptación
    es_aceptada = estado_actual in afd.estados_aceptacion
    return es_aceptada, pasos

def mostrar_simulacion(afd: AFD, cadena: str):
    """Muestra la simulación paso a paso de una cadena en el AFD"""
    print(f"\n{'='*60}")
    print(f"SIMULANDO CADENA: '{cadena}'")
    print(f"{'='*60}")
    
    es_aceptada, pasos = simular_afd_detallado(afd, cadena)
    
    # Mostrar información del AFD
    print(f"AFD:")
    print(f"  - Estado inicial: q{afd.estado_inicial}")
    print(f"  - Estados de aceptación: {{'q' + str(e) for e in sorted(afd.estados_aceptacion)}}")
    print(f"  - Alfabeto: {sorted(afd.alfabeto)}")
    
    print(f"\nSIMULACIÓN PASO A PASO:")
    print(f"{'Paso':<4} | {'Símbolo':<8} | {'Estado Ant.':<11} | {'Estado Act.':<11} | {'Restante':<15} | {'¿Aceptación?'}")
    print("-" * 85)
    
    for paso in pasos:
        paso_num = paso['paso']
        simbolo = paso['simbolo'] if paso['simbolo'] else '-'
        
        if paso.get('error'):
            estado_ant = f"q{paso['estado_anterior']}" if paso['estado_anterior'] is not None else '-'
            estado_act = 'ERROR'
            restante = paso['cadena_restante']
            aceptacion = 'NO'
            
            print(f"{paso_num:<4} | {simbolo:<8} | {estado_ant:<11} | {estado_act:<11} | '{restante}'<15 | {aceptacion}")
            print(f"\n❌ ERROR: {paso['error']}")
            break
        else:
            estado_ant = f"q{paso['estado_anterior']}" if paso['estado_anterior'] is not None else '-'
            estado_act = f"q{paso['estado_actual']}"
            restante = paso['cadena_restante']
            aceptacion = '✓' if paso['es_aceptacion'] else '✗'
            
            print(f"{paso_num:<4} | {simbolo:<8} | {estado_ant:<11} | {estado_act:<11} | '{restante}'<15 | {aceptacion}")
    
    # Resultado final
    print(f"\n{'='*60}")
    if es_aceptada:
        print(f"✅ RESULTADO: La cadena '{cadena}' ES ACEPTADA")
        print(f"   El estado final q{pasos[-1]['estado_actual']} es de aceptación.")
    else:
        if pasos[-1].get('error'):
            print(f"❌ RESULTADO: La cadena '{cadena}' NO ES ACEPTADA (Error)")
        else:
            print(f"❌ RESULTADO: La cadena '{cadena}' NO ES ACEPTADA")
            print(f"   El estado final q{pasos[-1]['estado_actual']} no es de aceptación.")
    print(f"{'='*60}")

def probar_multiple_cadenas(afd: AFD, cadenas: List[str]):
    """Prueba múltiples cadenas en el AFD"""
    print(f"\n{'='*70}")
    print(f"PRUEBA MÚLTIPLE DE CADENAS")
    print(f"{'='*70}")
    
    print(f"{'Cadena':<15} | {'Resultado':<10} | {'Estado Final'}")
    print("-" * 45)
    
    for cadena in cadenas:
        es_aceptada, pasos = simular_afd_detallado(afd, cadena)
        
        if pasos[-1].get('error'):
            resultado = "ERROR"
            estado_final = "N/A"
        else:
            resultado = "ACEPTA" if es_aceptada else "RECHAZA"
            estado_final = f"q{pasos[-1]['estado_actual']}"
        
        print(f"'{cadena}'<14 | {resultado:<10} | {estado_final}")

def interfaz_simulacion_interactiva(afd: AFD):
    """Interfaz interactiva para simular cadenas"""
    print(f"\n{'='*70}")
    print(f"SIMULADOR INTERACTIVO")
    print(f"{'='*70}")
    
    print(f"AFD cargado:")
    print(f"  - {len(afd.estados)} estados")
    print(f"  - Alfabeto: {sorted(afd.alfabeto)}")
    print(f"  - Estado inicial: q{afd.estado_inicial}")
    print(f"  - Estados de aceptación: {{'q' + str(e) for e in sorted(afd.estados_aceptacion)}}")
    
    print(f"\nIngresa cadenas para simular (escribe 'salir' para terminar):")
    
    while True:
        try:
            cadena = input("\n> Cadena: ").strip()
            
            if cadena.lower() == 'salir':
                print("¡Hasta luego!")
                break
            
            if cadena == "":
                # Cadena vacía
                print("Simulando cadena vacía (ε)...")
                mostrar_simulacion(afd, "")
            else:
                mostrar_simulacion(afd, cadena)
                
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"Error: {e}")

def generar_cadenas_prueba(alfabeto: Set[str], max_longitud: int = 4) -> List[str]:
    """Genera cadenas de prueba sistemáticamente"""
    cadenas = [""]  # Cadena vacía
    
    # Generar cadenas de diferentes longitudes
    from itertools import product
    
    for longitud in range(1, max_longitud + 1):
        for combinacion in product(alfabeto, repeat=longitud):
            cadenas.append(''.join(combinacion))
    
    return cadenas

def probar_simulacion():
    """Prueba completa de simulación"""
    casos_prueba = [
        {
            'regexp': 'a*',
            'cadenas_test': ['', 'a', 'aa', 'aaa', 'b', 'ab', 'ba']
        },
        {
            'regexp': '(a|b)*a',
            'cadenas_test': ['a', 'aa', 'ba', 'aba', 'bba', 'b', '', 'ab']
        },
        {
            'regexp': 'a+b*',
            'cadenas_test': ['a', 'ab', 'abb', 'aaa', 'aaabb', '', 'b', 'ba']
        }
    ]
    
    for caso in casos_prueba:
        regexp = caso['regexp']
        cadenas_test = caso['cadenas_test']
        
        print(f"\n{'='*80}")
        print(f"CASO: {regexp}")
        print(f"{'='*80}")
        
        # Construir AFD minimizado
        afn = regexp_a_afn(regexp)
        afd = afn_a_afd(afn)
        afd = optimizar_nombres_estados(afd)
        afd_min = minimizar_afd_hopcroft(afd)
        afd_min = optimizar_nombres_estados(afd_min)
        
        # Mostrar tabla de transiciones
        print(f"AFD Minimizado para '{regexp}':")
        mostrar_tabla_transiciones(afd_min)
        
        # Probar cadenas
        probar_multiple_cadenas(afd_min, cadenas_test)
        
        # Mostrar simulación detallada para algunas cadenas
        cadenas_detalle = cadenas_test[:3]  # Primeras 3 cadenas
        for cadena in cadenas_detalle:
            mostrar_simulacion(afd_min, cadena)

if __name__ == "__main__":
    probar_simulacion()