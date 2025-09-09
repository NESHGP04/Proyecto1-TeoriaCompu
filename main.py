"""
Proyecto 1 - Teoría de la Computación
Constructor de Autómatas Finitos - Versión Simplificada
Autor: Camila Richter 23183, Marinés García 23391 y Carlos Alburez 231311
Fecha: Septiembre 2025
"""
# Importar todos los módulos
from models.automata import AFD
from AFD.algorithms.shunting_yard import shunting_yard
from AFD.algorithms.thompson import construir_afn_thompson
from AFD.algorithms.subset_construction import afn_a_afd, afn_a_afd_completo, mostrar_tabla_transiciones, optimizar_nombres_estados, es_afd_completo
from AFD.algorithms.hopcroft import minimizar_afd_hopcroft
from AFD.algorithms.simulation import simular_afd_detallado, mostrar_simulacion

import os
import sys
from typing import Optional

def limpiar_pantalla():
    """Limpia la pantalla de la terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_banner():
    """Muestra el banner de la aplicación"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CONSTRUCTOR DE AUTÓMATAS FINITOS                          ║
║                         Teoría de la Computación                             ║
║                              Proyecto 1 - 2025                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def validar_regexp(regexp: str) -> bool:
    """Valida si una expresión regular tiene la sintaxis correcta"""
    try:
        # Caracteres permitidos
        permitidos = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789|*+()ε')
        
        # Verificar caracteres válidos
        for char in regexp:
            if char not in permitidos:
                print(f"ERROR: Carácter no permitido '{char}'")
                return False
        
        # Verificar paréntesis balanceados
        balance = 0
        for char in regexp:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
                if balance < 0:
                    print("ERROR: Paréntesis no balanceados")
                    return False
        
        if balance != 0:
            print("ERROR: Paréntesis no balanceados")
            return False
        
        # Verificar que no esté vacía
        if not regexp.strip():
            print("ERROR: Expresión regular vacía")
            return False
        
        return True
        
    except Exception as e:
        print(f"ERROR validando expresión: {e}")
        return False

