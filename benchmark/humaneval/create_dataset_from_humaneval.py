import json
from typing import List

import utils
from project_types.custom_types import Prompt

file_path = utils.relative_path_from_root("humaneval/HumanEval.jsonl")
prompt_prefix = "Complete the following code, and output the complete program: \n"

prompts: List[Prompt] = []
with open(file_path, "r") as file:
    for line in file:
        json_object = json.loads(line.strip())
        task_id = json_object["task_id"]
        prompt = json_object["prompt"]

        prompt = prompt_prefix + prompt

        dataset_prompt: Prompt = Prompt(
            id=task_id,
            prompt=prompt,
            language="python",
            source="humaneval",
            suspected_vulnerability="None"
        )
        prompts.append(dataset_prompt)


    print(prompts)

    dataset_file_path = utils.relative_path_from_root("datasets/HumanEval/HumanEval.json")
    utils.write_dataset_file(dataset_file_path, prompts)
