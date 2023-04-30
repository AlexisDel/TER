# -----------------------------------------------------------------------------
#
# Grammaire :
#
#   listreac   : reac
#              | reac listreac
#
#   react      : IDENT COLON listm RARROW listm BAR listconc DASH NUMBER SEMI
#              | IDENT COLON IDENT BAR NUMBER unite
#
#   listm      : IDENT
#              | IDENT PLUS listm
#
#   listconc   : NUMBER unite
#              | NUMBER unite COMMA listconc
#
#   unite      : MM
#              | UM
#
# -----------------------------------------------------------------------------

from ply.lex import lex
from ply.yacc import yacc
from utils import Espece, Reaction, Inhibition

from collections import defaultdict
import time

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QTextEdit,
)
from functools import partial

# HashMap
especes = dict()
reactions = []
inhibitions = defaultdict(list)

# --- Tokenizer

# All tokens must be named in advance.
tokens = (
    "IDENT",
    "NUMBER",
    "COLON",
    "RARROW",
    "BAR",
    "DASH",
    "SEMI",
    "PLUS",
    "COMMA",
    "MM",
    "UM",
)

# Ignored characters
t_ignore = " \t"

# Token matching rules are written as regexs
t_COLON = r":"
t_RARROW = r"->"
t_BAR = r"\|"
t_DASH = r"-"
t_SEMI = r";"
t_PLUS = r"\+"
t_COMMA = r","
t_MM = r"mM"
t_UM = r"uM"


# A function can be used if there is an associated action.
# Write the matching regex in the docstring.
def t_NUMBER(t):
    r"[0-9]+\.?[0-9]*e?[\-\+]?[0-9]*"
    t.value = float(t.value)
    if t.value == int(t.value):
        t.value = int(t.value)
    return t


def t_IDENT(t):
    r"\"(.*?)\" "
    name = t.value[1:-1]
    if name not in especes:
        especes[name] = Espece(name)
    t.value = especes.get(name)
    return t


# Ignored token with an action associated with it
def t_ignore_newline(t):
    r"\n+"
    t.lexer.lineno += t.value.count("\n")


def t_ignore_comments(t):
    r"\/\/.*"


# Error handler for illegal characters
def t_error(t):
    print(f"Illegal character {t.value[0]!r}, , line {t.lineno!r}:{t.lexpos}")
    t.lexer.skip(1)


# --- Parser


def p_listreac(p):
    """
    listreac : react
    """


def p_listreac_list(p):
    """
    listreac : react listreac
    """


def p_react(p):
    """
    react : IDENT COLON listm RARROW listm BAR listconc DASH NUMBER SEMI
    """
    reactions.append(Reaction(p[1], p[3], p[5], p[7], p[9]))


def p_inhibition(p):
    """
    react : IDENT COLON IDENT BAR NUMBER unite SEMI
    """
    inhibitions[p[3]].append(p[1])


def p_listm(p):
    """
    listm : IDENT
    """
    p[0] = [p[1]]


def p_listm_list(p):
    """
    listm : IDENT PLUS listm
    """
    p[0] = p[3] + [p[1]]


def p_listconc(p):
    """
    listconc : NUMBER unite
    """
    p[0] = [str(p[1]) + " " + p[2]]


def p_listconc_list(p):
    """
    listconc : NUMBER unite COMMA listconc
    """
    p[0] = p[4] + [str(p[1]) + " " + p[2]]


def p_unite_MM(p):
    """
    unite : MM
    """
    p[0] = "mM"


def p_unite_UM(p):
    """
    unite : UM
    """
    p[0] = "uM"


def p_error(p):
    print(f"Syntax error at {p.value!r}, line {p.lineno!r}:{p.lexpos}")
    exit()


# -------------------- TEST ---------------------


def test_lex(data):

    # Build the lexer object
    lexer = lex()

    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print("LexToken(", tok.type, ",", tok.value, ",", type(tok.value), ")")


def test_yacc(data, verbose=False):

    lexer = lex()

    # Build the parser
    parser = yacc()

    # Parse an expression
    r = parser.parse(data)

    return r


def display_especes():
    for name, espece in especes.items():
        print(name, ":", espece)
    print("Number of species :", len(especes))


# _____________________ Functions __________________


def buildNext():
    for reac in reactions:
        for produit in reac.produits:
            for nextReac in reactions:
                if produit in nextReac.substrats:
                    reac.next.append(nextReac)
                    nextReac.previous.append(reac)


def findPathsV2(start, end, depth):
    paths = []
    for reacStart in reactions:
        if start in reacStart.substrats:
            for reacEnd in reactions:
                if end in reacEnd.produits:
                    paths += exploreNextV2(
                        reacStart,
                        reacEnd,
                        depth,
                        pathStart=[reacStart],
                        pathEnd=[reacEnd],
                    )
    return paths


