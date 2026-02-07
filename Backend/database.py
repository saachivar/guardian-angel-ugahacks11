from pymongo import MongoClient

client = MongoClient("mongodb+srv://db_user:db_pass@guardian-angel.k4xhwty.mongodb.net/")

# Access a database (doesn't exist yet on server)
db = client["my_database"]

# Access a collection (like a table)
collection = db["users"]

# Insert a document (this triggers database creation)
collection.insert_one({"name": "Alice", "age": 25})

print("Inserted document! Database should now exist in MongoDB Atlas.")
