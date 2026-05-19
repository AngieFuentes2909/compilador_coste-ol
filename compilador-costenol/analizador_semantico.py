# analizador_semantico.py
from analizador_sintactico import (
    Program, VarDecl, Assign, Captura, Mensaje,
    BinaryOp, Number, String, VarRef
)


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = {}   # {name: {"tipo": str, "valor": any}}
        self.errors  = []

    def analyze(self, node):
        self.visit(node)
        if self.errors:
            msg = "Ey llave… esa vaina está mala, revisa bien:\n"
            for e in self.errors:
                msg += f"   ➤ {e}\n"
            raise Exception(msg)

    # ─── Dispatcher ───────────────────────────────────────────────────────────

    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        self.errors.append(
            f"Nojoda, quedé mamando con el nodo '{type(node).__name__}'."
        )
        return None, None

    # ─── Visitores ────────────────────────────────────────────────────────────

    def visit_Program(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_VarDecl(self, node):
        if node.name in self.symbols:
            self.errors.append(
                f"hey mi llave, ¿pa' qué declaras '{node.name}' otra vez? ¡Ya existe!"
            )
        else:
            self.symbols[node.name] = {"tipo": node.tipo, "valor": None}

    def visit_Assign(self, node):
        if node.name not in self.symbols:
            self.errors.append(
                f"hey loco, ¿y dónde declaraste '{node.name}'? Esa vaina ni existe."
            )
            return

        tipo_var = self.symbols[node.name]["tipo"]
        val, tipo_expr = self.visit(node.expr)

        if tipo_expr is not None and not self._compatible(tipo_var, tipo_expr):
            self.errors.append(
                f"Esa vaina no sirve: no puedes meter '{tipo_expr}' "
                f"en '{node.name}' que es '{tipo_var}'."
            )
        else:
            self.symbols[node.name]["valor"] = val

    def visit_Captura(self, node):
        # El tipo vendrá en tiempo de ejecución; devolvemos el tipo esperado
        return f"<Captura:{node.tipo}>", node.tipo

    def visit_Mensaje(self, node):
        self.visit(node.expr)
        return None, None

    def visit_BinaryOp(self, node):
        _, tl = self.visit(node.left)
        _, tr = self.visit(node.right)

        if tl not in ("Entero", "Real") or tr not in ("Entero", "Real"):
            self.errors.append(
                f"Aja llave… ¿cómo vas a operar '{tl}' con '{tr}'? "
                f"¡Eso no pega ni con gota mágica!"
            )
            return None, None

        tipo = "Real" if "Real" in (tl, tr) else "Entero"
        return None, tipo

    def visit_Number(self, node):
        # node.kind ya está bien capitalizado: "Entero" | "Real"
        return node.value, node.kind

    def visit_String(self, node):
        return node.value, "Texto"

    def visit_VarRef(self, node):
        if node.name not in self.symbols:
            self.errors.append(
                f"hey loco, '{node.name}' ¿esa vaina qué es?"
            )
            return None, None

        info = self.symbols[node.name]
        return info["valor"], info["tipo"]

    # ─── Compatibilidad de tipos ──────────────────────────────────────────────

    def _compatible(self, esperado, recibido):
        if esperado == recibido:
            return True
        # Entero y Real son compatibles entre sí
        if {esperado, recibido} <= {"Entero", "Real"}:
            return True
        return False