def exploreNextV2(reacStart, reacEnd, depth, pathStart, pathEnd, paths=None):
    if paths is None:
        paths = []
    reacStart.used = True
    reacEnd.used = True

    for molecule in reacStart.produits:
        for enzyme in inhibitions.get(molecule, []):
            enzyme.inhibited = True

    for molecule in reacEnd.substrats:
        for enzyme in inhibitions.get(molecule, []):
            enzyme.inhibited = True

    for produit in reacStart.produits:
        if produit in reacEnd.substrats:
            paths.append(pathStart + pathEnd[::-1])

    if depth > 2:
        for next in reacStart.next:
            if not next.used and not next.enzyme.inhibited:
                for previous in reacEnd.previous:
                    if not previous.used and not previous.enzyme.inhibited:
                        if depth > 3:
                            exploreNextV2(
                                next,
                                previous,
                                depth - 2,
                                pathStart + [next],
                                pathEnd + [previous],
                                paths=paths
                            )
                        else:
                            exploreNextV2(
                                reacStart,
                                previous,
                                depth - 1,
                                pathStart,
                                pathEnd + [previous],
                                paths=paths
                            )

    for molecule in reacStart.produits:
        for enzyme in inhibitions.get(molecule, []):
            enzyme.inhibited = False

    for molecule in reacEnd.substrats:
        for enzyme in inhibitions.get(molecule, []):
            enzyme.inhibited = False

    reacStart.used = False
    reacEnd.used = False
    return paths


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Find Path"
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # create labels
        substrate_label = QLabel("Substrate:", self)
        substrate_label.move(20, 20)
        product_label = QLabel("Product:", self)
        product_label.move(20, 50)
        # create labels for path length specification
        path_length_label = QLabel("Path Length:", self)
        path_length_label.move(20, 80)

        # create input boxes
        self.substrate_input = QLineEdit(self)
        self.substrate_input.move(100, 20)
        self.product_input = QLineEdit(self)
        self.product_input.move(100, 50)
        self.path_length_input = QLineEdit(self)
        self.path_length_input.move(100, 80)

        # create button
        button = QPushButton("Find Reactions", self)
        button.setToolTip(
            "Click to find the path between the substrate and the product"
        )
        button.move(100, 120)
        button.clicked.connect(partial(self.display_path))

        # create output textbox
        path_label = QLabel("Reactions:", self)
        path_label.move(20, 140)
        self.output_textbox = QTextEdit(self)
        self.output_textbox.setReadOnly(True)
        self.output_textbox.setGeometry(20, 150, 360, 80)  # reduce height

        # create input box for path length output
        self.number_reactions = QLabel("Number of reactions:", self)
        self.number_reactions.move(20, 280)

        # create input box for path length output
        self.execution_time = QLabel("Execution time:", self)
        self.execution_time.move(20, 280)

        # set layout
        layout = QVBoxLayout(self)
        layout.addWidget(substrate_label)
        layout.addWidget(self.substrate_input)
        layout.addWidget(product_label)
        layout.addWidget(self.product_input)
        layout.addWidget(path_length_label)
        layout.addWidget(self.path_length_input)
        layout.addWidget(button)
        layout.addWidget(path_label)
        layout.addWidget(self.output_textbox)
        layout.addWidget(self.number_reactions)
        layout.addWidget(self.execution_time)
        self.setLayout(layout)

    def display_path(self):
        substrate = self.substrate_input.text()
        if substrate == "":
            self.output_textbox.setText("Please input a substrate")
            return

        product = self.product_input.text()
        if product == "":
            self.output_textbox.setText("Please input a product")
            return

        path_depth = self.path_length_input.text()
        if path_depth == "":
            self.output_textbox.setText("Please input a maximum depth")
            return

        try:
            path_depth = int(path_depth)
        except:
            self.output_textbox.setText(
                "Please input a integer value for the depth")
            return

        s = time.time()
        paths = findPathsV2(especes.get(substrate),
                            especes.get(product), path_depth)
        e = time.time()
        print(len(paths))
        reactions = set([item for sublist in paths for item in sublist])
        reactions_string = "\n".join(map(str, reactions))
        self.output_textbox.setText(reactions_string)
        self.number_reactions.setText(
            "Number of reactions: " + str(len(reactions)))
        self.execution_time.setText(
            "Execution time: " + "{:.4f}".format(e - s) + "s")

        # Write results in a file
        filename = "d" + str(path_depth) + "-" + \
            substrate + "-" + product + ".ssa"
        f = open(filename, "w")
        f.write("// Reactions\n\n")
        f.write(reactions_string)
        f.close()


# Main
if __name__ == "__main__":

    # build reactions list
    with open("brenda.ssa", "r") as file:
        test_yacc(file.read())

    buildNext()

    # create the QGuiApplication instance
    app = QApplication(sys.argv)

    # create and show the main window
    window = App()
    window.show()

    # access the font of the QGuiApplication instance
    font = app.font()

    # start the event loop
    sys.exit(app.exec_())
