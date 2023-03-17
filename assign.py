import yaml
import re
import csv
import random
from natsort import natsorted


class SeatLoader:
    def __init__(self, file):
        with open(file) as f:
            seat_data = yaml.load(f, yaml.CLoader)['seats']
            self.spacing_priority = seat_data['spacing_priority']
            self.filter_unallocated = seat_data['filter_unallocated']
            self.output_file = seat_data['output_file']
            self.seats = []
            for id, srange in seat_data['name'].items():
                for num in range(srange[0], srange[1] + 1):
                    seat_name = id + str(num)
                    self.seats.append({
                        "name": seat_name,
                        "dex": "L" if any([re.fullmatch(h, seat_name) != None for h in seat_data['left_handed']]) else "R",
                        "allocated": False,
                    })

    def assign_seats(self, EnrolledStudents):
        max_empty = len(self.seats) - len(EnrolledStudents.students)
        self.seats.sort(key=lambda seat: next(
            (i for (i, h) in enumerate(self.spacing_priority)
             if re.fullmatch(h, seat["name"]) != None),
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
            self.seats[i].update({
                k: v for k, v in pick.pop().items() if k not in EnrolledStudents.filter_fields
            })
            self.seats[i]["allocated"] = True
        self.seats = natsorted(self.seats, key=lambda seat: seat["name"])

    def output_seats(self):
        keys = self.seats[0].keys()
        if self.filter_unallocated:
            keys = [key for key in self.seats[0].keys() if key != "allocated"]
        with open(self.output_file, "w") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            if self.filter_unallocated:
                writer.writerows(
                    filter(lambda seat: seat["allocated"], self.seats))
                return
            writer.writerows(self.seats)


class StudentLoader:
    def __init__(self, config):
        with open(config) as f:
            student_data = yaml.load(f, yaml.CLoader)['students']
            self.dexCol = student_data["dex"]
            self.filter_fields = student_data["filter_fields"]
            with open(student_data["file"]) as p:
                self.students = list(csv.DictReader(
                    p, delimiter=student_data["delimiter"]))
        random.shuffle(self.students)


if __name__ == "__main__":
    seats = SeatLoader("config.yaml")
    students = StudentLoader("config.yaml")
    seats.assign_seats(students)
    seats.output_seats()
