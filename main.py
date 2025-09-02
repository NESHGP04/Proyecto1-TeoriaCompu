"""
Proyecto 1 - Teoría de la Computación
Constructor de Autómatas Finitos
Autor: Camila Richter 23183, Marinés García 23391 y Carlos Alburez 231311
Fecha: Septiembre 2025
"""
# Importar todos los módulos
from models.automata import AFD
from AFD.algorithms.shunting_yard import shunting_yard
from AFD.algorithms.thompson import construir_afn_thompson
from AFD.algorithms.subset_construction import afn_a_afd, mostrar_tabla_transiciones, optimizar_nombres_estados
from AFD.algorithms.hopcroft import minimizar_afd_hopcroft
from AFD.algorithms.simulation import generar_cadenas_prueba, interfaz_simulacion_interactiva, probar_multiple_cadenas, simular_afd_detallado, mostrar_simulacion

import os
import sys
from typing import Optional
import argparse

# Importar todos los módulos creados
# (En un proyecto real, estos estarían en archivos separados)

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

def mostrar_menu():
    """Muestra el menú principal"""
    print("""
┌─────────────────────────── MENÚ PRINCIPAL ───────────────────────────────┐
│                                                                           │
│  1. Construir autómata desde expresión regular                           │
│  2. Simular cadenas en AFD                                              │
│  3. Mostrar información de autómata                                      │
│  4. Generar archivos de ejemplo                                         │
│  5. Modo interactivo de simulación                                      │
│  0. Salir                                                               │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
    """)

def validar_regexp(regexp: str) -> bool:
    """Valida si una expresión regular tiene la sintaxis correcta"""
    try:
        # Caracteres permitidos
        permitidos = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789|*+()ε')
        
        # Verificar caracteres válidos
        for char in regexp:
            if char not in permitidos:
                print(f"❌ Error: Carácter no permitido '{char}'")
                return False
        
        # Verificar paréntesis balanceados
        balance = 0
        for char in regexp:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
                if balance < 0:
                    print("❌ Error: Paréntesis no balanceados")
                    return False
        
        if balance != 0:
            print("❌ Error: Paréntesis no balanceados")
            return False
        
        # Verificar que no esté vacía
        if not regexp.strip():
            print("❌ Error: Expresión regular vacía")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validando expresión: {e}")
        return False

def construir_automata_completo(regexp: str) -> Optional[AFD]:
    """Construye el autómata completo paso a paso"""
    print(f"\n{'='*70}")
    print(f"CONSTRUCCIÓN DE AUTÓMATA PARA: {regexp}")
    print(f"{'='*70}")
    
    try:
        # Paso 1: Shunting Yard
        print("\n📝 Paso 1: Convertir a notación postfix (Shunting Yard)")
        postfix = shunting_yard(regexp)
        print(f"   Expresión infija:  {regexp}")
        print(f"   Expresión postfix: {postfix}")
        
        # Paso 2: Construir AFN (Thompson)
        print("\n🔨 Paso 2: Construir AFN (Algoritmo de Thompson)")
        afn = construir_afn_thompson(postfix)
        afn.establecer_inicial(0)  # Asegurar que tiene estado inicial
        
        # Encontrar y establecer estados de aceptación
        if afn.transiciones:
            # El último estado creado debería ser el de aceptación
            max_estado = max(max(t.origen, t.destino) for t in afn.transiciones)
            afn.establecer_aceptacion(max_estado)
        
        print(f"   AFN creado con {len(afn.estados)} estados")
        print(f"   Alfabeto: {sorted(afn.alfabeto)}")
        
        # Exportar AFN
        nombre_base = regexp.replace('|', '_or_').replace('*', '_star').replace('+', '_plus').replace('(', '').replace(')', '')
        afn.exportar_json(f"afn_{nombre_base}.json")
        afn.visualizar(f"afn_{nombre_base}")
        
        # Paso 3: Convertir AFN a AFD (Construcción de Subconjuntos)
        print("\n🔄 Paso 3: Convertir AFN a AFD (Construcción de Subconjuntos)")
        afd = afn_a_afd(afn)
        afd = optimizar_nombres_estados(afd)
        
        print(f"   AFD creado con {len(afd.estados)} estados")
        
        # Exportar AFD
        afd.exportar_json(f"afd_{nombre_base}.json")
        afd.visualizar(f"afd_{nombre_base}")
        
        # Paso 4: Minimizar AFD (Hopcroft)
        print("\n⚡ Paso 4: Minimizar AFD (Algoritmo de Hopcroft)")
        afd_min = minimizar_afd_hopcroft(afd)
        afd_min = optimizar_nombres_estados(afd_min)
        
        print(f"   AFD minimizado con {len(afd_min.estados)} estados")
        
        reduccion = len(afd.estados) - len(afd_min.estados)
        if reduccion > 0:
            print(f"   ✅ Reducción: {reduccion} estados eliminados")
        else:
            print(f"   ℹ️  No se pudo reducir más")
        
        # Exportar AFD minimizado
        afd_min.exportar_json(f"afd_min_{nombre_base}.json")
        afd_min.visualizar(f"afd_min_{nombre_base}")
        
        # Mostrar tabla de transiciones final
        print(f"\n📊 Tabla de transiciones del AFD minimizado:")
        mostrar_tabla_transiciones(afd_min)
        
        print(f"\n✅ CONSTRUCCIÓN COMPLETA")
        print(f"   Archivos generados:")
        print(f"   - afn_{nombre_base}.json/png")
        print(f"   - afd_{nombre_base}.json/png") 
        print(f"   - afd_min_{nombre_base}.json/png")
        
        return afd_min
        
    except Exception as e:
        print(f"\n❌ Error durante la construcción: {e}")
        import traceback
        traceback.print_exc()
        return None

