from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import Optional
from datetime import datetime
from bson.objectid import ObjectId


class ProcessStatus(str, Enum):
    SUCCESS: str = "SUCCESS"
    PENDING: str = "PENDING"
    FAILED: str = "FAILED"
    
class ArticleSteps(BaseModel):
    completed_at: Optional[datetime] = None
    status: ProcessStatus = ProcessStatus.PENDING

class ArticleProcess(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    
    article_id: ObjectId
    crawled_process: ArticleSteps
    categorization_process: ArticleSteps = Field(default_factory=ArticleSteps)
    sentiment_analysis_process: ArticleSteps = Field(default_factory=ArticleSteps)
    summarization_process: ArticleSteps = Field(default_factory=ArticleSteps)
    
    @field_serializer("article_id")
    def serialize_article_id(self, article_id: ObjectId):
        return str(article_id)