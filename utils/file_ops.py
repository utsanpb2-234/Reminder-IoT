import json


def writeFile(filename, msg, option="a"):
    with open(filename, option) as f:
        f.writelines(f"{msg}")


def writeFileFromList(filename, data, option="a"):
    with open(filename, option) as f:
        for idx, element in enumerate(data):
            element_str = ",".join(str(v) for v in element)
            f.writelines(f"{element_str}\n")


def save_to_json(data, path):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def read_from_json(path):
    with open(path, "r") as file:
        data = json.load(file)
        return data