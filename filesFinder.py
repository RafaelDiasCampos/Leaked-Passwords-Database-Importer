import os
import re

class FilesFinder():
    def __init__(self, directory:str="Adding", saveFileName:str=".saveDatabaseImport", filenameRegex:str=r"\.txt$"):
        self.directory = directory
        self.saveFileName = saveFileName
        self.filenameRegex = re.compile(filenameRegex)

        try:
            open(self.saveFileName, "x").close()
        except:
            pass
        self.saveFile = open(self.saveFileName, "r+")

        self.lastAddedFile = self.saveFile.readline()

    def getFilenames(self) -> list:
        pwd = os.getcwd()
        path = os.path.join(pwd, self.directory)

        filenames = []
        for root, d_names, f_names in os.walk(path):
            for f in f_names:
                if re.search(self.filenameRegex, f):
                    filenames.append(os.path.join(root, f))

        if self.lastAddedFile and self.lastAddedFile in filenames:
            filenames = filenames[filenames.index(self.lastAddedFile) + 1:]
        return filenames

    def markAdded(self, filename:str) -> bool:
        self.saveFile.seek(0)
        self.saveFile.write(filename)
        self.saveFile.truncate()

        return True