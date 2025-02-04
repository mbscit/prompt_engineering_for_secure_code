import logging
import os
import re
import sys
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

import openai
from dotenv import load_dotenv

sys.path.append("../sec_prompt_benchmark")

import utils
from project_types.custom_types import Approach, Task, Sample


class AbsIterationAttempt(ABC):
    def __init__(self, base_approach_path: str, attempt_description: str, attempt_name: str):
        load_dotenv()


        base_approach_file_name = os.path.basename(base_approach_path)[:-5]
        base_of_base = re.sub(r"-iteration-\d+", "", base_approach_file_name)

        if base_approach_file_name.startswith(attempt_name):
            iteration_pattern = fr"{base_of_base}-iteration-(\d+)"

            iteration_match = re.search(iteration_pattern, base_approach_file_name)
            if iteration_match:
                current_iteration = int(iteration_match.group(1))
                next_iteration = current_iteration + 1
                attempt_name = f"{base_approach_file_name.replace(f'-iteration-{current_iteration}', '')}-iteration-{next_iteration}"
            else:
                attempt_name = f"{attempt_name}-from-{base_approach_file_name}-iteration-1"
        else:
            attempt_name = f"{attempt_name}-from-{base_approach_file_name}-iteration-1"

        print(attempt_name)

        self.base_attempt_path = utils.relative_path_from_root(base_approach_path)
        self.attempt_name = attempt_name
        self.attempt_description = attempt_description

    @abstractmethod
    def add_new_prompt(self, model: str, sample: Sample, task: Task, original_sample: Sample) -> str:
        pass

    def create(self):
        data_folder_path = os.path.dirname(utils.relative_path_from_root(os.getenv("DATA_FILE_PATH")))
        data_file_path = os.path.join(data_folder_path, self.attempt_name + ".json")

        base_approach = utils.read_approaches_file(self.base_attempt_path)
        try:
            existing_approach = utils.read_approaches_file(data_file_path)
        except FileNotFoundError:
            existing_approach = None

        approach = self.create_approach(base_approach, existing_approach)

        utils.write_approaches_file(data_file_path, approach)

    def create_approach(self, base_approach: Approach, existing_approach: Approach) -> Approach:
        num_samples = int(os.getenv("SAMPLES_PER_TASK"))

        tasks = []

        if num_samples > len(base_approach.tasks[0].samples):
            raise ValueError("Number of requested samples per task is greater than the number of samples in the base approach.")

        all_samples = []

        for original_task in base_approach.tasks:
            task = Task(
                id=original_task.id,
                original_prompt=original_task.modified_prompt if original_task.modified_prompt else "Sample-specific prompt",
                suspected_vulnerabilities=original_task.suspected_vulnerabilities,
                language=original_task.language,
            )

            samples = []

            for original_sample in original_task.samples:
                if original_sample.index < num_samples:
                    sample = Sample(
                        index=original_sample.index,
                    )
                    if original_sample.modified_prompt:
                        sample.original_prompt = original_sample.modified_prompt

                    if existing_approach:
                        for existing_task in existing_approach.tasks:
                            if existing_task.id == original_task.id:
                                for existing_sample in existing_task.samples:
                                    if existing_sample.index == original_sample.index:
                                        sample = existing_sample
                                        break

                    samples.append(sample)
                    all_samples.append((sample, original_task, original_sample))
            task.samples = samples
            tasks.append(task)

        with ThreadPoolExecutor() as executor:
            try:

                print(f"Number of samples: {len(all_samples)}")
                futures = {
                    executor.submit(self.add_new_prompt, os.getenv("MODEL_FOR_NEW_ATTEMPTS"), sample, original_task, original_sample): (
                        sample, original_task, original_sample)
                    for sample, original_task, original_sample in all_samples if not sample.modified_prompt
                }

                print(f"Number of futures created: {len(futures)}")

                utils.handle_futures_with_ratelimit(futures)

            except openai.RateLimitError as e:
                logging.error("Rate limit exceeded, samples incomplete")
            except Exception as e:
                raise e
            finally:
                approach = Approach(
                    id=self.attempt_name,
                    model=os.getenv("MODEL_FOR_NEW_ATTEMPTS"),
                    description=self.attempt_description,
                    tasks=tasks,
                )
                return approach
