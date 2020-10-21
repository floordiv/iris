from iris.core.textutils import remove_spaces, remove_comment


KEYWORDS = (
    'func',
    'class',
    'return',
)


def compose(source):
    composed = ''
    lines = source.split('\n')

    for line in lines:
        line = remove_comment(line).strip().strip('\t')

        for operator in KEYWORDS:
            if line.startswith(operator + ' '):
                operator_length = len(operator)
                composed += operator + ' ' + remove_spaces(line)[operator_length:]

                break
        else:
            composed += remove_spaces(remove_comment(line))

    return composed
