import yaml
import re
import csv


class Seats:
    def __init__(self, file):
        self.file = file
        self.seats = self.load_seats()
        self.max_spacing = self.get_max_spacing()
        self.spacing_priority = self.get_spacing_priority()

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


class Students:
    def __init__(self, config):
        self.config = config
        self.students = self.load_students()

    def load_students(self):
        with open(self.config) as f:
            student_data = yaml.load(f, yaml.CLoader)['students']
            with open(student_data["file"]) as p:
                return list(csv.DictReader(p, delimiter=student_data["delimiter"]))


if __name__ == "__main__":
    seats = Seats("config.yaml")
    students = Students("config.yaml")
