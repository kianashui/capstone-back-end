class Trip:
    def __init__(self, id, name, start_date, end_date, itinerary_entries):
        self.id = id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.itinerary_entries = itinerary_entries

    def create_response_body(self):
        response_body = {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "itinerary_entries": self.itinerary_entries
        }
        return response_body