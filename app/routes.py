from flask import Blueprint, jsonify, make_response, abort
from app.models.Trip import Trip

sf_itinerary_entries = [
    {
        "activity_type": "Food",
        "name": "Bouchon Bistro",
        "location": "Napa, CA",
        "price": 50.50,
        "start_time": "1:00 PM",
        "end_time": "2:00 PM"
    },
    {
        "activity_type": "Accommodations",
        "name": "Andaz Hyatt Napa",
        "location": "Napa, CA",
        "price": 0,
        "start_time": "2:00 PM",
        "end_time": "3:00 PM"
    }
]

chile_itinerary_entries = [
    {
        "activity_type": "Flight",
        "name": "LAX-LIM flight",
        "location": "Los Angeles, CA",
        "price": 105,
        "start_time": "8:00 PM",
        "end_time": "9:00 PM"
    },
    {
        "activity_type": "Flight",
        "name": "LIM-SCL flight",
        "location": "Lima, Peru",
        "price": 0,
        "start_time": "6:00 AM",
        "end_time": "9:00 AM"
    }
]

trips = [
    Trip(1, "San Francisco Road Trip", "2022-08-19", "2022-08-28", sf_itinerary_entries),
    Trip(2, "Chile", "2023-01-28", "2023-02-12", chile_itinerary_entries)
]

trip_bp = Blueprint("trip_bp", __name__, url_prefix="/trips")

# trips = [
#     {
#         "name": "San Francisco Road Trip",
#         "start_date": "2022-08-19",
#         "end_date": "2022-08-28",
#         "itinerary_entries": [
#             {
#                 "activity_type": "Food",
#                 "name": "Bouchon Bistro",
#                 "location": "Napa, CA",
#                 "price": 50.50,
#                 "start_time": "1:00 PM",
#                 "end_time": "2:00 PM"
#             },
#             {
#                 "activity_type": "Accommodations",
#                 "name": "Andaz Hyatt Napa",
#                 "location": "Napa, CA",
#                 "price": 0,
#                 "start_time": "2:00 PM",
#                 "end_time": "3:00 PM"
#             }
#         ]
#     },
#     {
#         "name": "Chile",
#         "start_date": "2023-01-28",
#         "end_date": "2023-02-12",
#         "itinerary_entries": [
#             {
#                 "activity_type": "Flight",
#                 "name": "LAX-LIM flight",
#                 "location": "Los Angeles, CA",
#                 "price": 105,
#                 "start_time": "8:00 PM",
#                 "end_time": "9:00 PM"
#             },
#             {
#                 "activity_type": "Flight",
#                 "name": "LIM-SCL flight",
#                 "location": "Lima, Peru",
#                 "price": 0,
#                 "start_time": "6:00 AM",
#                 "end_time": "9:00 AM"
#             }
#         ]
#     }
# ]

def validate_id(id):
    try:
        id = int(id)
    except ValueError:
        abort(make_response({"error": f"{id} is an invalid ID. ID must be an integer."}, 400))
    
    return id

# def retrieve_object(id, Model):


@trip_bp.route("", methods=["GET"])
def get_trips():
    response_body = []

    for trip in trips:
        response_body.append(
            {
                "id": trip.id,
                "name": trip.name,
                "start_date": trip.start_date,
                "end_date": trip.end_date,
                "itinerary_entries": trip.itinerary_entries
            }
        )

    return jsonify(response_body), 200

@trip_bp.route("/<trip_id>", methods=["GET"])
def get_one_trip(trip_id):
    trip_id = validate_id(trip_id)
    response_body = []

    for trip in trips:
        if trip.id == trip_id:
            response_body.append(
                {
                    "id": trip.id,
                    "name": trip.name,
                    "start_date": trip.start_date,
                    "end_date": trip.end_date,
                    "itinerary_entries": trip.itinerary_entries
                }
            )
    
    if not response_body:
        return abort(make_response({"error": f"Trip with id {trip_id} not found."}, 404))
    
    return jsonify(response_body), 200