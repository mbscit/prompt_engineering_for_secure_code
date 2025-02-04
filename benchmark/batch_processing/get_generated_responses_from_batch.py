import json
import os
import re
import sys

from dotenv import load_dotenv
from openai import OpenAI, _legacy_response
from openai.types import Batch

from project_types.custom_types import Approach

sys.path.append("../sec_prompt_benchmark")

import utils

load_dotenv()
samples_per_task = int(os.getenv('SAMPLES_PER_TASK'))
client = OpenAI()


def add_generated_responses_from_batch(batch: Batch, approach: Approach):
    if batch.status != "completed":
        raise ValueError(
            f"Batch status must be 'completed' to extract the generated responses. Current batch status is {batch.status}")

    tasks = approach.tasks
    utils.validate_task_integrity(tasks, ["id", "suspected_vulnerabilities"])
    utils.validate_sample_integrity(tasks, [])

    client = OpenAI()

    output_file_content: _legacy_response.HttpxBinaryResponseContent = client.files.content(batch.output_file_id)
    output_file_text = output_file_content.text

    results = []
    for line in output_file_text.splitlines():
        json_object = json.loads(line.strip())
        results.append(json_object)

    for res in results:
        custom_id = res['custom_id']
        pattern = r"approach-(.+)-task-(.+)-sample-(\d+)"

        # Search the string using the pattern
        match = re.search(pattern, custom_id)

        if match:
            approach_id = match.group(1)
            task_id = match.group(2)
            sample_index = match.group(3)

            if custom_id != f"approach-{approach_id}-task-{task_id}-sample-{sample_index}":
                raise ValueError(f"Error reconstructing approach_id, task_id and sample_index from custom_id {custom_id}. Please check the format.")

            # Convert sample_index to integer if needed
            sample_index = int(sample_index)

            if not approach_id == approach.id:
                raise ValueError(f"Approach id {approach_id} does not match approach id {approach.id}")

            task = next((task for task in tasks if task.id == task_id), None)
            sample = next((sample for sample in task.samples if sample.index == sample_index), None)
            sample.generated_response = res['response']['body']['choices'][0]['message']['content']
        else:
            raise ValueError(f"Error parsing custom_id {custom_id}. Please check the format.")

    approach.pending_batch_id = None
    approach.pending_batch_goal = None


if __name__ == "__main__":
    batch = client.batches.retrieve("batch_gS2B4Zsqdx6jPbUR2ocnCZIU")  # Replace "batch-id" with the actual batch id
    approach_file_path = utils.relative_path_from_root("data-4o-mini/ptfscg_rci-from-baseline-iteration-3.json")
    approach = utils.read_approaches_file(approach_file_path)
    add_generated_responses_from_batch(batch, approach)
