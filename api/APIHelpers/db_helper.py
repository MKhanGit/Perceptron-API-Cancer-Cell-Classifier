import pymongo


class DBConnection:
    def __init__(self, host, port, database, collection):
        self.host = host
        self.port = port
        self.client = pymongo.MongoClient(self.host, self.port)
        self.db = self.client[database]
        self.collection = self.db[collection]

    def record_count(self, document):
        return self.collection.count_documents(document)

    def record_exists(self, document):
        return bool(self.record_count(document))

    def write_document(self, document):
        return self.collection.insert_one(document).inserted_id

    def write_documents(self, documents):
        return self.collection.insert_many(documents).inserted_ids

    def read_document(self, match):
        return self.collection.find_one(match)

    def read_documents(self, match):
        return self.collection.find(match)

    def remove_document(self, match):
        return self.collection.delete_one(match).deleted_count

    def remove_documents(self, match):
        return self.collection.delete_many(match).deleted_count

    def update_document(self, match, update):
        return self.collection.update_one(match, {"$set": update}).modified_count

    def replace_document(self, match):
        return self.collection.find_one_and_replace(match)