def construir_automata_completo(regexp: str) -> Optional[AFD]:
    """Construye el autómata completo paso a paso"""
    print(f"\n{'='*70}")
    print(f"PROCESANDO EXPRESIÓN REGULAR: {regexp}")
    print(f"{'='*70}")
    
    try:
        # Paso 1: Shunting Yard
        print("\nPaso 1: Convertir a notación postfix (Shunting Yard)")
        postfix = shunting_yard(regexp)
        print(f"   Expresión infija:  {regexp}")
        print(f"   Expresión postfix: {postfix}")
        
        # Paso 2: Construir AFN (Thompson)
        print("\nPaso 2: Construir AFN (Algoritmo de Thompson)")
        afn = construir_afn_thompson(postfix)
        afn.establecer_inicial(0)
        
        # Encontrar y establecer estados de aceptación
        if afn.transiciones:
            max_estado = max(max(t.origen, t.destino) for t in afn.transiciones)
            afn.establecer_aceptacion(max_estado)
        
        print(f"   AFN creado con {len(afn.estados)} estados")
        print(f"   Alfabeto: {sorted(afn.alfabeto)}")
        print(f"   Estado inicial: {afn.estado_inicial}")
        print(f"   Estados de aceptación: {sorted(afn.estados_aceptacion)}")
        
        # Exportar AFN
        nombre_base = regexp.replace('|', '_or_').replace('*', '_star').replace('+', '_plus').replace('(', '').replace(')', '')
        afn.exportar_json(f"afn_{nombre_base}.json")
        afn.visualizar(f"afn_{nombre_base}")
        print(f"   Archivo AFN: afn_{nombre_base}.json")
        print(f"   Gráfico AFN: afn_{nombre_base}.png")
        
        # Paso 3: Convertir AFN a AFD COMPLETO (CON ESTADOS TRAMPA)
        print("\nPaso 3: Convertir AFN a AFD (Construcción de Subconjuntos)")
        print("   Creando AFD completo con estados trampa...")
        
        # Usar afn_a_afd_completo con completar=True
        afd = afn_a_afd_completo(afn, completar=True, mostrar_detalles=True)
        afd = optimizar_nombres_estados(afd)
        
        print(f"   AFD completo creado con {len(afd.estados)} estados")
        print(f"   Alfabeto: {sorted(afd.alfabeto)}")
        print(f"   Estado inicial: {afd.estado_inicial}")
        print(f"   Estados de aceptación: {sorted(afd.estados_aceptacion)}")
        
        # Verificar que esté completo
        if es_afd_completo(afd):
            print(f"   AFD está completo (tiene transiciones para todos los símbolos)")
        else:
            print(f"   WARNING: AFD no está completo")
        
        afd.exportar_json(f"afd_{nombre_base}.json")
        afd.visualizar(f"afd_{nombre_base}")
        print(f"   Archivo AFD: afd_{nombre_base}.json")
        print(f"   Gráfico AFD: afd_{nombre_base}.png")
        
        # Paso 4: Minimizar AFD (SIN ESTADOS TRAMPA)
        print("\nPaso 4: Minimizar AFD (Algoritmo de Hopcroft)")
        print("   Eliminando estados trampa durante minimización...")
        
        afd_min = minimizar_afd_hopcroft(afd)
        afd_min = optimizar_nombres_estados(afd_min)
        
        print(f"   AFD minimizado con {len(afd_min.estados)} estados")
        print(f"   Estado inicial: {afd_min.estado_inicial}")
        print(f"   Estados de aceptación: {sorted(afd_min.estados_aceptacion)}")
        
        reduccion = len(afd.estados) - len(afd_min.estados)
        if reduccion > 0:
            print(f"   Reducción: {reduccion} estados eliminados")
            print(f"      (Estados trampa y equivalentes removidos)")
        else:
            print(f"   No se pudo reducir más")
        
        # Verificar que el minimal NO esté completo (no debe tener estados trampa)
        if not es_afd_completo(afd_min):
            print(f"   AFD minimal es incompleto (sin estados trampa) - CORRECTO")
        else:
            print(f"   WARNING: AFD minimal está completo (podría tener estados trampa)")
        
        # Exportar AFD minimizado
        afd_min.exportar_json(f"afd_min_{nombre_base}.json")
        afd_min.visualizar(f"afd_min_{nombre_base}")
        print(f"   Archivo AFD Minimal: afd_min_{nombre_base}.json")
        print(f"   Gráfico AFD Minimal: afd_min_{nombre_base}.png")
        
        # Mostrar tabla de transiciones final
        print(f"\nTabla de transiciones del AFD minimizado:")
        mostrar_tabla_transiciones(afd_min)
        
        # Resumen de archivos generados
        print(f"\nCONSTRUCCIÓN COMPLETA")
        print(f"Archivos generados:")
        print(f"   - afn_{nombre_base}.json/png")
        print(f"   - afd_{nombre_base}.json/png (COMPLETO con estados trampa)")
        print(f"   - afd_min_{nombre_base}.json/png (MINIMAL sin estados trampa)")
        
        # Mostrar resumen de reducciones mejorado
        print(f"\nResumen de reducciones:")
        print(f"   AFN -> AFD:        {len(afn.estados)} -> {len(afd.estados)} estados (completo)")
        print(f"   AFD -> Minimal:    {len(afd.estados)} -> {len(afd_min.estados)} estados (sin trampa)")
        print(f"   Total (AFN -> Min): {len(afn.estados)} -> {len(afd_min.estados)} estados")
        
        return afd_min
        
    except Exception as e:
        print(f"\nERROR durante la construcción: {e}")
        import traceback
        traceback.print_exc()
        return None

def generar_cadenas_basicas(alfabeto, max_long=3):
    """Genera cadenas básicas de prueba"""
    cadenas = []
    
    # Cadena vacía
    cadenas.append("")
    
    # Símbolos individuales
    simbolos_sin_epsilon = sorted([s for s in alfabeto if s != 'ε'])
    for simbolo in simbolos_sin_epsilon:
        cadenas.append(simbolo)
    
    # Combinaciones de longitud 2
    if len(simbolos_sin_epsilon) >= 1:
        primer_simbolo = simbolos_sin_epsilon[0]
        cadenas.append(primer_simbolo + primer_simbolo)  # aa
        
        if len(simbolos_sin_epsilon) >= 2:
            segundo_simbolo = simbolos_sin_epsilon[1]
            cadenas.append(primer_simbolo + segundo_simbolo)  # ab
            cadenas.append(segundo_simbolo + primer_simbolo)  # ba
            cadenas.append(segundo_simbolo + segundo_simbolo)  # bb
    
    # Algunas cadenas más largas
    if len(simbolos_sin_epsilon) >= 1:
        s1 = simbolos_sin_epsilon[0]
        cadenas.append(s1 * 3)  # aaa
        
        if len(simbolos_sin_epsilon) >= 2:
            s2 = simbolos_sin_epsilon[1]
            cadenas.append(s1 + s2 + s1)  # aba
            cadenas.append(s2 + s1 + s2)  # bab
    
    return cadenas[:10]  # Limitar a 10 cadenas

