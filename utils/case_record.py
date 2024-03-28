import time
from file_ops import writeFile


class caseRecord():
    def __init__(self, filename="test.csv") -> None:
        self.file = filename

        # header
        # writeFile(self.file, "case,start,end\n", option="w")

    def run(self):
        while True:
            cmd = input("enter subject+number to start, or q to quit: ")
            if not cmd:
                print("no input")
                continue
            elif cmd == "q":
                break
            else:
                case_info = f"{cmd},s{time.time()}"
                subject_name = cmd
                while True:
                    sign = input(f"enter event for {subject_name} or e to end: ")
                    if not sign:
                        print("no input")
                        continue
                    elif sign == "e":
                        case_info += f",e{time.time()}"
                        break
                    else:
                        # other events
                        case_info += f",{sign}{time.time()}"
                        
                writeFile(self.file, f"{case_info}\n", "a")
        print("case recording stopped.")


if __name__ == "__main__":
    case1 = caseRecord("data/caseinfo.csv")
    case1.run()