import re


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


def parse_function_call(funcall):
    funcname, funcargs = funcall.split('(', maxsplit=1)
    funcargs = funcargs.rstrip(')')

    return (funcname, *parse_args(funcargs))


def parse_args(string):
    raw = parse_func_call_args(string)
    args = []
    kwargs = {}

    for arg in raw:
        if isinstance(arg, list):
            var, val = arg
            kwargs[var] = val
        else:
            args.append(arg)

    return args, kwargs


def parse_func_call_args(args, raise_err_if_kwarg=None):
    """
    returns RAW (without datatypes) function arguments
    """

    funcargs = split(args, ',')
    kwarg_pattern = re.compile(r'[^\d]\w*=.+')
    result = []

    for arg in funcargs:
        if kwarg_pattern.match(arg):
            if raise_err_if_kwarg is not None:
                raise raise_err_if_kwarg('kwargs not allowed!')

            result.append(parse_kwarg(arg))
        else:
            result.append(arg)

    if result[-1] == '':
        result = result[:-1]

    return result


def parse_kwarg(kwarg):
    return kwarg.split('=', maxsplit=1)


# print(parse_function_call('someFunc(args,arg2="ok,got")'))
