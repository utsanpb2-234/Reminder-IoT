def writeFile(filename, msg, option="a"):
    with open(filename, option) as f:
        f.writelines(f"{msg}")

def writeFileFromList(filename, data, option="a"):
    with open(filename, option) as f:
        for idx, element in enumerate(data):
            element_str = ",".join(str(v) for v in element)
            f.writelines(f"{element_str}\n")
