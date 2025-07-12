import logging
from datetime import datetime
from scrapy import Spider
from models.article import Article
from processors.article_cleaner import ArticleCleaner
from repositories.crawler_repository import CrawelerRepository
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
        
class RepositoryPipeline:
    
    def __init__(self):
        load_dotenv()
        self.default_crawl_date: datetime = self.get_default_crawl_recent_date(os.getenv("DEFAULT_CRAWL_RECENT_DATE"))
        
    def get_default_crawl_recent_date(self, default_crawl_datetime_str: str) -> datetime:
        datetime_fmt = "%Y-%m-%dT%H:%M:%S%z"
        return datetime.strptime(default_crawl_datetime_str, datetime_fmt)
        
    def set_crawler_repository(self, spider: Spider) -> None:
        spider.repository = CrawelerRepository()
        
    def set_recent_published_date(self, spider: Spider) -> None:
        # Get the latest published date from each news source
        news_source_name = getattr(spider, "source_name", spider.name)
        recent_published_date: datetime = spider.repository.get_recent_published_date(news_source_name)
        
        # Set spider's recent_published_date if exists, or set it to the default crawl date (2025-01-01)
        spider.recent_published_date = recent_published_date or self.default_crawl_date
    
    def open_spider(self, spider: Spider) -> None:
        self.set_crawler_repository(spider)
        self.set_recent_published_date(spider)
        
    def close_spider(self, spider: Spider) -> None:
        spider.repository.close()
    
class CleanerPipeline:
    
    def __init__(self, cleaner: ArticleCleaner):
        self.cleaner = cleaner
        
    def clean_article_content(self, content: str) -> str:
        return self.cleaner.clean(content)
        
    def create_article_model(self, item) -> Article:
        cleaned_content = self.clean_article_content(item["content"])  
        article = Article(
            language = item["language"],
            market = item["market"],
            source = item["source"],
            url = item["url"],
            published_at = item["published_at"],
            title = item["title"],
            content = cleaned_content,
            img_url = item["img_url"],
        )
        return article
    
    def process_item(self, item, spider):
        try:
            article_model = self.create_article_model(item)
            spider.repository.create_article(article_model)    
        except Exception as e:
            logger.error(e)
            
        return item
        
class BICleanerPipeline(CleanerPipeline):
    
    def __init__(self):
        super().__init__(
            ArticleCleaner(
                remove_selections = {
                    "tag": ["blockquote", "style", "script", "u",],
                    "class": ["in-post-sticky", "tipranks-extra-content", "dad-related-posts-component", "tout-title", "post-promo",],
                    "style": ["text-decoration: underline;",  "padding-top: 5px;"],
                    "css": ["strong > em", "[href*='mailto:']"],
                }
            )
        )
    
class CNBCCleanerPipeline(CleanerPipeline):
    
    def __init__(self):
        super().__init__(
            ArticleCleaner(
                remove_selections = {
                    "tag": ["script", "style", "em"],
                    "class": ["RelatedContent-relatedContent", "RelatedQuotes-relatedQuotes", "DO-widget-wrapper"],
                    "id": ["ArticleBody-MobileAdhesion"],
                    "data-test": ["InlineImage", "InlineVideo"],
                    "css": ["[role='button']", "[class*='Interactive']"],
                }
            )
        )
    
class ReutersCleanerPipeline(CleanerPipeline):
    def __init__(self):
        super().__init__(
            ArticleCleaner(
                remove_selections = {
                    "tag": ["button"],
                    "class": ["ad-banner"],
                    "data-testid": [
                        "NewTabSymbol", 
                        "AuthorBio", 
                        "nx-banner-placement", 
                        "Body", 
                        "Tags", 
                        "ArticleToolbar", 
                        "promo-box",
                        "ContextWidget",
                        "LicenceContentButton",
                        "SignOff"
                    ],
                    "style": ["border:0", "white-space:nowrap"],
                }
            )
        )