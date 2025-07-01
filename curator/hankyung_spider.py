import scrapy
from scrapy.crawler import CrawlerProcess

class HankyungSpider(scrapy.Spider):
    name = "hankyung"
    MAX_PAGE = 150
    
    async def start(self):
        yield scrapy.Request(
            url = "https://www.hankyung.com/koreamarket/news/all-news?page=1",
            callback = self.parse,
            meta = {
                "page": 1
            }
        )
        
    def parse(self, response):
        article_links = response.css("ul.news-list li figure.thumb a::attr(href)").getall()
        for link in article_links:
            yield response.follow(
                url = link,
                callback = self.parse_article
            )
            
        # Go to next page
        current_page = response.meta["page"]
        if current_page < self.MAX_PAGE:
            yield scrapy.Request(
                url = f"https://www.hankyung.com/koreamarket/news/all-news?page={current_page+1}",
                callback = self.parse,
                meta = {
                    "page": current_page + 1
                }
            )
        
    def parse_article(self, response):
        yield {
            "title": response.css("h1.article-headline span::text").get(),
            "url": response.url
        }

crawler_settings = {
    "AUTOTHROTTLE_ENABLED": True,
    "AUTOTHROTTLE_MAX_DELAY": 15.0,
    "AUTOTHROTTLE_TARGET_CONCURRENCY" : 1.5,
    "RANDOMIZE_DOWNLOAD_DELAY": True,
    "AUTOTHROTTLE_DEBUG": True,
}

process = CrawlerProcess(crawler_settings)
process.crawl(HankyungSpider)
process.start()
        
