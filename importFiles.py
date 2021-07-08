import pymongo

# if __name__ == '__main__':
#     from databaseConnector import DatabaseConnector
#     from filesFinder import FilesFinder
#     from parsers.baseParser import Parser
# else:
#     from .databaseConnector import DatabaseConnector
#     from .filesFinder import FilesFinder
#     from .parsers.parser import Parser

from databaseConnector import DatabaseConnector
from filesFinder import FilesFinder
from parsers.baseParser import Parser
# from parsers.autodetectParser import AutodetectParser

class ImportFiles():
    def __init__(self, parser:Parser, databaseConnector:DatabaseConnector=DatabaseConnector(), filesFinder=FilesFinder(), lines_read_at_time:int=10000):
        self.parser = parser
        self.databaseConnector = databaseConnector
        self.filesFinder = filesFinder
        self.lines_read_at_time = lines_read_at_time
        self.mainFields = ["username", "phoneNumber"]
        self.relationalFields = self.mainFields + []

        self.filenames = self.filesFinder.getFilenames()

    def parseNextFile(self) -> list:
        currentFilename = self.filenames.pop(0)
        currentFile = open(currentFilename, "r", encoding="ascii", errors="ignore")

        updateOps = []
        relationsUpdateOps = []
        
        while True:
            lines = currentFile.readlines(self.lines_read_at_time)
            if len(lines) == 0:
                break
            for line in lines:        
                parsedLine = self.parser.parse(line)

                if len(parsedLine) == 0:
                    continue
                if "password" not in parsedLine:
                    continue
                if "emailLocal" in parsedLine and "emailDomain" in parsedLine:
                    updateOps.append(pymongo.UpdateOne({
                                                        "emailLocal": parsedLine["emailLocal"],
                                                        "emailDomain": parsedLine["emailDomain"]
                                                       },
                                                       {
                                                           "$addToSet": {"passwords": parsedLine["password"]}
                                                       }))
                    self.databaseConnector.mergeOnFields(parsedLine, self.relationalFields, True)
                else:
                    for field in self.mainFields:
                        if field in parsedLine:
                            updateOps.append(pymongo.UpdateOne({
                                                        field: parsedLine[field]
                                                       },
                                                       {
                                                           "$addToSet": {"passwords": parsedLine["password"]}
                                                       }))
                            
                            self.databaseConnector.mergeOnFields(parsedLine, [x for x in self.relationalFields if x is not field], False)
                            break
                    
        currentFile.close()
        return updateOps

    def getNextFileName(self) -> str:
        if len(self.filenames) > 0:
            return self.filenames[0]
        return None

    def importNext(self) -> bool:
        addingFilename = self.getNextFileName()
        print(f"Creating update ops for {addingFilename} and inserting relational data.")
        updateOps = self.parseNextFile()

        print(f"Requesting update on {len(updateOps)} lines.")
        updateResult = self.databaseConnector.executeCommands(updateOps)
        self.filesFinder.markAdded(addingFilename)
        print(f"Update completed. Result: {updateResult}")

        return True

    def importAll(self) -> bool:
        while len(self.filenames) > 0:
            self.importNext()
