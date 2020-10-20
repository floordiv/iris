PRIMITIVE = 'primitive'
NUMBER = 'number'
VARIABLE = 'variable'
CONSTANT = 'constant'
OPERATOR = 'operator'
PARENTHESIS = 'parenthesis'

STRING = 'string'
TUPLE = 'tuple'
LIST = 'list'
FCALL = 'function_call'
OBJECT = 'object'

OTHER = 'other'

types2py = {
    int: NUMBER,
    float: NUMBER,
    bool: NUMBER,
    str: STRING,
}
