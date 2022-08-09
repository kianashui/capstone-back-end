from flask import Blueprint, jsonify, make_response, abort, request
from app.models.ItineraryEntry import ItineraryEntry
from app.models.Trip import Trip
from app import db
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from datetime import datetime

# collection = db.trips
# print(db.list_collection_names())
# for doc in collection.find():
#     print(doc)
#     print(doc["_id"])
# ---------------------------------BLUEPRINTS---------------------------------

trip_bp = Blueprint("trip_bp", __name__, url_prefix="/trips")
itinerary_entry_bp = Blueprint("itinerary_entry_bp", __name__, url_prefix="/itinerary_entries")

# ------------------------------HELPER FUNCTIONS------------------------------

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
                "location": entry["location"],
                "notes": entry["notes"]
            }
        )
    return itinerary_entries

def to_dict_insert(entry):
    entry.start_time = datetime.fromisoformat(entry.start_time)
    entry.end_time = datetime.fromisoformat(entry.end_time)

    return {
        "name": entry.name,
        "start_time": entry.start_time,
        "end_time": entry.end_time,
        "activity_type": entry.activity_type,
        "price": entry.price,
        "location": entry.location,
        "notes": entry.notes,
        "user_id": entry.user_id
    }
# def generate_set_to_update_document(field: str, changes: dict) -> dict:
#     new_set = {}
#     for change in changes.keys():
#         new_set[f"{field}.$.{change}"] = changes[change]
#     return new_set

# ---------------------------------TRIP ROUTES---------------------------------
@trip_bp.route("", methods=["GET"])
def get_trips():
    request_header_user_id = request.headers["user_id"]

    response_body = []
    try:
        trips = db["trips"].find({"user_id": request_header_user_id}).sort("start_date")
    except:
        return abort(make_response({"error": "Could not execute find method with database"}))
    
    for trip in trips:
        response_body.append(create_trip_response_body(trip))
        
    return jsonify(response_body), 200

@trip_bp.route("/<trip_id>", methods=["GET"])
def get_trip_by_id(trip_id):
    trip_id = validate_id(trip_id)
    request_header_user_id = request.headers["user_id"]
    
    try:
        trip = db["trips"].find_one({"_id": ObjectId(trip_id), "user_id": request_header_user_id})
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
    request_header_user_id = request.headers["user_id"]

    try:
        trip = Trip(
                name=request_body["name"], 
                start_date=request_body["start_date"], 
                end_date=request_body["end_date"],
                user_id=request_header_user_id
            )
    except KeyError:
        return abort(make_response({"error": f"Trip info must include name, start_date, and end_date."}, 400))

    trip = trip.to_dict_insert()

    try:
        db["trips"].insert_one(trip)    
    except:
        return abort(make_response({"error": f"Could not execute insert_one method with database."}, 400))
    
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

    try:
        trip = Trip(
                name=request_body["name"], 
                start_date=request_body["start_date"], 
                end_date=request_body["end_date"],
                itinerary_entries=request_body["itinerary_entries"]
            )
    except KeyError:
        return abort(make_response({"error": f"Trip info must include name, start_date, end_date, and itinerary_entries."}, 400))

    trip = trip.to_dict_insert()

    try:
        trip = db["trips"].find_one_and_replace({"_id": ObjectId(trip_id)}, trip)
    except:
        return abort(make_response({"error": f"Could not execute find_one_and_replace method with database."}, 400))

    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    return jsonify({"message": f"Trip with id {trip_id} successfully updated."}), 200


# ----------------------------ITINERARY ENTRY ROUTES----------------------------
@trip_bp.route("/<trip_id>/itinerary_entries",methods=["GET"])
def get_itinerary_entries_for_one_trip(trip_id):
    trip_id = validate_id(trip_id)

    request_header_user_id = request.headers["user_id"]

    try:
        trip = db["trips"].find_one({"_id": ObjectId(trip_id), "user_id": request_header_user_id})
    except:
        return abort(make_response({"error": "Could not execute find_one method with database"}))
    
    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    response_body = create_itinerary_entry_response_body(trip["itinerary_entries"])
    
    return jsonify(response_body), 200


