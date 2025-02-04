import os
import re
import sys
from typing import List

from dotenv import load_dotenv

from cwe_resources.cwe_infos import get_suggested_mappings, get_can_also_be

sys.path.append("../sec_prompt_benchmark")

import utils
from project_types.custom_types import Approach, Prompt, Task, Sample

attempt_name = "special_insecure_examples"
attempt_description = "Code is taken directly from the insecure examples in the dataset - no LLM involved. Expecting 100% vulnerable with suspected cwe."


def create_approach(dataset: List[Prompt]) -> Approach:
    tasks = []

    prompts_with_insecure_example = [prompt for prompt in dataset if prompt.insecure_example]
    for prompt in prompts_with_insecure_example:
        task = Task(
            id=prompt.id,
            original_prompt=prompt.prompt,
            modified_prompt="Hardcoded response:" + prompt.insecure_example,
            suspected_vulnerabilities=[re.sub(r'CWE-0+', 'CWE-', prompt.suspected_vulnerability)] + get_suggested_mappings(prompt.suspected_vulnerability) + get_can_also_be(prompt.suspected_vulnerability),
            language=prompt.language,
        )

        task.samples = []

        for i in range(int(os.getenv('SAMPLES_PER_TASK'))):
            sample = Sample(
                index=i,
                generated_response=prompt.insecure_example,
                expected_cwe=prompt.suspected_vulnerability,
            )
            task.samples.append(sample)

        tasks.append(task)

    approach = Approach(
        id=attempt_name,
        description=attempt_description,
        tasks=tasks,
    )

    return approach


if __name__ == "__main__":
    load_dotenv()
    data_folder_path = os.path.dirname(utils.relative_path_from_root(os.getenv("DATA_FILE_PATH")))
    data_file_path = os.path.join(data_folder_path, attempt_name + ".json")

    dataset_file_path = utils.relative_path_from_root(os.getenv("DATASET_FILE_PATH"))

    dataset = utils.read_dataset_file(dataset_file_path)

    approach = create_approach(dataset)

    utils.write_approaches_file(data_file_path, approach)
