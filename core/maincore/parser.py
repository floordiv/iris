from string import punctuation as punctuation_chars

from iris.core.maincore.priority import OPERATORS_PRIORITY, HIGH
from iris.core.maincore.textutils import parse_args
from iris.core.maincore.tokentypes import (PRIMITIVE, NUMBER, VARIABLE,
                                           OPERATOR, PARENTHESIS, FCALL,
                                           STRING, OBJECT, OTHER, types2py)

punctuation = punctuation_chars.replace('.', '').replace('_', '')    # dot and underline are valid chars

OPERATORS = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
    '%': lambda a, b: a % b,
    '&': lambda a, b: a & b,
    '|': lambda a, b: a | b,
    '^': lambda a, b: a ^ b,
    '>': lambda a, b: a > b,
    '<': lambda a, b: a < b,
    '>=': lambda a, b: a >= b,
    '<=': lambda a, b: a <= b,
    '>>': lambda a, b: a >> b,
    '<<': lambda a, b: a << b,
    '**': lambda a, b: a ** b,
    '//': lambda a, b: a // b,
    '==': lambda a, b: a == b,
    '!=': lambda a, b: a != b,
    '&&': lambda a, b: a and b,
    '||': lambda a, b: a or b,
    '===': lambda a, b: a is b,
}

# all characters from OPERATORS, but without repetitions
SPECIAL_CHARACTERS = set(list(''.join(OPERATORS.keys())))


def is_valid_var_name(name):
    if not name:
        return False

    return name[0] not in map(str, range(10)) and not any(map(lambda char: char in punctuation, name))


class Token:
    def __init__(self, typeof, value, priority=None, unary=1):
        self.type = typeof
        self.value = value
        self.priority = priority
        self.unary = unary
        self.processed = False

    def __str__(self):
        return f'Token(type={self.type}, value={repr(self.value)}, unary={self.unary}, processed={self.processed})'

    __repr__ = __str__


class ParenthesisOp:
    def __init__(self, tokens, unary=1):
        """
        unary: number with a sign to be converted after executing
        """

        self.tokens = self.value = tokens
        self.unary = unary
        self.type = PARENTHESIS
        self.processed = False

    def __str__(self):
        return f'ParenthesisOp(tokens=[{", ".join([str(token) for token in self.tokens])}], unary={self.unary})'

    __repr__ = __str__


class FunctionCall:
    def __init__(self, name, arguments, kwarguments, unary=1):
        self.name = name
        self.args = arguments
        self.kwargs = kwarguments

        self.priority = HIGH
        self.unary = unary
        self.value = None
        self.type = FCALL
        self.processed = False

    def call(self, functions):
        obj = functions[self.name]

        return obj(*self.export_args(), **self.export_kwargs())

    def export_args(self):
        return [token.value for token in self.args]

    def export_kwargs(self):
        exported_kwargs = {}

        for var, val in self.kwargs.items():
            if not isinstance(val, str):
                val = val.value

            exported_kwargs[var] = val

        return exported_kwargs

    def __str__(self):
        return f'FunctionCall(name={repr(self.name)}, args={self.args}, kwargs={self.kwargs}, unary={self.unary})'

    __repr__ = __str__


