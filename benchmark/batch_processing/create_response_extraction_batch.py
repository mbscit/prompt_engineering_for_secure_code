import json
import os
import re
import sys

from dotenv import load_dotenv
from openai import OpenAI
from openai.types import FileObject, Batch

from project_types.custom_types import Sample, language_extensions, Approach

sys.path.append("../sec_prompt_benchmark")

import utils

load_dotenv()
samples_per_task = int(os.getenv('SAMPLES_PER_TASK'))


def get_confirmation():
    while True:
        user_input = input("Proceed creating the batch job? (Y/N): ").strip().lower()
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")


def create_response_extraction_batch(approach: Approach) -> str:
    tasks = approach.tasks

    utils.validate_task_integrity(tasks, ["id", "language"])
    utils.validate_sample_integrity(tasks, ["generated_response"])

    requests_file_path = utils.relative_path_from_root(
        f"batch_processing/{approach.id}_{approach.model}_response_extraction_batch.jsonl")

    requests = []

    for task in tasks:
        for sample_index in range(samples_per_task):
            sample: Sample = next((sample for sample in task.samples if sample.index == sample_index), None)
            if not sample.extracted_code:
                code_blocks = utils.get_code_blocks(sample.generated_response)

                code = ""
                if len(code_blocks) == 0:
                    code = sample.generated_response
                elif len(code_blocks) == 1:
                    code = code_blocks[0][1]

                if code and utils.is_complex_code(code):
                    sample.extracted_code = code

                if not sample.extracted_code:
                    message_content = (
                        f"Only output the {language_extensions.get(task.language)} code and nothing else, so that when I copy your answer into a file, "
                        f"it will be a valid {language_extensions.get(task.language)} file.")

                    requests.append({
                        "custom_id": "approach-" + approach.id + "-task-" + task.id + "-sample-" + str(sample.index),
                        "method": "POST", "url": "/v1/chat/completions",
                        "body": {
                            "model": approach.model,
                            "messages": [
                                {"role": "user",
                                 "content": sample.modified_prompt if sample.modified_prompt else task.modified_prompt},
                                {"role": "assistant", "content": sample.generated_response},
                                {
                                    "role": "user",
                                    "content": message_content
                                }
                            ]
                        }
                    })

    custom_ids = [request["custom_id"] for request in requests]
    duplicated_ids = [id for id in set(custom_ids) if custom_ids.count(id) > 1]
    for duplicate_custom_id in duplicated_ids:
        raise f"Duplicate custom_id {duplicate_custom_id}"

    with open(requests_file_path, 'w') as file:
        for record in requests:
            json.dump(record, file)
            file.write('\n')

    print(f"Requests successfully written to {requests_file_path}")

    client: OpenAI = OpenAI()

    batch_input_file: FileObject = client.files.create(
        file=open(requests_file_path, "rb"),
        purpose="batch"
    )

    print(f"Batch input file created with id {batch_input_file.id}, name {batch_input_file.filename}")

    batch_input_file_id = batch_input_file.id

    batch: Batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "approach_id": approach.id,
            "model": approach.model
        }
    )

    print(f"Batch job created with id {batch.id}")
    return batch.id


if __name__ == "__main__":
    data_file_path = utils.relative_path_from_root("validation-4o-mini/baseline.json")
    if os.path.isfile(data_file_path):
        approach = utils.read_approaches_file(data_file_path)
        batch_id = create_response_extraction_batch(approach)
        approach.pending_batch_id = batch_id
        approach.pending_batch_goal = "response_generation"
        utils.write_approaches_file(data_file_path, approach)
    else:
        raise FileNotFoundError(f"Data file not found at {data_file_path}")
