def split(text, splitby=' ', skipby='"\'', skipby_close_is_same=True):
    """
    splits by ONE LETTER, but you can set multiple, and it will split it by them
    """

    result = ['']
    in_skipper = False
    prev_skipper_opener = None
    close_skipper = lambda char: char == prev_skipper_opener if skipby_close_is_same else char != prev_skipper_opener

    for letter in text:
        if letter in splitby and not in_skipper:
            result.append('')
        else:
            if letter in skipby:
                if in_skipper and close_skipper(letter):
                    in_skipper = False
                elif not in_skipper:
                    in_skipper = True
                    prev_skipper_opener = letter

            result[-1] += letter

    return result


def split_arguments(args):
    opened_braces = 0
    result = ['']
    in_string = False
    prev_string_opener = None

    for letter in args:
        if letter in tuple('"\''):
            if not in_string:
                in_string = True
                prev_string_opener = letter
            elif prev_string_opener == letter:
                in_string = False

        if letter == '(':
            opened_braces += 1
        elif letter == ')':
            opened_braces -= 1

        if letter == ',' and opened_braces <= 0 and not in_string:
            result.append('')
        else:
            result[-1] += letter

    if result[-1] == '':
        result = result[:-1]

    return result


def parse_function_call(funcall, special_characters):
    funcname, funcargs = funcall.split('(', maxsplit=1)
    funcargs = funcargs.rstrip(')')

    return (funcname, *parse_args(funcargs, special_characters))


def parse_args(string, special_characters):
    raw = parse_func_call_args(string, special_characters)
    args = []
    kwargs = {}

    for arg in raw:
        if isinstance(arg, list):
            var, val = arg
            kwargs[var] = val
        else:
            args.append(arg)

    return args, kwargs


def parse_func_call_args(args, special_characters, raise_err_if_kwarg=None):
    """
    returns RAW (without datatypes) function arguments
    """

    funcargs = split_arguments(args)
    result = []

    for arg in funcargs:
        if '=' in arg:
            first_eq_index = arg.find('=')

            if arg[first_eq_index - 1] in special_characters or arg[first_eq_index + 1] in special_characters \
                    or '(' in arg[:first_eq_index]:
                result.append(arg)
                continue

            if raise_err_if_kwarg is not None:
                raise raise_err_if_kwarg('kwargs not allowed!')

            result.append(parse_kwarg(arg))
        else:
            result.append(arg)

    if result and result[-1] == '':
        result = result[:-1]

    return result


def parse_kwarg(kwarg):
    return kwarg.split('=', maxsplit=1)


# print(split_arguments('a(hello,world),ok,"ok,baby!"'))
