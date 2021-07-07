import re

if __name__ == '__main__':
    from baseParser import Parser
else:
    from .baseParser import Parser


# This class parses lines as an email (emaiLocal and emailDomain) and password.
# Example of accepted lines are:
# email@domain.com:pass
# email@domain.com;pass
# pass:email@domain.com
# pass;email@domain.com
class EmailParser(Parser):
    def __init__(self):
        super().__init__()
        self.patternSeparator = re.compile(':|;')
        self.patternEmail = re.compile('@')
    
    def parse(self, line:str) -> dict:
        splittedLine = re.split(self.patternSeparator, line, maxsplit=1)
        if len(splittedLine) != 2:
            return {}

        if '@' in splittedLine[0]:
            emailPart = splittedLine[0]
            passPart = splittedLine[1]
        elif '@' in splittedLine[1]:
            emailPart = splittedLine[1]
            passPart = splittedLine[0]
        else:
            return {}
        
        emailSplit = re.split(self.patternEmail, emailPart, maxsplit=1)
        return {
            "emailLocal": emailSplit[0].rstrip().lstrip().lower(),
            "emailDomain": emailSplit[1].rstrip().lstrip().lower(),
            "password": passPart
        }

def _test():
    parser = EmailParser()
    
    testLines = [
        "email@domain.com:pass",
        "abc@def:ghi",
        "abc@def;ghi",
        "ghi:abc@def",
        "ghi;abc@def",
        "abc def",
        "abc:def",
        "abc@def"
    ]

    expectedResults = [
        {
            "emailLocal": "email",
            "emailDomain": "domain.com",
            "password": "pass"
        },
        {
            "emailLocal": "abc",
            "emailDomain": "def",
            "password": "ghi"
        },
        {
            "emailLocal": "abc",
            "emailDomain": "def",
            "password": "ghi"
        },
        {
            "emailLocal": "abc",
            "emailDomain": "def",
            "password": "ghi"
        },
        {
            "emailLocal": "abc",
            "emailDomain": "def",
            "password": "ghi"
        },
        {},
        {},
        {}
    ]

    for line, expectedResult in zip(testLines, expectedResults):
        result = parser.parse(line)
        print(f"Parsing line: {line}. Expected Result: {expectedResult}. Actual Result: {result}")
        assert result == expectedResult
    
    print(f"All tests succeeded")

if __name__ == '__main__':
    _test()