class Parser:
    def __init__(self, context=None):
        if context is None:
            context = {}

        self.context = context

    def splitexpr(self, expr) -> list:
        tokens = [Token(PRIMITIVE, '')]
        skip_iters = 0

        for index, letter in enumerate(expr):
            if skip_iters:
                skip_iters -= 1
                continue

            if letter == '(':
                if tokens[-1].type != PARENTHESIS and is_valid_var_name(tokens[-1].value):  # looks like a function call
                    raw_function_args_kwargs, skip_iters = self.get_array_ending(expr[index:], '(', ')')

                    name = tokens[-1].value
                    args, kwargs = parse_args(raw_function_args_kwargs, SPECIAL_CHARACTERS)

                    args_as_tokens = [self.execute(arg, return_token=True) for arg in args]
                    kwargs_as_tokens = dict([(kw_var, self.execute(kw_val, return_token=True)) for kw_var, kw_val in kwargs.items()])

                    tokens[-1] = FunctionCall(name, args_as_tokens, kwargs_as_tokens)
                    continue
                else:
                    expr_in_braces, skip_iters = self.get_array_ending(expr[index:], '(', ')')
                    split_expr_in_braces = self.splitexpr(expr_in_braces)

                    if split_expr_in_braces:
                        if split_expr_in_braces[0].type != PARENTHESIS and split_expr_in_braces[0].value == '':
                            split_expr_in_braces = split_expr_in_braces[1:]

                    tokens.append(ParenthesisOp(split_expr_in_braces))
                continue
            elif letter in ('"', "'"):
                string, skip_iters = self.get_string_ending(expr[index:])
                tokens.append(Token(STRING, string))
                continue

            if letter in SPECIAL_CHARACTERS:
                if isinstance(tokens[-1], ParenthesisOp) or tokens[-1].type != OPERATOR or tokens[-1].value + letter not in OPERATORS:
                    tokens.append(Token(OPERATOR, ''))
            elif tokens[-1].type in (PARENTHESIS, FCALL) or tokens[-1].type == OPERATOR:   # letter is not a special character
                tokens.append(Token(PRIMITIVE, ''))

            tokens[-1].value += letter

        if tokens[0].type not in (FCALL, PARENTHESIS) and tokens[0].value == '':
            tokens = tokens[1:]

        return self.unarize_tokens(tokens)

    def unarize_tokens(self, tokens: list) -> list:
        unarized_tokens = []
        current_unary_signs = []

        for index, token in enumerate(tokens, start=1):
            if token.processed or token.type in (STRING,):
                pass
            elif token.type == OPERATOR and (len(unarized_tokens) == 0 or unarized_tokens[-1].type == OPERATOR):
                current_unary_signs.append(token.value)
                continue
            elif token.type != OPERATOR and current_unary_signs:
                token.unary = 1 if self.get_final_unary_sign_of_array(current_unary_signs) == '+' else -1
                current_unary_signs = []

            unarized_tokens.append(token)

        return self.process_tokens(unarized_tokens)

    def get_final_unary_sign_of_array(self, signs: list) -> str:
        if [sign for sign in signs if sign not in tuple('+-')]:  # if some of the unary signs are not + or -
            raise SyntaxError('bad unary operator!')

        reversed_signs = signs[::-1]    # unary sign is parsing from right to left
        previous_sign = reversed_signs[0]

        for sign in reversed_signs[1:]:
            if sign == '-' and previous_sign == '-':
                previous_sign = '+'
            elif sign == '+' and previous_sign == '-':
                previous_sign = '-'
            else:
                previous_sign = sign

        return previous_sign

    def process_tokens(self, tokens) -> list:
        for index, token in enumerate(tokens):
            if token.type in (PARENTHESIS, FCALL, STRING):
                continue

            if token.type == OPERATOR:
                token.priority = OPERATORS_PRIORITY[token.value]
                continue
            elif token.value.replace('.', '').isdigit():
                token.type = NUMBER
            elif is_valid_var_name(token.value):
                token.type = VARIABLE
            else:
                raise SyntaxError(f'bad value: "{token.value}"')

            tokens[index] = self.process_token(token)

        return tokens

    def process_token(self, token) -> Token:
        if token.type == VARIABLE:
            token.value = self.context[token.value]

            if token.value in types2py:
                token.type = types2py[type(token.value)]
            else:
                token.type = OTHER

            return self.process_token_unary(token)
        if token.type in (FCALL, STRING):
            return token

        if isinstance(token.value, str) and {token.value[0], token.value[-1]} in ({'"'}, {"'"}):
            token.type = STRING
            token.value = token.value[1:-1]
        else:
            token.type = NUMBER
            token.value = float(token.value)

            if token.value.is_integer():
                token.value = int(token.value)

            token = self.process_token_unary(token)

        return token

    def process_token_unary(self, token) -> Token:
        if not token.processed and token.type == NUMBER:
            token.processed = True
            token.value *= token.unary

        return token

    def get_array_ending(self, string: str, opener: str, closer=None) -> (str, int):
        """
        expr: a string with opener
        opener: single char, which starts an array
        closer: single char, which ends an array

        :returns: in-brace expression, brace-expression-end-index
        """

        openers_opened = 0

        for index, letter in enumerate(string):
            if letter == opener:
                openers_opened += 1
            elif letter == closer:
                openers_opened -= 1

            if openers_opened == 0:
                return string[1:index], index

        return string[1:-1], len(string) - 1

    def get_string_ending(self, string: str) -> (str, int):
        for index, letter in enumerate(string[1:], start=1):
            if letter == string[0]:  # if letter is string opener
                return string[1:index], index

        return string[1:-1], len(string) - 1

    def process_kwargs(self, kwargs: dict) -> None:
        for var, val in kwargs.items():
            primitive_token = Token(PRIMITIVE, val)
            token = self.process_token(primitive_token)

            kwargs[var] = token

    def peek_most_priority_op(self, tokens) -> (list or ParenthesisOp or FunctionCall):
        most_priority_trio = None

        for index, token in enumerate(tokens):
            if token.type in (PARENTHESIS, FCALL):
                return token

            if token.type == OPERATOR:
                if most_priority_trio is None or most_priority_trio[1].priority < token.priority:
                    most_priority_trio = [tokens[index - 1], token, tokens[index + 1]]

        return most_priority_trio

    def execute_binop(self, left, op, right) -> int:
        return OPERATORS[op.value](left.value, right.value)

    def execute(self, expr=None, context=None, return_token=False) -> (int or Token):
        if context:
            self.context = context

        if isinstance(expr, str):
            expr = self.splitexpr(expr)

        cooked_expr = expr[:]

        while len(cooked_expr) > 1 or cooked_expr[0].type in (PARENTHESIS, FCALL):
            binop = self.peek_most_priority_op(cooked_expr)

            if binop is None:
                break

            if isinstance(binop, ParenthesisOp):
                executed_parenthesis = self.execute(binop.tokens)
                executed_parenthesis *= binop.unary

                cooked_expr[cooked_expr.index(binop)] = Token(NUMBER, value=executed_parenthesis)
                continue
            elif isinstance(binop, FunctionCall):
                result = binop.call(self.context)

                if type(result) not in types2py:    # we've got some object
                    token = Token(OBJECT, value=result)
                else:
                    token = Token(NUMBER, value=result * binop.unary)

                cooked_expr[cooked_expr.index(binop)] = token
                continue

            binop_result = self.execute_binop(*binop)
            binop_index = self.find_sublist_of_3_elements(cooked_expr, binop)
            binop_response_type = types2py[type(binop_result)]
            cooked_expr[binop_index:binop_index + 3] = [Token(binop_response_type, value=binop_result)]

        answer = cooked_expr[0]  # the only element if the list

        if not return_token:
            answer = answer.value

        return answer

    def find_sublist_of_3_elements(self, source, pattern: list) -> (Token or None):
        for index, elem in enumerate(source[1:-1], start=1):
            if [source[index - 1], elem, source[index + 1]] == pattern:
                return index - 1

        return None


parser = Parser()
