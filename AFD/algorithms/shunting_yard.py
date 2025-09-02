''''
Algoritmo Shunting Yard para convertir expresiones regulares de infija a postfix
Regexp -> Postfix
'''
from models.automata import OPERADORES, PRECEDENCIA

def agregar_concatenacion_explicita(regexp: str) -> str:
    """
    Agrega el operador de concatenación '.' donde sea necesario
    Ejemplo: 'ab' -> 'a.b', '(a|b)c' -> '(a|b).c'
    """
    resultado = []
    for i, char in enumerate(regexp):
        resultado.append(char)
        
        # Agregar concatenación después de:
        # - Un símbolo (letra, dígito, epsilon)
        # - '*' o '+'
        # - ')'
        if i < len(regexp) - 1:
            siguiente = regexp[i + 1]
            
            # Si el carácter actual es un símbolo, *, + o )
            # Y el siguiente es un símbolo o (
            if ((char not in OPERADORES or char in ['*', '+', ')']) and
                (siguiente not in OPERADORES or siguiente == '(')):
                resultado.append('.')
    
    return ''.join(resultado)

def shunting_yard(regexp: str) -> str:
    """
    Convierte una expresión regular en notación infija a postfix
    usando el algoritmo Shunting Yard de Dijkstra
    """
    # Primero agregamos concatenación explícita
    regexp_con_concat = agregar_concatenacion_explicita(regexp)
    
    salida = []
    pila_operadores = []
    
    # Actualizar precedencias para incluir concatenación
    precedencias = {'|': 1, '.': 2, '*': 3, '+': 3}
    
    for token in regexp_con_concat:
        if token not in OPERADORES and token != '.':
            # Es un operando (símbolo del alfabeto)
            salida.append(token)
            
        elif token == '(':
            pila_operadores.append(token)
            
        elif token == ')':
            # Pop hasta encontrar '('
            while pila_operadores and pila_operadores[-1] != '(':
                salida.append(pila_operadores.pop())
            
            if pila_operadores:
                pila_operadores.pop()  # Remover '('
                
        elif token in ['|', '.', '*', '+']:
            # Manejar operadores según precedencia y asociatividad
            while (pila_operadores and 
                   pila_operadores[-1] != '(' and
                   pila_operadores[-1] in precedencias and
                   precedencias[pila_operadores[-1]] >= precedencias[token]):
                salida.append(pila_operadores.pop())
            
            pila_operadores.append(token)
    
    # Vaciar la pila
    while pila_operadores:
        salida.append(pila_operadores.pop())
    
    return ''.join(salida)

# Función de prueba
def probar_shunting_yard():
    """Pruebas del algoritmo Shunting Yard"""
    casos_prueba = [
        "a",
        "ab",
        "a|b", 
        "a*",
        "a+",
        "(a|b)*",
        "(a|b)*abb(a|b)*",
        "a(b|c)*d"
    ]
    
    print("=== Pruebas Shunting Yard ===")
    for caso in casos_prueba:
        postfix = shunting_yard(caso)
        print(f"Infija:  {caso}")
        print(f"Postfix: {postfix}")
        print()

if __name__ == "__main__":
    probar_shunting_yard()