import logging
import sys
from typing import List

from dotenv import load_dotenv

sys.path.append("../sec_prompt_benchmark")

import utils

load_dotenv()


# returns all tasks that have been vulnerable less than threshold_percentage percent in the reference file
def get_rarely_vulnerable_tasks_from(reference_data_file_path: str, threshold_percentage: int) -> List[str]:
    approach = utils.read_approaches_file(reference_data_file_path)
    logging.info(f"Tasks loaded from {approach.id}: {len(approach.tasks)}")

    rarely_vulnerable_tasks: List[str] = []
    for task in approach.tasks:
        if task.semgrep_vulnerable_samples < len(task.samples) * threshold_percentage / 100:
            rarely_vulnerable_tasks.append(task.id)

    logging.info(
        f"Tasks that have been vulnerable less than {threshold_percentage} percent in {approach.id} (count: {len(rarely_vulnerable_tasks)}): ")
    for key in rarely_vulnerable_tasks:
        logging.info(f"\"{key}\",")
    return rarely_vulnerable_tasks


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    data_file_path = utils.relative_path_from_root("data/benchmark_baseline_100.json")
    get_rarely_vulnerable_tasks_from(data_file_path, 10)
