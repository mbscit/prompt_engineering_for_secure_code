import logging
import os
import sys
from typing import List

from dotenv import load_dotenv

sys.path.append("../sec_prompt_benchmark")

import utils


def get_never_filtered_vulnerable_tasks(reference_file_path: str) -> List[str]:
    data_folder_path = os.path.dirname(utils.relative_path_from_root(os.getenv("DATA_FILE_PATH")))

    approach = utils.read_approaches_file(reference_file_path)
    logging.info(f"Tasks loaded from reference approach {approach.id}: {len(approach.tasks)}")
    task_ids = [task.id for task in approach.tasks]

    for file in os.listdir(data_folder_path):
        data_file_path = os.path.join(data_folder_path, file)
        # checking if it is a file
        if os.path.isfile(data_file_path):
            approach = utils.read_approaches_file(data_file_path)
            for task in approach.tasks:
                for sample in task.samples:
                    # remove task if vulnerability is found / task is vulnerable
                    if sample.semgrep_filtered_vulnerability_found:
                        if task.id in task_ids:
                            task_ids.remove(task.id)

    logging.info(f"Tasks that have NEVER been classified as vulnerable (count: {len(task_ids)}): ")
    for task_id in task_ids:
        logging.info(f"\"{task_id}\",")

    return task_ids


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    load_dotenv()
    dataset_file_path = utils.relative_path_from_root(os.getenv("DATA_FILE_PATH"))
    get_never_filtered_vulnerable_tasks(dataset_file_path)
