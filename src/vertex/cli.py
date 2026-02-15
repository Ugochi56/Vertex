import sys
import os
from .lexer import tokenize
from .parser import Parser
from .codegen import compile_to_python

# -------------------------
# CLI
# -------------------------
def main(argv):
    if len(argv) < 2:
        print("Usage: python -m vertex input.vx [-o out.py]")
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

    with open(infile, 'r', encoding='utf8') as f:
        code = f.read()
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

def entry_point():
    sys.exit(main(sys.argv))
