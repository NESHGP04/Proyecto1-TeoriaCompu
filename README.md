# Proyecto1-Teoria de Computación

Este proyecto implementa un Autómata Finito Determinista (AFD) usando Python y Graphviz para la visualización.

## Requisitos

- Python 3.x
- Graphviz (sistema)
- python-graphviz (paquete de Python)

## Instalación y Configuración

### Opción 1: Instalación Global (macOS con Homebrew)

Si prefieres instalar las dependencias globalmente en tu sistema:

```bash
# Instalar Graphviz a nivel del sistema
brew install graphviz

# Instalar el paquete de Python globalmente
brew install python-graphviz
```

**Ejecutar el proyecto:**
```bash
python3 main.py
```

### Opción 2: Entorno Virtual (Recomendado)

Para mantener las dependencias aisladas y seguir buenas prácticas de desarrollo:

#### 1. Crear y activar el entorno virtual

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```

#### 2. Instalar dependencias

```bash
# Instalar Graphviz a nivel del sistema (requerido)
brew install graphviz

# Instalar el paquete de Python en el entorno virtual
pip install graphviz
```

#### 3. Ejecutar el proyecto

```bash
python3 main.py
```

#### 4. Desactivar el entorno virtual (cuando termines)

```bash
deactivate
```

## Estructura del Proyecto

```
Proyecto1-TeoriaCompu/
├── main.py
├── models/
│   ├── automata.py
│   └── init.py
├── AFD/
│   ├── algorithms/
│       ├── hopcroft.py
│       ├── shunting_yard.py
│       ├── simulation.py
│       ├── subset_contruction.py
│       └── thompson.py
│   └── tests/
│   ├── utils/
│   └── fragmento_afn.py
└── README.md
```

## Uso

### Ejecución básica

```bash
python3 main.py
```

### Trabajar con entorno virtual

Si usas entorno virtual, recuerda activarlo cada vez que trabajes en el proyecto:

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar proyecto
python3 main.py

# Desactivar cuando termines
deactivate
```

## Visualizar Autómatas

Para ver las imágenes y archivos JSON creados de los autómatas, ir a:

Proyecto1-TeoriaCompu/
├── cadena_automata.json
|__ cadena_automata.png

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'graphviz'"

**Causa:** No tienes instalado el módulo graphviz.

**Solución:**
- **Con entorno virtual:** Activa el entorno y ejecuta `pip install graphviz`
- **Sin entorno virtual:** Ejecuta `brew install python-graphviz`

### Error: "externally-managed-environment"

**Causa:** Tu sistema previene instalaciones globales de pip por seguridad.

**Soluciones:**
1. Usa un entorno virtual (recomendado)
2. Usa Homebrew: `brew install python-graphviz`
3. Instala con flag de usuario: `pip3 install --user graphviz`

### Error de visualización de gráficos

**Causa:** Graphviz no está instalado a nivel del sistema.

**Solución:**
```bash
brew install graphviz
```

## Comandos Útiles

### Gestión de entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Verificar paquetes instalados
pip list

# Desactivar entorno virtual
deactivate

# Eliminar entorno virtual
rm -rf venv
```

### Verificar instalación

```bash
# Verificar Python
python3 --version

# Verificar Graphviz (sistema)
dot -V

# Verificar graphviz (Python) - dentro del entorno si lo usas
python3 -c "import graphviz; print('Graphviz Python package is installed')"
```

## Notas

- **macOS con Homebrew:** Se recomienda usar Homebrew para instalar Graphviz a nivel del sistema
- **Entorno virtual:** Recomendado para desarrollo, especialmente si trabajas en múltiples proyectos Python
- **Primer uso:** Si es tu primera vez ejecutando el proyecto, asegúrate de tener todas las dependencias instaladas

## Contacto

Si encuentras problemas o tienes preguntas sobre el proyecto, no dudes en contactar al equipo de desarrollo.