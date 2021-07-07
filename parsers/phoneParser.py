import re

if __name__ == '__main__':
    from baseParser import Parser
else:
    from .baseParser import Parser


# This class parses lines as an phone number and password.
# Example of accepted lines are:
# 5531123456789:pass
# 5531123456789;pass
class PhoneParser(Parser):
    def __init__(self):
        super().__init__()
        self.patternSeparator = re.compile(':|;')
        self.specialPhoneCharacters = "()+- "
        self.isNotPhoneNumberRegex = re.compile(f"[^0-9{re.escape(self.specialPhoneCharacters)}]")
        
    
    def parse(self, line:str) -> dict:
        splittedLine = re.split(self.patternSeparator, line, maxsplit=1)
        if len(splittedLine) != 2:
            return {}

        if not re.search(self.isNotPhoneNumberRegex, splittedLine[0]):
            phonePart = splittedLine[0]
            passPart = splittedLine[1]
        elif not re.search(self.isNotPhoneNumberRegex, splittedLine[1]):
            phonePart = splittedLine[1]
            passPart = splittedLine[0]
        else:
            return {}

        for specialCharacter in self.specialPhoneCharacters:
            phonePart = phonePart.replace(specialCharacter, "")

        return {
            "phoneNumber": phonePart.lstrip().rstrip(),
            "password": passPart
        }

def _test():
    parser = PhoneParser()
    
    testLines = [
        "5531123456789:pass",
        "+55(31)12345-6789:pass",
        "pass:5531123456789",
        "pass:+55(31)12345-6789",
        "+55(31)12345-6789;pass",
        "+55(31)12345-6789 pass",
        "user:pass",
    ]

    expectedResults = [
        {
            "phoneNumber": "5531123456789",
            "password": "pass"
        },
        {
            "phoneNumber": "5531123456789",
            "password": "pass"
        },
        {
            "phoneNumber": "5531123456789",
            "password": "pass"
        },
        {
            "phoneNumber": "5531123456789",
            "password": "pass"
        },
        {
            "phoneNumber": "5531123456789",
            "password": "pass"
        },
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
