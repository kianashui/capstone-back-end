from bson import ObjectId
from mongoengine import Document, ListField, StringField, DateField, ObjectIdField

class Trip(Document):
    id = ObjectIdField(default=ObjectId, primary_key=True)
    name = StringField(required=True, max_length=50)
    start_date = DateField(required=True)
    end_date = DateField(required=True)
    itinerary_entries = ListField(default=[])
    meta = {"collection": "trips", "ordering": ["-start_date"]}
    
    def to_dict_insert(self):
        return {
            # "_id": self._id,
            "name": self.name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "itinerary_entries": self.itinerary_entries
        }
    
    def to_dict_with_object_id(self):
        return {
            "name": self["name"],
            "start_date": self["start_date"],
            "end_date": self["end_date"],
            "itinerary_entries": self["itinerary_entries"],
            "_id": str(self["_id"])
        }
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