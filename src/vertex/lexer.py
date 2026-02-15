import re
from typing import List

# -------------------------
# Lexer
# -------------------------
TOKEN_SPEC = [
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('STRING',   r'"([^"\\]|\\.)*"'),
    ('LET',      r'\blet\b'),
    ('CONST',    r'\bconst\b'),
    ('PRINT',    r'\bprint\b'),
    ('IF',       r'\bif\b'),
    ('ELSE',     r'\belse\b'),
    ('ID',       r'[A-Za-z_]\w*'),
    ('EQ',       r'=='),
    ('NEQ',      r'!='),
    ('LTE',      r'<='),
    ('GTE',      r'>='),
    ('LT',       r'<'),
    ('GT',       r'>'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
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
