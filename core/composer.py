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


code = """
// short example of the lang

func hello_world() {
    func out(string) {
        print(string);
    };
    out('Hello, world!');
    
    return 5;
};

a = hello_world();

if (a == 5) {
    out("a equals 5");
}; elif (a == 6) {
    out("a equals 6");
}; else {
    out("a equals", a);
};
"""

# print(compose(code))
