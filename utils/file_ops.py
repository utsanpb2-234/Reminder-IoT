def writeFile(filename, msg, option="a"):
    with open(filename, option) as f:
        f.writelines(f"{msg}")
