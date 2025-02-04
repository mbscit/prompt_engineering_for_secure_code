import logging
import sys
from typing import List

from dotenv import load_dotenv

sys.path.append("../sec_prompt_benchmark")

import utils

load_dotenv()


# returns all tasks where the scanners agree have been vulnerable (after applying the filters)
# more than threshold_percentage percent in the reference file
def get_often_filtered_scanners_agree_vulnerable_tasks_in_reference_run(reference_data_file_path: str, threshold_percentage: int) -> List[str]:
    approach = utils.read_approaches_file(reference_data_file_path)
    logging.info(f"Tasks loaded from {approach.id}: {len(approach.tasks)}")

    often_scanners_agree_vulnerable: List[str] = []
    for task in approach.tasks:
        if task.scanners_agree_filtered_vulnerable > len(task.samples) * threshold_percentage / 100:
            often_scanners_agree_vulnerable.append(task.id)

    logging.info(
        f"Tasks that have scanners haver agreed on being filtered vulnerable more than {threshold_percentage} percent in {approach.id} (count: {len(often_scanners_agree_vulnerable)}): ")
    for key in often_scanners_agree_vulnerable:
        logging.info(f"\"{key}\",")
    return often_scanners_agree_vulnerable


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    data_file_path = utils.relative_path_from_root("data/special_insecure_examples.json")
    get_often_filtered_scanners_agree_vulnerable_tasks_in_reference_run(data_file_path, 90)