def menu_simulacion(afd: AFD):
    """Menú para simulación de cadenas"""
    while True:
        print(f"\n┌─────────────────── MENÚ DE SIMULACIÓN ───────────────────┐")
        print(f"│  1. Simular una cadena específica                       │")
        print(f"│  2. Simular múltiples cadenas                           │")
        print(f"│  3. Generar cadenas de prueba automáticamente           │")
        print(f"│  4. Volver al menú principal                            │")
        print(f"└─────────────────────────────────────────────────────────┘")
        
        try:
            opcion = input("\n> Selecciona una opción: ").strip()
            
            if opcion == '1':
                cadena = input("\n> Ingresa la cadena a simular: ").strip()
                mostrar_simulacion(afd, cadena)
                
            elif opcion == '2':
                print("\n> Ingresa cadenas separadas por comas:")
                cadenas_input = input("> ").strip()
                if cadenas_input:
                    cadenas = [c.strip() for c in cadenas_input.split(',')]
                    probar_multiple_cadenas(afd, cadenas)
                else:
                    print("❌ No se ingresaron cadenas")
                    
            elif opcion == '3':
                try:
                    max_long = int(input("\n> Longitud máxima de cadenas (1-6): "))
                    if 1 <= max_long <= 6:
                        cadenas_auto = generar_cadenas_prueba(afd.alfabeto, max_long)
                        print(f"\n📝 Generando {len(cadenas_auto)} cadenas de prueba...")
                        probar_multiple_cadenas(afd, cadenas_auto[:20])  # Limitar a 20
                        if len(cadenas_auto) > 20:
                            print(f"   (Mostrando solo las primeras 20 de {len(cadenas_auto)})")
                    else:
                        print("❌ Longitud debe estar entre 1 y 6")
                except ValueError:
                    print("❌ Ingresa un número válido")
                    
            elif opcion == '4':
                break
                
            else:
                print("❌ Opción no válida")
                
        except KeyboardInterrupt:
            print("\n\nVolviendo al menú principal...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def generar_ejemplos():
    """Genera archivos de ejemplo para diferentes expresiones regulares"""
    ejemplos = [
        {
            'regexp': 'a*',
            'descripcion': 'Cero o más "a"'
        },
        {
            'regexp': '(a|b)*',
            'descripcion': 'Cualquier cadena sobre {a,b}'
        },
        {
            'regexp': '(a|b)*a',
            'descripcion': 'Cadenas que terminan en "a"'
        },
        {
            'regexp': 'a+b*',
            'descripcion': 'Una o más "a" seguidas de cero o más "b"'
        },
        {
            'regexp': '(ab)*',
            'descripcion': 'Cero o más repeticiones de "ab"'
        }
    ]
    
    print(f"\n📁 Generando ejemplos...")
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"\n{i}. {ejemplo['regexp']} - {ejemplo['descripcion']}")
        
        try:
            afd = construir_automata_completo(ejemplo['regexp'])
            if afd:
                # Probar algunas cadenas
                cadenas_test = generar_cadenas_prueba(afd.alfabeto, 3)[:10]
                print(f"   Probando cadenas: {cadenas_test}")
                
                for cadena in cadenas_test:
                    es_aceptada, _ = simular_afd_detallado(afd, cadena)
                    resultado = "✓" if es_aceptada else "✗"
                    print(f"     '{cadena}' -> {resultado}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Ejemplos generados completamente")

