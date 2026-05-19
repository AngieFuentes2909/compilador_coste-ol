# analizador_sintactico.py
import ply.yacc as yacc
from analizador_lexico import tokens, lexer


# ─────────────────────────────────────────────
#  NODOS DEL AST
# ─────────────────────────────────────────────

class Node:
    pass


class Program(Node):
    def __init__(self, stmts):
        self.stmts = stmts


class VarDecl(Node):
    def __init__(self, name, tipo):
        self.name = name
        self.tipo = tipo


class Assign(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


class Captura(Node):
    """Lectura de usuario: nombre = Captura.Tipo()"""
    def __init__(self, tipo):
        self.tipo = tipo


class Mensaje(Node):
    """Escritura: Mensaje.Texto(expr)"""
    def __init__(self, expr):
        self.expr = expr        # puede ser String, VarRef, BinaryOp, Number


class BinaryOp(Node):
    def __init__(self, op, left, right):
        self.op    = op
        self.left  = left
        self.right = right


class Number(Node):
    def __init__(self, value, kind):
        self.value = value
        self.kind  = kind      # "Entero" | "Real"


class String(Node):
    def __init__(self, value):
        self.value = value


class VarRef(Node):
    def __init__(self, name):
        self.name = name


# ─────────────────────────────────────────────
#  PRECEDENCIA
# ─────────────────────────────────────────────

precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
)

start = "program"


# ─────────────────────────────────────────────
#  PRODUCCIONES
# ─────────────────────────────────────────────

def p_program(p):
    "program : stmt_list"
    p[0] = Program(p[1])


def p_stmt_list_multi(p):
    "stmt_list : stmt_list statement"
    p[0] = p[1] + [p[2]]


def p_stmt_list_single(p):
    "stmt_list : statement"
    p[0] = [p[1]]


def p_statement(p):
    """statement : declaracion PUNTOYCOMA
                 | asignacion PUNTOYCOMA
                 | lectura PUNTOYCOMA
                 | escritura PUNTOYCOMA"""
    p[0] = p[1]


# DECLARACIÓN: nombre Tipo;
def p_declaracion(p):
    "declaracion : ID TIPO"
    p[0] = VarDecl(p[1], p[2])


# ASIGNACIÓN: nombre = expresion;
def p_asignacion(p):
    "asignacion : ID ASSIGN expresion"
    p[0] = Assign(p[1], p[3])


# LECTURA: nombre = Captura.Tipo();
def p_lectura(p):
    "lectura : ID ASSIGN FUNCION PUNTO TIPO PAREN_A PAREN_C"
    p[0] = Assign(p[1], Captura(p[5]))


# ESCRITURA con cadena literal: Mensaje.Texto("…");
def p_escritura_cadena(p):
    "escritura : FUNCION PUNTO TIPO PAREN_A CADENA PAREN_C"
    txt = p[5][1:-1]          # quitar comillas
    p[0] = Mensaje(String(txt))


# ESCRITURA con variable / expresión: Mensaje.Texto(nombre);
def p_escritura_expr(p):
    "escritura : FUNCION PUNTO TIPO PAREN_A expresion PAREN_C"
    p[0] = Mensaje(p[5])


# EXPRESIONES
def p_expresion_binaria(p):
    """expresion : expresion PLUS  expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion"""
    p[0] = BinaryOp(p[2], p[1], p[3])


def p_expresion_paren(p):
    "expresion : PAREN_A expresion PAREN_C"
    p[0] = p[2]


def p_expresion_numero(p):
    """expresion : ENTERO
                 | REAL"""
    raw = p[1]
    if "," in raw:
        p[0] = Number(raw, "Real")
    else:
        p[0] = Number(int(raw), "Entero")


def p_expresion_cadena(p):
    "expresion : CADENA"
    p[0] = String(p[1][1:-1])


def p_expresion_id(p):
    "expresion : ID"
    p[0] = VarRef(p[1])


# ERROR SINTÁCTICO
def p_error(p):
    if p:
        raise SyntaxError(
            f"Aja llave… ¿y esa vaina qué? "
            f"'{p.value}' (tipo={p.type}) no va ahí, revise la línea {p.lineno}."
        )
    else:
        raise SyntaxError("Nojoda, como que te faltó algo por ahí al final del código.")


def build_parser(debug=False):
    return yacc.yacc(debug=debug)
