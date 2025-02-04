import logging
import sys

from helper.task_filters_metadata_based.abs_get_prompt_ids_by import GetIDsBy
from project_types.custom_types import Prompt

sys.path.append("../sec_prompt_benchmark")


class ByLanguage(GetIDsBy):

    def __init__(self, language: str):
        self.language = language

    def condition(self, prompt: Prompt) -> bool:
        return prompt.language == self.language


if __name__ == "__main__":
    ByLanguage("python").filtered_from_dataset(print_ids=True)
