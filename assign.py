import yaml
import re


class Seats:
    def __init__(self, file):
        self.file = file
        self.seats = self.load_seats()
        self.max_spacing = self.get_max_spacing()
        self.spacing_priority = self.get_spacing_priority()
        print(self.seats[1:5])

    def load_seats(self):
        seats = []
        with open(self.file) as f:
            seat_data = yaml.load(f, yaml.CLoader)['seats']
            left_handed_regex = map(lambda reg: re.compile(
                reg), seat_data['left_handed'])

            for id, srange in seat_data['name'].items():
                for num in range(srange[0], srange[1] + 1):
                    seat_name = id + str(num)
                    seats.append({
                        "name": seat_name,
                        "dex": "L" if any([h.match(seat_name) for h in left_handed_regex]) else "R"
                    })
        return seats

    def get_max_spacing(self):
        with open(self.file) as f:
            seat_data = yaml.load(f, yaml.CLoader)['seats']
            return seat_data['max_spacing']

    def get_spacing_priority(self):
        with open(self.file) as f:
            seat_data = yaml.load(f, yaml.CLoader)['seats']
            return seat_data['spacing_priority']


if __name__ == "__main__":
    seats = Seats("room.yaml")
