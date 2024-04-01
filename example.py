
class A:
    def a1(p1:str) -> str:
        return f"-{p1}-"
    def a2() -> None:
        return 2
    class B:
        def b1(p1:int) -> int:
            return p1 + 1

    def no1(x:int, y:int):
        z = 2*x + y
        xx = 3*z
        xxx = 4*xx
        return z - xxx

def if_else():
    a = 1
    if a == 1:
        return 1
    else:
        return 2

def func_in_func():
    a = 1
    def inner_func():
        return 1
    b = a + inner_func()
    return b + 1

a = "33"
b = func_in_func()
