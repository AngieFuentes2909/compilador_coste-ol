# interprete.py
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QTextCursor


class Interpreter:
    def __init__(self, gui=None):
        self.memory     = {}    # {name: value}
        self.output_log = []
        self.gui        = gui

    # ─── Ejecución de nodos ───────────────────────────────────────────────────

    def run(self, node):
        cls = node.__class__.__name__
        try:
            if cls == "Program":
                for stmt in node.stmts:
                    self.run(stmt)

            elif cls == "VarDecl":
                self.memory[node.name] = None
                self.log(f"📦 Variable declarada: {node.name} ({node.tipo})", "info")

            elif cls == "Assign":
                value = self.eval(node.expr)
                self.memory[node.name] = value
                self.log(f"✏️  {node.name} = {value}", "info")

            elif cls == "Mensaje":
                value = self.eval(node.expr)
                self.log(str(value), "output")

            else:
                raise RuntimeError(f"No puedo ejecutar nodo de tipo '{cls}'.")

        except Exception as e:
            self.log(f"💥 Error en ejecución ({cls}): {e}", "error")
            raise

    # ─── Evaluación de expresiones ────────────────────────────────────────────

    def eval(self, node):
        cls = node.__class__.__name__

        if cls == "BinaryOp":
            left  = self._as_number(self.eval(node.left))
            right = self._as_number(self.eval(node.right))
            if node.op == "+":
                result = left + right
            elif node.op == "-":
                result = left - right
            elif node.op == "*":
                result = left * right
            elif node.op == "/":
                if right == 0:
                    raise ZeroDivisionError("Nojoda llave, no se puede dividir entre cero.")
                result = left / right
            else:
                raise ValueError(f"Operador '{node.op}' inválido.")

            # Devolver entero si no hay decimales, o real con coma
            if isinstance(result, float) and result == int(result):
                return int(result)
            if isinstance(result, float):
                return self._to_comma(result)
            return result

        elif cls == "Number":
            return node.value

        elif cls == "String":
            return node.value

        elif cls == "VarRef":
            if node.name not in self.memory:
                raise NameError(f"Variable '{node.name}' no existe.")
            val = self.memory[node.name]
            if val is None:
                raise ValueError(f"La variable '{node.name}' aún no tiene valor asignado.")
            return val

        elif cls == "Captura":
            return self._leer_input(node.tipo)

        else:
            raise RuntimeError(f"No hay eval para el nodo '{cls}'.")

    # ─── Entrada del usuario ──────────────────────────────────────────────────

    def _leer_input(self, tipo):
        if self.gui:
            self.log(f"⌨️  Ingresa un valor de tipo {tipo} y presiona Enter:", "info")

            # Mostrar prompt en área de salida
            cursor = self.gui.output_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(">> ")
            self.gui.output_area.setTextCursor(cursor)

            # Esperar input del usuario
            self.gui.input_ready = False
            self.gui.input_line.setEnabled(True)
            self.gui.input_line.setFocus()

            while not self.gui.input_ready:
                QApplication.processEvents()

            value = self.gui.input_value
            self.gui.input_line.setEnabled(False)

            # Echar en consola lo ingresado
            cursor = self.gui.output_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(value + "\n")
            self.gui.output_area.setTextCursor(cursor)

            return value
        else:
            return input(f"Ingresa {tipo}: ")

    # ─── Conversión numérica ──────────────────────────────────────────────────

    def _as_number(self, value):
        """Convierte '12,5' → 12.5 o '7' → 7 para operar."""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            if "," in value:
                return float(value.replace(",", "."))
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    pass
        raise TypeError(
            f"No se puede operar con el valor '{value}' de tipo {type(value).__name__}."
        )

    def _to_comma(self, num):
        """Convierte 12.5 → '12,5'."""
        return str(num).replace(".", ",")

    # ─── Log de mensajes ──────────────────────────────────────────────────────

    def log(self, text, kind="info"):
        self.output_log.append(text)
        if self.gui:
            self.gui.print_message(text, kind)
        else:
            print(text)