def simular_cadena_con_transiciones(afd: AFD, cadena: str) -> tuple[bool, str]:
    """
    Simula una cadena mostrando todas las transiciones paso a paso
    Retorna: (es_aceptada, mensaje_resultado)
    """
    if not cadena:
        cadena_display = "ε (cadena vacía)"
    else:
        cadena_display = f"'{cadena}'"
    
    estado_actual = afd.estado_inicial
    transiciones = [f"q{estado_actual}"]
    
    # Procesar cada símbolo
    for simbolo in cadena:
        # Verificar si el símbolo está en el alfabeto
        if simbolo not in afd.alfabeto:
            error_msg = f"ERROR: Símbolo '{simbolo}' no encontrado en el alfabeto {sorted(afd.alfabeto)}"
            return False, error_msg
        
        # Buscar transición
        transicion_encontrada = False
        for t in afd.transiciones:
            if t.origen == estado_actual and t.simbolo == simbolo:
                estado_actual = t.destino
                transiciones.append(f"--{simbolo}-->")
                transiciones.append(f"q{estado_actual}")
                transicion_encontrada = True
                break
        
        if not transicion_encontrada:
            error_msg = f"ERROR: No hay transición desde q{estado_actual} con símbolo '{simbolo}'"
            return False, error_msg
    
    # Determinar si la cadena es aceptada
    es_aceptada = estado_actual in afd.estados_aceptacion
    
    # Construir mensaje de resultado
    secuencia_transiciones = " ".join(transiciones)
    estado_tipo = "ACEPTACIÓN" if es_aceptada else "NO ACEPTACIÓN"
    resultado_simbolo = "ACEPTA" if es_aceptada else "RECHAZA"
    
    mensaje = f"""   Cadena: {cadena_display}
   Transiciones: {secuencia_transiciones}
   Estado final: q{estado_actual} ({estado_tipo})
   Resultado: {resultado_simbolo}"""
    
    return es_aceptada, mensaje

def simulacion_interactiva(afd: AFD):
    """Permite al usuario probar cadenas interactivamente"""
    print(f"\n{'='*50}")
    print(f"SIMULACIÓN DE CADENAS - AFD MINIMAL")
    print(f"{'='*50}")
    print(f"AFD con {len(afd.estados)} estados")
    print(f"Alfabeto: {sorted(afd.alfabeto)}")
    print(f"Estado inicial: q{afd.estado_inicial}")
    print(f"Estados de aceptación: {[f'q{e}' for e in sorted(afd.estados_aceptacion)]}")
    
    # Simulación interactiva
    print(f"\nSimulación interactiva:")
    print(f"Ingresa cadenas para probar (Enter vacío para salir)")
    print(f"Las transiciones se mostrarán automáticamente")
    print(f"Ejemplo: 'aba', 'ab', '' (cadena vacía)")
    
    while True:
        try:
            entrada = input(f"\n> ").strip()
            
            if entrada == "":
                # Cadena vacía - usar cadena vacía literal
                cadena = ""
            elif entrada.lower() == "salir":
                print(f"Finalizando simulación...")
                break
            else:
                cadena = entrada
            
            # Simular la cadena con transiciones
            print(f"\nSimulando...")
            es_aceptada, mensaje = simular_cadena_con_transiciones(afd, cadena)
            print(mensaje)
            
        except KeyboardInterrupt:
            print(f"\n\nFinalizando simulación...")
            break
        except Exception as e:
            print(f"   ERROR inesperado: {e}")

def main():
    """Función principal simplificada"""
    try:
        # Limpiar pantalla y mostrar banner
        limpiar_pantalla()
        mostrar_banner()
        
        # Pedir expresión regular
        print(f"Conversor Regex -> AFN -> AFD -> AFD Minimal")
        print(f"=" * 70)
        
        regexp = input("\nIngresa una expresión regular: ").strip()
        
        if not regexp:
            print("No ingresaste ninguna expresión regular.")
            return
        
        # Validar expresión regular
        if not validar_regexp(regexp):
            print("Expresión regular inválida. Programa terminado.")
            return
        
        # Construir autómata completo
        afd_minimal = construir_automata_completo(regexp)
        
        if afd_minimal is None:
            print("Error construyendo autómata. Programa terminado.")
            return
        
        # Iniciar simulación interactiva
        print(f"\n" + "="*70)
        simulacion_interactiva(afd_minimal)
        
        print(f"\nPrograma completado exitosamente!")
        
    except KeyboardInterrupt:
        print(f"\n\nPrograma interrumpido por el usuario.")
    except Exception as e:
        print(f"\nERROR inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()