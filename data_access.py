import json

def read_file():
    with open("data.json", "r") as f:
        return json.load(f)

def write_file(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
