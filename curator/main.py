from repositories.mongo_db import MongoDB
from repositories.crawler_repository import CrawelerRepository
repo = CrawelerRepository()

recents = repo.get_recent_published_date("CNBC")
print(recents)
print(type(recents))

# db = MongoDB()
# article = db.find_one(
#     collection_name = "articles",
#     filter = {
#         "source": "CNBC"
#     }
# )

# print(article.get("published_at"))
# print(type(article.get("published_at")))