import pymongo
import os

class DatabaseConnector():
    def __init__(self, host:str=os.getenv("MONGO_URL"), dbName:str="pentesting", collectionName:str="leaks", relationsCollectionName="relations"):
        self.host = host
        self.dbName = dbName
        self.collectionName = collectionName
        self.relationsCollectionName = relationsCollectionName

        self.client = pymongo.MongoClient(host)
        self.db = self.client[dbName]
        self.collection = self.db[collectionName]        
        self.relationsCollection = self.db[relationsCollectionName]

    def createIndexes(self, indexes, relationsIndexes):
        self.collection.create_index()

    def executeCommands(self, commands:list) -> dict:
        try:
            commandResults = self.collection.bulk_write(commands, ordered=False)
            return {
                "inserted": commandResults.inserted_count,
                "modified": commandResults.modified_count,
                "upserted": commandResults.upserted_count
            }
        except pymongo.errors.BulkWriteError as error:
            print(f"Errors while executing commands: {error}")
            return {
                "inserted": 0,
                "modified": 0,
                "upserted": 0
            }

    def findDocumentsToMerge(self, document, fields, hasEmail):
        findFilter = {"$or": []}

        for field in fields:
            findFilter["$or"].append({field: document[field]})
            
        if hasEmail:
            findFilter["$or"].append({ "email": {"emailLocal": document["emailLocal"], "emailDomain": document["emailDomain"]} })

        mergeDocuments = list(self.relationsCollection.find(findFilter))

        return mergeDocuments

    def getInsertUpdateDocument(self, document, fields, hasEmail):
        insertUpdateDocument = {}

        for field in document:
            insertUpdateDocument[field] = [document[field]]

        if hasEmail:
            insertUpdateDocument["email"] = [{"emailLocal": document["emailLocal"], "emailDomain": document["emailDomain"]}]
            del insertUpdateDocument["emailLocal"]
            del insertUpdateDocument["emailDomain"]

        return insertUpdateDocument

    def mergeDocuments(self, documents):
        mergedDocument = {}

        for document in documents:
            for field in document:
                if field == "_id":
                    continue
                if field not in mergedDocument:
                    mergedDocument[field] = []
                mergedDocument[field] += document[field]

        return mergedDocument

    def mergeOnFields(self, document, fields, hasEmail) -> bool:
        if "password" in document:
            del document["password"]

        foundFields = [x for x in document if x in fields]

        # No merge required
        if len(foundFields) == 0:
            return True

        mergeDocuments = self.findDocumentsToMerge(document, foundFields, hasEmail)

        insertUpdateDocument = self.getInsertUpdateDocument(document, foundFields, hasEmail)

        # No documents to merge. Insert current document and return
        if len(mergeDocuments) == 0:
            self.relationsCollection.insert_one(insertUpdateDocument)
            return True

        updateDocumentId = mergeDocuments[0]["_id"]

        mergedDocument = self.mergeDocuments(mergeDocuments + [insertUpdateDocument])

        if len(mergeDocuments) >= 1:
            for mergeDocument in mergeDocuments[1:]:
                self.relationsCollection.delete_one(mergeDocument)
        
        updateCommand = {"$addToSet": {}}
        for field in mergedDocument:
            updateCommand["$addToSet"][field] = {"$each": mergedDocument[field]}
        self.relationsCollection.update_one({"_id": updateDocumentId}, updateCommand)

        return True