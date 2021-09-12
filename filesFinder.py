import os
import re
import json

class FilesFinder():
    def __init__(self, directory:str="Adding", saveFileName:str=".saveDatabaseImport", filenameRegex:str=r"\.txt$"):
        self.directory = directory
        self.saveFileName = saveFileName
        self.filenameRegex = re.compile(filenameRegex)

        self.lastAddedData = self.loadLastAddedData()
    
    def loadLastAddedData(self) -> dict[str, str]:
        try:
            with open(self.saveFileName, "r") as saveFile:
                saveFileData = json.load(saveFile)
                return saveFileData
        except:
            return {
                "lastAddedFile": None,
                "lastAddedLine": 0
            }

    def getFilenames(self) -> list:
        pwd = os.getcwd()
        path = os.path.join(pwd, self.directory)

        filenames = []
        for root, d_names, f_names in os.walk(path):
            for f in f_names:
                if re.search(self.filenameRegex, f):
                    filenames.append(os.path.join(root, f))

        lastAddedFile = self.lastAddedData["lastAddedFile"]
        if lastAddedFile and lastAddedFile in filenames:
            filenames = filenames[filenames.index(lastAddedFile):]
        return filenames, self.lastAddedData["lastAddedLine"]

    def markAdded(self, filename:str=None, n_lines:int=None) -> bool:
        if filename:            
            self.lastAddedData["lastAddedFile"] = filename
        if n_lines:
            self.lastAddedData["lastAddedLine"] += n_lines

        with open(self.saveFileName, "w") as saveFile:
            json.dump(self.lastAddedData, saveFile)

        return True