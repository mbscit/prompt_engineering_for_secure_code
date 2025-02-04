import os
import sys

from attempts.template.abs_attempt import AbsAttempt
from project_types.custom_types import Prompt

sys.path.append("../sec_prompt_benchmark")


class NaiveSecureAttempt(AbsAttempt):
    def __init__(self):
        super().__init__("Prompting Techniques for Secure Code Generation: Comprehensive (0-shot)",
                         os.path.basename(__file__)[:-3])

    def modified_prompt(self, prompt: Prompt) -> str:
        prompt.prompt = prompt.prompt.replace("Generate Python code for the following:",
                                              "Generate secure Python code that prevents top security weaknesses listed in CWE for the following: ")
        prompt.prompt = prompt.prompt.replace("Complete the following code, and output the complete program:",
                                              "Complete the following code while preventing top security weaknesses listed in CWE, and output the complete, secure program:")

        return prompt.prompt


if __name__ == "__main__":
    NaiveSecureAttempt().create()
