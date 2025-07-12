import os
from abc import ABC
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult
from pymongo.cursor import Cursor
from pymongo import ASCENDING
from typing import Dict, List, Any, Optional, Tuple, Union
from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING

class MongoDB():
    
    ARTICLE_COLLECTION = "articles"
    ARTICLE_PROCESS_COLLECTION = "article_process"
    
    def __init__(self):
        load_dotenv()
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB_NAME")
        self.client = MongoClient(self.mongo_uri, server_api = ServerApi("1"))
        self.db: Database = self.client[self.db_name]
        
    def _get_collection(self, collection_name: str) -> Collection:
        return self.db[collection_name]
    
    """ CREATE """

    def insert_one(
        self, 
        collection_name: str,
        document: Dict[str, Any]
    ) -> Dict[str, Any]:
        collection: Collection = self._get_collection(collection_name)
        result: InsertOneResult = collection.insert_one(document)
        return {
            "inserted_id": result.inserted_id, 
            "acknowledged": result.acknowledged 
        }
    
    def insert_many(
        self, 
        collection_name: str,
        documents: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        collection: Collection = self._get_collection(collection_name)
        results: InsertManyResult = collection.insert_many(documents)
        return {
            "inserted_ids": results.inserted_ids, 
            "acknowledged": results.acknowledged
        }
    
    """ READ """
    
    def find_one(
        self, 
        collection_name: str, 
        filter: Dict[str, Any] = None, 
        projection: Dict[str, Any] = None,
        sort: Union[Tuple[str, int], List[Tuple[str, int]]] = None
    ) -> Optional[Dict[str, Any]]:
        collection: Collection = self._get_collection(collection_name)
        if sort:
            sort_field = [sort] if isinstance(sort, Tuple) else sort
            cursor: Cursor = collection.find(filter, projection).sort(sort_field).limit(1)
            return next(cursor, None)
        else:
            return collection.find_one(filter, projection)
        
    def find_many(
        self,
        collection_name: str,
        filter: Dict[str, Any] = None,
        projection: Dict[str, Any] = None,
        limit: Optional[int] = None,
        sort: Union[Tuple[str, int], List[Tuple[str, int]]] = None
    ) -> List[Dict[str, Any]]:
        collection = self._get_collection(collection_name)
        cursor = collection.find(filter, projection)
        if limit:
            cursor.limit(limit)
        if sort:
            sort_field = [sort] if isinstance(sort, Tuple) else sort
            cursor.sort(sort_field)
        return list(cursor)
    
    """ UPDATE """
    
    def update_one(
        self, 
        collection_name: str,
        filter: Dict[str, str], 
        statement: Dict[str, Any], 
        upsert: bool = False
    ) -> Dict[str, Any]:
        if not filter:
            raise Exception("Updating without filters is not safe.")
        
        collection = self._get_collection(collection_name)
        result = collection.update_one(filter, statement, upsert=upsert)
        return {
            "acknowledged": result.acknowledged,
            "matched": result.matched_count,
            "modified": result.modified_count,
            "did_upsert": result.did_upsert
        }
    
    def update_many(
        self, 
        collection_name: str,
        filter: Dict[str, str], 
        statement: Dict[str, Any], 
        upsert: bool = False
    ) -> Dict[str, Any]:
        if not filter:
            raise Exception("Updating without filters is not safe.")
    
        collection = self._get_collection(collection_name)
        results = collection.update_many(filter, statement, upsert=upsert)
        return {
            "acknowledged": results.acknowledged,
            "matched": results.matched_count,
            "modified": results.modified_count,
            "did_upsert": results.did_upsert
        }
    
    """ DELETE """
    
    def delete_one(
        self, 
        collection_name: str,
        filter: Dict[str, str]
    ) -> int:
        if not filter:
            raise Exception("Deleting without filters is not safe.")
        
        collection = self._get_collection(collection_name)
        return collection.delete_one(filter).deleted_count
    
    def delete_many(
        self, 
        collection_name: str,
        filter: Dict[str, str]
    ) -> int:
        if not filter:
            raise Exception("Deleting without filters is not safe.")
        
        collection = self._get_collection(collection_name)
        return collection.delete_many(filter).deleted_count
    
    def count(
        self, 
        collection_name: str,
        filter: Optional[Dict[str, Any]]
    ) -> int:
        collection = self._get_collection(collection_name)
        return collection.count_documents(filter)
    
    # Converts pydantic models to dict
    def convert_model_to_dict(self, model: BaseModel) -> Dict[str, Any]:
        return model.model_dump()
    
    def close(self) -> None:
        self.client.close()
    
        