from sys import argv, exit

from iris.core.interpreter import interpret


"""
currently DOESN'T WORK.
The best way to run a code is still running it in pycharm with source-root iris.
"""


if __name__ == '__main__':

    if len(argv) == 1:
        print('Iris: python3 run.py <filename>.ir')
        exit(1)

    file = argv[1]

    if not file.endswith('.ir'):
        print('Iris: bad file extension:', file)
        exit(1)

    try:
        with open(file) as fd:
            source = fd.read()
    except FileNotFoundError:
        print('Iris: file not found:', file)
        exit(1)

    interpret(source)
