import os
import sys

from openai import OpenAI

from attempts.template.abs_iteration_attempt import AbsIterationAttempt
from project_types.custom_types import Task, Sample

sys.path.append("../sec_prompt_benchmark")


class CoTAnswerExtraction(AbsIterationAttempt):

    def __init__(self, base_approach_path: str):
        attempt_name = os.path.basename(__file__)[:-3]

        super().__init__(base_approach_path, "Prompting Techniques for Secure Code Generation: CoT answer extraction", attempt_name)
        self.client = OpenAI()

    def add_new_prompt(self, model, sample: Sample, task: Task, original_sample: Sample):
        if sample.modified_prompt:
            return
        else:
            modified_prompt = f"{task.modified_prompt}\n" \
                              f"A: {original_sample.generated_response}\n" \
                              f"Therefore the {task.language} code is"
            sample.modified_prompt = modified_prompt
