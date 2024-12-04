import os
from file_ops import save_to_json, read_from_json
from collections import Counter


def label_by_frame(dir):
    
    # list all files
    for file in os.listdir(dir):

        # pass unwanted files
        if "data_info.json"  not in file:
            continue
        
        file_path = os.path.join(dir, file)
        
        session_name = file.split("_")[0]
        
        session_info_list = read_from_json(file_path)
        
        label = {}

        for session_info in session_info_list:
            for idx in range(session_info["start"], session_info["end"]+1):
                label[f"{session_name}_{idx}"] = session_info["position"]
        label_name = f"{session_name}_label_by_frame.json"
        label_file_path = os.path.join(dir, label_name)
        save_to_json(label, label_file_path)


def get_most_common(data_list):
    result = Counter(data_list)
    return result.most_common(1)[0][0]


def label_by_window(dir, window_size_frame):
    print("This function should be run after you run label_by_frame once.")
    
    subject_label = []
    subject_name = None

    # list all files
    for file in sorted(os.listdir(dir)):

        # pass unwanted files
        if "label_by_frame.json"  not in file:
            continue

        act_seq_frame = []
        act_seq_window = []
        
        file_path = os.path.join(dir, file)
        
        session_name = file.split("_")[0]
        scenario_id = int(session_name[1])
        
        # update subject_name
        if subject_name is None:
            subject_name = session_name[0]
        
        session_info_dict = read_from_json(file_path)
        act_seq_frame = list(session_info_dict.items())
        idx = 0
        while act_seq_frame[idx][1] != "door_in":
            idx += 1

        # get act sequence in window size
        while idx < len(act_seq_frame):
            act_seq_window.append(get_most_common([act[1] for act in act_seq_frame[idx:idx+window_size_frame]]))
            idx += window_size_frame
        
        # pop out empty
        while act_seq_window[-1] == "empty":
            act_seq_window.pop(-1)
        
        session_label = {}
        session_label["session"] = session_name
        session_label["seq"] = act_seq_window
        session_label["subject"] = subject_name
        session_label["toilet"] = "yes" if scenario_id <=2 else "no"

        subject_label.append(session_label)
    
    label_file_path = os.path.join(dir, f"{subject_name}_label_by_window.json")
    save_to_json(subject_label, label_file_path)


if __name__ == "__main__":
    
    # window_size in second
    window_size = 3
    fs = 5
    window_size_frame = window_size*fs

    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    data_dir = os.path.join(parent_dir, "data")

    # data folder
    folder_name = "20241109_8"
    folder = os.path.join(data_dir, folder_name)

    # dataset folder
    dataset_folder = os.path.join(folder, "dataset")

    # label_by_frame(dataset_folder)
    label_by_window(dataset_folder, window_size_frame)
