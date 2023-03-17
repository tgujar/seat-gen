import yaml
import re
import csv
import random


class Seats:
    def __init__(self, file):
        self.file = file
        self.seats = self.load_seats()
        self.spacing_priority = self.get_spacing_priority()

    def load_seats(self):
        seats = []
        with open(self.file) as f:
            seat_data = yaml.load(f, yaml.CLoader)['seats']
            left_handed_regex = map(
                lambda reg: re.compile(reg),
                seat_data['left_handed']
            )

            for id, srange in seat_data['name'].items():
                for num in range(srange[0], srange[1] + 1):
                    seat_name = id + str(num)
                    seats.append({
                        "name": seat_name,
                        "dex": "L" if any([h.match(seat_name) for h in left_handed_regex]) else "R",
                        "unallocated": True,
                    })
        return seats

    def get_spacing_priority(self):
        with open(self.file) as f:
            seat_data = yaml.load(f, yaml.CLoader)['seats']
            r = list(map(lambda reg: re.compile(reg),
                     seat_data['spacing_priority']))
            return r

    def assign_seats(self, EnrolledStudents):
        max_empty = len(self.seats) - len(EnrolledStudents.students)
        self.seats.sort(key=lambda seat: next(
            (i for (i, h) in enumerate(self.spacing_priority)
             if h.fullmatch(seat["name"]) != None),
            len(self.spacing_priority)
        ))
        left, right, ambi = [], [], []

        for student in EnrolledStudents.students:
            if student.get(EnrolledStudents.dexCol, "R") == "L":
                left.append(student)
            elif student.get(EnrolledStudents.dexCol, "R") == "R":
                right.append(student)
            else:
                ambi.append(student)

        for i in range(len(self.seats)):
            if i % 2 != 0 and max_empty > 0 and self.seats[i]["dex"] != "L":
                max_empty -= 1
                continue

            order = [right, ambi, left]
            if self.seats[i]["dex"] == "L":
                order = [left, ambi, right]

            pick = next((l for l in order if len(l) > 0), None)
            if pick == None:
                break
            self.seats[i]["student"] = pick.pop()
            self.seats[i]["unallocated"] = False


class Students:
    def __init__(self, config):
        self.config = config
        self.students = self.load_students()
        self.dexCol = self.get_dex_col()
        random.shuffle(self.students)

    def load_students(self):
        with open(self.config) as f:
            student_data = yaml.load(f, yaml.CLoader)['students']
            with open(student_data["file"]) as p:
                return list(csv.DictReader(p, delimiter=student_data["delimiter"]))

    def get_dex_col(self):
        with open(self.config) as f:
            student_data = yaml.load(f, yaml.CLoader)['students']
            return student_data["dex"]


if __name__ == "__main__":
    seats = Seats("config.yaml")
    students = Students("config.yaml")
    seats.assign_seats(students)
    # h = re.compile('[F-L].*')
    # print(seats.spacing_priority[0].fullmatch("F1"))
    # print(next(
    #     (i for (i, h) in enumerate(seats.spacing_priority)
    #      if h.fullmatch("F1") != None),
    #     len(seats.spacing_priority)
    # ))
