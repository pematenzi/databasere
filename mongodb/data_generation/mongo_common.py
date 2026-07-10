"""
Shared MongoDB connection helper.
Tries a real mongod first; falls back to a shared in-memory mongomock client
"""
_client = None

def get_client():
    global _client
    if _client is not None:
        return _client
    try:
        from pymongo import MongoClient
        c = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=500)
        c.admin.command("ping")
        print("[mongo_common] Connected to a real MongoDB server.")
        _client = c
    except Exception:
        import mongomock
        print("[mongo_common] No local mongod found - using mongomock in-memory engine.")
        _client = mongomock.MongoClient()
    return _client

def get_db():
    return get_client().university_portal
