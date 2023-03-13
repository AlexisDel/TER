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
    reactions.append(Reaction(p[1], p[3], p[5]))


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
    p[0] = [p[1]]


def p_listconc_list(p):
    """
    listconc : NUMBER unite COMMA listconc
    """
    p[0] = p[4] + [p[1]]


def p_unite_MM(p):
    """
    unite : MM
    """


def p_unite_UM(p):
    """
    unite : UM
    """


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


def findPaths(start, end, depth):
    paths = []
    for reac in reactions:
        if start in reac.substrats:
            paths += exploreNext(reac, end, depth, path=[reac])
    return paths


def exploreNext(reac, end, depth, path=[], paths=[]):
    reac.used = True

    for molecule in reac.produits:
        for enzyme in inhibitions.get(molecule, []):
            enzyme.inhibited = True

    if end in reac.produits:
        paths.append(path)
    else:
        for n in reac.next:
            if depth > 1 and not n.used and not n.enzyme.inhibited:
                exploreNext(n, end, depth - 1, path + [n], paths)
    reac.used = False
    return paths


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


def exploreNextV2(reacStart, reacEnd, depth, pathStart, pathEnd, paths=[]):
    reacStart.used = True
    reacEnd.used = True

    for molecule in reacStart.produits:
        for enzyme in inhibitions.get(molecule, []):
            enzyme.inhibited = True

    for molecule in reacEnd.substrats:
        for enzyme in inhibitions.get(molecule, []):
            enzyme.inhibited = True

    add_reac = False
    for produit in reacStart.produits:
        if produit in reacEnd.substrats:
            add_reac = True
            paths.append(pathStart + pathEnd)

    if not add_reac:
        if depth > 1:
            for next in reacStart.next:
                if not next.used and not next.enzyme.inhibited:
                    for previous in reacEnd.previous:
                        if depth > 2:
                            exploreNextV2(next, previous, depth - 2)
                        else:
                            exploreNextV2(reacStart, previous, depth - 1)
    return paths


# Main
if __name__ == "__main__":

    # build reactions list
    with open("brenda.ssa", "r") as file:
        test_yacc(file.read())

    print(len(reactions))
    print(len(inhibitions))

    print("Build next")
    s = time.time()
    buildNext()
    print("execution time :", time.time() - s)

    print("Find path")
    s = time.time()
    paths = findPaths(especes.get("NAD+"), especes.get("Acetophenone"), 3)
    print(len(set([item for items in paths for item in items])))
    print("execution time :", time.time() - s)
