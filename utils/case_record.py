import time
from file_ops import writeFile


class caseRecord():
    def __init__(self, filename="test.csv") -> None:
        self.file = filename

        # header
        writeFile(self.file, "case,start,end\n", option="w")

    def run(self):
        while True:
            cmd = input("enter subject+number to start, or q to quit: ")
            if not cmd:
                print("no input")
                continue
            elif cmd == "q":
                break
            else:
                time_start = time.time()
                while True:
                    stop_sign = input("enter s to stop current case: ")
                    if (not stop_sign) or (stop_sign != "s"):
                        print("invalid input")
                        continue
                    else:
                        break
                time_stop = time.time()
                case_info = f"{cmd},{time_start},{time_stop}\n"
                writeFile(self.file, case_info, "a")
        print("case recording stopped.")


if __name__ == "__main__":
    case1 = caseRecord("data/caseinfo.csv")
    case1.run()