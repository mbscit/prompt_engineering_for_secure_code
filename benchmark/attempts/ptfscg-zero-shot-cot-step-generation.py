import os
import sys

sys.path.append("../sec_prompt_benchmark")

from attempts.template.abs_attempt import AbsAttempt
from project_types.custom_types import Prompt


class ZeroShotCoTStepGeneration(AbsAttempt):
    def __init__(self):
        super().__init__("Prompting Techniques for Secure Code Generation: zero-shot CoT step generation",
                         os.path.basename(__file__)[:-3])

    def modified_prompt(self, prompt: Prompt) -> str:
        prompt.prompt = prompt.prompt.replace("Generate Python code for the following:",
                                              "Q: Generate secure Python code for the following:")
        prompt.prompt = prompt.prompt.replace("Complete the following code, and output the complete program:",
                                              "Q: Complete the following code securely, and output the complete, secure program:")

        prompt.prompt = prompt.prompt + "\nA: Let’s think step by step."

        return prompt.prompt


if __name__ == "__main__":
    ZeroShotCoTStepGeneration().create()
