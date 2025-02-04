import os
import shutil
import time
import uuid
from typing import List

from dotenv import load_dotenv

import analyze_scan_results
import utils
from compare_attempts import compare
from cwe_resources.structures.enum.detection_effectiveness import DetectionEffectivenessEnumeration
from cwe_resources.structures.enum.detection_method import DetectionMethodEnumeration
from cwe_resources.structures.enum.usage import UsageEnumeration
from filter_config import SEMGREP_SCAN_RESULT_FILTERS, CODEQL_SCAN_RESULT_FILTERS
from helper.task_filters_metadata_based.by_cwe_detection_method import ByCWEDetectionMethod
from helper.task_filters_metadata_based.by_cwe_mapping_level import ByCWEMappingLevel
from helper.task_filters_result_based.get_often_filtered_scanners_agree_non_vulnerable_tasks_in_reference_run import \
    get_often_filtered_scanners_agree_non_vulnerable_tasks_in_reference_run
from helper.task_filters_result_based.get_often_filtered_scanners_agree_vulnerable_tasks_in_reference_run import \
    get_often_filtered_scanners_agree_vulnerable_tasks_in_reference_run
from helper.task_filters_result_based.get_rarely_filtered_vulnerable_tasks_in_reference_run import get_rarely_filtered_vulnerable_tasks_from
from process_all import process_all


def process_ignore(data_folder_path: str, tasks_to_ignore: List[str]):
    tasks_to_ignore = set(tasks_to_ignore)

    working_dir = utils.relative_path_from_root('./tmp_data')
    os.makedirs(working_dir, exist_ok=True)
    subfolder = utils.relative_path_from_root(os.path.join(working_dir, str(uuid.uuid4())))
    os.makedirs(subfolder)

    # make a copy of the data files in a tmp directory
    for file in os.listdir(data_folder_path):
        data_file_path = os.path.join(data_folder_path, file)
        if os.path.isfile(data_file_path):
            shutil.copy(data_file_path, subfolder)

    # remove the ignored tasks from the copied files
    for file in os.listdir(subfolder):
        data_file_path = os.path.join(subfolder, file)
        # checking if it is a file
        if os.path.isfile(data_file_path):
            approach = utils.read_approaches_file(data_file_path)
            remaining_tasks = [task for task in approach.tasks if task.id not in tasks_to_ignore]
            approach.tasks = remaining_tasks
            analyze_scan_results.analyze(approach, SEMGREP_SCAN_RESULT_FILTERS, CODEQL_SCAN_RESULT_FILTERS)
            utils.write_approaches_file(data_file_path, approach)

    print("Original compare result:")
    compare(data_folder_path)
    print("\n")
    print("Filtered compare result:")
    compare(subfolder)

    shutil.rmtree(subfolder)

def process_only(data_folder_path: str, tasks_to_consider: List[str]):
    tasks_to_consider = set(tasks_to_consider)

    working_dir = utils.relative_path_from_root('./tmp_data')
    os.makedirs(working_dir, exist_ok=True)
    subfolder = utils.relative_path_from_root(os.path.join(working_dir, str(uuid.uuid4())))
    os.makedirs(subfolder)

    # make a copy of the data files in a tmp directory
    for file in os.listdir(data_folder_path):
        data_file_path = os.path.join(data_folder_path, file)
        if os.path.isfile(data_file_path):
            shutil.copy(data_file_path, subfolder)

    # remove the ignored tasks from the copied files
    for file in os.listdir(subfolder):
        data_file_path = os.path.join(subfolder, file)
        # checking if it is a file
        if os.path.isfile(data_file_path):
            approach = utils.read_approaches_file(data_file_path)
            remaining_tasks = [task for task in approach.tasks if task.id in tasks_to_consider]
            approach.tasks = remaining_tasks
            analyze_scan_results.analyze(approach, SEMGREP_SCAN_RESULT_FILTERS, CODEQL_SCAN_RESULT_FILTERS)
            utils.write_approaches_file(data_file_path, approach)

    print("Original compare result:")
    compare(data_folder_path)
    print("\n")
    print("Filtered compare result:")
    compare(subfolder)

    shutil.rmtree(subfolder)

if __name__ == "__main__":
    st = time.time()

    load_dotenv()
    data_folder_path = os.path.dirname(utils.relative_path_from_root(os.getenv("DATA_FILE_PATH")))

    dataset_file_path = utils.relative_path_from_root(os.getenv("DATASET_FILE_PATH"))
    dataset = utils.read_dataset_file(dataset_file_path)

    process_all(data_folder_path)
    compare(data_folder_path)

    reference_file_path = utils.relative_path_from_root("data/benchmark_baseline_100.json")

    tasks_to_consider: List[str] = [prompt.id for prompt in dataset]

    tasks_to_consider = ByCWEMappingLevel([UsageEnumeration.ALLOWED]).filtered_from_ids(tasks_to_consider)
    tasks_to_consider = ByCWEDetectionMethod(
        [
         DetectionMethodEnumeration.AUTOMATED_STATIC_ANALYSIS___SOURCE_CODE
         ], [DetectionEffectivenessEnumeration.HIGH]).filtered_from_ids(tasks_to_consider)

    # tasks_to_consider = get_often_filtered_scanners_agree_non_vulnerable_tasks_in_reference_run(
    #     utils.relative_path_from_root("data/special_secure_examples.json"), 90)
    #
    # tasks_to_consider.extend(get_often_filtered_scanners_agree_vulnerable_tasks_in_reference_run(
    #     utils.relative_path_from_root("data/special_insecure_examples.json"), 90))

    process_only(data_folder_path, tasks_to_consider)

    et = time.time()
    print(f"Total execution time: {(et - st):.2f}s")
