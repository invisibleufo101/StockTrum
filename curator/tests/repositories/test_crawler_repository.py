import pytest
import mongomock

from repositories.mongo_db import MongoDB
from repositories.crawler_repository import CrawelerRepository
from models.article import Article
from models.article_process import ArticleProcess, ProcessStatus
from datetime import datetime, timezone
from bson.objectid import ObjectId

@pytest.fixture(autouse=True)
def patch_pymongo(monkeypatch):
    def mongomock_init(self):
        self.client = mongomock.MongoClient()
        self.db = self.client["test_collection"]
    monkeypatch.setattr(MongoDB, "__init__", mongomock_init)
    
@pytest.fixture
def repo():
    return CrawelerRepository()

class TestCrawlerRepository:
    
    TEST_COLLECTION = "test_collection"
    
    def test_create_article_document(self):
        repo = CrawelerRepository()
        test_article = Article(
            language = "en",
            market = "US",
            source = "Test News",
            url = "https://www.example.com/example-news/example-article",
            published_at = datetime(2025, 3, 2, 12, 12, 0),
            title = "Example Title",
            content = "Example Content",
            img_url = "https://example.com/test_img.png"
        )
        article_result = repo._create_article_document(test_article)
        
        assert article_result.get("acknowledged") is True
        assert isinstance(article_result.get("inserted_id"), ObjectId)
        
    def test_create_article_process_document(self):
        repo = CrawelerRepository()
        
        test_article_id = ObjectId('687353a0b0d5fe5f67c9bad2')
        article_process_result = repo._create_article_process_document(
            article_id = test_article_id
        )
        
        print(article_process_result)
        
        assert article_process_result.get("acknowledged") is True
        assert isinstance(article_process_result.get("inserted_id"), ObjectId)
        
    def test_get_recent_published_date(self):
        repo = CrawelerRepository()
        
        test_article = Article(
            language = "en",
            market = "US",
            source = "Test News",
            url = "https://www.example.com/example-news/example-article",
            published_at = datetime(2025, 3, 2, 12, 12, 0),
            title = "Example Title",
            content = "Example Content",
            img_url = "https://example.com/test_img.png"
        )
        
        repo._create_article_document(test_article)
        
        recent_published_date = repo.get_recent_published_date("Test News")
        
        assert isinstance(recent_published_date, datetime)
        assert recent_published_date == datetime(2025, 3, 2, 12, 12, 0, tzinfo=timezone.utc)
        
        
        
        
        
        
    