from main import site

def store(text):
    return text[:: 1]

def test():
    assert store("aston") == "aston"
