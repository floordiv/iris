from timeit import timeit

from iris.core.interpreter import interpret


code = """
func test(second_call=none) {
    print("hi there! second_call kwarg's value is:", second_call);
 
    if (second_call) {
        print('Second call, baby!');
        return 3;
    };
    
    return test;
};

a = test();
print("Function in the second time returned", a(second_call=1));
print("a == 5 is", a == 5);
"""

interpret(code)
# print('timeit:', timeit('interpret(code)', globals={'code': code, 'interpret': interpret}, number=1))
