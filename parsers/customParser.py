import re

if __name__ == '__main__':
    from baseParser import Parser
else:
    from .baseParser import Parser


# This class parses lines in a custom configuration.
class CustomParser(Parser):
    def __init__(self, config):
        super().__init__()
        self.config = self.parseConfiguration(config)

    def parseConfiguration(self, config:dict) -> dict:
        # Builds a lookup array for the fields
        config["firstParsing"]["fieldsBySplit"] = []

        for i in range(config["firstParsing"]["maxSplits"] + 2):
            config["firstParsing"]["fieldsBySplit"].append([])
        for splitSetting in config["firstParsing"]["splitSettings"]:
            config["firstParsing"]["fieldsBySplit"][ splitSetting["splits"] + 1 ] = splitSetting["fields"]

        config["firstParsing"]["compiledRegex"] = re.compile(config["firstParsing"]["separatorRegex"])

        # Builds a lookup array for the recursive fields
        config["recursiveParsing"]["fields"] = {}        

        for recursiveSetting in config["recursiveParsing"]["settings"]:            
            recursiveSetting["compiledRegex"] = re.compile(recursiveSetting["separatorRegex"])

            recursiveSetting["fieldsBySplit"] = []         
            
            for i in range(recursiveSetting["maxSplits"] + 2):
                recursiveSetting["fieldsBySplit"].append([])
            for splitSetting in recursiveSetting["splitSettings"]:
                recursiveSetting["fieldsBySplit"][ splitSetting["splits"] + 1 ] = splitSetting["fields"]                

            config["recursiveParsing"]["fields"][recursiveSetting["fieldName"]] = recursiveSetting
        del config["recursiveParsing"]["settings"]

        return config

    def firstParse(self, line:str) -> dict:
        splittedLine = re.split(self.config["firstParsing"]["compiledRegex"], line, maxsplit=self.config["firstParsing"]["maxSplits"])

        fields = self.config["firstParsing"]["fieldsBySplit"][len(splittedLine)]

        parsedLine = {}
        for field, result in zip(fields, splittedLine):
            parsedLine[field] = result    
        return parsedLine

    def recursiveParsing(self, parsedLine:dict) -> dict:
        newFields = {}
        foundNewFields = False
        for key, value in parsedLine.items():
            if key in self.config["recursiveParsing"]["fields"]:
                foundNewFields = True
                splittedLine = re.split(self.config["recursiveParsing"]["fields"][key]["compiledRegex"], value, maxsplit=self.config["recursiveParsing"]["fields"][key]["maxSplits"])
                
                fields = self.config["recursiveParsing"]["fields"][key]["fieldsBySplit"][len(splittedLine)]

                for field, result in zip(fields, splittedLine):
                    newFields[field] = result
        
        if foundNewFields:
            newFields |= self.recursiveParsing(newFields)
        return parsedLine | newFields

    def parse(self, line:str) -> dict:
        parsedLine = self.firstParse(line)
        parsedLine = self.recursiveParsing(parsedLine)

        outputLine = {}

        for key, value in parsedLine.items():
            if key in self.config["outFields"]:
                outputLine[key] = value

        return outputLine

def _test():
    config = {
        "firstParsing": {
            "separatorRegex": ":|;",
            "maxSplits": 2,
            "splitSettings": [
                {
                    "splits": 1,
                    "fields": [
                        "username",
                        "password"
                    ]
                },
                {
                    "splits": 2,
                    "fields": [
                        "username",
                        "email",
                        "password"
                    ]
                }

            ],
        },
        "recursiveParsing": {
            "settings":  [
                {
                    "fieldName": "email",
                    "separatorRegex": "@",
                    "maxSplits": 1,
                    "splitSettings": [
                            {
                                "splits": 1,
                                "fields": [
                                    "emailLocal",
                                    "emailDomain"
                                ]
                            }
                    ]
                }
            ]
        },
        "outFields": [
            "username",
            "emailLocal",
            "emailDomain",
            "password"
        ]
    }
    
    parser = CustomParser(config)

    testLines = [
        "user:pass",
        "user;pass",
        "user:email@domain.com:pass",
        "user:email@domain.com;pass"
    ]

    expectedResults = [
        {
            "username": "user",
            "password": "pass"
        },
        {
            "username": "user",
            "password": "pass"
        },
        {
            "username": "user",
            "emailLocal": "email",
            "emailDomain": "domain.com",
            "password": "pass"
        },
        {
            "username": "user",
            "emailLocal": "email",
            "emailDomain": "domain.com",
            "password": "pass"
        }
    ]

    for line, expectedResult in zip(testLines, expectedResults):
        result = parser.parse(line)
        print(f"Parsing line: {line}. Expected Result: {expectedResult}. Actual Result: {result}")
        assert result == expectedResult
    
    print(f"All tests succeeded")

if __name__ == '__main__':
    _test()
