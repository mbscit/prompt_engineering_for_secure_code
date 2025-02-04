import json
import os
import sys

from dotenv import load_dotenv

sys.path.append("../sec_prompt_benchmark")

import utils

load_dotenv()

if __name__ == "__main__":
    dataset_file_path = utils.relative_path_from_root(os.getenv("DATASET_FILE_PATH"))

    dataset = utils.read_dataset_file(dataset_file_path)

    security_eval_dataset_path = utils.relative_path_from_root(
        os.path.join("datasets", "origins", "SecurityEval", "SecurityEval-dataset.jsonl"))

    security_eval_entries = {}
    with open(security_eval_dataset_path, 'r') as f:
        for line in f:
            entry = json.loads(line)
            # Use the "ID" field as the key and the rest of the entry as the value
            key = entry.pop("ID")
            # remove .py ending from key to match format used in the dataset
            key = key[:-3] if key.endswith(".py") else key
            security_eval_entries[key] = entry

    for prompt in dataset:
        if prompt.source == "SecurityEval" and prompt.language == "python":
            secure_example_path = utils.relative_path_from_root(os.path.join(
                "datasets", "origins", "SecurityEval", "secure_examples", prompt.suspected_vulnerability,
                prompt.id + ".py"))

            security_eval_prompt = security_eval_entries.get(prompt.id)
            if security_eval_prompt:
                if "Insecure_code" in security_eval_prompt:
                    prompt.insecure_example = security_eval_prompt["Insecure_code"]
                else:
                    print(f"Insecure example for prompt {prompt.id} not found")
            else:
                print(f"Original prompt for {prompt.id} not found")

    with open(dataset_file_path, 'w') as file:
        json.dump([prompt.dict(exclude_defaults=True) for prompt in dataset], file, indent=4)
