# Iris
Iris PL - just a fun-project. Interpritating (on Python, heh) with pre-compiling code into the blocks

Currently, this language supports: variable assignments, functions (nested, too), different contexts, conditions, all the operators which python has. Also supports math expressions, comments, data types (numbers[int, float], boolean, strings), etc.

In the next release, I'm planning to add try/except blocks, loops, and more datatypes

Code example:

```
func hello_world(additional_string=none) {
  print('Hello, world!', end=' ');
  
  if (additional_string) {
    print(additional_string);
  }; else {
    print();
  };
};

var = hello_world();

if (var === none) {
  print('Yes, hello!');
};
```
