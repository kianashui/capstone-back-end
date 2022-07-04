from flask import Blueprint, jsonify, make_response, abort, request
from app.models.Trip import Trip
from app import db
from bson.objectid import ObjectId

# sf_itinerary_entries = [
#     {
#         "activity_type": "Food",
#         "name": "Bouchon Bistro",
#         "location": "Napa, CA",
#         "price": 50.50,
#         "start_time": "1:00 PM",
#         "end_time": "2:00 PM"
#     },
#     {
#         "activity_type": "Accommodations",
#         "name": "Andaz Hyatt Napa",
#         "location": "Napa, CA",
#         "price": 0,
#         "start_time": "2:00 PM",
#         "end_time": "3:00 PM"
#     }
# ]

# chile_itinerary_entries = [
#     {
#         "activity_type": "Flight",
#         "name": "LAX-LIM flight",
#         "location": "Los Angeles, CA",
#         "price": 105,
#         "start_time": "8:00 PM",
#         "end_time": "9:00 PM"
#     },
#     {
#         "activity_type": "Flight",
#         "name": "LIM-SCL flight",
#         "location": "Lima, Peru",
#         "price": 0,
#         "start_time": "6:00 AM",
#         "end_time": "9:00 AM"
#     }
# ]
# collection = db.trips
# print(db.list_collection_names())
# for doc in collection.find():
#     print(doc)
#     print(doc["_id"])

trip_bp = Blueprint("trip_bp", __name__, url_prefix="/trips")

def validate_id(id):
    try:
        id = str(id)
    except ValueError:
        abort(make_response({"error": f"{id} is an invalid ID. ID must be a string."}, 400))
    
    return id

def create_trip_response_body(trip):
    itinerary_entries = []
    for entry in trip["itinerary_entries"]:
        itinerary_entries.append(
            {
                "activity_type": entry["activity_type"],
                "name": entry["name"]
            }
        )

    return {
        "name": trip["name"],
        "start_date": trip["start_date"],
        "end_date": trip["end_date"],
        "itinerary_entries": itinerary_entries,
        "_id": str(trip["_id"])
    }

# def retrieve_object(id, Model):
#     if Model == Trip:
#         items = db["trips"]

#     item = items.find_one({"_id": ObjectId(id)})

#     return item

@trip_bp.route("", methods=["GET"])
def get_trips():
    response_body = []
    try:
        for trip in db["trips"].find():
            response_body.append(create_trip_response_body(trip))
    except:
        return abort(make_response({"error": "Could not execute find method with database"}))
        
    return jsonify(response_body), 200

@trip_bp.route("/<trip_id>", methods=["GET"])
def get_trip_by_id(trip_id):
    trip_id = validate_id(trip_id)
    
    response_body = []
    
    try:
        trip = db["trips"].find_one({"_id": ObjectId(trip_id)})
    except:
        return abort(make_response({"error": "Could not execute find_one method with database"}))
    # trip = retrieve_object(trip_id, Trip)
    
    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    response_body.append(create_trip_response_body(trip))
    
    return jsonify(response_body), 200

@trip_bp.route("", methods=["POST"])
def add_trip():
    request_body = request.get_json()
    trip = Trip(
            name=request_body["name"], 
            start_date=request_body["start_date"], 
            end_date=request_body["end_date"]
        )

    trip = trip.to_dict_insert()
    db["trips"].insert_one(trip)
    return jsonify(create_trip_response_body(trip)), 201

@trip_bp.route("/<trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    trip = db["trips"].find_one_and_delete({"_id": ObjectId(trip_id)})

    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    return jsonify({"message": f"Trip with id {trip_id} successfully deleted."}), 200