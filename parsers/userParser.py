import re

if __name__ == '__main__':
    from baseParser import Parser
else:
    from .baseParser import Parser


# This class parses lines as an username and password.
# Example of accepted lines are:
# user:pass
# user;pass
class UserParser(Parser):
    def __init__(self):
        super().__init__()
        self.patternSeparator = re.compile(':|;')
    
    def parse(self, line:str) -> dict:
        splittedLine = re.split(self.patternSeparator, line, maxsplit=1)
        if len(splittedLine) != 2:
            return {}

        return {
            "username": splittedLine[0].rstrip().lstrip().lower(),
            "password": splittedLine[1]
        }

def _test():
    parser = UserParser()
    
    testLines = [
        "user:pass",
        "abc:def",
        "abc;def",
        "abc def"
    ]

    expectedResults = [
        {
            "username": "user",
            "password": "pass"
        },
        {
            "username": "abc",
            "password": "def"
        },
        {
            "username": "abc",
            "password": "def"
        },
        {}
    ]

    for line, expectedResult in zip(testLines, expectedResults):
        result = parser.parse(line)
        print(f"Parsing line: {line}. Expected Result: {expectedResult}. Actual Result: {result}")
        assert result == expectedResult
    
    print(f"All tests succeeded")

if __name__ == '__main__':
    _test()
