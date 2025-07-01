import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult
from pymongo import ASCENDING
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


class MongoDB:
    
    def __init__(self):
        load_dotenv()
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_NAME")
        self.collection_name = os.getenv("MONGO_COLLECTION")
        self.client = MongoClient(self.mongo_uri, server_api = ServerApi("1"))
        self.db: Database = self.client[self.db_name]
        self.collection: Collection = self.db[self.collection_name]
        # Create a unique index on article urls
        self.collection.create_index([("url", ASCENDING)], unique = True)
    
    """ CREATE """
    
    def insert_one(self, document: Dict[str, str]) -> Dict[str, Any]:
        result: InsertOneResult = self.collection.insert_one(document)
        return {
            "inserted_id": result.inserted_id, 
            "acknowledged": result.acknowledged 
        }
    
    def insert_many(self, documents: List[Dict[str, str]]) -> Dict[str, Any]:
        results: InsertManyResult = self.collection.insert_many(documents)
        return {
            "inserted_ids": results.inserted_ids, 
            "acknowledged": results.acknowledged
        }
    
    """ READ """
    
    def find_one(
        self,
        filter: Dict[str, Any],
        projection: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        return self.collection.find_one(filter, projection, show_record_id = True)
        
    def find_many(
        self,
        filter: Dict[str, Any],
        projection: Dict[str, Any] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        cursor = self.collection.find(filter, projection, show_record_id = True)
        if limit:
            cursor.limit(limit)
        return list(cursor)
    
    """ UPDATE """
    
    def update_one(
        self, 
        filter: Dict[str, str], 
        statement: Dict[str, Any], 
        upsert: bool = False
    ) -> Dict[str, Any]:
        result = self.collection.update_one(filter, statement, upsert=upsert)
        return {
            "acknowledged": result.acknowledged,
            "matched": result.matched_count,
            "modified": result.modified_count,
            "did_upsert": result.did_upsert
        }
    
    def update_many(
        self, 
        filter: Dict[str, str], 
        statement: Dict[str, Any], 
        upsert: bool = False
    ) -> Dict[str, Any]:
        results = self.collection.update_many(filter, statement, upsert=upsert)
        return {
            "acknowledged": results.acknowledged,
            "matched": results.matched_count,
            "modified": results.modified_count,
            "did_upsert": results.did_upsert
        }
    
    """ DELETE """
    
    def delete_one(self, filter: Dict[str, str]) -> int:
        if not filter:
            return 0
        
        return self.collection.delete_one(filter).deleted_count
    
    def delete_many(self, filter: Dict[str, str]) -> int:
        if not filter:
            return 0
        
        return self.collection.delete_many(filter).deleted_count
    
    def count(self, filter: Optional[Dict[str, Any]]) -> int:
        return self.collection.count_documents(filter)
    
    def close(self) -> None:
        self.client.close()
    
        