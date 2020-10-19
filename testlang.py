from timeit import timeit

from iris.core.interpreter import interpret


code = """
func hello_world() {
    func out(string, second="ok") {  // just a wrapper to test nested functions
        print(string, second);
        //print(second);
    };
    out('Hello, world!');

    return 1;
};

a = hello_world();

if (a == 5) {
    out("a equals 5");
}; elif (a == 6) {
    out("a equals 6");
}; else {
    out("a equals", second=a);
};
"""

print('timeit:', timeit('interpret(code)', globals={'code': code, 'interpret': interpret}, number=1))
