from iris.core.constants import (IF_STMNT, ELIF_STMNT, ELSE_STMNT, CONDITION,
                                 FUNC_ASSIGN, CLASS_ASSIGN, VAR_ASSIGN,
                                 RETURN_TOKEN,
                                 FUNCTION)
from iris.core.maincore.parser import parser


class Token:
    def __init__(self, eid, typeof, value):
        self.eid = eid
        self.type = typeof
        self.value = value

    def __str__(self):
        return f'Token(eid={self.eid}, type={self.type}, value={repr(self.value)})'

    __repr__ = __str__


class IfExpression:
    def __init__(self, eid, expression, body):
        self.eid = eid
        self.expr = expression
        self.body = body

        self.type = IF_STMNT

    def __str__(self):
        return f'IfCondition(eid={self.eid})'

    __repr__ = __str__


class ElifExpression:
    def __init__(self, eid, expression, body):
        self.eid = eid
        self.expr = expression
        self.body = body

        self.type = ELIF_STMNT

    def __str__(self):
        return f'ElifCondition(eid={self.eid})'

    __repr__ = __str__


class ElseExpression:
    def __init__(self, eid, body):
        self.eid = eid
        self.body = body

        self.type = ELSE_STMNT

    def __str__(self):
        return f'ElseCondition(eid={self.eid})'

    __repr__ = __str__


class ConditionBranch:
    def __init__(self, if_expr, *elif_expr, else_expr=None):
        self.if_expr = if_expr
        self.elif_expr = list(elif_expr)
        self.else_expr = else_expr

        self.type = CONDITION

    def get_branch(self, context):
        """
        executor: core.maincore.parser.Parser
        """

        for branch in [self.if_expr] + self.elif_expr:
            if parser.execute(branch.expr, context=context):
                return branch

        return self.else_expr

    def __str__(self):
        return f'ConditionBranch(if={self.if_expr}, elif={self.elif_expr}, else={self.else_expr})'

    __repr__ = __str__


class VarAssign:
    def __init__(self, eid, var, val):
        self.eid = eid
        self.name, self.value = var, val
        self.type = VAR_ASSIGN

    def __str__(self):
        return f'Var(eid={self.eid}, name={repr(self.name)}, value={repr(self.value)}'

    __repr__ = __str__


class Function:
    def __init__(self, eid, name, args, kwargs, body, context, block_executor):
        self.eid = eid
        self.name = name
        self.args = args
        self.kwargs = {}
        self.body = body
        self.context = context
        self.executor = block_executor

        for kw_var, kw_val in kwargs.items():
            self.kwargs[kw_var] = parser.execute(kw_val, context=context)

        self.type = FUNCTION

    def call(self, *args, **kwargs):
        func_args_len, given_args_len = len(self.args), len(args)

        if func_args_len != given_args_len:
            raise TypeError(f'{self.name}(): {func_args_len} args expected, got {given_args_len} instead')

        for arg_name, given_arg_value in zip(self.args, args):
            self.context[arg_name] = given_arg_value

        for kw_var, kw_val in {**self.kwargs, **kwargs}.items():
            if kw_var not in self.kwargs:
                raise TypeError(f'{self.name}(): unexpected kwarg: {kw_var}')

            self.context[kw_var] = kw_val

        return self.executor(self.body)

    def __str__(self):
        return f'Function(eid={self.eid}, name={repr(self.name)}, args={self.args}, kwargs={self.kwargs})'

    __call__ = call
    __repr__ = __str__
