# interfaz_compilador.py
"""
Compilador Costeñol — Interfaz gráfica 

"""

import sys
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QFileDialog, QSplitter, QLineEdit,
    QFrame, QStatusBar, QMessageBox, QSizePolicy
)
from PyQt5.QtGui import (
    QColor, QTextCharFormat, QTextCursor,
    QFont, QSyntaxHighlighter, QPalette, QIcon,
    QLinearGradient, QBrush
)
from PyQt5.QtCore import Qt, QRegExp, QSize

from analizador_lexico import lexer, listar_errores_lexicos, reset_errores
from analizador_sintactico import build_parser
from analizador_semantico import SemanticAnalyzer
from interprete import Interpreter


#  PALETA DE COLORES


C = {
    "bg_main":    "#0D1117",   #
    "bg_editor":  "#161B22",   
    "bg_console": "#0A0F16",   
    "bg_panel":   "#1C2333",   
    "accent":     "#00E5C8",   
    "accent2":    "#FF6B35",   
    "accent3":    "#F7C948",   
    "text":       "#E6EDF3",   
    "text_dim":   "#7D8590", 
    "green":      "#2EA043",   
    "red":        "#DA3633",   
    "yellow":     "#D29922",  
    "border":     "#30363D",   
    "token_kw":   "#00E5C8",   
    "token_fn":   "#FF6B35",   
    "token_str":  "#F7C948",  
    "token_num":  "#A371F7",   
    "token_cmt":  "#4A5568",  
    "btn_run":    "#00E5C8",
    "btn_hover":  "#00BFA5",
    "btn_step":   "#1C2333",
    "btn_step_h": "#2D3A4F",
}



#  RESALTADO DE SINTAXIS

class CosteñolHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        self.error_lines = set()

        # Formatos
        kw_fmt = self._fmt(C["token_kw"], bold=True)
        fn_fmt = self._fmt(C["token_fn"], italic=True)
        str_fmt = self._fmt(C["token_str"])
        num_fmt = self._fmt(C["token_num"])
        cmt_fmt = self._fmt(C["token_cmt"], italic=True)
        op_fmt  = self._fmt(C["accent2"])

        keywords = ["Entero", "Real", "Texto", "Logico",
                    "Si", "Sino", "Mientras", "Fin", "Entonces",
                    "Inicio", "Programa", "Verdadero", "Falso"]

        functions = ["Captura", "Mensaje"]

        for kw in keywords:
            self.rules.append((QRegExp(r"\b" + kw + r"\b"), kw_fmt))

        for fn in functions:
            self.rules.append((QRegExp(r"\b" + fn + r"\b"), fn_fmt))

        self.rules.append((QRegExp(r'"[^"]*"'),           str_fmt))
        self.rules.append((QRegExp(r"\b\d+([,\.]\d+)?\b"), num_fmt))
        self.rules.append((QRegExp(r"//[^\n]*"),           cmt_fmt))
        self.rules.append((QRegExp(r"[+\-*/=]"),           op_fmt))

    @staticmethod
    def _fmt(color, bold=False, italic=False):
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold:
            f.setFontWeight(QFont.Bold)
        if italic:
            f.setFontItalic(True)
        return f

    def highlightBlock(self, text):
        # Resaltar sintaxis
        for pattern, fmt in self.rules:
            expr = QRegExp(pattern)
            idx = expr.indexIn(text)
            while idx >= 0:
                length = expr.matchedLength()
                self.setFormat(idx, length, fmt)
                idx = expr.indexIn(text, idx + length)

        # Resaltar líneas con error
        line_num = self.currentBlock().blockNumber()
        if line_num in self.error_lines:
            err_fmt = QTextCharFormat()
            err_fmt.setBackground(QColor("#2D0A0A"))
            err_fmt.setUnderlineColor(QColor(C["red"]))
            err_fmt.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            self.setFormat(0, len(text), err_fmt)

    def mark_error(self, line):
        self.error_lines.add(line)
        self.rehighlight()

    def clear_errors(self):
        self.error_lines.clear()
        self.rehighlight()


# --------------------------------------------------───────────────────────────
#  BOTÓN ESTILIZADO
# --------------------------------------------------───────────────────────────

