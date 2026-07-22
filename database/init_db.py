"""Initialize MongoDB indexes."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import get_db


def init_indexes():
    app = create_app()
    with app.app_context():
        db = get_db()
        db.users.create_index("email", unique=True)
        db.users.create_index("username", unique=True)
        db.predictions.create_index([("user_email", 1), ("created_at", -1)])
        db.predictions.create_index("primary_label")
        print("MongoDB indexes created.")


if __name__ == "__main__":
    init_indexes()
