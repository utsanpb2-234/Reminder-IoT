import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import sys
import time
import numpy as np
import pandas as pd
from record_config import sensors_info
from data_record import Sensor
import io
from file_ops import save_to_json


def print_classes(key, class_list):
    info = f"Pick one {key} from the following:\n"
    for idx, label in enumerate(class_list):
        info += f"{idx}. {label}\n"
    return info


def get_int_input(msg, min_value=None, max_value=None):
    input_int = None
    while True:
        input_str = input(msg)
        try:
            input_int = int(input_str)
            if (min_value and input_int < min_value) or (max_value and input_int > max_value):
                print("Invalid input, try again.")
            else:
                break
        except:
            print("Invalid input, try again.")
    
    return input_int


def generate_info(work_dir, multi_classes:dict, save_dir, redo=False):
    
    for file in sorted(os.listdir(work_dir)):
        file_path = os.path.join(work_dir, file)
        if os.path.isdir(file_path):
            data_info_file = f"{os.path.join(save_dir, file)}_data_info.json"
            
            # check if need to redo
            if not redo and os.path.exists(data_info_file):
                print(f"{data_info_file} exists, skip.")
                continue
            
            print(f"Generating data info for {file}")
            data_info = []
            
            # each loop is a data info card, namely data slice
            while True:
                data_slice = {}
                cmd = input("Input a to add new, or q to quit, or e to end the program: ")
                if cmd == "a":
                    
                    # get frame info
                    data_slice["start"] = get_int_input("Input the start frame (inclusive): ")
                    data_slice["end"] = get_int_input("Input the end frame (inclusive): ")

                    # get labels
                    for key in multi_classes.keys():
                        prompt = print_classes(key, multi_classes[key])
                        num_values = len(multi_classes[key])
                        data_slice[key] = multi_classes[key][get_int_input(prompt, min_value=0, max_value=num_values-1)]
                    
                    data_info.append(data_slice)

                elif cmd == "q":
                    break
                elif cmd == "e":
                    print("Exit the program.")
                    sys.exit(0)
                else:
                    print("Wrong input, try again.")
            
            print(data_info, end="\n\n\n")
            if data_info:
                save_to_json(data_info, data_info_file)


if __name__ == "__main__":
    multi_classes = {
        "position": ["empty", "door_in", "door_out", "sink", "toilet", "other"],
    }

    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    data_dir = os.path.join(parent_dir, "data")

    # data folder
    folder_name = "20241109_4"
    folder = os.path.join(data_dir, folder_name)

    # dataset dir
    dataset_dir  = os.path.join(folder, "dataset")

    # pic dir
    pic_dir = os.path.join(folder, "pics")
    
    # generate info
    generate_info(pic_dir, multi_classes, dataset_dir)
