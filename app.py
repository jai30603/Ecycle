import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Setup logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database - PostgreSQL preferred, SQLite fallback for local dev
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    # Handle Heroku style postgresql URL
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if not database_url:
    # SQLite fallback for local development
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecycle.db")
    database_url = f"sqlite:///{db_path}"
    logging.info(f"No DATABASE_URL set, using SQLite: {db_path}")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the SQLAlchemy extension
db.init_app(app)

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()

# Import and register routes
from routes import *

# Create default admin user on startup if one doesn't exist
with app.app_context():
    from models import Admin
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        logging.info("Default admin user created (username: admin, password: admin123)")

