from db.mongo_db import MongoDB


db = MongoDB()

# insert_result = db.insert_one(
#     {
#         "language": "en",
#         "url": "https://www.yandex.com"
#     }
# )
# print(insert_result)

# search_result = db.find_many({})
# print(search_result)

# update_result = db.update_one(
#     filter = {
#         "language": "en"
#     },
#     statement = {
#         "$set": {
#             "market": "us"
#         }
#     }
# )

# print(update_result)

# del_result = db.delete_one(
#     {
#         "url": "https://www.google.com"
#     }
# )

res = db.find_many({})
print(res)