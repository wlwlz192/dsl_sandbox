# reglex.py

import ply.lex as lex

reserved = {
    'block': 'BLOCK_KEYWORD',
    'register': 'REGISTER_KEYWORD',
    'field': 'FIELD_KEYWORD',
}

# List of token names. This is always required
tokens = [
    'PARAMETER_NAME',
    'ID',
    'NUMBER_LITERAL',
] + list(set(reserved.values()))

literals = ['{', '}']

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_PARAMETER_NAME(t):
    r'(offset)|(lsb)|(size)'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER_LITERAL(t):
    r'((\d+)(\.\d+)?)|(\.\d+)|(0x[a-fA-F0-9]+)'
    return t

def t_WHITESPACE(t):
    r'[ \t]+'
    pass

def t_error(t):
    print("Unknown token on line {}: {}".format(t.lexer.lineno, t.value[0]))
    exit(1)

lexer = lex.lex()

if __name__ == "__main__":
    import sys
    data = sys.stdin.read()
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            break
        
        print("{0.type}: {0.value}".format(tok))
