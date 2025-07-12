import scrapy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, List
from urllib.parse import urlparse

class ReuterSpider(scrapy.Spider):
    
    name = "reuters"
    source_name = "Reuters"
    ARTICLE_SECTION_TYPE = set([
        "world",
        "business",
        "markets",
        "technology"
    ])
    custom_settings = {
        "ITEM_PIPELINES": {
            "news_crawlers.pipelines.ReutersCleanerPipeline": 300,
            "news_crawlers.pipelines.RepositoryPipeline": 100,
        }
    }

    def _get_past_dates(self) -> List[Dict[str, str]]:
        past_dates = []
        current_datetime = datetime.now()
        end_datetime = self.recent_published_date
        while current_datetime >= end_datetime:
            past_dates.append({
                "year": current_datetime.year,
                "month": f"{current_datetime.month:02}",
                "day": f"{current_datetime.day:02d}"
            })
            current_datetime -= timedelta(days=1)
        return past_dates

    async def start(self):
        past_dates = self._get_past_dates()
        for past_date in past_dates:
            yield scrapy.Request(
                url = f"https://www.reuters.com/sitemap/{past_date["year"]}-{past_date["month"]}/{past_date["day"]}/1/",
                callback = self.parse_article_links,
                meta = {"impersonate": "chrome120"}
            )

    def do_articles_exist(self, response) -> bool:
        if response.css("div[data-testid='EmptyPage']").get():
            return False
        return True
    
    def is_crawlable_article(self, url: str) -> bool:
        parsed_url = urlparse(url)
        news_categories = set(parsed_url.path.strip("/").split("/")[:-1])
        if news_categories & self.ARTICLE_SECTION_TYPE:
            return True
        return False
    
    def parse_article_links(self, response):
        if not self.do_articles_exist(response):
            return
                
        # Scrape article inks
        article_links = response.css("li[data-testid='FeedListItem'] a[data-testid='TitleLink']::attr(href)").getall()
        for article_link in article_links:
            # Only scrape Business related articles
            if self.is_crawlable_article(article_link):
                yield response.follow(
                    url = article_link,
                    callback = self.parse_article,
                    meta = {"impersonate" : "chrome120"}
                )
                
        # Look for next page
        next_page_link = response.css("div[data-testid='SitemapFeedPagination'] a[data-testid='SitemapFeedPaginationNextButton']::attr(href)").get()
        if next_page_link is not None:
            yield response.follow(
                url = next_page_link,
                callback = self.parse_article_links,
                meta = {"impersonate": "chrome120"}
            )
            
    def parse_article(self, response):
        yield {    
            "language": "en",
            "market": "US",
            "source": self.source_name,
            "url" : response.url,
            "published_at": response.css("time[data-testid='Body']::attr(datetime)").get(),
            "title" : response.css("h1[data-testid='Heading']::text").get(),
            "content" : response.css("div[data-testid='ArticleBody']").get(),
            "img_url": response.css("div[data-testid='Image'] img::attr(src)").get(),   
        }
        
    

        
        
