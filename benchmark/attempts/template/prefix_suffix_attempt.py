import sys

from attempts.template.abs_attempt import AbsAttempt

sys.path.append("../sec_prompt_benchmark")

from project_types.custom_types import Prompt


class PrefixSuffixAttempt(AbsAttempt):

    def __init__(self, attempt_description: str, attempt_name: str, prefix: str, suffix: str):
        super().__init__(attempt_description, attempt_name)
        self.prefix = prefix
        self.suffix = suffix

    def modified_prompt(self, prompt: Prompt) -> str:
        return self.prefix + prompt.prompt + self.suffix
