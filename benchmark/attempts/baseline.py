import os
import sys

from attempts.template.abs_attempt import AbsAttempt

sys.path.append("../sec_prompt_benchmark")

from project_types.custom_types import Prompt


class BaselineAttempt(AbsAttempt):
    def __init__(self):
        super().__init__("Baseline - no prompt modification", os.path.basename(__file__)[:-3])

    def modified_prompt(self, prompt: Prompt) -> str:
        return prompt.prompt


if __name__ == "__main__":
    BaselineAttempt().create()
