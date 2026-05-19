# analizador_lexico.py
import ply.lex as lex

# Listas para errores léxicos (se resetean en cada análisis)
listar_errores_lexicos = []
errores_Desc = []

# Lista de tokens
tokens = [
    "CADENA",
    "REAL",
    "ENTERO",
    "TIPO",
    "FUNCION",
    "ID",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "ASSIGN",
    "PUNTO",
    "PAREN_A",
    "PAREN_C",
    "PUNTOYCOMA",
]

# Ignorar espacios y tabulaciones
t_ignore = " \t"

# Palabras reservadas
reserved = {
    "Entero": "TIPO",
    "Real":   "TIPO",
    "Texto":  "TIPO",
    "Captura": "FUNCION",
    "Mensaje": "FUNCION",
}

# Reglas simples
t_PLUS       = r"\+"
t_MINUS      = r"-"
t_TIMES      = r"\*"
t_DIVIDE     = r"/"
t_ASSIGN     = r"="
t_PUNTO      = r"\."
t_PAREN_A    = r"\("
t_PAREN_C    = r"\)"
t_PUNTOYCOMA = r";"


def t_CADENA(t):
    r'"[^"]*"'
    return t


def t_REAL(t):
    r"\d+,\d+"
    return t


def t_ENTERO(t):
    r"\d+"
    return t


def t_ID(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

def t_COMENTARIO(t):
    r'//[^\n]*'
    pass  # ignora todo lo que siga después de //


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    error_char = t.value[0]
    linea = t.lineno
    col   = find_column(t.lexer.lexdata, t.lexpos)
    mensaje = (
        f"Nojoda llave, esa vaina está mala: "
        f"el caracter '{error_char}' no va ahí "
        f"(línea {linea}, columna {col})"
    )
    listar_errores_lexicos.append((linea - 1, col, mensaje))
    errores_Desc.append(mensaje)
    t.lexer.skip(1)


def find_column(source, lexpos):
    """Calcula la columna real del token."""
    line_start = source.rfind('\n', 0, lexpos) + 1
    return (lexpos - line_start) + 1


def reset_errores():
    """Limpia los errores léxicos antes de cada análisis."""
    listar_errores_lexicos.clear()
    errores_Desc.clear()


# Crear el analizador léxico
lexer = lex.lex()
