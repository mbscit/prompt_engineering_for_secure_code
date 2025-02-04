import logging
import os
import sys

from openai import OpenAI

from attempts.template.abs_iteration_attempt import AbsIterationAttempt
from project_types.custom_types import Task, Sample
from utils import retry_on_rate_limit

sys.path.append("../sec_prompt_benchmark")


class RCIAttempt(AbsIterationAttempt):

    def __init__(self, base_approach_path: str):
        attempt_name = os.path.basename(__file__)[:-3]

        super().__init__(base_approach_path, "Prompting Techniques for Secure Code Generation: RCI", attempt_name)
        self.client = OpenAI()

    def add_new_prompt(self, model, sample: Sample, task: Task, original_sample: Sample):
        logging.debug(f"Adding new prompt for task {task.id} sample {sample.index}")
        if sample.modified_prompt:
            return
        else:
            critique = retry_on_rate_limit(self.get_llm_review, model, original_sample.extracted_code)
            modified_prompt = f"Based on the critique: \n" \
                   f"{critique}\n" \
                   f"improve the following answer: \n" \
                   f"```\n{original_sample.extracted_code}\n```"
            sample.modified_prompt = modified_prompt

    def get_llm_review(self, model, generated_code: str) -> str:
        prompt = f"Review the following answer and find security problems with it: \n" \
                 f"```\n{generated_code}\n```"

        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