def make_btn(label, color_bg, color_hover, color_text="#0D1117",
             font_size=10, width=None, bold=True):
    btn = QPushButton(label)
    weight = "bold" if bold else "normal"
    btn.setFont(QFont("Cascadia Code, Consolas, monospace", font_size))
    btn.setCursor(Qt.PointingHandCursor)
    style = f"""
        QPushButton {{
            background-color: {color_bg};
            color: {color_text};
            border: none;
            border-radius: 6px;
            padding: 8px 14px;
            font-weight: {weight};
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{
            background-color: {color_hover};
        }}
        QPushButton:pressed {{
            background-color: {color_bg};
            padding-top: 9px;
        }}
        QPushButton:disabled {{
            background-color: #1C2333;
            color: #4A5568;
        }}
    """
    btn.setStyleSheet(style)
    if width:
        btn.setFixedWidth(width)
    return btn



#  VENTANA PRINCIPAL


class CompiladorCosteñol(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compilador Costenol — PQEK 1.0")
        self.setMinimumSize(1100, 720)
        self.resize(1200, 800)

        self.file_path   = None
        self.input_ready = False
        self.input_value = ""

        self.parser = build_parser()

        self._build_ui()
        self._apply_global_style()
        self.statusBar().showMessage("¡Listo llave! Escribe tu código o abre un archivo .pqek")

    # ─── Construcción de la UI ────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header --------------------------------------------------────────
        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(f"background-color: {C['bg_panel']}; border-bottom: 1px solid {C['border']};")

        logo = QLabel("COMPILADOR COSTEÑOL")
        logo.setFont(QFont("Cascadia Code, Consolas", 16, QFont.Bold))
        logo.setStyleSheet(f"color: {C['accent']}; letter-spacing: 2px; background: transparent; border: none;")

        subtitle = QLabel("PQEK — Lenguaje Costeño 1.0")
        subtitle.setFont(QFont("Cascadia Code, Consolas", 9))
        subtitle.setStyleSheet(f"color: {C['text_dim']}; background: transparent; border: none;")

        header_left = QVBoxLayout()
        header_left.setSpacing(2)
        header_left.addWidget(logo)
        header_left.addWidget(subtitle)

        # Botones de archivo
        self.btn_open  = make_btn("Abrir",   C["bg_panel"], C["btn_step_h"], C["accent"],   9, 130)
        self.btn_save  = make_btn("Guardar",  C["bg_panel"], C["btn_step_h"], C["accent3"],  9, 130)
        self.btn_nuevo = make_btn("Nuevo",    C["bg_panel"], C["btn_step_h"], C["text_dim"], 9, 130)

        file_btns = QHBoxLayout()
        file_btns.setSpacing(6)
        file_btns.addWidget(self.btn_nuevo)
        file_btns.addWidget(self.btn_open)
        file_btns.addWidget(self.btn_save)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.addLayout(header_left)
        header_layout.addStretch()
        header_layout.addLayout(file_btns)

        # ── Editor --------------------------------------------------────────
        editor_label = self._section_label("EDITOR DE CODIGO")

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Cascadia Code, Consolas, monospace", 12))
        self.editor.setTabStopWidth(28)
        self.editor.setLineWrapMode(QTextEdit.NoWrap)
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {C['bg_editor']};
                color: {C['text']};
                border: 1px solid {C['border']};
                border-radius: 6px;
                padding: 10px;
                selection-background-color: #1F3A5F;
            }}
            QScrollBar:vertical {{
                background: {C['bg_main']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {C['border']};
                border-radius: 4px;
            }}
        """)
        self.editor.setPlaceholderText(
            "// Escribe tu código Costeñol aquí, llave...\n"
            "// Ejemplo:\n"
            "// nombre Texto;\n"
            "// nombre = Captura.Texto();\n"
            "// Mensaje.Texto(nombre);\n"
        )
        self.highlighter = CosteñolHighlighter(self.editor.document())

        editor_col = QVBoxLayout()
        editor_col.setSpacing(6)
        editor_col.addWidget(editor_label)
        editor_col.addWidget(self.editor)

        # ── Consola --------------------------------------------------───────
        console_label = self._section_label("CONSOLA DE SALIDA")

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Cascadia Code, Consolas, monospace", 11))
        self.output_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {C['bg_console']};
                color: {C['text']};
                border: 1px solid {C['border']};
                border-radius: 6px;
                padding: 10px;
            }}
            QScrollBar:vertical {{
                background: {C['bg_main']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {C['border']};
                border-radius: 4px;
            }}
        """)

        # Input de usuario
        input_label = QLabel("Entrada del usuario:")
        input_label.setFont(QFont("Cascadia Code, Consolas", 8))
        input_label.setStyleSheet(f"color: {C['text_dim']}; margin-top: 4px;")

        self.input_line = QLineEdit()
        self.input_line.setFont(QFont("Cascadia Code, Consolas, monospace", 11))
        self.input_line.setPlaceholderText("Ingresa aquí cuando el programa lo pida…")
        self.input_line.setStyleSheet(f"""
            QLineEdit {{
                background-color: {C['bg_panel']};
                color: {C['accent']};
                border: 1px solid {C['accent']};
                border-radius: 5px;
                padding: 7px 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {C['accent2']};
            }}
        """)
        self.input_line.setEnabled(False)
        self.input_line.returnPressed.connect(self._handle_input)

        console_col = QVBoxLayout()
        console_col.setSpacing(4)
        console_col.addWidget(console_label)
        console_col.addWidget(self.output_area)
        console_col.addWidget(input_label)
        console_col.addWidget(self.input_line)

        # ── Splitter editor/consola ──────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #30363D; width: 2px; }")

        editor_w = QWidget()
        editor_w.setLayout(editor_col)
        console_w = QWidget()
        console_w.setLayout(console_col)

        splitter.addWidget(editor_w)
        splitter.addWidget(console_w)
        splitter.setSizes([600, 500])

        # ── Barra de acciones ────────────────────────────────────────────────
        actions_bar = QWidget()
        actions_bar.setFixedHeight(60)
        actions_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {C['bg_panel']};
                border-top: 1px solid {C['border']};
            }}
        """)

        # Botones de análisis por paso
        self.btn_lex = make_btn(
            "Analisis Lexico", C["btn_step"], C["btn_step_h"],
            C["accent3"], 9, bold=False
        )
        self.btn_sin = make_btn(
            "Analisis Sintactico", C["btn_step"], C["btn_step_h"],
            C["accent3"], 9, bold=False
        )
        self.btn_sem = make_btn(
            "Analisis Semantico", C["btn_step"], C["btn_step_h"],
            C["accent3"], 9, bold=False
        )

        # Botón principal
        self.btn_run = make_btn(
            "COMPILAR & EJECUTAR", C["accent"], C["btn_hover"],
            "#0D1117", 11, bold=True
        )
        self.btn_run.setFixedWidth(220)
        self.btn_run.setFixedHeight(42)

        # Limpiar
        self.btn_clear = make_btn(
            "Limpiar", C["bg_main"], "#2D0A0A",
            C["red"], 9, bold=False
        )

        steps_layout = QHBoxLayout()
        steps_layout.setSpacing(8)
        for b in [self.btn_lex, self.btn_sin, self.btn_sem]:
            b.setFixedHeight(38)
            steps_layout.addWidget(b)

        steps_layout.addStretch()
        self.btn_clear.setFixedHeight(38)
        steps_layout.addWidget(self.btn_clear)

        actions_layout = QHBoxLayout(actions_bar)
        actions_layout.setContentsMargins(16, 10, 16, 10)
        actions_layout.addLayout(steps_layout)
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_run)

        # ── Layout raíz --------------------------------------------------───
        root_layout = QVBoxLayout()
        root_layout.setSpacing(0)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(header)
        root_layout.addWidget(splitter)
        root_layout.addWidget(actions_bar)

        container = QWidget()
        container.setLayout(root_layout)
        self.setCentralWidget(container)

        # ── Conexiones --------------------------------------------------─────
        self.btn_open.clicked.connect(self._open_file)
        self.btn_save.clicked.connect(self._save_file)
        self.btn_nuevo.clicked.connect(self._new_file)
        self.btn_lex.clicked.connect(self._run_lexico)
        self.btn_sin.clicked.connect(self._run_sintactico)
        self.btn_sem.clicked.connect(self._run_semantico)
        self.btn_run.clicked.connect(self._run_all)
        self.btn_clear.clicked.connect(self._clear)

        # Status bar
        self.status = QStatusBar()
        self.status.setStyleSheet(f"""
            QStatusBar {{
                background-color: {C['bg_panel']};
                color: {C['text_dim']};
                font-size: 9px;
                border-top: 1px solid {C['border']};
            }}
        """)
        self.setStatusBar(self.status)

    # ─── Estilo global --------------------------------------------------──────

    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {C['bg_main']};
            }}
            QSplitter {{
                background-color: {C['bg_main']};
            }}
            QLabel {{
                color: {C['text']};
                background: transparent;
            }}
            QMessageBox {{
                background-color: {C['bg_panel']};
                color: {C['text']};
            }}
        """)

    @staticmethod
    def _section_label(text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Cascadia Code, Consolas", 8, QFont.Bold))
        lbl.setStyleSheet(f"color: {C['text_dim']}; letter-spacing: 1px; margin-bottom: 2px;")
        return lbl

    # ─── Archivos --------------------------------------------------───────────

    def _new_file(self):
        if self.editor.toPlainText():
            r = QMessageBox.question(
                self, "Nuevo archivo",
                "¿Descartar los cambios actuales, llave?",
                QMessageBox.Yes | QMessageBox.No
            )
            if r != QMessageBox.Yes:
                return
        self.editor.clear()
        self.output_area.clear()
        self.file_path = None
        self.setWindowTitle("Compilador Costenol — Nuevo archivo")
        self.status.showMessage("Nuevo archivo creado.")

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo", "",
            "Archivos Costeñol (*.pqek *.costenol *.txt);;Todos (*)"
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setText(f.read())
            self.file_path = path
            self.setWindowTitle(f"Compilador Costenol — {os.path.basename(path)}")
            self.status.showMessage(f"Archivo abierto: {path}")
            self.print_message(f"Archivo cargado: {os.path.basename(path)}", "info")

    def _save_file(self):
        if not self.file_path:
            path, _ = QFileDialog.getSaveFileName(
                self, "Guardar archivo", "",
                "Archivos Costeñol (*.pqek);;Todos (*)"
            )
            if not path:
                return
            self.file_path = path

        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())
        self.setWindowTitle(f"Compilador Costenol — {os.path.basename(self.file_path)}")
        self.status.showMessage(f"Guardado: {self.file_path}")
        self.print_message(f"Archivo guardado: {os.path.basename(self.file_path)}", "success")

    # ─── Análisis por pasos --------------------------------------------------─

    def _get_code(self):
        code = self.editor.toPlainText().strip()
        if not code:
            self.print_message("hey loco, ¿qué voy a analizar si no hay nada?", "warning")
        return code

    def _run_lexico(self):
        code = self._get_code()
        if not code:
            return
        self._clear_output()
        self.print_message("─" * 50, "dim")
        self.print_message("🔍  ANÁLISIS LÉXICO", "header")
        self.print_message("─" * 50, "dim")

        reset_errores()
        lexer.lineno = 1
        lexer.input(code)

        tokens_encontrados = []
        try:
            while True:
                tok = lexer.token()
                if not tok:
                    break
                tokens_encontrados.append(tok)
                self.print_message(
                    f"  TOKEN  {tok.type:<14}  →  '{tok.value}'   "
                    f"[línea {tok.lineno}]",
                    "token"
                )
        except Exception as e:
            self.print_message(f"ERROR: Error inesperado: {e}", "error")
            return

        if listar_errores_lexicos:
            self.print_message("", "info")
            for (linea, col, msg) in listar_errores_lexicos:
                self.print_message(f"ERROR: {msg}", "error")
                self.highlighter.mark_error(linea)
            self.status.showMessage(f"Análisis léxico: {len(listar_errores_lexicos)} error(es).")
        else:
            self.print_message("", "info")
            self.print_message(
                f"Analisis lexico OK — {len(tokens_encontrados)} token(s) encontrados.", "success"
            )
            self.status.showMessage("Análisis léxico completado sin errores.")

    def _run_sintactico(self):
        code = self._get_code()
        if not code:
            return
        self._clear_output()
        self.print_message("─" * 50, "dim")
        self.print_message("🌳  ANÁLISIS SINTÁCTICO", "header")
        self.print_message("─" * 50, "dim")
        try:
            reset_errores()
            lexer.lineno = 1
            ast = self.parser.parse(code, lexer=lexer)
            if ast:
                self.print_message("Estructura sintactica correcta.", "success")
                self._print_ast(ast)
            self.status.showMessage("Análisis sintáctico completado sin errores.")
            return ast
        except SyntaxError as e:
            self.print_message(f"ERROR: {e}", "error")
            self.status.showMessage("Error sintáctico detectado.")
        except Exception as e:
            self.print_message(f"ERROR: {e}", "error")
            self.status.showMessage("Error sintáctico detectado.")

    def _run_semantico(self):
        code = self._get_code()
        if not code:
            return
        self._clear_output()
        self.print_message("─" * 50, "dim")
        self.print_message("🧠  ANÁLISIS SEMÁNTICO", "header")
        self.print_message("─" * 50, "dim")
        try:
            reset_errores()
            lexer.lineno = 1
            ast = self.parser.parse(code, lexer=lexer)
            sem = SemanticAnalyzer()
            sem.analyze(ast)
            self.print_message("Analisis semantico correcto.", "success")
            self.print_message("", "info")
            self.print_message("TABLA DE SIMBOLOS:", "header")
            for name, info in sem.symbols.items():
                val = info["valor"] if info["valor"] is not None else "<sin valor>"
                self.print_message(
                    f"    {name:<16} tipo={info['tipo']:<10}  valor={val}", "token"
                )
            self.status.showMessage("Análisis semántico completado sin errores.")
        except Exception as e:
            self.print_message(f"ERROR: {str(e)}", "error")
            self.status.showMessage("Error semántico detectado.")

    def _run_all(self):
        code = self._get_code()
        if not code:
            return
        self._clear_output()

        self.print_message("═" * 50, "dim")
        self.print_message("COMPILAR & EJECUTAR — Compilador Costeñol", "header")
        self.print_message("═" * 50, "dim")

        # ── Léxico
        self.print_message("\nAnalisis lexico…", "info")
        reset_errores()
        lexer.lineno = 1
        lexer.input(code)
        try:
            while lexer.token():
                pass
        except Exception as e:
            self.print_message(f"ERROR: Error léxico: {e}", "error")
            return

        if listar_errores_lexicos:
            for (linea, col, msg) in listar_errores_lexicos:
                self.print_message(f"   ERROR: {msg}", "error")
                self.highlighter.mark_error(linea)
            self.status.showMessage("Errores léxicos encontrados. Corrígelos primero.")
            return
        self.print_message("   OK", "success")

        # ── Sintáctico
        self.print_message("\nAnalisis sintactico…", "info")
        try:
            reset_errores()
            lexer.lineno = 1
            ast = self.parser.parse(code, lexer=lexer)
            self.print_message("   OK", "success")
        except Exception as e:
            self.print_message(f"   ERROR: {e}", "error")
            self.status.showMessage("Error sintáctico.")
            return

        # ── Semántico
        self.print_message("\nAnalisis semantico…", "info")
        try:
            sem = SemanticAnalyzer()
            sem.analyze(ast)
            self.print_message("   OK", "success")
        except Exception as e:
            self.print_message(f"   ERROR: {e}", "error")
            self.status.showMessage("Error semántico.")
            return

        # ── Ejecución
        self.print_message("\nEjecutando programa…", "info")
        self.print_message("─" * 50, "dim")
        try:
            interp = Interpreter(gui=self)
            interp.run(ast)
            self.print_message("─" * 50, "dim")
            self.print_message("Ejecucion finalizada exitosamente.", "success")
            self.status.showMessage("Ejecución completada sin errores.")
        except Exception as e:
            self.print_message(f"ERROR: Error en ejecución: {e}", "error")
            self.status.showMessage("Error durante la ejecución.")

    # ─── Impresión de mensajes en consola ────────────────────────────────────

    COLORS = {
        "info":    "#E6EDF3",
        "success": "#2EA043",
        "error":   "#DA3633",
        "warning": "#D29922",
        "token":   "#A371F7",
        "header":  "#00E5C8",
        "output":  "#F7C948",
        "dim":     "#4A5568",
    }

    def print_message(self, text, kind="info"):
        color = self.COLORS.get(kind, self.COLORS["info"])
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if kind == "header":
            fmt.setFontWeight(QFont.Bold)

        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.setCharFormat(fmt)
        cursor.insertText(text + "\n")
        self.output_area.setTextCursor(cursor)
        self.output_area.moveCursor(QTextCursor.End)
        QApplication.processEvents()

    # ─── Limpiar --------------------------------------------------───────────

    def _clear_output(self):
        self.output_area.clear()
        self.highlighter.clear_errors()

    def _clear(self):
        self.editor.clear()
        self._clear_output()
        self.status.showMessage("Todo limpio, llave. Escribe de nuevo.")

    # ─── Input del usuario --------------------------------------------------─

    def _handle_input(self):
        self.input_value = self.input_line.text()
        self.input_line.clear()
        self.input_ready = True

    # ─── Visualización del AST ───────────────────────────────────────────────

    def _print_ast(self, node, indent=0):
        cls = node.__class__.__name__
        prefix = "    " * indent + ("└─ " if indent > 0 else "")
        if cls == "Program":
            self.print_message(f"{prefix}Program ({len(node.stmts)} instrucciones)", "dim")
            for s in node.stmts:
                self._print_ast(s, indent + 1)
        elif cls == "VarDecl":
            self.print_message(f"{prefix}VarDecl: {node.name} : {node.tipo}", "dim")
        elif cls == "Assign":
            self.print_message(f"{prefix}Assign: {node.name} =", "dim")
            self._print_ast(node.expr, indent + 2)
        elif cls == "Mensaje":
            self.print_message(f"{prefix}Mensaje:", "dim")
            self._print_ast(node.expr, indent + 2)
        elif cls == "Captura":
            self.print_message(f"{prefix}Captura({node.tipo})", "dim")
        elif cls == "BinaryOp":
            self.print_message(f"{prefix}BinaryOp: {node.op}", "dim")
            self._print_ast(node.left,  indent + 2)
            self._print_ast(node.right, indent + 2)
        elif cls == "Number":
            self.print_message(f"{prefix}Number({node.kind}): {node.value}", "dim")
        elif cls == "String":
            self.print_message(f'{prefix}String: "{node.value}"', "dim")
        elif cls == "VarRef":
            self.print_message(f"{prefix}VarRef: {node.name}", "dim")


# --------------------------------------------------───────────────────────────
#  PUNTO DE ENTRADA
# --------------------------------------------------───────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Paleta base oscura
    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(C["bg_main"]))
    palette.setColor(QPalette.WindowText,      QColor(C["text"]))
    palette.setColor(QPalette.Base,            QColor(C["bg_editor"]))
    palette.setColor(QPalette.AlternateBase,   QColor(C["bg_panel"]))
    palette.setColor(QPalette.ToolTipBase,     QColor(C["bg_panel"]))
    palette.setColor(QPalette.ToolTipText,     QColor(C["text"]))
    palette.setColor(QPalette.Text,            QColor(C["text"]))
    palette.setColor(QPalette.Button,          QColor(C["bg_panel"]))
    palette.setColor(QPalette.ButtonText,      QColor(C["text"]))
    palette.setColor(QPalette.BrightText,      QColor(C["accent"]))
    palette.setColor(QPalette.Link,            QColor(C["accent"]))
    palette.setColor(QPalette.Highlight,       QColor(C["accent"]))
    palette.setColor(QPalette.HighlightedText, QColor(C["bg_main"]))
    app.setPalette(palette)

    window = CompiladorCosteñol()
    window.show()
    sys.exit(app.exec_())
