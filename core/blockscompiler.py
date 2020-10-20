from re import compile

from iris.core.parsers import (if_expr_parser, elif_expr_parser, else_expr_parser,
                               func_assign_parser, class_assign_parser, var_assign_parser,
                               TokenParser)
from iris.core.blocks import (IfExpression, ElifExpression, ElseExpression, ConditionBranch,
                              Function, VarAssign, Token)


token_parser = TokenParser()

# variable, does not starts with an integer, has =, can be surrounded by different symbols (for ex. quotes or braces)
VARIABLE_ASSIGN = compile(r'[^\d]\w*=.+')

# blocks
IF_BLOCK = compile(r'if\(.*\){.*}')
ELIF_BLOCK = compile(r'elif\(.*\){.*}')
ELSE_BLOCK = compile(r'else{.*}')

FUNC_BLOCK = compile(r'func [^\d]\w*\(.*\){.*}')
CLASS_BLOCK = compile(r'class ([^\d]\w*){.*}')

RETURN_TOKEN = compile(r'return .*')

block_types = {
    'ELIF_BLOCK': ELIF_BLOCK,
    'IF_BLOCK': IF_BLOCK,
    'ELSE_BLOCK': ELSE_BLOCK,
    'FUNC_ASSIGN': FUNC_BLOCK,
    'CLASS_ASSIGN': CLASS_BLOCK,
    'VAR_ASSIGN': VARIABLE_ASSIGN,
}
blocktypes2parsers = {
    'IF_BLOCK': if_expr_parser,
    'ELIF_BLOCK': elif_expr_parser,
    'ELSE_BLOCK': else_expr_parser,
    'FUNC_ASSIGN': func_assign_parser,
    'CLASS_ASSIGN': class_assign_parser,
    'VAR_ASSIGN': var_assign_parser,
}
blocktypes2blocks = {
    'IF_BLOCK': IfExpression,
    'ELIF_BLOCK': ElifExpression,
    'ELSE_BLOCK': ElseExpression,
    'FUNC_ASSIGN': Function,
    'VAR_ASSIGN': VarAssign,
}


def get_block_type(raw):
    for block_type, block_pattern in block_types.items():
        if block_pattern.fullmatch(raw):
            return block_type

    return 'TOKEN'


def compile_block(eid, raw, context, executor):
    block_type = get_block_type(raw)

    if block_type == 'TOKEN':
        return token_parser.parse(eid, raw, context)

    parsed = blocktypes2parsers[block_type](raw)
    block = blocktypes2blocks[block_type]

    if block_type == 'FUNC_ASSIGN':
        parsed += (context, executor)

    if not isinstance(parsed, str):
        return block(eid, *parsed)
    else:
        return block(eid, parsed)