# @itinerary_entry_bp.route("/<trip_id>",methods=["GET"])
# def get_itinerary_entries_for_one_trip(trip_id):
#     trip_id = validate_id(trip_id)

#     request_header_user_id = request.headers["user_id"]

#     try:
#         trip = db["trips"].find_one({"_id": ObjectId(trip_id), "user_id": request_header_user_id})
#     except:
#         return abort(make_response({"error": "Could not execute find_one method with database"}))
    
#     if not trip:
#         return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
#     response_body = create_itinerary_entry_response_body(trip["itinerary_entries"])
    
#     return jsonify(response_body), 200

@trip_bp.route("/<trip_id>/itinerary_entries", methods=["POST"])
def add_itinerary_entry_to_trip(trip_id):
    trip_id = validate_id(trip_id)

    request_body = request.get_json()
    request_header_user_id = request.headers["user_id"]

    try:
        itinerary_entry = ItineraryEntry(
            name=request_body["name"], 
            start_time=request_body["start_time"], 
            end_time=request_body["end_time"],
            activity_type=request_body["activity_type"],
            price=request_body["price"],
            location=request_body["location"],
            notes=request_body["notes"],
            user_id=request_header_user_id,
            trip_id=trip_id
        )
    except KeyError:
        return abort(make_response({"error": f"Itinerary entry must include name, start_time, end_time, activity_type, price, location, and notes."}, 400))

    try:
        trip = db["trips"].find_one_and_update({"_id": ObjectId(trip_id)},{"$addToSet": {"itinerary_entries": to_dict_insert(itinerary_entry)}},return_document=ReturnDocument.AFTER)
    except:
        return abort(make_response({"error": "Could not execute find_one_and_update method with database"}), 400)

    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    response_body = create_itinerary_entry_response_body(trip["itinerary_entries"])

    return jsonify(response_body), 201


@itinerary_entry_bp.route("/<trip_id>", methods=["POST"])
def add_itinerary_entry_to_trip(trip_id):
    trip_id = validate_id(trip_id)

    request_body = request.get_json()
    request_header_user_id = request.headers["user_id"]

    try:
        itinerary_entry = ItineraryEntry(
            name=request_body["name"], 
            start_time=request_body["start_time"], 
            end_time=request_body["end_time"],
            activity_type=request_body["activity_type"],
            price=request_body["price"],
            location=request_body["location"],
            notes=request_body["notes"],
            user_id=request_header_user_id,
            trip_id=trip_id
        )
    except KeyError:
        return abort(make_response({"error": f"Itinerary entry must include name, start_time, end_time, activity_type, price, location, and notes."}, 400))

    try:
        trip = db["trips"].find_one_and_update({"_id": ObjectId(trip_id)},{"$addToSet": {"itinerary_entries": to_dict_insert(itinerary_entry)}},return_document=ReturnDocument.AFTER)
    except:
        return abort(make_response({"error": "Could not execute find_one_and_update method with database"}), 400)

    if not trip:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    response_body = create_itinerary_entry_response_body(trip["itinerary_entries"])

    return jsonify(response_body), 201


# @itinerary_entry_bp.route("/<trip_id>", methods=["PATCH"])
# def update_itinerary_entry(trip_id):
#     trip_id = validate_id(trip_id)

#     request_body = request.get_json()

#     try:
#         itinerary_entry = ItineraryEntry(
#             name=request_body["name"], 
#             start_time=request_body["start_time"], 
#             end_time=request_body["end_time"],
#             activity_type=request_body["activity_type"],
#             price=request_body["price"],
#             location=request_body["location"],
#             notes=request_body["notes"],
#             trip_id=trip_id
#         )
#     except KeyError:
#         return abort(make_response({"error": f"Itinerary entry must include name, start_time, end_time, activity_type, price, location, and notes."}, 400))

#     try:
#         trip = db["trips"].find_one_and_update({"_id": ObjectId(trip_id)},{"$addToSet": {"itinerary_entries": to_dict_insert(itinerary_entry)}},return_document=ReturnDocument.AFTER)
#     except:
#         return abort(make_response({"error": "Could not execute find_one_and_update method with database"}), 400)

#     if not trip:
#         return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
#     response_body = create_itinerary_entry_response_body(trip["itinerary_entries"])

#     return jsonify(response_body), 201
    



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