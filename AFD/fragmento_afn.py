# AFD/utils/fragmento_afn.py

class FragmentoAFN:
    """
    Clase para representar un fragmento de AFN (Autómata Finito No Determinista)
    Útil para la construcción de Thompson
    """
    
    def __init__(self, estado_inicial=None, estado_final=None):
        """
        Inicializa un fragmento AFN
        
        Args:
            estado_inicial: Estado inicial del fragmento
            estado_final: Estado final del fragmento
        """
        self.estado_inicial = estado_inicial
        self.estado_final = estado_final
    
    def __str__(self):
        return f"FragmentoAFN(inicial: {self.estado_inicial}, final: {self.estado_final})"
    
    def __repr__(self):
        return self.__str__()