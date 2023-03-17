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
            self.filter_seat_dex = seat_data['filter_seat_dex']
            self.output_file = seat_data['output_file']
            self.seats = []
            for id, srange in seat_data['name'].items():
                for num in range(srange[0], srange[1] + 1):
                    seat_name = id + str(num)
                    self.seats.append({
                        "seat_name": seat_name,
                        "dex": "L" if any([re.fullmatch(h, seat_name) != None for h in seat_data['left_handed']]) else "R",
                        "allocated": False,
                    })

    def assign_seats(self, EnrolledStudents):
        max_empty = len(self.seats) - len(EnrolledStudents.students)
        if max_empty < 0:
            raise Exception("Not enough seats for students")

        # Sort seats by spacing priority, higher priority seats are assigned spacing first
        self.seats.sort(key=lambda seat: next(
            (i for (i, h) in enumerate(self.spacing_priority)
             if re.fullmatch(h, seat["seat_name"]) != None),
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
                order = [left, ambi, right]  # prioritize left handed students

            pick = next((l for l in order if len(l) > 0), None)

            # if no students left, break
            if pick == None:
                break

            self.seats[i].update({
                k: v for k, v in pick.pop().items() if k not in EnrolledStudents.filter_fields
            })

            self.seats[i]["allocated"] = True  # mark seat as allocated

    def output_seats(self):
        self.seats = natsorted(self.seats, key=lambda seat: seat["seat_name"])
        filter_keys = [] + (["allocated"] if self.filter_unallocated else []) + \
            (["dex"] if self.filter_seat_dex else [])

        keys = [key for key in self.seats[0].keys() if key not in filter_keys]

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
                self.students = list(
                    csv.DictReader(p, delimiter=student_data["delimiter"]))

        random.shuffle(self.students)  # shuffle students to randomize seating


if __name__ == "__main__":
    seats = SeatLoader("config.yaml")
    students = StudentLoader("config.yaml")
    seats.assign_seats(students)
    seats.output_seats()
