from flask import Blueprint, jsonify, make_response, abort, request
from app.models.ItineraryEntry import ItineraryEntry
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

# BLUEPRINTS
trip_bp = Blueprint("trip_bp", __name__, url_prefix="/trips")
itinerary_entry_bp = Blueprint("itinerary_entry_bp", __name__, url_prefix="/itinerary_entries")

# HELPER FUNCTIONS
def validate_id(id):
    try:
        id = str(id)
    except ValueError:
        abort(make_response({"error": f"{id} is an invalid ID. ID must be a string."}, 400))
    
    # MongoDB object ID string length is 24
    if len(id) != 24:
        abort(make_response({"error": f"{id} is an invalid ID. ID must be a 24 character string."}, 400))

    return id

def create_trip_response_body(trip):
    return {
        "name": trip["name"],
        "start_date": trip["start_date"],
        "end_date": trip["end_date"],
        "itinerary_entries": create_itinerary_entry_response_body(trip["itinerary_entries"]),
        "_id": str(trip["_id"])
    }

def create_itinerary_entry_response_body(itin_entries):
    itinerary_entries = []
    for entry in itin_entries:
        itinerary_entries.append(
            {
                "name": entry["name"],
                "start_time": entry["start_time"],
                "end_time": entry["end_time"],
                "activity_type": entry["activity_type"],
                "price": str(entry["price"]),
                "location": entry["location"]
            }
        )
    return itinerary_entries


# def generate_set_to_update_document(field: str, changes: dict) -> dict:
#     new_set = {}
#     for change in changes.keys():
#         new_set[f"{field}.$.{change}"] = changes[change]
#     return new_set

# def retrieve_object(id, Model):
#     if Model == Trip:
#         items = db["trips"]

#     item = items.find_one({"_id": ObjectId(id)})

#     return item

# TRIP ROUTES
@trip_bp.route("", methods=["GET"])
def get_trips():
    response_body = []

    try:
        trips = db["trips"].find().sort("start_date")
    except:
        return abort(make_response({"error": "Could not execute find method with database"}))
    
    for trip in trips:
        response_body.append(create_trip_response_body(trip))
        
    return jsonify(response_body), 200

@trip_bp.route("/<trip_id>", methods=["GET"])
def get_trip_by_id(trip_id):
    trip_id = validate_id(trip_id)
    
    try:
        trip = db["trips"].find_one({"_id": ObjectId(trip_id)})
    except:
        return abort(make_response({"error": "Could not execute find_one method with database"}))
    
    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    response_body = []
    response_body.append(create_trip_response_body(trip))
    
    return jsonify(response_body), 200

@trip_bp.route("", methods=["POST"])
def add_trip():
    request_body = request.get_json()

    try:
        trip = Trip(
                name=request_body["name"], 
                start_date=request_body["start_date"], 
                end_date=request_body["end_date"]
            )
    except KeyError:
        return abort(make_response({"error": f"Trip info must include name, start_date, and end_date."}, 400))

    trip = trip.to_dict_insert()
    db["trips"].insert_one(trip)
    return jsonify(create_trip_response_body(trip)), 201

