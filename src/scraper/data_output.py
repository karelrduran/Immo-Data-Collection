import csv
import json
import os


class DataOutput:
    """
    A class to handle data output operations.

    Methods:
    to_json_file(data): Writes data to a JSON file.
    to_csv_file(csv_file_path): Writes data from a JSON file to a CSV file.
    """
    def __init__(self):
        pass

    def to_json_file(self, data) -> None:
        """
        Writes data to a JSON file.

        Args:
        data: The data to be written to the file.
        """
        with open(os.path.join("data", "data.json"), "a", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
            file.write("\n")

    def to_csv_file(self, csv_file_path):
        """
        Writes data from a JSON file to a CSV file.

        Args:
        csv_file_path: The path to the CSV file.
        """
        json_file_path = os.path.join("data", "data.json")
        with open(json_file_path, "r") as json_file:
            data = [json.loads(line) for line in json_file]

        with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
