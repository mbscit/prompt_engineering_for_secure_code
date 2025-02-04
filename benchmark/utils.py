import ast
import concurrent
import json
import logging
import os
import re
import time
import warnings
from typing import List

import openai

from project_types.custom_types import Prompt, Task, Approach


def relative_path_from_root(file_path):
    """
    Get the relative path to the file from the root directory of the project.

    Args:
        file_path (str): The file path relative to the root directory of the project.

    Returns:
        str: The relative path to the file from the current working directory.
    """
    # Get the current working directory
    current_dir = os.getcwd()

    root_dir = current_dir
    while not os.path.exists(os.path.join(root_dir, '.git')) and root_dir != os.path.dirname(root_dir):
        root_dir = os.path.dirname(root_dir)

    relative_to_root = os.path.relpath(root_dir, current_dir)
    full_relative_path = os.path.join(relative_to_root, file_path)

    return full_relative_path


def increment_counter(counter):
    with counter.get_lock():
        counter.value += 1


def validate_task_integrity(tasks: List[Task], required_attributes: List[str]):
    errors: List[str] = []

    # find duplicated task.id in tasks
    task_ids = [task.id for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        duplicated_ids = [id for id in set(task_ids) if task_ids.count(id) > 1]
        for id in duplicated_ids:
            errors.append(f"Duplicate task id {id} in dataset")

    for task in tasks:
        for attribute in required_attributes:
            if not hasattr(task, attribute) or not getattr(task, attribute):
                errors.append(f"Task {task.id} is missing {attribute}")

    if errors:
        raise ValueError(f"Errors in dataset - Aborting:\n" + "\n".join(errors))


def validate_sample_integrity(tasks: List[Task], required_attributes: List[str], num_samples: int = -1):
    errors: List[str] = []

    if any(task.modified_prompt for task in tasks) and any(
            sample.modified_prompt for task in tasks for sample in task.samples):
        raise ValueError("Both task and sample modified prompts are present. Only one can be used.")

    # take the length of the first samples array for reference
    if num_samples == -1:
        num_samples = len(tasks[0].samples)

    for i in range(num_samples):
        for task in tasks:
            task.samples = sorted(task.samples, key=lambda sample: sample.index)

            samples = [sample for sample in task.samples if sample.index == i]
            if len(samples) < 1:
                errors.append(f"Task {task.id} has no sample with index {i}")
            elif len(samples) > 1:
                errors.append(f"Task {task.id} has multiple samples with index {i}")

            for sample in samples:
                for attribute in required_attributes:
                    if ((not hasattr(sample, attribute))
                            or (
                                    getattr(sample, attribute) != 0 and (not getattr(sample, attribute)))):
                        errors.append(f"Task {task.id}, Sample {i} is missing {attribute}")
                    if isinstance(getattr(sample, attribute), bool) and not getattr(sample, attribute):
                        errors.append(
                            f"Task {task.id}, Sample {i}  {attribute} is False, check the errors attribute of the attempt.")

    if errors:
        raise ValueError(f"Errors in dataset - Aborting:\n" + "\n".join(errors))


def handle_futures_with_ratelimit(futures):
    try:
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except openai.RateLimitError as e:
                # Cancel all not started futures
                for f in futures:
                    if f.running() or f.done():
                        continue
                    f.cancel()
                # Wait for all started futures to finish
                concurrent.futures.wait([f for f in futures if f.running()])
                # Raise the RateLimitError
                raise e
    except Exception as e:
        raise e


def read_approaches_file(data_file_path) -> Approach:
    file_name, file_extension = os.path.splitext(data_file_path)
    with open(f"{file_name}{file_extension}", 'r') as file:
        data = json.load(file)
    approach = Approach(**data)
    return approach


def write_approaches_file(data_file_path, approach: Approach):
    file_name, file_extension = os.path.splitext(data_file_path)
    extracted_data_file_path = f"{file_name}{file_extension}"
    with open(extracted_data_file_path, 'w') as file:
        json.dump(approach.dict(exclude_defaults=True), file, indent=4)


def read_dataset_file(dataset_file_path) -> List[Prompt]:
    file_name, file_extension = os.path.splitext(dataset_file_path)
    with open(f"{file_name}{file_extension}", 'r') as file:
        data = json.load(file)

    dataset = [Prompt(**d) for d in data]
    return dataset


def write_dataset_file(data_file_path, prompts: List[Prompt]):
    file_name, file_extension = os.path.splitext(data_file_path)
    extracted_data_file_path = f"{file_name}{file_extension}"
    with open(extracted_data_file_path, 'w') as file:
        json.dump([prompt.dict(exclude_defaults=True) for prompt in prompts], file, indent=4, default=vars)


def convert_to_enum_identifier(text: str) -> str:
    return text.replace(" ", "_").replace("/", "_").replace("-", "_").upper()


def retry_on_rate_limit(func, *args, **kwargs):
    waiting_period_seconds = 15
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except openai.RateLimitError:
            retries += 1
            if retries < max_retries:
                logging.warning(
                    f"Rate limit error encountered. Retrying after {waiting_period_seconds} seconds...")
                time.sleep(15)
            else:
                logging.error("Max retries reached. Function call failed due to rate limit.")
                raise


def get_ast_height(node):
    """
    Recursively calculate the height of an AST.
    """
    if not isinstance(node, ast.AST) or not list(ast.iter_child_nodes(node)):
        return 1
    return 1 + max(get_ast_height(child) for child in ast.iter_child_nodes(node))


def is_complex_code(string, min_height=3):
    """
    Determine if the Python code in the string is complex enough
    based on the AST height.
    """
    try:
        # Parse the string into an AST
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=SyntaxWarning)
            tree = ast.parse(string)

        # Compute the height of the AST
        height = get_ast_height(tree)

        # Check if the height meets the minimum threshold
        return height >= min_height
    except SyntaxError:
        # If there's a syntax error, the string is not valid Python code
        return False


def get_code_blocks(text) -> List[str]:
    code_blocks = re.findall(r"```(\S*)\n(.*?)```", text, re.DOTALL)
    return code_blocks
