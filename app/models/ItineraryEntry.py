from bson import ObjectId
from mongoengine import Document, StringField, DateField, ObjectIdField, DecimalField, ReferenceField
from app import db
from app.models.Trip import Trip
import datetime

ACTIVITY_TYPES = ('Flight', 'Accommodations', 'Food', 'Activity', 'Miscellaneous')

class ItineraryEntry(Document):
    id = ObjectIdField(default=ObjectId, required=True, primary_key=True)
    name = StringField(required=True, max_length=50, db_field="name")
    start_time = DateField(required=True, db_field="start_time")
    end_time = DateField(required=True, db_field="end_time")
    activity_type = StringField(required=True, db_field="activity_type", choices=ACTIVITY_TYPES)
    price = DecimalField(min_value=0, max_value=10000000, db_field="price")
    location = StringField(required=True, max_length=75, db_field="location")
    notes = StringField(max_length=1000, db_field="notes")
    trip_id = ReferenceField(Trip)
    # meta = {"collection": "trips", "ordering": ["-start_date"]}
    
    def to_dict(self):
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "activity_type": self.activity_type,
            "price": str(self.price),
            "location": self.location,
            "notes": self.notes
        }
    
    def to_dict_insert(self):
        self.start_time = datetime.datetime.fromisoformat(self.start_time)
        self.end_time = datetime.datetime.fromisoformat(self.end_time)

        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "activity_type": self.activity_type,
            "price": str(self.price),
            "location": self.location,
            "notes": self.notes
        }
    
    def to_dict_with_object_id(self):
        return {
            "_id": str(self["_id"]),
            "name": self["name"],
            "start_time": self["start_time"],
            "end_time": self["end_time"],
            "activity_type": self["activity_type"],
            "price": self["price"],
            "location": self["location"],
            "notes": self["notes"]
        }