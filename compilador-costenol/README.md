# 🌊 Compilador Costeñol — PQEK 

> *"Un compilador caribeño "*

Compilador educativo completo para el lenguaje **Costeñol (PQEK)**, construido con Python, PLY y PyQt5. Implementa todas las fases clásicas de un compilador: análisis léxico, sintáctico, semántico, AST e interpretación, con una interfaz gráfica moderna de estética caribeña.

---

## 📁 Estructura del proyecto

```
compilador-costenol/
│
├── analizador_lexico.py       # Análisis léxico con PLY
├── analizador_sintactico.py   # Gramática + construcción del AST
├── analizador_semantico.py    # Validación semántica + tabla de símbolos
├── interprete.py              # Intérprete del AST (ejecución)
├── interfaz_compilador.py     # Interfaz gráfica PyQt5 (entrada principal)
├── requirements.txt
│
└── ejemplos/
    ├── hola_mundo.pqek
    ├── calculo_variables.pqek
    └── interactivo.pqek
```

---

## 🛠️ Instalación

### 1. Clonar o descomprimir el proyecto

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux / macOS)
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la interfaz

```bash
python interfaz_compilador.py
```

---

## 🌴 Sintaxis del lenguaje Costeñol

### Tipos de datos

| Tipo     | Descripción              |
|----------|--------------------------|
| `Entero` | Número entero (ej: `5`) |
| `Real`   | Número decimal con coma (ej: `3,14`) |
| `Texto`  | Cadena de texto         |

### Operaciones

```
// Declaración de variable
nombre Tipo;

// Asignación
nombre = expresion;

// Entrada del usuario
nombre = Captura.Tipo();

// Salida (cadena literal)
Mensaje.Texto("texto aquí");

// Salida (variable)
Mensaje.Texto(nombre);

// Operaciones aritméticas
resultado = a + b * 2;
```

### Ejemplo completo

```
nombre Texto;
edad Entero;
salario Real;

nombre = Captura.Texto();
edad = Captura.Entero();
salario = 2500000;

Mensaje.Texto("Nombre:");
Mensaje.Texto(nombre);
Mensaje.Texto("Edad:");
Mensaje.Texto(edad);
```

---

## 🔧 Componentes del compilador

### `analizador_lexico.py`
- Construido con **PLY (lex)**
- Reconoce: `ENTERO`, `REAL`, `CADENA`, `ID`, `TIPO`, `FUNCION`, operadores y puntuación
- Palabras reservadas: `Entero`, `Real`, `Texto`, `Captura`, `Mensaje`
- Errores con mensajes costeños y registro de línea/columna
- Función `reset_errores()` para limpiar estado entre compilaciones

### `analizador_sintactico.py`
- Construido con **PLY (yacc)**
- Gramática completa para declaraciones, asignaciones, lectura y escritura
- Soporte de expresiones con `Mensaje.Texto(variable)` y `Mensaje.Texto("literal")`
- Construye un **AST** con nodos: `Program`, `VarDecl`, `Assign`, `Captura`, `Mensaje`, `BinaryOp`, `Number`, `String`, `VarRef`

### `analizador_semantico.py`
- Tabla de símbolos (`dict`) con tipo y valor de cada variable
- Valida: declaraciones duplicadas, variables no declaradas, tipos incompatibles
- Compatibilidad automática `Entero ↔ Real`

### `interprete.py`
- Recorre el AST ejecutando cada instrucción
- Soporta `Captura` con entrada desde GUI o terminal
- Manejo correcto de reales con coma (12,5) ↔ punto (12.5) para operaciones
- Log de mensajes diferenciado: info, output, error

### `interfaz_compilador.py`
- Interfaz moderna con **estética caribeña** (paleta oscura turquesa/naranja)
- **Editor de código** con resaltado de sintaxis en tiempo real
- **Consola de salida** con colores por tipo de mensaje
- **Campo de entrada** para programas interactivos
- **Análisis por pasos**: Léxico → Sintáctico → Semántico
- **Compilar & Ejecutar** en un solo clic
- Visualización del **AST** tras análisis sintáctico
- Visualización de la **tabla de símbolos** tras análisis semántico
- Resaltado de líneas con error en rojo en el editor


## 📋 Requisitos

- Python 3.8+
- PLY 3.11
- PyQt5 5.15.x

---

*Proyecto académico — Compiladores — Corporación Universitaria Latinoamericana (CUL) Angie Fuentes, Daniela Heredia, Wildherman Betancourt y Alejandro Payares*
