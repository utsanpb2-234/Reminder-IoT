#!/bin/bash

# presence module

python presence_module_train_test.py --module sink --dataset_date 20241109 --failure_type sensor_failure
python presence_module_train_test.py --module sink --dataset_date 20241109 --failure_type data_pollution
python presence_module_train_test.py --module sink --dataset_date 20241109 --failure_type latency_mismatch

python presence_module_train_test.py --module toilet --dataset_date 20241109 --failure_type sensor_failure
python presence_module_train_test.py --module toilet --dataset_date 20241109 --failure_type data_pollution
python presence_module_train_test.py --module toilet --dataset_date 20241109 --failure_type latency_mismatch

python presence_module_train_test.py --module sink --dataset_date 20250207 --failure_type sensor_failure
python presence_module_train_test.py --module sink --dataset_date 20250207 --failure_type data_pollution
python presence_module_train_test.py --module sink --dataset_date 20250207 --failure_type latency_mismatch

python presence_module_train_test.py --module toilet --dataset_date 20250207 --failure_type sensor_failure
python presence_module_train_test.py --module toilet --dataset_date 20250207 --failure_type data_pollution
python presence_module_train_test.py --module toilet --dataset_date 20250207 --failure_type latency_mismatch

# movement module

python movement_module_train_test.py --module door --dataset_date 20241109 --failure_type sensor_failure
python movement_module_train_test.py --module door --dataset_date 20241109 --failure_type data_pollution
python movement_module_train_test.py --module door --dataset_date 20241109 --failure_type latency_mismatch

python movement_module_train_test.py --module door --dataset_date 20250207 --failure_type sensor_failure
python movement_module_train_test.py --module door --dataset_date 20250207 --failure_type data_pollution
python movement_module_train_test.py --module door --dataset_date 20250207 --failure_type latency_mismatch
