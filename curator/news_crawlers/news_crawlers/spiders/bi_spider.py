import scrapy
import json

class BISpider(scrapy.Spider):
    
    name = "bi"
    MAX_PAGE = 60
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'}
    ARTICLE_SECTION_TYPE = set([
        "Finance",
        "Economy",
        "Markets",
        "Tech"
    ])

    # Go to first page
    async def start(self):
        yield scrapy.Request(
            url = "https://markets.businessinsider.com/news",
            callback = self.parse_links,
            meta = {"page": 1}
        )
        
    # Parse the article links in headline section first
    def parse_headline_links(self, response):
        article_links = response.css("div.image-news-list div.image-news-list__story a.image-news-list__image-link::attr(href)").getall()
        for link in article_links:
            yield response.follow(
                url = link,
                callback = self.parse_bi,
                meta = {"page": 1}
            )
        
    # Parse JSON response and scrape article links
    def parse_links(self, response):
        if response.meta["page"] == 1:
            self.parse_headline_links(response)
            
        articles = response.css("div.latest-news div.latest-news__story")
        for article in articles:
            if article.css("span.latest-news__source::text").get() == "TipRanks":
                yield response.follow(
                    url = article.css("h3.latest-news__title a::attr(href)").get(),
                    callback = self.parse_tipranks
                )
            
            elif article.css("span.latest-news__source::text").get() == "Business Insider":
                yield response.follow(
                    url = article.css("h3.latest-news__title a::attr(href)").get(),
                    callback = self.parse_bi
                )
                
        # Go to next page
        current_page = response.meta["page"]
        if current_page < self.MAX_PAGE:
            yield response.follow(
                url = f"https://markets.businessinsider.com/news?p={current_page+1}",
                callback = self.parse_links,
                meta = {"page": current_page+1}
            )
        
    # Parse TipRanks article
    def parse_tipranks(self, response):
        ld_json = json.loads(response.css("main.site-content div.row.equalheights script[type='application/ld+json']::text").get())
        yield {
            "market": "US",
            "source": "Business Insider",
            "url": response.url,
            "published_at": ld_json.get("datePublished"),
            "title": ld_json.get("headline"),
            "content": response.css("div.news-content").get(),
            "image_url": ld_json.get("image", {}).get("url"),
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
                "source": "Business Insider",
                "url": response.url,
                "published_at": ld_json.get("datePublished"),
                "title": ld_json.get("headline"),
                "content": response.css("section[data-component-type='post-body-content']").get(),
                "img_url": ld_json.get("image", {}).get("url"),
            }