from iris.core.blocks import Token
from iris.core.maincore.parser import parser, SPECIAL_CHARACTERS
from iris.core.maincore.textutils import parse_function_call, parse_func_call_args
from iris.core.constants import RETURN_TOKEN, BREAK_TOKEN, CONTINUE_TOKEN, SKIPITER_TOKEN, EXPRESSION


def if_expr_parser(raw):
    """
    if(expr){body;}
    """
    expr, raw_body = raw[3:].split(')', maxsplit=1)

    return expr, raw_body[1:-1]


def elif_expr_parser(raw):
    """
    elif(expr){body;}
    """

    return if_expr_parser(raw[2:])  # haha, classic


def else_expr_parser(raw):
    """
    else{body;}
    """

    return raw[5:-1]


def func_assign_parser(raw):
    """
    func funcName(funcargs){body;}
    """
    
    half_cooked = raw[5:-1]
    func, body = half_cooked.split('{', maxsplit=1)

    return (*parse_function_call(func, SPECIAL_CHARACTERS), body)


def class_assign_parser(raw):
    """
    class ClassName{body;}
    """
    
    class_name, class_body = raw[6:-1].split('{', maxsplit=1)
    
    return class_name, class_body


def var_assign_parser(raw):
    """
    variable=value
    """
    
    return raw.split('=', maxsplit=1)


class TokenParser:
    def __init__(self):
        self.operators = {
            'return': RETURN_TOKEN,
            'break': BREAK_TOKEN,
            'continue': CONTINUE_TOKEN,
            'skipiter': SKIPITER_TOKEN
        }

    def parse(self, eid, raw, context):
        for operator, operator_type in self.operators.items():
            if raw.startswith(operator):
                operator_args = raw[len(operator):].lstrip()

                if operator_args:
                    operator_args = parse_func_call_args(operator_args, SPECIAL_CHARACTERS, raise_err_if_kwarg=SyntaxError)

                    for index, arg in enumerate(operator_args):
                        operator_args[index] = parser.execute(arg, context=context)

                    if len(operator_args) == 1:
                        operator_args = operator_args[0]

                return Token(eid, operator_type, operator_args or None)

        return Token(eid, EXPRESSION, raw)
