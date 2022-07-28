from flask import Flask
import os
from dotenv import load_dotenv
import pymongo
import dns #needed to use mongodb+srv:// URIs
from pymongo import MongoClient
from flask_cors import CORS
# from flask_mongoengine import MongoEngine

load_dotenv()
client = pymongo.MongoClient(os.environ.get("MONGODB_CONNECTION_STRING"))
db = client.trip_planner

def create_app(test_config=None):
    app = Flask(__name__)
    
    app.config['MONGODB_SETTINGS'] = {'host': os.environ.get("MONGODB_CONNECTION_STRING")}

    from .routes import trip_bp
    app.register_blueprint(trip_bp)

    from .routes import itinerary_entry_bp
    app.register_blueprint(itinerary_entry_bp)
    
    CORS(app)
    
    return app