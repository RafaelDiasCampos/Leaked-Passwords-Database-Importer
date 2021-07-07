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

    def executeCommands(self, commands:list) -> dict:
        commandResults = self.collection.bulk_write(commands, ordered=False)
        return {
            "inserted": commandResults.inserted_count,
            "modified": commandResults.modified_count,
            "upserted": commandResults.upserted_count
        }

    def mergeOnFields(self, document, fields, hasEmail) -> bool:
        foundFields = [x for x in document and x in fields]

        findFilter = {"$or": []}

        for foundField in foundFields:
            findFilter["$or"].append({foundField: document[foundField]})
            
        if hasEmail:
            findFilter["$or"].append({"email.emailLocal": document["emailLocal"], "email.emailDomain": document["emailDomain"]})

        mergeDocuments = self.relationsCollection.find(findFilter)

        if len(mergeDocuments) == 0:
            self.relationsCollection.insert_one(document)
            return True

        updateDocument = mergeDocuments.pop()
        if len(mergeDocuments) >= 1:
            for mergeDocument in mergeDocuments:
                for field in mergeDocument:
                    if field not in document:
                        document[field] = mergeDocument[field]
                    else:
                        document[field] += mergeDocument[field]
                self.relationsCollection.delete_one(mergeDocument)
        
        updateCommand = {"$addToSet": {}}
        for field in document:
            updateCommand["$addToSet"][field] = {"$each": document[field]}
        self.relationsCollection.update_one(updateDocument, updateCommand)

        return True