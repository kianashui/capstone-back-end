from flask import Flask
import os
from dotenv import load_dotenv
import pymongo
import dns #needed to use mongodb+srv:// URIs
# from pymongo import MongoClient
import mongoengine
from mongoengine import connect

load_dotenv()
client = pymongo.MongoClient(os.environ.get("MONGODB_CONNECTION_STRING"))
db = client.trip_planner
# print(db.list_collection_names())
connect(host=os.environ.get("MONGODB_CONNECTION_STRING"))
def create_app(test_config=None):
    app = Flask(__name__)
    
    # mongoengine.register_connection(alias='default', db="trip_planner")
    app.config['MONGODB_SETTINGS'] = {'db':'trip_planner', 'alias':'default'}

    from .routes import trip_bp
    app.register_blueprint(trip_bp)

    return app