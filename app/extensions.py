"""Flask extensions and shared clients."""
from pymongo import MongoClient

mongo_client = None
db = None


def init_mongo(app):
    """Initialize MongoDB connection."""
    global mongo_client, db
    if app.config.get("TESTING"):
        import mongomock

        mongo_client = mongomock.MongoClient()
        db_name = app.config["MONGO_URI"].rsplit("/", 1)[-1]
        db = mongo_client[db_name]
        return
    mongo_client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=3000)
    db = mongo_client.get_default_database()


def get_db():
    """Return MongoDB database handle."""
    return db
