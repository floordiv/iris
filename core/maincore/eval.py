from iris.core.maincore.parser import Parser

from math import pi
import timeit

exprs = (
    "2+2*2",
    "(2+2)+(2+2)",
    "-(2+2)+-(2+2)",
    "(2+2)*-(2+2)",
    "-(-(-(-(3*88888))))",
    "pi*2",
    "(pi+1)*(pi+2)",
    "-pi",
    "pi**2",
    '1+(1+1)',
    '(1+1)+1',
    '(1+1)+(1+1)',
    '-(1+1)+(1+1)',
    '+-(1+1)+(1+1)',
    '-+(1+1)+(1+1)',
    '(-5)',
    '-(1+x)',
    '---1',

    '"hello"+" "+"world"',
    '"hello"*2',

    'sum(-(1+1),-(3))',
    '-sum(-(1+1),-(3))',
    '+sum(-(1+1),-(3))',
    'func_no_args()',
)

constants = {
    "pi": pi,
    "x": 2,
    "sum": lambda a, b: a + b,
    "func_no_args": lambda: 5
}

itercount = 1000
parser = Parser(context=constants)

print("Evaluator test:")

for expr in exprs:
    print(expr, "=", parser.execute(expr),
          "timeit: ", end="", flush=True)
    print(timeit.timeit("parser.execute(expr)", globals={
        "parser": parser, "expr": expr}, number=itercount))
