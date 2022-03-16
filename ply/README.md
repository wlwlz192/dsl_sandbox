This is a DSL implemented using lex & yacc. More specifically the PLY package based in Python.

example.rsl is the actual DSL content. The rest is the lexer and parser. The output is a simple register spec in JSON.

To run, the *ply* package needs to be installed first in the python environment. After that

```
cat example.rsl | python regparse.py
```
