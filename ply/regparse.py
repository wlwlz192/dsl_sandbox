import sys
import ply.yacc as yacc
from reglex import tokens

def p_spec(p):
    """
    spec : empty_statement
         | spec spec_statement 
    """
    if len(p) == 2:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_spec_statement(p):
    """
    spec_statement : block_statement
                   | instantiation_statement
    """
    p[0] = p[1]

def p_empty_statement(p):
    """
    empty_statement : 
    """
    pass

def p_statements(p):
    """
    statements : empty_statement
               | statements statement
    """
    if len(p) == 2:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]


def p_statement(p):
    """
    statement : block_statement
              | instantiation_statement
    """
    p[0] = p[1]

def p_block_statement(p):
    """
    block_statement : BLOCK_KEYWORD ID '{' block_contents '}'
    """
    block = {}
    block['name'] = p[2]
    block['type'] = 'block'
    
    for n in p[4]:
        if type(n) is tuple:
            block[n[0]] = n[1]
        elif type(n) is dict:
            if 'registers' not in block:
                block['registers'] = []

            block['registers'].append(n)

    p[0] = block

def p_block_contents(p):
    """
    block_contents : empty_statement
                   | block_contents block_content
    """
    if len(p) == 2:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_block_content(p):
    """
    block_content : parameter_statement
                  | register_statement
    """
    p[0] = p[1]

def p_register_statement(p):
    """
    register_statement : REGISTER_KEYWORD ID '{' register_contents '}'
    """
    register = {}
    register['name'] = p[2]
    
    for n in p[4]:
        if type(n) is tuple:
            register[n[0]] = n[1]
        elif type(n) is dict:
            if 'fields' not in register:
                register['fields'] = []

            register['fields'].append(n)

    p[0] = register
    
def p_register_contents(p):
    """
    register_contents : empty_statement
                      | register_contents register_content
    """
    if len(p) == 2:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_register_content(p):
    """
    register_content : parameter_statement
                     | field_statement
    """
    p[0] = p[1]

def p_field_statement(p):
    """
    field_statement : FIELD_KEYWORD ID '{' field_contents '}'
    """
    field = {}
    field['name'] = p[2]
    
    for n in p[4]:
        field[n[0]] = n[1]

    p[0] = field

def p_field_contents(p):
    """
    field_contents : empty_statement
                   | field_contents field_content
    """
    if len(p) == 2:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_field_content(p):
    """
    field_content : parameter_statement
    """
    p[0] = p[1]

def p_parameter_statement(p):
    """
    parameter_statement : PARAMETER_NAME NUMBER_LITERAL
    """
    p[0] = (p[1], int(p[2]))

def p_instantiation_statement(p):
    """
    instantiation_statement : ID ID
    """
    p[0] = {
        'class': p[1],
        'inst':  p[2]
    }

def p_error(p):
    line = 0 if p is None else p.lineno
    print("ERROR(line {}): syntax error".format(line))
    print(p)
    sys.exit(1)

def parse(filename=None, debug_mode=False):
    if debug_mode:
        parser = yacc.yacc()
    else:
        parser = yacc.yacc(debug=False, errorlog=yacc.NullLogger())
    
    if filename is not None:
        source = open(filename, 'r').read()
    else:
        source = sys.stdin.read()

    parse_tree = parser.parse(source)
    
    return parse_tree

if __name__ == "__main__":
    import json
    tree = parse(None, True)
    print(json.dumps(tree, indent=2))
