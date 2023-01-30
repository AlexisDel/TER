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
from utils import Espece

# HashMap
especes = dict()

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
    if t.value not in especes:
        especes[t.value] = Espece(t.value)
    t.value = especes.get(t.value)
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
    p[0] = p[1]


def p_listreac_list(p):
    """
    listreac : react listreac
    """
    p[0] = ("listreac", p[1], p[2])


def p_react(p):
    """
    react : IDENT COLON listm RARROW listm BAR listconc DASH NUMBER SEMI
    """
    p[0] = ("react", p[1], p[3], p[5], p[7])


def p_inhibition(p):
    """
    react : IDENT COLON IDENT BAR NUMBER unite SEMI
    """
    p[0] = ("inhibition", p[1], p[3], p[5])


def p_listm(p):
    """
    listm : IDENT
    """
    p[0] = p[1]


def p_listm_list(p):
    """
    listm : IDENT PLUS listm
    """
    p[0] = ("listm", p[1], p[3])


def p_listconc(p):
    """
    listconc : NUMBER unite
    """
    p[0] = p[1]


def p_listconc_list(p):
    """
    listconc : NUMBER unite COMMA listconc
    """
    p[0] = ("listconc", p[1], p[4])


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

    if verbose:
        print(r)


def display_especes():
    for name, espece in especes.items():
        print(name, ":", espece)
    print("Number of species :", len(especes))


# Main
if __name__ == "__main__":
    with open("brenda.ssa", "r") as file:
        test_yacc(file.read())
