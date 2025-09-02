### Estructura Base del Proyecto - Clases y Tipos de Datos ###
from typing import Set, Dict, List, Tuple, Optional
import json
from collections import defaultdict, deque
from graphviz import Digraph

class Estado:
    """Representa un estado en el autómata"""
    def __init__(self, id: int, es_aceptacion: bool = False):
        self.id = id
        self.es_aceptacion = es_aceptacion
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, Estado) and self.id == other.id
    
    def __repr__(self):
        return f"q{self.id}{'*' if self.es_aceptacion else ''}"

class Transicion:
    """Representa una transición en el autómata"""
    def __init__(self, origen: int, simbolo: str, destino: int):
        self.origen = origen
        self.simbolo = simbolo  # 'ε' para epsilon
        self.destino = destino
    
    def __repr__(self):
        return f"({self.origen}, {self.simbolo}, {self.destino})"

class Automata:
    """Clase base para AFN y AFD"""
    def __init__(self):
        self.estados: Dict[int, Estado] = {}
        self.alfabeto: Set[str] = set()
        self.transiciones: List[Transicion] = []
        self.estado_inicial: int = 0
        self.estados_aceptacion: Set[int] = set()
        self.contador_estados = 0
    
    def agregar_estado(self, es_aceptacion: bool = False) -> int:
        """Agrega un nuevo estado y retorna su ID"""
        id_estado = self.contador_estados
        self.estados[id_estado] = Estado(id_estado, es_aceptacion)
        if es_aceptacion:
            self.estados_aceptacion.add(id_estado)
        self.contador_estados += 1
        return id_estado
    
    def agregar_transicion(self, origen: int, simbolo: str, destino: int):
        """Agrega una transición"""
        self.transiciones.append(Transicion(origen, simbolo, destino))
        if simbolo != 'ε':  # epsilon no va en el alfabeto
            self.alfabeto.add(simbolo)
    
    def establecer_inicial(self, estado: int):
        """Establece el estado inicial"""
        self.estado_inicial = estado
    
    def establecer_aceptacion(self, estado: int):
        """Marca un estado como de aceptación"""
        if estado in self.estados:
            self.estados[estado].es_aceptacion = True
            self.estados_aceptacion.add(estado)
    
    def exportar_json(self, nombre_archivo: str):
        """Exporta el autómata a formato JSON"""
        automata_dict = {
            "ESTADOS": list(self.estados.keys()),
            "SIMBOLOS": sorted(list(self.alfabeto)),
            "INICIO": self.estado_inicial,
            "ACEPTACION": sorted(list(self.estados_aceptacion)),
            "TRANSICIONES": [(t.origen, t.simbolo, t.destino) for t in self.transiciones]
        }
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(automata_dict, f, indent=2, ensure_ascii=False)
    
    def visualizar(self, nombre_archivo: str = "automata"):
        """Genera visualización con Graphviz"""
        dot = Digraph(comment='Autómata')
        dot.attr(rankdir='LR')
        
        # Estados
        for id_estado, estado in self.estados.items():
            if estado.es_aceptacion:
                dot.node(str(id_estado), f'q{id_estado}', shape='doublecircle')
            else:
                dot.node(str(id_estado), f'q{id_estado}', shape='circle')
        
        # Estado inicial
        dot.node('start', '', shape='point')
        dot.edge('start', str(self.estado_inicial))
        
        # Transiciones
        for transicion in self.transiciones:
            dot.edge(str(transicion.origen), str(transicion.destino), 
                    label=transicion.simbolo)
        
        dot.render(nombre_archivo, format='png', cleanup=True)
        return f"{nombre_archivo}.png"

class AFN(Automata):
    """Autómata Finito No Determinista"""
    pass

class AFD(Automata):
    """Autómata Finito Determinista"""
    
    def simular(self, cadena: str) -> Tuple[bool, List[int]]:
        """Simula la ejecución de una cadena y retorna si es aceptada y la secuencia de estados"""
        estado_actual = self.estado_inicial
        secuencia_estados = [estado_actual]
        
        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                return False, secuencia_estados
            
            # Buscar transición
            transicion_encontrada = False
            for t in self.transiciones:
                if t.origen == estado_actual and t.simbolo == simbolo:
                    estado_actual = t.destino
                    secuencia_estados.append(estado_actual)
                    transicion_encontrada = True
                    break
            
            if not transicion_encontrada:
                return False, secuencia_estados
        
        es_aceptada = estado_actual in self.estados_aceptacion
        return es_aceptada, secuencia_estados

# Constantes
EPSILON = 'ε'  # Símbolo para epsilon
OPERADORES = {'|', '*', '+', '(', ')'}
PRECEDENCIA = {'|': 1, '+': 2, '*': 2, '(': 0}
