from flask import Blueprint, jsonify

trip_bp = Blueprint("trip_bp", __name__, url_prefix="/trips")

trips = [
    {
        "name": "San Francisco Road Trip",
        "start_date": "2022-08-19",
        "end_date": "2022-08-28",
        "itinerary_entries": [
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
    },
    {
        "name": "Chile",
        "start_date": "2023-01-28",
        "end_date": "2023-02-12",
        "itinerary_entries": [
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
    }
]


@trip_bp.route("", methods=["GET"])
def get_trips():
    response_body = trips
    return jsonify(response_body), 200