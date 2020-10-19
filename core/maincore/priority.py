MINIMAL = 1
MEDIUM = 2
HIGH = 3
MAXIMAL = 4


OPERATORS_PRIORITY = {
    '>': MINIMAL,
    '<': MINIMAL,
    '==': MINIMAL,
    '>=': MINIMAL,
    '<=': MINIMAL,
    '!=': MINIMAL,
    '&&': MINIMAL,
    '||': MINIMAL,
    '===': MINIMAL,

    '+':  MINIMAL,
    '-':  MINIMAL,
    '&': MINIMAL,
    '|': MINIMAL,
    '^': MINIMAL,
    '>>': MINIMAL,
    '<<': MINIMAL,

    '*':  MEDIUM,
    '/':  MEDIUM,
    '%':  MEDIUM,
    '//': MEDIUM,

    '**':  HIGH,
}
