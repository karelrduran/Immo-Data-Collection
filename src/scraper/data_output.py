import json


class DataOutput:
    def __init__(self):
        pass

    def to_json_file(self, data) -> None:
        with open(f"data.json", "a", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
            file.write("\n")

    @classmethod
    def to_csv_file(cls) -> None:
        pass
