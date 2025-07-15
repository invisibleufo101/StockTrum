from typing import Dict
from datetime import datetime, timezone
from repositories.mongo_db import MongoDB
from models.article import Article
from models.article_process import ArticleProcess, ProcessStatus
from bson.objectid import ObjectId
import logging

logger = logging.getLogger(__name__)

class CrawelerRepository(MongoDB):
    
    def save_article(self, article: Article) -> None:
        article_result = self._create_article_document(article)
        if article_result.get("acknowledged"):
            article_result_id = article_result.get("inserted_id")
            self._create_article_process_document(article_result_id)
        
    def _create_article_document(self, article: Article) -> Dict:
        try:
            article_document = article.model_dump()
            article_document["url"] = str(article_document["url"])
            if article_document.get("img_url") is not None:
                article_document["img_url"] = str(article_document["img_url"])
            
            return self.insert_one(
                collection_name = self.ARTICLE_COLLECTION,
                document = article_document
            )
        except Exception as e:
            logger.error(e)
    
    def _create_article_process_document(self, article_id: ObjectId) -> Dict:
        try:
            article_process = ArticleProcess(
                article_id = article_id,
                crawled_process = {
                    "completed_at" : datetime.now(),
                    "status" : ProcessStatus.SUCCESS
                }
            )
            article_process_document = article_process.model_dump()
            return self.insert_one(
                collection_name = self.ARTICLE_PROCESS_COLLECTION,
                document = article_process_document
            )
        except Exception as e:
            logger.error(e)
            
    def get_recent_published_date(self, source_name: str) -> datetime:
        result = {}
        try:
            result = self.find_one(
                collection_name = self.ARTICLE_COLLECTION,
                filter = {"source" : source_name},
                projection = {"published_at" : 1},
                sort = ("published_at", -1)
            )
            # Return datetime string as Timezone aware datetime object
            return result.get("published_at").replace(tzinfo=timezone.utc)
        except Exception as e:
            logger.error(e)