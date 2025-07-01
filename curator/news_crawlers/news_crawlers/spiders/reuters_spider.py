import scrapy
from datetime import datetime
from zoneinfo import ZoneInfo

class ReuterSpider(scrapy.Spider):
    name = "reuters"

    async def start(self):
        for month in range(5, 6)[::-1]:    
            yield scrapy.Request(
                url = f"https://www.reuters.com/sitemap/2025-{month:02}/01/1/",
                callback = self.parse_article_links,
                meta = {"impersonate": "chrome120"}
            )

    def parse_article_links(self, response):
        # Scrape article inks
        article_links = response.css("li[data-testid='FeedListItem']")
        for article_link in article_links:
            category = article_link.css("span[data-testid='KickerLabel'] > span[data-testid='KickerText']::text").get()
            # Only scrape Business related articles
            if category == "Business":
                url = article_link.css("a[data-testid='TitleLink']::attr(href)").get()
                yield response.follow(
                    url = url,
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
            "source": "Reuters",
            "url" : response.url,
            "published_at": response.css("time[data-testid='Body']::attr(datetime)").get(),
            "title" : response.css("h1[data-testid='Heading']::text").get(),
            "content" : response.css("div[data-testid='ArticleBody']").get(),
            "img_url": response.css("div[data-testid='Image'] img::attr(src)").get(),   
        }
        
    def get_past_months(self) -> list:
        current_month = datetime.now(ZoneInfo("America/New_York")).month
        return [f"{m:02d}" for m in range(current_month, 0, -1)]

        
        
