import json
import os
import sys
from collections import OrderedDict
from dotenv import load_dotenv

import utils

sys.path.append("../sec_prompt_benchmark")

load_dotenv()

data_folder_path = os.path.dirname(utils.relative_path_from_root(os.getenv("DATA_FILE_PATH")))
dataset_file_path = utils.relative_path_from_root(os.getenv("DATASET_FILE_PATH"))

# Function to rename keys and preserve order
def rename_keys_preserve_order(data, renames):
    if isinstance(data, dict):
        new_data = OrderedDict()
        for key, value in data.items():
            new_key = renames.get(key, key)
            new_data[new_key] = value
        return new_data
    return data

# Iterate over files in the data folder
for file in os.listdir(data_folder_path):
    data_file_path = os.path.join(data_folder_path, file)
    # Check if it is a file
    if os.path.isfile(data_file_path):
        with open(data_file_path, 'r') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        # Renaming logic
        if isinstance(data, dict):
            # Rename attributes in the root
            data = rename_keys_preserve_order(data, {
                "expected_cwe_percentage": "semgrep_filtered_vulnerable_percentage",
                "sample_expected_cwe_percentages": "semgrep_filtered_sample_vulnerable_percentages"
            })

            # Rename attributes in tasks
            if "tasks" in data and isinstance(data["tasks"], list):
                for i, task in enumerate(data["tasks"]):
                    data["tasks"][i] = rename_keys_preserve_order(task, {
                        "expected_cwe_samples": "filtered_vulnerable_samples"
                    })

                    if "samples" in task and isinstance(task["samples"], list):
                        for j, sample in enumerate(task["samples"]):
                            task["samples"][j] = rename_keys_preserve_order(sample, {
                                "cwe_filtered_scanner_report": "filtered_scanner_report"
                            })
                            task["samples"][j] = rename_keys_preserve_order(sample, {
                                "expected_cwe_found": "filtered_vulnerability_found"
                            })

        # Save the modified data back to the file
        with open(data_file_path, 'w') as f:
            json.dump(data, f, indent=4)

print("Attribute renaming completed.")
