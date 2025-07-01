import scrapy
import json

class CNBCSpider(scrapy.Spider):
    name = 'cnbc'
    
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'}
    PAGE_SIZE = 30
    MAX_PAGE = 7
    
    async def start(self):
        yield scrapy.Request(
            url = self.get_api_url(0),
            callback = self.parse_links,
            headers = self.HEADERS,
            meta = {"page": 1},
        )
        
    def parse_links(self, response):
        json_response = json.loads(response.body)
        for article in json_response["data"]["assetList"]["assets"]:
            yield scrapy.Request(
                url = article["url"],
                callback = self.parse_article,
                headers = self.HEADERS
            )
            
        # Go to next page via API query offset
        current_page = response.meta["page"]
        if current_page < self.MAX_PAGE:
            yield response.follow(
                url = self.get_api_url(current_page * self.PAGE_SIZE),
                callback = self.parse_links,
                headers = self.HEADERS,
                meta = {"page": current_page + 1}
            )
    
    def parse_article(self, response):
        yield {
            "language": "en",
            "source": "CNBC",
            "url": response.url,
            "published_at": response.css("time[data-testid='published-timestamp']::attr(datetime)").get(), 
            "title": response.css("h1.ArticleHeader-headline::text").get(),
            "content": response.css("div[data-module='ArticleBody']").get(),
            "img_url": response.css("meta[itemprop='primaryImageOfPage']::attr(content)").get(),
        }
            
    def get_api_url(self, offset: int) -> str:
        return f"https://webql-redesign.cnbcfm.com/graphql?operationName=getAssetList&variables=%7B%22id%22%3A%2220910258%22%2C%22offset%22%3A{offset}%2C%22pageSize%22%3A{self.PAGE_SIZE}%2C%22nonFilter%22%3Atrue%2C%22includeNative%22%3Afalse%2C%22include%22%3A%5B%5D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2243ed5bcff58371b2637d1f860e593e2b56295195169a5e46209ba0abb85288b7%22%7D%7D"

# custom_settings = {
#     "AUTOTHROTTLE_ENABLED": True,
#     "AUTOTHROTTLE_MAX_DELAY": 30.0,
#     "AUTOTHROTTLE_TARGET_CONCURRENCY" : 1.5,
#     "AUTOTHROTTLE_DEBUG": True,
# }    



