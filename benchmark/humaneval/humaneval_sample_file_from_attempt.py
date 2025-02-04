import json
import os

from dotenv import load_dotenv

import utils
from project_types.custom_types import Approach

load_dotenv()

data_file_path = utils.relative_path_from_root(os.getenv("DATA_FILE_PATH"))
approach: Approach = utils.read_approaches_file(data_file_path)

samples = []

for task in approach.tasks:
    for sample in task.samples:
        samples.append({
            "task_id": task.id,
            "completion": sample.extracted_code
        })

# write to jsonl file
output_file_name = approach.id + "-" + approach.model + ".jsonl"
output_file_path = utils.relative_path_from_root("humaneval/samples/" + output_file_name)
with open(output_file_path, "w") as file:
    for sample in samples:
        file.write(f"{json.dumps(sample)}\n")
