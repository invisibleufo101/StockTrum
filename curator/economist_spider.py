import scrapy
import json
from scrapy.crawler import CrawlerProcess

class EconomistSpider(scrapy.Spider):
    name = "economist"
    headers = {'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}
    
    MAX_PAGE = 150
    
    async def start(self):
        yield scrapy.Request(
            url = "https://economist.co.kr/article/items/ecn_SC001001000?returnType=ajax&page=1",
            callback = self.parse,
            headers = self.headers,
            meta = {
                "page": 1
            }
        )
        
    # Parse pages with links
    def parse(self, response):
        resp_json = json.loads(response.body)
        articles = resp_json["result"]["items"]
        for article in articles:
            yield {
                "article_id": article["aid"],
                "title": article["title"]
            }
        
        current_page = response.meta["page"]
        if current_page < self.MAX_PAGE:
            yield response.follow(
                url = f"https://economist.co.kr/article/list/ecn_SC013001000?returnType=ajax&limit=10&page={current_page+1}",
                callback = self.parse,
                headers = self.headers,
                meta = {
                    "page": current_page + 1
                }
            )
        

crawler_settings = {
    "AUTOTHROTTLE_ENABLED": True,
    "AUTOTHROTTLE_MAX_DELAY": 15.0,
    "AUTOTHROTTLE_TARGET_CONCURRENCY" : 1.5,
    "RANDOMIZE_DOWNLOAD_DELAY": True,
    "AUTOTHROTTLE_DEBUG": True,
}

process = CrawlerProcess(crawler_settings)
process.crawl(EconomistSpider)
process.start()
        