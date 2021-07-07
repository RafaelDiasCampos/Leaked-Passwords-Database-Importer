import re

if __name__ == '__main__':
    from baseParser import Parser
else:
    from .baseParser import Parser


# This class parses an input line as an username or email and password combo. It tries to autodetect a line before parsing.
# Methods for autodetecting are as follows:
# email@domain.com:pass -> parsed as email and password
# pass:email@domain.com -> parsed as password and email
# user:pass -> parsed as username and password
# email@domain.com:hash:salt -> parsed as email and password (hash + salt)
# random:email@domain.com:pass -> parsed as email and password
# hash:salt:email@domain.com -> parsed as email and password (hash+salt)
# user:hash:salt -> parsed as username and password (hash+salt)

class AutodetectParser(Parser):
    def __init__(self):
        super().__init__()
        self.patternSeparator = re.compile(':|;')
        self.patternEmail = re.compile('@')
    
    def parse(self, line:str) -> dict:
        splittedLine = re.split(self.patternSeparator, line, maxsplit=2)
        parseUsername = False
        if len(splittedLine) == 1:
            return {}
        elif len(splittedLine) == 2:
            if '@' in splittedLine[0]:
                idPart = splittedLine[0]
                passPart = splittedLine[1]
            elif '@' in splittedLine[1]:
                idPart = splittedLine[1]
                passPart = splittedLine[0]
            else:
                idPart = splittedLine[0]
                passPart = splittedLine[1]
                parseUsername = True
        else:
            if '@' in splittedLine[0]:
                idPart = splittedLine[0]
                passPart = re.split(self.patternSeparator, line, maxsplit=1)[1]
            elif '@' in splittedLine[1]:
                idPart = splittedLine[1]
                passPart = splittedLine[2]
            elif '@' in splittedLine[2]:
                idPart = splittedLine[2]
                # Strips from the end of the string, instead of the beginning
                # Reverse the line, split, grab the second result (originally was the first one), reverse again.
                passPart = re.split(self.patternSeparator, line[::-1], maxsplit=1)[1][::-1]
            else:
                idPart = splittedLine[0]
                passPart = re.split(self.patternSeparator, line, maxsplit=1)[1]
                parseUsername = True

        if len(idPart) == 0 or len(passPart) == 0:
            return {}

        if parseUsername:
            return {
                "username": idPart.rstrip().lstrip().lower(),
                "password": passPart
            }
        
        emailSplit = re.split(self.patternEmail, idPart, maxsplit=1)

        if len(emailSplit[0]) > 0 and len(emailSplit[1]) > 0:
            return {
                "emailLocal": emailSplit[0].rstrip().lstrip().lower(),
                "emailDomain": emailSplit[1].rstrip().lstrip().lower(),
                "password": passPart
            }        
            
        return {
            "username": splittedLine[0],
            "password": splittedLine[1]
        }

def _test():
    parser = AutodetectParser()
    
    testLines = [
        "user:pass",
        "abc:def",
        "abc;def",
        "abc def",
        "email@domain.com:pass",
        "abc@def:ghi",
        "abc@def;ghi",
        "ghi:abc@def",
        "ghi;abc@def",
        "abc def",
        "abc@def",
        "user:hash:salt",
        "user:pass:pass:pass",
        "email@domain.com:hash:salt",
        "email@domain.com:pass:pass:pass",
        "hash:salt:email@domain.com"
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
        {},
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
        {
            "username": "user",
            "password": "hash:salt"
        },
        {
            "username": "user",
            "password": "pass:pass:pass"
        },
        {
            "emailLocal": "email",
            "emailDomain": "domain.com",
            "password": "hash:salt"
        },
        {
            "emailLocal": "email",
            "emailDomain": "domain.com",
            "password": "pass:pass:pass"
        },
        {
            "emailLocal": "email",
            "emailDomain": "domain.com",
            "password": "hash:salt"
        }
    ]

    for line, expectedResult in zip(testLines, expectedResults):
        result = parser.parse(line)
        print(f"Parsing line: {line}. Expected Result: {expectedResult}. Actual Result: {result}")
        assert result == expectedResult
    
    print(f"All tests succeeded")

if __name__ == '__main__':
    _test()