def mostrar_info_automata():
    """Permite cargar y mostrar información de un autómata guardado"""
    print(f"\n📄 Archivos JSON disponibles:")
    
    # Buscar archivos JSON
    archivos_json = []
    for archivo in os.listdir('.'):
        if archivo.endswith('.json') and (archivo.startswith('afd_') or archivo.startswith('afn_')):
            archivos_json.append(archivo)
    
    if not archivos_json:
        print("❌ No se encontraron archivos de autómatas")
        return
    
    for i, archivo in enumerate(archivos_json, 1):
        print(f"  {i}. {archivo}")
    
    try:
        seleccion = int(input(f"\n> Selecciona un archivo (1-{len(archivos_json)}): "))
        if 1 <= seleccion <= len(archivos_json):
            archivo_seleccionado = archivos_json[seleccion - 1]
            
            # Cargar y mostrar información
            with open(archivo_seleccionado, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
                
            print(f"\n📊 Información del autómata: {archivo_seleccionado}")
            print(f"   Estados: {len(data['ESTADOS'])}")
            print(f"   Alfabeto: {data['SIMBOLOS']}")
            print(f"   Estado inicial: {data['INICIO']}")
            print(f"   Estados de aceptación: {data['ACEPTACION']}")
            print(f"   Transiciones: {len(data['TRANSICIONES'])}")
            
            # Mostrar transiciones
            print(f"\n   Transiciones:")
            for origen, simbolo, destino in data['TRANSICIONES']:
                print(f"     q{origen} --{simbolo}--> q{destino}")
                
        else:
            print("❌ Selección inválida")
            
    except ValueError:
        print("❌ Ingresa un número válido")
    except Exception as e:
        print(f"❌ Error cargando archivo: {e}")

def main():
    """Función principal de la aplicación"""
    afd_actual = None
    
    while True:
        try:
            limpiar_pantalla()
            mostrar_banner()
            
            if afd_actual:
                print(f"📊 AFD cargado: {len(afd_actual.estados)} estados, alfabeto {sorted(afd_actual.alfabeto)}")
            
            mostrar_menu()
            opcion = input("\n> Selecciona una opción: ").strip()
            
            if opcion == '0':
                print("\n👋 ¡Hasta luego!")
                break
                
            elif opcion == '1':
                print("\n📝 CONSTRUCCIÓN DE AUTÓMATA")
                regexp = input("\n> Ingresa la expresión regular: ").strip()
                
                if validar_regexp(regexp):
                    afd_actual = construir_automata_completo(regexp)
                    if afd_actual:
                        input("\n⏸️  Presiona Enter para continuar...")
                else:
                    input("\n⏸️  Presiona Enter para continuar...")
                    
            elif opcion == '2':
                if afd_actual is None:
                    print("\n❌ Primero debes construir un autómata (opción 1)")
                    input("\n⏸️  Presiona Enter para continuar...")
                else:
                    menu_simulacion(afd_actual)
                    
            elif opcion == '3':
                mostrar_info_automata()
                input("\n⏸️  Presiona Enter para continuar...")
                
            elif opcion == '4':
                generar_ejemplos()
                input("\n⏸️  Presiona Enter para continuar...")
                
            elif opcion == '5':
                if afd_actual is None:
                    print("\n❌ Primero debes construir un autómata (opción 1)")
                    input("\n⏸️  Presiona Enter para continuar...")
                else:
                    interfaz_simulacion_interactiva(afd_actual)
                    
            else:
                print("\n❌ Opción no válida")
                input("\n⏸️  Presiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            input("\n⏸️  Presiona Enter para continuar...")

def modo_linea_comandos():
    """Modo de línea de comandos para uso automatizado"""
    parser = argparse.ArgumentParser(description='Constructor de Autómatas Finitos')
    parser.add_argument('regexp', help='Expresión regular a procesar')
    parser.add_argument('--test', nargs='*', help='Cadenas a probar separadas por espacios')
    parser.add_argument('--no-files', action='store_true', help='No generar archivos')
    parser.add_argument('--verbose', action='store_true', help='Mostrar información detallada')
    
    args = parser.parse_args()
    
    print(f"Procesando expresión regular: {args.regexp}")
    
    if not validar_regexp(args.regexp):
        sys.exit(1)
    
    try:
        # Construir autómata
        afd = construir_automata_completo(args.regexp)
        
        if afd is None:
            print("❌ Error construyendo autómata")
            sys.exit(1)
        
        # Probar cadenas si se proporcionaron
        if args.test:
            print(f"\n📝 Probando cadenas: {args.test}")
            probar_multiple_cadenas(afd, args.test)
        
        print(f"\n✅ Proceso completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo línea de comandos
        modo_linea_comandos()
    else:
        # Modo interactivo
        main()