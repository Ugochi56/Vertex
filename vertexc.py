#!/usr/bin/env python3
"""
vertexc.py - Minimal Vertex compiler (Vertex -> Python)

Supported Vertex constructs (MVP):
- let <name> [: <type>] = <expr>
- print <expr>
- expressions: numbers, strings, identifiers, + - * /, parentheses
- optional type annotations are parsed but ignored by this MVP (reserved for later semantic checks)
- no semicolons; newline-separated statements

Limitations:
- No functions, no classes, no async in MVP
- No sophisticated error recovery
- Generated Python aims to be readable and simple
"""

import re
import sys
import os
from typing import List, Tuple, Any, Optional

# -------------------------
# Lexer
# -------------------------
TOKEN_SPEC = [
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('STRING',   r'"([^"\\]|\\.)*"'),
    ('LET',      r'\blet\b'),
    ('CONST',    r'\bconst\b'),
    ('PRINT',    r'\bprint\b'),
    ('ID',       r'[A-Za-z_]\w*'),
    ('ASSIGN',   r'='),
    ('COLON',    r':'),
    ('PLUS',     r'\+'),
    ('MINUS',    r'-'),
    ('MULT',     r'\*'),
    ('DIV',      r'/'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('NEWLINE',  r'\n'),
    ('SKIP',     r'[ \t\r]+'),
    ('MISMATCH', r'.'),
]
TOK_REGEX = '|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_SPEC)
_tok_re = re.compile(TOK_REGEX, re.M)

class Token:
    def __init__(self, type_, value, pos):
        self.type = type_
        self.value = value
        self.pos = pos
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def tokenize(code: str) -> List[Token]:
    tokens = []
    for m in _tok_re.finditer(code):
        kind = m.lastgroup
        val = m.group()
        pos = m.start()
        if kind == 'SKIP' or kind == 'NEWLINE':
            if kind == 'NEWLINE':
                tokens.append(Token('NEWLINE', val, pos))
            continue
        if kind == 'MISMATCH':
            raise SyntaxError(f"Unexpected character {val!r} at {pos}")
        tokens.append(Token(kind, val, pos))
    # Append EOF token
    tokens.append(Token('EOF', '', len(code)))
    return tokens

# -------------------------
# Simple AST node representations (tuples for brevity)
# Statement nodes:
#   ('let', name, type_or_none, expr_node)
#   ('print', expr_node)
# Expression nodes:
#   ('number', float)
#   ('string', str)
#   ('var', name)
#   ('binop', op_token, left_node, right_node)
# -------------------------

# -------------------------
# Parser (recursive descent)
# -------------------------
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def cur(self) -> Token:
        return self.tokens[self.pos]

    def eat(self, *expected) -> Token:
        tok = self.cur()
        if expected and tok.type not in expected:
            raise SyntaxError(f"Expected {' or '.join(expected)}, got {tok.type} ('{tok.value}') at pos {tok.pos}")
        self.pos += 1
        return tok

    def at(self, ttype: str) -> bool:
        return self.cur().type == ttype

    def parse(self) -> List[Any]:
        stmts = []
        while not self.at('EOF'):
            # skip optional NEWLINEs
            while self.at('NEWLINE'):
                self.eat('NEWLINE')
            if self.at('EOF'):
                break
            stmts.append(self.parse_statement())
            # require newline or EOF after top-level statement
            if self.at('NEWLINE'):
                self.eat('NEWLINE')
            elif not self.at('EOF'):
                # allow EOF, else force newline for readability
                # but be lenient: if next token starts a statement keyword, allow it
                pass
        return stmts

    def parse_statement(self):
        if self.at('LET'):
            return self.parse_let()
        if self.at('PRINT'):
            return self.parse_print()
        tok = self.cur()
        raise SyntaxError(f"Unexpected token {tok.type} ('{tok.value}') at pos {tok.pos}")

    def parse_let(self):
        self.eat('LET')
        name_tok = self.eat('ID')
        var_name = name_tok.value
        var_type = None
        if self.at('COLON'):
            self.eat('COLON')
            type_tok = self.eat('ID')
            var_type = type_tok.value
        # assignment
        self.eat('ASSIGN')
        expr = self.parse_expression()
        return ('let', var_name, var_type, expr)

    def parse_print(self):
        self.eat('PRINT')
        expr = self.parse_expression()
        return ('print', expr)

    # expression parsing with precedence
    def parse_expression(self):
        return self.parse_addsub()

    def parse_addsub(self):
        node = self.parse_muldiv()
        while self.at('PLUS') or self.at('MINUS'):
            op = self.eat('PLUS', 'MINUS').type
            right = self.parse_muldiv()
            node = ('binop', op, node, right)
        return node

    def parse_muldiv(self):
        node = self.parse_unary()
        while self.at('MULT') or self.at('DIV'):
            op = self.eat('MULT', 'DIV').type
            right = self.parse_unary()
            node = ('binop', op, node, right)
        return node

    def parse_unary(self):
        if self.at('PLUS') or self.at('MINUS'):
            op = self.eat('PLUS', 'MINUS').type
            node = self.parse_unary()
            # treat unary as binop with 0 on left for simplicity
            zero = ('number', 0.0)
            return ('binop', op, zero, node)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.cur()
        if tok.type == 'NUMBER':
            self.eat('NUMBER')
            return ('number', float(tok.value))
        if tok.type == 'STRING':
            # remove surrounding quotes and unescape simple escapes
            s = tok.value[1:-1]
            s = s.replace(r'\"', '"').replace(r'\\', '\\')
            self.eat('STRING')
            return ('string', s)
        if tok.type == 'ID':
            self.eat('ID')
            return ('var', tok.value)
        if tok.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_expression()
            self.eat('RPAREN')
            return node
        raise SyntaxError(f"Unexpected token {tok.type} ('{tok.value}') at pos {tok.pos}")

# -------------------------
# Helper: detect whether an expression AST contains a string literal
# (directly or nested inside binary ops). Used to decide when to coerce.
# -------------------------
def expr_contains_string(node) -> bool:
    if not isinstance(node, tuple):
        return False
    t = node[0]
    if t == 'string':
        return True
    if t == 'binop':
        _, _op, left, right = node
        return expr_contains_string(left) or expr_contains_string(right)
    return False

# -------------------------
# Code generation (Vertex AST -> Python source)
# -------------------------
def codegen_expr(node) -> str:
    t = node[0]
    if t == 'number':
        v = node[1]
        # print integers as integers when possible
        if int(v) == v:
            return str(int(v))
        return repr(v)
    if t == 'string':
        return repr(node[1])
    if t == 'var':
        return node[1]
    if t == 'binop':
        _, op, left, right = node
        op_map = {'PLUS': '+', 'MINUS': '-', 'MULT': '*', 'DIV': '/'}
        pyop = op_map.get(op, op)

        # Special handling for '+' when concatenating strings:
        # If either side contains a string literal (directly or nested),
        # coerce the other side to str(...) to avoid Python TypeError.
        if op == 'PLUS':
            left_is_stry = expr_contains_string(left)
            right_is_stry = expr_contains_string(right)
            left_code = codegen_expr(left)
            right_code = codegen_expr(right)

            if left_is_stry or right_is_stry:
                # If left side is not string-producing, wrap with str(...)
                if not left_is_stry:
                    left_code = f"str({left_code})"
                # If right side is not string-producing, wrap with str(...)
                if not right_is_stry:
                    right_code = f"str({right_code})"
                return f"(({left_code}) + ({right_code}))"

        # Default numeric / arithmetic behavior
        return f"({codegen_expr(left)} {pyop} {codegen_expr(right)})"

    raise RuntimeError(f"Unknown expr node: {node}")

def codegen_stmt(stmt) -> str:
    t = stmt[0]
    if t == 'let':
        _, name, var_type, expr = stmt
        # we ignore var_type in this MVP; you can add runtime checks later
        return f"{name} = {codegen_expr(expr)}"
    if t == 'print':
        _, expr = stmt
        return f"print({codegen_expr(expr)})"
    raise RuntimeError(f"Unknown stmt node: {stmt}")

def compile_to_python(ast: List[Any], module_name: str = None) -> str:
    lines = []
    lines.append("# Generated by vertexc.py - Vertex -> Python (MVP)")
    lines.append("import sys")
    lines.append("") 
    for s in ast:
        lines.append(codegen_stmt(s))
    lines.append("") 
    return "\n".join(lines)

# -------------------------
# CLI
# -------------------------
def main(argv):
    if len(argv) < 2:
        print("Usage: python vertexc.py input.vx [-o out.py]")
        return 1
    infile = argv[1]
    outfile = None
    if '-o' in argv:
        i = argv.index('-o')
        if i+1 < len(argv):
            outfile = argv[i+1]
    if not outfile:
        # default: replace .vx with _gen.py
        base = os.path.splitext(os.path.basename(infile))[0]
        outfile = base + "_gen.py"

    code = open(infile, 'r', encoding='utf8').read()
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()

    py_src = compile_to_python(ast, module_name=None)

    # write output
    os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)
    with open(outfile, 'w', encoding='utf8') as f:
        f.write(py_src)

    print(f"Wrote {outfile}")
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
