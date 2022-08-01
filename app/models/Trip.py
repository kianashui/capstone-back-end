from bson import ObjectId
from mongoengine import Document, ListField, StringField, DateField, ObjectIdField
from app import db
import datetime

class Trip(Document):
    id = ObjectIdField(default=ObjectId, primary_key=True)
    name = StringField(required=True, max_length=50, db_field="name")
    start_date = DateField(required=True, db_field="start_date")
    end_date = DateField(required=True, db_field="end_date")
    itinerary_entries = ListField(default=[], db_field="itinerary_entries")
    meta = {"collection": "trips", "ordering": ["-start_date"]}
    
    def to_dict_insert(self):
        # convert start and end dates to date objects
        start_date = self.start_date
        start_year = int(start_date[0:4])
        start_month = int(start_date[5:7])
        start_day = int(start_date[8:10])
        self.start_date = datetime.datetime(start_year, start_month, start_day)

        end_date = self.end_date
        end_year = int(end_date[0:4])
        end_month = int(end_date[5:7])
        end_day = int(end_date[8:10])
        self.end_date = datetime.datetime(end_year, end_month, end_day)
        
        return {
            "name": self.name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "itinerary_entries": self.itinerary_entries
        }
    
    def to_dict_with_object_id(self):
        return {
            "_id": str(self["_id"]),
            "name": self["name"],
            "start_date": self["start_date"],
            "end_date": self["end_date"],
            "itinerary_entries": self["itinerary_entries"]
        }

# class Trip(Document):
#     id = ObjectIdField(default=ObjectId, primary_key=True)
#     name = StringField(required=True, max_length=50)
#     start_date = DateField(required=True)
#     end_date = DateField(required=True)
#     itinerary_entries = ListField(default=[])
#     meta = {"collection": "trips", "ordering": ["-start_date"]}
    
#     def to_dict_insert(self):
#         return {
#             # "_id": self._id,
#             "name": self.name,
#             "start_date": self.start_date,
#             "end_date": self.end_date,
#             "itinerary_entries": self.itinerary_entries
#         }
    
#     def to_dict_with_object_id(self):
#         return {
#             "name": self["name"],
#             "start_date": self["start_date"],
#             "end_date": self["end_date"],
#             "itinerary_entries": self["itinerary_entries"],
#             "_id": str(self["_id"])
#         }
    # def __init__(self, id, name, start_date, end_date, itinerary_entries):
    #     self.id = id
    #     self.name = name
    #     self.start_date = start_date
    #     self.end_date = end_date
    #     self.itinerary_entries = itinerary_entries

    # def create_response_body(self):
    #     response_body = {
    #         "id": self.id,
    #         "name": self.name,
    #         "start_date": self.start_date,
    #         "end_date": self.end_date,
    #         "itinerary_entries": self.itinerary_entries
    #     }
    #     return response_body