@trip_bp.route("/<trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    trip_id = validate_id(trip_id)
    try:
        trip = db["trips"].find_one_and_delete({"_id": ObjectId(trip_id)})
    except:
        return abort(make_response({"error": f"Could not execute find_one_and_delete method with database."}, 400))

    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    return jsonify({"message": f"Trip with id {trip_id} successfully deleted."}), 200

@trip_bp.route("/<trip_id>", methods=["PUT"])
def update_trip(trip_id):
    trip_id = validate_id(trip_id)
    request_body = request.get_json()

    if "name" not in request_body:
        return abort(make_response({"error": f"Trip info must include name."}, 400))
    elif "start_date" not in request_body:
        return abort(make_response({"error": f"Trip info must include start_date."}, 400))
    elif "end_date" not in request_body:
        return abort(make_response({"error": f"Trip info must include end_date."}, 400))
    elif "itinerary_entries" not in request_body:
        return abort(make_response({"error": f"Trip info must include itinerary_entries."}, 400))

    trip = db["trips"].find_one_and_replace({"_id": ObjectId(trip_id)}, request_body)

    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    return jsonify({"message": f"Trip with id {trip_id} successfully updated."}), 200

@itinerary_entry_bp.route("/<trip_id>",methods=["GET"])
def get_itinerary_entries_for_one_trip(trip_id):
    trip_id = validate_id(trip_id)

    try:
        trip = db["trips"].find_one({"_id": ObjectId(trip_id)})
    except:
        return abort(make_response({"error": "Could not execute find_one method with database"}))
    
    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    response_body = create_itinerary_entry_response_body(trip["itinerary_entries"])
    
    return jsonify(response_body), 200

@itinerary_entry_bp.route("/<trip_id>", methods=["POST"])
def add_itinerary_entry_to_trip(trip_id):
    trip_id = validate_id(trip_id)

    request_body = request.get_json()

    try:
        itinerary_entry = ItineraryEntry(
            name=request_body["name"], 
            start_time=request_body["start_time"], 
            end_time=request_body["end_time"],
            activity_type=request_body["activity_type"],
            price=request_body["price"],
            location=request_body["location"],
            trip_id=trip_id
        )
    except KeyError:
        return abort(make_response({"error": f"Itinerary entry must include name, start_time, end_time, activity_type, price, and location."}, 400))

    try:
        trip = db["trips"].find_one({"_id": ObjectId(trip_id)})
    except:
        return abort(make_response({"error": "Could not execute find_one method with database"}))
    
    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    # itinerary_entry = itinerary_entry.to_dict()
    # try:
    #     trip = db["trips"].update_one({"_id": ObjectId(trip_id)},{"$addToSet": {"itinerary_entries": itinerary_entry}},upsert=True)
    # except:
    #     return abort(make_response({"error": "Could not execute update_one method with database"}))
    # response_body = create_itinerary_entry_response_body(trip["itinerary_entries"])
    # return jsonify(response_body), 201
    trip["itinerary_entries"].append(itinerary_entry)
    response_body = create_itinerary_entry_response_body(trip["itinerary_entries"])

    try:
        trip = db["trips"].update_one({"_id": ObjectId(trip_id)},{"$set": {"itinerary_entries": response_body}},upsert=True)
    except:
        return abort(make_response({"error": "Could not execute update_one method with database"}))
    
    if trip.acknowledged == False:
        return abort(make_response({"error": "Could not execute update_one method with database"}))

    return jsonify(response_body), 201




# @trip_bp.route("/<trip_id>", methods=["PATCH"])
# def update_trip_with_itinerary_entry(trip_id):
#     trip_id = validate_id(trip_id)
#     request_body = request.get_json()
    
#     itinerary_entry = ItineraryEntry(
#         name=request_body["name"], 
#         start_time=request_body["start_time"], 
#         end_time=request_body["end_time"],
#         activity_type=request_body["activity_type"],
#         price=request_body["price"],
#         location=request_body["location"],
#         trip_id=trip_id
#     )

#     itinerary_entry = itinerary_entry.to_dict()
#     changes = generate_set_to_update_document("itinerary_entries", itinerary_entry)

#     try:
#         # trip = db["trips"].find_one_and_update({"_id": ObjectId(trip_id)}, {'$set': changes})
#         trip = db["trips"].update_one({"_id": ObjectId(trip_id)}, {'$set': changes})
#     except:
#         return abort(make_response({"error": "Could not execute update_one method with database"}))
    
#     if not trip:
#         return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404)) 
    
#     response_body = []
#     response_body.append(create_trip_response_body(trip))
#     return jsonify(response_body), 200