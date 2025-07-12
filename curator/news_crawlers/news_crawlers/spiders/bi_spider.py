import scrapy
import json
from datetime import datetime


class BISpider(scrapy.Spider):
    
    name = "bi"
    source_name = "Business Insider"
    MAX_PAGE = 501
    
    ARTICLE_SECTION_TYPE = set([
        "Finance",
        "Economy",
        "Markets",
        "Tech"
    ])
    custom_settings = {
        "ITEM_PIPELINES": {
            "news_crawlers.pipelines.BICleanerPipeline": 300,
            "news_crawlers.pipelines.RepositoryPipeline": 100,
        }
    }

    # Go to first page
    async def start(self):
        yield scrapy.Request(
            url = "https://markets.businessinsider.com/news",
            callback = self.parse_links,
            meta = {
                "impersonate": "chrome120",
                "page": 1
            }
        )
        
    # Parse the article links in headline section first
    def parse_headline_links(self, response):
        article_links = response.css("div.image-news-list div.image-news-list__story a.image-news-list__image-link::attr(href)").getall()
        for link in article_links:
            yield response.follow(
                url = link,
                callback = self.parse_bi,
                meta = {
                    "impersonate": "chrome120"
                }
            )
            
    def should_stop_crawl(self, date_published_str: str) -> bool:
        datetime_fmt = "%m/%d/%Y %I:%M:%S %p"
        date_published: datetime = datetime.strptime(date_published_str, datetime_fmt)
        if date_published < self.recent_published_date:
            return True
        return False
        
    # Parse JSON response and scrape article links
    def parse_links(self, response):
        if response.meta["page"] == 1:
            self.parse_headline_links(response)
            
        articles = response.css("div.latest-news div.latest-news__story")
        for article in articles:
            if article.css("span.latest-news__source::text").get() == "TipRanks":
                datePublished = article.css("time.latest-news__date::attr(datetime)").get()
                if self.should_stop_crawl(datePublished):
                    return
                
                yield response.follow(
                    url = article.css("h3.latest-news__title a::attr(href)").get(),
                    callback = self.parse_tipranks
                )
            
            elif article.css("span.latest-news__source::text").get() == "Business Insider":
                datePublished = article.css("time.latest-news__date::attr(datetime)").get()
                if self.should_stop_crawl(datePublished):
                    return
                
                yield response.follow(
                    url = article.css("h3.latest-news__title a::attr(href)").get(),
                    callback = self.parse_bi,
                    meta = {
                        "impersonate": "chrome120"
                    }
                )
                
        # Go to next page
        current_page = response.meta["page"]
        if current_page < self.MAX_PAGE:
            yield response.follow(
                url = f"https://markets.businessinsider.com/news?p={current_page+1}",
                callback = self.parse_links,
                meta = {
                    "impersonate": "chrome120",
                    "page": current_page+1
                }
            )
        
    # Parse TipRanks article
    def parse_tipranks(self, response):
        ld_json = json.loads(response.css("main.site-content div.row.equalheights script[type='application/ld+json']::text").get())
        yield {
            "language": "en",
            "market": "US",
            "source": self.source_name,
            "url": response.url,
            "published_at": ld_json.get("datePublished"),
            "title": ld_json.get("headline"),
            "content": response.css("div.news-content").get(),
            "img_url": ld_json.get("image", {}).get("url"),
        }
    
    # Check if the current BI article is stock/economy related
    def is_parseable_article(self, ld_json: dict) -> bool:
        article_type = set(ld_json.get("articleSection").split(","))
        return bool(article_type & self.ARTICLE_SECTION_TYPE)
    
    # Parse Business Insider article
    def parse_bi(self, response):
        ld_json = json.loads(response.css("script[type='application/ld+json']::text").get())
        if self.is_parseable_article(ld_json):
            yield {
                "language": "en",
                "market": "US",
                "source": self.source_name,
                "url": response.url,
                "published_at": response.css("meta[name='datePublished']::attr(content)").get(),
                "title": response.css("section.post-headline h1.headline::text").get(),
                "content": response.css("section[data-component-type='post-body-content']").get(),
                "img_url": ld_json.get("image", {}).get("url"),
            }