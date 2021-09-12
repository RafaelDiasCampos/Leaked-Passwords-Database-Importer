from filesFinder import FilesFinder
from importFiles import ImportFiles
from databaseConnector import DatabaseConnector

from parsers.autodetectParser import AutodetectParser

# from parsers.customParser import CustomParser
# from parsers.configs.emailUserPass import parserConfig

directory = r"Adding\ChineseLeaked\Gaming Databases"

myParser = AutodetectParser()
# myParser = CustomParser(parserConfig)

finder = FilesFinder(directory=directory, filenameRegex=r"\.txt$")
connector = DatabaseConnector()

filesImporter = ImportFiles(parser=myParser, databaseConnector = connector, filesFinder=finder, bytes_read_at_time=3*1024*1024)

filesImporter.importAll()