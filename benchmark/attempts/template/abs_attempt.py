import os
import re
import sys
from abc import ABC, abstractmethod
from typing import List

from dotenv import load_dotenv

from cwe_resources.cwe_infos import get_suggested_mappings, get_can_also_be

sys.path.append("../sec_prompt_benchmark")

import utils
from project_types.custom_types import Approach, Prompt, Task


class AbsAttempt(ABC):
    def __init__(self, attempt_description: str, attempt_name: str):
        self.attempt_name = attempt_name
        self.attempt_description = attempt_description
        load_dotenv()

    @abstractmethod
    def modified_prompt(self, prompt: Prompt) -> str:
        pass

    def create(self):
        data_folder_path = os.path.dirname(utils.relative_path_from_root(os.getenv("DATA_FILE_PATH")))
        data_file_path = os.path.join(data_folder_path, self.attempt_name + ".json")

        dataset_file_path = utils.relative_path_from_root(os.getenv("DATASET_FILE_PATH"))

        dataset = utils.read_dataset_file(dataset_file_path)

        approach = self.create_approach(dataset)

        utils.write_approaches_file(data_file_path, approach)

    def create_approach(self, dataset: List[Prompt]) -> Approach:
        tasks = []

        for prompt in dataset:
            task = Task(
                id=prompt.id,
                original_prompt=prompt.prompt,
                modified_prompt=self.modified_prompt(prompt),
                suspected_vulnerabilities=[re.sub(r'CWE-0+', 'CWE-', prompt.suspected_vulnerability)]
                                          + get_suggested_mappings(prompt.suspected_vulnerability)
                                          + get_can_also_be(prompt.suspected_vulnerability),
                language=prompt.language,
            )
            tasks.append(task)

        approach = Approach(
            id=self.attempt_name,
            description=self.attempt_description,
            model=os.getenv("MODEL_FOR_NEW_ATTEMPTS"),
            tasks=tasks,
        )

        return approach
