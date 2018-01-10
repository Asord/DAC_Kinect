def none(obj):
    return obj is None

def test_or(test, *args):
    for arg in args:
        if arg == test:
            return True
    return False

def test_and(test, *args):
    for arg in args:
        if arg != test:
            return False
    return True