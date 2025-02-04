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

    for prompt in dataset:
        if prompt.source == "LLMSecEval" and prompt.language == "python":
            secure_example_path = utils.relative_path_from_root(os.path.join(
                "datasets", "origins", "LLMSecEval", "secure_examples", prompt.suspected_vulnerability, prompt.id + ".py"))

            if os.path.exists(secure_example_path):
                with open(secure_example_path, "r") as f:
                    prompt.secure_example = f.read()

            if not prompt.secure_example:
                print(f"Secure example for prompt {prompt.id} not found")

    with open(dataset_file_path, 'w') as file:
        json.dump([prompt.dict(exclude_defaults=True) for prompt in dataset], file, indent=4)
