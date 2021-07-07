from filesFinder import FilesFinder
from importFiles import ImportFiles
from databaseConnector import DatabaseConnector
# from parsers.autodetectParser import AutodetectParser
from parsers.customParser import CustomParser

from parsers.configs.grindScape import parserConfig

# directory = r"Adding\reAdd"
directory = r"Adding\grindScape"

# myParser = AutodetectParser()
myParser = CustomParser(parserConfig)
finder = FilesFinder(directory=directory, filenameRegex=r"\.txt$")
connector = DatabaseConnector(dbName="test")

filesImporter = ImportFiles(parser=myParser, databaseConnector = connector, filesFinder=finder)

filesImporter.importAll()