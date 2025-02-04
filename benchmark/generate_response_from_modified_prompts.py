import logging
import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Value
from typing import List

import openai
from dotenv import load_dotenv
from openai import OpenAI

import utils
from project_types.custom_types import Approach, SampleError, Task, Sample
from utils import increment_counter


class ResponseGenerator:

    def __init__(self):
        self.client: OpenAI = OpenAI()
        self.errors: List[SampleError] = []
        self.successful_generations = Value('i', 0)
        self.skipped_samples = Value('i', 0)
        self.error_samples = Value('i', 0)

    def generate_response(self, model: str, prompt: str):
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content

    def generate_responses_for_index(self, approach: Approach, task: Task, sample_index: int):
        sample: Sample = next((sample for sample in task.samples if sample.index == sample_index), None)
        try:
            if not sample:
                if task.modified_prompt:
                    sample = Sample(index=sample_index)
                    task.samples.append(sample)
            if not sample.generated_response:
                if task.modified_prompt:
                    sample.generated_response = self.generate_response(approach.model, task.modified_prompt)
                    increment_counter(self.successful_generations)
                elif sample.modified_prompt:
                    sample.generated_response = self.generate_response(approach.model, sample.modified_prompt)
                    increment_counter(self.successful_generations)
                else:
                    raise ValueError(f"No prompt available for task {task.id} sample {sample_index}")
            else:
                logging.info(f"Skipping {task.id} - response already generated for sample {sample_index}")
                increment_counter(self.skipped_samples)

        except openai.RateLimitError as e:
            logging.error(f"Rate limit exceeded at {task.id}: {e}")
            self.errors.append(
                SampleError(task_id=task.id, sample_index=sample.index, error="Rate limit exceeded"))
            increment_counter(self.error_samples)
            raise
        except Exception as e:
            logging.error(f"Error generating response for {task.id}: {e}")
            self.errors.append(SampleError(task_id=task.id, sample_index=sample.index, error=str(e)))
            increment_counter(self.error_samples)

    def generate_missing(self, approach: Approach, sample_index: int):
        tasks: List[Task] = approach.tasks
        utils.validate_task_integrity(tasks, [])
        if not all(task.modified_prompt for task in tasks) and not all(sample.modified_prompt for task in tasks for sample in task.samples):
            raise ValueError("No modified prompts available. Either all tasks or all samples must have a modified prompt")

        if all(any(sample.index == sample_index and sample.generated_response for sample in task.samples) for task in
               tasks):
            print(f"Response for sample {sample_index} has already been generated for all tasks")
        else:
            with ThreadPoolExecutor() as executor:
                try:
                    futures = {executor.submit(self.generate_responses_for_index, approach, task, sample_index): task for task in
                               tasks}
                    utils.handle_futures_with_ratelimit(futures)
                except openai.RateLimitError as e:
                    logging.error("Rate limit exceeded, samples incomplete")
                    raise e
                except Exception as e:
                    raise e
                finally:
                    approach.update_errors("generate_response", self.errors, sample_index)

            print(f"Summary:")
            print(f"Total Samples: {len(tasks)}")
            print(f"Successful Generations: {self.successful_generations.value}")
            print(f"Skipped Samples: {self.skipped_samples.value}")
            print(f"Error Samples: {self.error_samples.value}")


if __name__ == "__main__":
    load_dotenv()
    data_file_path = utils.relative_path_from_root(os.getenv('DATA_FILE_PATH'))
    sample_index = int(os.getenv('SAMPLE_INDEX'))

    approach = utils.read_approaches_file(data_file_path)

    response_generator = ResponseGenerator()

    try:
        ResponseGenerator().generate_missing(approach, sample_index)
    except Exception as e:
        raise e
    finally:
        utils.write_approaches_file(data_file_path, approach)
