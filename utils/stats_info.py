# count the info of label_by_frame.json for each folder
# support folder list
import os
from file_ops import read_from_json
from collections import Counter


def stats_label_by_frame(dir):

    position_list = []
    subject_name = None

    # list all files
    for file in os.listdir(dir):
        
        # pass unwanted files
        if "label_by_frame.json"  not in file:
            continue
        
        file_path = os.path.join(dir, file)
        
        session_name = file.split("_")[0]
        
        # if have not assigned subject_name
        # do it
        if not subject_name:
            subject_name = session_name[0]
        
        session_info_dict = read_from_json(file_path)
        for session in session_info_dict.keys():
            position_list.append(session_info_dict[session])

    stats_info = Counter(position_list)
    print(f"{subject_name}: ")
    for key in sorted(stats_info.keys()):
        print(f"{key}: {stats_info[key]}")

    return stats_info


if __name__ == "__main__":
    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    data_dir = os.path.join(parent_dir, "data")


    folder_list = ["20241109_4", "20241109_6", "20241109_8"]
    stats_whole = None

    for folder_name in folder_list:
        
        # folder path
        folder = os.path.join(data_dir, folder_name)

        # dataset folder
        dataset_folder = os.path.join(folder, "dataset")

        # get single stats
        stats_single = stats_label_by_frame(dataset_folder)

        # aggregate info
        if not stats_whole:
            stats_whole = stats_single
        else:
            stats_whole += stats_single

    print("total: ")
    for key in sorted(stats_whole.keys()):
        print(f"{key}: {stats_whole[key]}")
    print(sum(stats_whole.values()))
