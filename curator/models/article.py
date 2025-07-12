from pydantic import BaseModel, HttpUrl, constr, Field, ConfigDict
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2
from typing import Optional, List
from datetime import datetime    


class Category(BaseModel):
    category: str
    
class Sentiment(BaseModel):
    sentiment: str
    status: str

class Summary(BaseModel):
    summary: List[str]

class ArticleMeta(BaseModel):
    category: Category = None
    sentiment: Sentiment = None
    summary: Summary = None

class Article(BaseModel):
    model_config = ConfigDict(
        json_encoders = {
            HttpUrl: lambda v: str(v),
            # datetime:  lambda v: v.replace(tzinfo=None)  # or v.isoformat()
        }
    )
    language: LanguageAlpha2 # ISO 639-1 alpha-2 Language Code Format
    market: CountryAlpha2 # ISO 3166-1 alpha-2 Country Code Format
    source: str
    url: HttpUrl
    published_at: datetime
    title: str
    content: str
    img_url: Optional[HttpUrl]
    meta: ArticleMeta = Field(default_factory = ArticleMeta)
    