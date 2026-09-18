global a
a = "123"


def changeA(a):
    a = "456"
    return a


b = changeA(a)

print(a, b)
