import scrapy
import json
from datetime import datetime

class CNBCSpider(scrapy.Spider):
    name = "cnbc"
    source_name = "CNBC"
    custom_settings = {
        "ITEM_PIPELINES": {
            "news_crawlers.pipelines.CNBCCleanerPipeline": 300,
            "news_crawlers.pipelines.RepositoryPipeline": 100,
        }
    }
    PAGE_SIZE = 20
    MAX_PAGE_OFFSET = 180
    
    async def start(self):
        yield scrapy.Request(
            url = self.get_api_url(page_offset=0),
            callback = self.parse_links,
            meta = {
                "offset": 0,
                "impersonate": "chrome120"
            }
        )
        
    def should_stop_crawl(self, date_published_str: str) -> bool:
        datetime_fmt = "%Y-%m-%dT%H:%M:%S%z"
        date_published: datetime = datetime.strptime(date_published_str, datetime_fmt)
        if date_published < self.recent_published_date:
            return True
        return False
    
    def parse_links(self, response):
        # Get all article links 
        json_response = json.loads(response.body)
        for article in json_response["data"]["assetList"]["assets"]:
            date_published = article.get("datePublished")
            if self.should_stop_crawl(date_published):
                return
            
            yield scrapy.Request(
                url = article["url"],
                callback = self.parse_article,
                meta = {
                    "impersonate": "chrome120"
                }
            )
        
        # Go to next page via API query offset
        current_offset = response.meta["offset"]
        if current_offset < self.MAX_PAGE_OFFSET:
            yield response.follow(
                url = self.get_api_url(current_offset + self.PAGE_SIZE),
                callback = self.parse_links,
                meta = {
                    "offset": current_offset + self.PAGE_SIZE,
                    "impersonate": "chrome120"
                }
            )
    
    def parse_article(self, response):
        yield {
            "language": "en",
            "market": "US",
            "source": self.source_name,
            "url": response.url,
            "published_at": response.css("time[data-testid='published-timestamp']::attr(datetime)").get(), 
            "title": response.css("h1.ArticleHeader-headline::text").get(),
            "content": response.css("div[data-module='ArticleBody']").get(),
            "img_url": response.css("meta[itemprop='primaryImageOfPage']::attr(content)").get(),
        }
            
    def get_api_url(self, page_offset: int) -> str:
        return f"https://webql-redesign.cnbcfm.com/graphql?operationName=getAssetList&variables=%7B%22id%22%3A%2220910258%22%2C%22offset%22%3A{page_offset}%2C%22pageSize%22%3A{self.PAGE_SIZE}%2C%22nonFilter%22%3Atrue%2C%22includeNative%22%3Afalse%2C%22include%22%3A%5B%5D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2243ed5bcff58371b2637d1f860e593e2b56295195169a5e46209ba0abb85288b7%22%7D%7D"




