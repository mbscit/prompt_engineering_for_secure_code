import json
import os
import re
import sys

from dotenv import load_dotenv
from openai import OpenAI, _legacy_response
from openai.types import FileObject, Batch

from project_types.custom_types import Sample, SampleError, Approach

sys.path.append("../sec_prompt_benchmark")

import utils

load_dotenv()
samples_per_task = int(os.getenv('SAMPLES_PER_TASK'))
client = OpenAI()


def add_extracted_code_from_batch(batch: Batch, approach: Approach):
    if batch.status != "completed":
        raise ValueError(
            f"Batch status must be 'completed' to extract the generated responses. Current batch status is {batch.status}")

    errors = []

    tasks = approach.tasks
    utils.validate_task_integrity(tasks, ["id", "suspected_vulnerabilities"])
    utils.validate_sample_integrity(tasks, ["generated_response"])

    client = OpenAI()

    output_file_content: _legacy_response.HttpxBinaryResponseContent = client.files.content(batch.output_file_id)
    output_file_text = output_file_content.text

    results = []
    for line in output_file_text.splitlines():
            # Parsing the JSON string into a dict and appending to the list of results
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
            code = res['response']['body']['choices'][0]['message']['content']

            code_blocks = utils.get_code_blocks(code)

            if len(code_blocks) > 1:
                errors.append(
                    SampleError(task_id=task.id, sample_index=sample.index, error=f"Multiple code blocks found for {task.id} sample {sample.index}."))
            elif len(code_blocks) == 1:
                sample.extracted_code = code_blocks[0][1]
            else:
                sample.extracted_code = code
        else:
            raise ValueError(f"Error parsing custom_id {custom_id}. Please check the format.")


    for sample_index in set([error.sample_index for error in errors]):
        approach.update_errors("extract_response", errors, sample_index)


if __name__ == "__main__":
    batch = client.batches.retrieve("batch_gS2B4Zsqdx6jPbUR2ocnCZIU")  # Replace "batch-id" with the actual batch id
    approach_file_path = utils.relative_path_from_root("data-4o-mini/ptfscg_rci-from-baseline-iteration-3.json")
    approach = utils.read_approaches_file(approach_file_path)
    add_extracted_code_from_batch(batch, approach)
