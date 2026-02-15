from typing import List, Any
from .lexer import Token

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
        if self.at('IF'):
            return self.parse_if()
        if self.at('WHILE'):
            return self.parse_while()
        if self.at('ID'):
            return self.parse_assign()
        tok = self.cur()
        raise SyntaxError(f"Unexpected token {tok.type} ('{tok.value}') at pos {tok.pos}")

    def parse_assign(self):
        name = self.eat('ID').value
        self.eat('ASSIGN')
        expr = self.parse_expression()
        return ('assign', name, expr)

    def parse_while(self):
        self.eat('WHILE')
        cond = self.parse_expression()
        block = self.parse_block()
        return ('while', cond, block)

    def parse_if(self):
        self.eat('IF')
        cond = self.parse_expression()
        then_block = self.parse_block()
        else_block = []
        if self.at('ELSE'):
            self.eat('ELSE')
            if self.at('IF'):
                # else if -> treat as a single statement block containing the if
                else_block = [self.parse_if()]
            else:
                else_block = self.parse_block()
        return ('if', cond, then_block, else_block)

    def parse_block(self):
        self.eat('LBRACE')
        stmts = []
        while not self.at('RBRACE') and not self.at('EOF'):
            # skip optional NEWLINEs inside block
            while self.at('NEWLINE'):
                self.eat('NEWLINE')
            if self.at('RBRACE'):
                break
            stmts.append(self.parse_statement())
            # statement separator inside block
            if self.at('NEWLINE'):
                self.eat('NEWLINE')
        self.eat('RBRACE')
        return stmts

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
        return self.parse_comparison()

    def parse_comparison(self):
        node = self.parse_addsub()
        # comparison operators: == != < > <= >=
        # we treat them as binary operators with lower precedence than + -
        while self.cur().type in ('EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE'):
            op = self.eat('EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE').type
            right = self.parse_addsub()
            node = ('binop', op, node, right)
        return node

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
