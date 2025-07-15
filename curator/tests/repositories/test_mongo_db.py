import pytest
import mongomock
from exceptions.repositories.unsafe_operation_exception import UnsafeOperationException

from repositories.mongo_db import MongoDB

"""
Monkey-patch MongoDB.__init__ to use mongomock for an in-memory test database.
"""
@pytest.fixture(autouse=True)
def patch_pymongo(monkeypatch):
    def mongomock_init(self):
        self.client = mongomock.MongoClient()
        self.db = self.client["test_collection"]
    monkeypatch.setattr(MongoDB, "__init__", mongomock_init)

class TestMongoDB:
    """
    Unit tests for the MongoDB class methods, including:
    - insert_one / find_one
    - insert_many / find_many
    - update_one and update_many with upsert
    - delete_one / delete_many
    - update/delete safety measures (raises exceptions on empty filters)
    """
    
    TEST_COLLECTION = "test_collection"
    
    def test_insert_and_find_one(self):
        """
        Ensure that inserting a single document is acknowledged,
        and the document can be retrieved via its ObjectId.
        """
        
        db = MongoDB()
        test_doc = {"foo": "bar", "num": 11}
        
        # Inserting one test document
        result = db.insert_one(
            collection_name = "test_collection", 
            document = test_doc
        )
        
        # Assert that the operation was successful
        assert result.get("acknowledged") == True
        inserted_id = result.get("inserted_id")
        
        # Try to find the inserted document in the collection
        found_result = db.find_one(
            collection_name = "test_collection", 
            filter = {
                "_id": inserted_id
            }
        )
        
        # Assert that the test document is found in collection
        assert found_result is not None
        assert found_result["foo"] == "bar"
        assert found_result["num"] == 11
        
        db.close()
        
    def test_insert_and_find_many(self):    
        """
        Test bulk insert of multiple documents and retrieval of all matching docs.
        """
        
        db = MongoDB()
        test_docs = [
            {"num": 1, "foo": "bar"},
            {"num": 2, "foo": "bar"},
            {"num": 3, "foo": "bar"},
            {"num": 4, "foo": "bar"},
            {"num": 5, "foo": "bar"}
        ]
        many_results = db.insert_many(
            collection_name = self.TEST_COLLECTION,
            documents=test_docs
        )
        
        assert many_results.get("acknowledged") == True
        assert isinstance(many_results.get("inserted_ids"), list)
        
        found_results = db.find_many(
            collection_name = self.TEST_COLLECTION,
            filter = {
                "foo": "bar"
            }
        )
        
        inserted_ids = many_results.get("inserted_ids")
        found_ids = [result.get("_id") for result in found_results]
        assert inserted_ids == found_ids
        
    def test_update_one(self):
        """
        Ensure update_many updates all matching documents,
        without upsert, and returns correct counts.
        """
        
        db = MongoDB()
        test_doc = {"foo": "bar"}
        db.insert_one(
            collection_name = self.TEST_COLLECTION,
            document = test_doc
        )
        
        update_result = db.update_one(
            collection_name = self.TEST_COLLECTION,
            filter = {
                "foo": "bar"
            },
            statement = {
                "$set": {
                    "foo": "baz"
                }
            },
            upsert = True
        )
        
        assert update_result.get("acknowledged") == True
        assert update_result.get("matched") == 1
        assert update_result.get("modified") == 1
        assert update_result.get("did_upsert") == True
        
        found_update_result = db.find_one(
            collection_name = self.TEST_COLLECTION,
            filter = {
                "foo": "baz"
            }
        )
        
        assert found_update_result.get("foo") == "baz"
        
    def test_update_many(self):
        """
        Ensure update_many updates all matching documents,
        without upsert, and returns correct counts.
        """
        
        db = MongoDB()
        test_docs = [
            {"num": 1, "foo": "bar"},
            {"num": 2, "foo": "bar"},
            {"num": 3, "foo": "bar"},
            {"num": 4, "foo": "bar"},
            {"num": 5, "foo": "bar"},
            {"num": 6, "baz": "bar"}
        ]
        db.insert_many(
            collection_name = self.TEST_COLLECTION,
            documents = test_docs
        )
        
        update_results = db.update_many(
            collection_name = self.TEST_COLLECTION,
            filter = {
                "foo": "bar"
            },
            statement = {
                "$set": {
                    "foo": "baz"
                }
            },
            upsert = False
        )
        
        assert update_results.get("acknowledged") == True
        assert update_results.get("matched") == 5
        assert update_results.get("modified") == 5
        # Did upserting take place? Yes
        assert update_results.get("did_upsert") == True 
        
        found_update_results = db.find_many(
            collection_name = self.TEST_COLLECTION,
            filter = {
                "foo": "baz"
            }
        )
        
        found_update_foo = [result.get("foo") for result in found_update_results]
        
        assert found_update_foo == ["baz", "baz", "baz", "baz", "baz"]
    
    def test_delete_one(self):
        """
        Test deletion of a single document by filter, returning count == 1.
        """
        
        db = MongoDB()
        test_doc = {
            "foo": "bar"
        }
        
        # Insert one test document
        db.insert_one(
            collection_name = self.TEST_COLLECTION,
            document = test_doc
        )
        
        # Delete the corresponding document
        result = db.delete_one(
            collection_name = self.TEST_COLLECTION,
            filter = {
                "foo": "bar"
            }
        )
        
        # Assert that only 1 document has been deleted
        assert result == 1
        
    def test_delete_many(self):
        """
        Verify delete_many removes all matching documents.
        """
        
        db = MongoDB()
        test_docs = [
            {"num": 1, "foo": "bar"},
            {"num": 2, "foo": "bar"},
            {"num": 3, "foo": "bar"},
            {"num": 4, "foo": "bar"},
            {"num": 5, "foo": "bar"}
        ]
        db.insert_many(
            collection_name=self.TEST_COLLECTION,
            documents=test_docs
        )
        
        delete_results = db.delete_many(
            collection_name=self.TEST_COLLECTION,
            filter={
                "foo": "bar"
            }
        )
        
        assert delete_results == len(test_docs)
        
    def test_empty_update_safety_measure(self):
        """
        Confirm that update operations with empty filter raise UnsafeOperationException.
        """
        
        db = MongoDB()
        with pytest.raises(UnsafeOperationException) as error_info:
            db.update_one(
                collection_name=self.TEST_COLLECTION,
                filter = {},
                statement = {
                    "foo": "bar"
                }
            )
            
        assert str(error_info.value) == "Updating without filters is not safe."
        
        with pytest.raises(UnsafeOperationException) as error_info:
            db.update_many(
                collection_name=self.TEST_COLLECTION,
                filter={},
                statement={
                    "foo": "bar"
                }
            )
        
        assert str(error_info.value) == "Updating without filters is not safe."
        
    def test_empty_delete_safety_measure(self):
        """
        Confirm that delete operations with empty filter raise UnsafeOperationException.
        """
        
        db = MongoDB()
        with pytest.raises(UnsafeOperationException) as error_info:
            db.delete_one(
                collection_name=self.TEST_COLLECTION,
                filter = {}
            )
            
        assert str(error_info.value) == "Deleting without filters is not safe."
        
        with pytest.raises(UnsafeOperationException) as error_info:
            db.delete_many(
                collection_name=self.TEST_COLLECTION,
                filter={}
            )
        
        assert str(error_info.value) == "Deleting without filters is not safe."
        
    
            
        