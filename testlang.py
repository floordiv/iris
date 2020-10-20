from timeit import timeit

from iris.core.interpreter import interpret


code = """
func test(second_call=0) {
    print(second_call, "hi there!");
 
    if (second_call) {
        print(second_call, 'Second call, baby!');
        return 3;
    };
    
    return test;
};

a = test();
print(a(second_call=1));
"""

print('timeit:', timeit('interpret(code)', globals={'code': code, 'interpret': interpret}, number=1))
