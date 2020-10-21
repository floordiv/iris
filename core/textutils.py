import re
from itertools import chain


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


def remove_spaces(line):
    result = ''

    in_string = False
    prev_string_opener = None

    for index, letter in enumerate(line):
        if letter in ('"', "'") and line[index - 1] != '\\':
            if in_string and letter == prev_string_opener:
                in_string = False
            elif not in_string:
                in_string = True
                prev_string_opener = letter

        if letter not in (' ', '\t') or in_string:
            result += letter

    return result


def remove_comment(line, comment='//'):
    if line.startswith(comment):
        return ''

    string_pairs = get_string_pairs_indexes(line)

    for comment_index in re.finditer(comment, line):
        comment_index = comment_index.start()

        if comment_index not in string_pairs:
            return line[:comment_index]

    return line


def get_string_pairs_indexes(line):
    indexes = []
    in_string = False
    prev_string_opener = None

    for index, letter in enumerate(line):
        if letter in ('"', "'"):
            if letter == prev_string_opener:
                in_string = False
            elif not in_string:
                in_string = True
                prev_string_opener = letter

            indexes.append(index)

    if len(indexes) % 2 != 0:
        indexes = indexes[:-1]

    return list(chain.from_iterable([range(*pair) for pair in group_by_pairs(indexes)]))


def group_by_pairs(lst):
    result = []

    for index in range(0, len(lst), 2):
        result.append([lst[index], lst[index + 1]])

    return result


def get_nested(source, opener, closer):
    blocks = ['']
    opened_braces = 0
    in_string = False
    prev_string_opener = None

    for letter in source:
        if letter in ('"', "'"):
            if in_string and letter == prev_string_opener:
                in_string = False
            elif not in_string:
                in_string = True
                prev_string_opener = letter

        if not in_string:
            if letter == opener:
                opened_braces += 1
            elif letter == closer:
                opened_braces -= 1

                if opened_braces == 0:
                    blocks[-1] += closer
                    blocks.append('')
                    continue

        blocks[-1] += letter

    return blocks[:-1]


def get_array_ending(string: str, opener: str, closer=None) -> (str, int):
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


def get_string_ending(string: str) -> (str, int):
    for index, letter in enumerate(string[1:], start=1):
        if letter == string[0]:  # if letter is string opener
            return string[1:index], index

    return string[1:-1], len(string) - 1


def cut_blocks(source):
    temp = ['']
    skip_iters = 0

    for index, letter in enumerate(source):
        if skip_iters:
            skip_iters -= 1
            continue

        if letter in ('"', "'"):
            expr, skip_iters = get_string_ending(source[index:])
            temp[-1] += letter + expr + letter
        elif letter == '{':
            expr, skip_iters = get_array_ending(source[index:], '{', '}')
            temp[-1] += '{' + expr + '}'
        elif letter == ';':
            temp.append('')
        else:
            temp[-1] += letter

    if temp[-1] == '':
        temp = temp[:-1]

    return temp
