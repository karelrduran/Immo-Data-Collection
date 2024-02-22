import csv
import json


class DataOutput:
    def __init__(self):
        pass

    def to_json_file(self, data) -> None:
        with open(f"data.json", "a", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
            file.write("\n")

    def to_csv_file(self, csv_file_path):
        json_file_path = "data.json"
        with open(json_file_path, "r") as json_file:
            data = [json.loads(line) for line in json_file]

        with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
