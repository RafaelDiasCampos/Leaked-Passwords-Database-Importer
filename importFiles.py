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
    def __init__(self, parser:Parser, databaseConnector:DatabaseConnector=DatabaseConnector(), filesFinder=FilesFinder(), bytes_read_at_time:int=10000):
        self.parser = parser
        self.databaseConnector = databaseConnector
        self.filesFinder = filesFinder
        self.bytes_read_at_time = bytes_read_at_time
        self.mainFields = ["username", "phoneNumber"]
        self.relationalFields = self.mainFields + []

        self.filenames, self.lastAddedLine = self.filesFinder.getFilenames()

    def parseFile(self, file) -> list:         
        while True:
            updateOps = []
            relationsUpdateOps = []

            lines = file.readlines(self.bytes_read_at_time)
            n_lines = len(lines)

            if n_lines == 0:
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

            print(f"Requesting update on {n_lines} lines.")
            updateResult = self.databaseConnector.executeCommands(updateOps)

            print(f"Update completed. Result: {updateResult}")

            try:
                self.filesFinder.markAdded(n_lines = n_lines)
            except:
                print(f"Error while marking file as added. Will retry on next file")
                    
        return True

    def importAll(self) -> bool:
        if len(self.filenames) > 0:
            firstFileName = self.filenames.pop(0)
            
            with open(firstFileName, "r", encoding="utf-8", errors="ignore") as firstFile:
                for i in range(self.lastAddedLine):
                    firstFile.readline()
                
                try:
                    print(f"Starting import with file {firstFileName} at line {self.lastAddedLine}.")
                except:
                    print(f"Starting import with non utf-8 file at line {self.lastAddedLine}.")

                self.parseFile(firstFile)

        while len(self.filenames) > 0:
            currentFilename = self.filenames.pop(0)
            with open(currentFilename, "r", encoding="utf-8", errors="ignore") as currentFile:
                try:
                    print(f"Creating update ops for {currentFilename} and inserting relational data.")
                except:
                    print(f"Creating update ops for non utf-8 file and inserting relational data.")
                
                try:
                    self.filesFinder.markAdded(filename=currentFilename)
                except:
                    print(f"Error while marking file as added. Will retry on next file")

                self.parseFile(currentFile)
