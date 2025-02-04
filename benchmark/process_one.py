import json
import logging
import os
import re
import time
from typing import List, Callable

from dotenv import load_dotenv
from openai import OpenAI
from openai.types import Batch

import analyze_scan_results
import utils
from batch_processing.create_response_extraction_batch import create_response_extraction_batch
from batch_processing.create_response_generation_batch import create_response_generation_batch
from batch_processing.get_extracted_code_from_batch import add_extracted_code_from_batch
from batch_processing.get_generated_responses_from_batch import add_generated_responses_from_batch
from codeql_scan import CodeQLScanner
from extract_code_from_generated_response import CodeExtractor
from filter_config import SEMGREP_SCAN_RESULT_FILTERS, CODEQL_SCAN_RESULT_FILTERS
from generate_response_from_modified_prompts import ResponseGenerator
from project_types.custom_types import Approach, Task, Sample
from semgrep_scan import SemgrepScanner
from utils import retry_on_rate_limit


def re_extract(relevant_scan_errors, num_regenerations, approach, i):
    re_generate = not num_regenerations & 1  # only re-generate on even tries, otherwise only re-extract
    print(
        f"Syntax errors found in {len(set([(error.sample_index, error.task_id) for error in relevant_scan_errors]))} samples at index {i}, "
        f"{'re-extracting' if re_generate else 're-generating'} "
        f"and rescanning affected samples")
    error_tasks = [task for task in approach.tasks if
                   task.id in [error.task_id for error in relevant_scan_errors]]

    for task in error_tasks:
        samples_with_index = [sample for sample in task.samples if sample.index == i]
        if len(samples_with_index) == 1:
            sample = samples_with_index[0]
        else:
            raise ValueError(f"Task {task.id} has multiple samples with index {i}")
        sample.extracted_code = None
        sample.semgrep_successfully_scanned = False
        sample.semgrep_scanner_report = None
        sample.semgrep_filtered_scanner_report = None

        sample.codeql_successfully_scanned = False
        sample.codeql_scanner_report = None
        sample.codeql_filtered_scanner_report = None

        if re_generate:
            sample.generated_response = None

    # re-initialize workers to reset statistics
    response_generator = ResponseGenerator()
    code_extractor = CodeExtractor()

    if re_generate:
        retry_on_rate_limit(response_generator.generate_missing, approach, i)

    # (re-)extract affected samples
    # if we didn't re-generate, we will use GPT to extract the code this time
    retry_on_rate_limit(code_extractor.extract_missing, approach, i, not re_generate)


def save_if_changed(file_path, approach, previous_approach_dict):
    current_approach_dict = approach.dict(exclude_defaults=True)
    if current_approach_dict != previous_approach_dict:
        with open(file_path, 'w') as file:
            json.dump(current_approach_dict, file, indent=4)
        return current_approach_dict
    return previous_approach_dict


def get_num_gpt_extracts(samples_to_extract):
    num_gpt_extracts = len(samples_to_extract)
    for sample_to_extract in samples_to_extract:
        code_blocks = utils.get_code_blocks(sample_to_extract.generated_response)

        code = ""
        if len(code_blocks) == 0:
            code = sample_to_extract.generated_response
        elif len(code_blocks) == 1:
            code = code_blocks[0][1]

        if code and utils.is_complex_code(code):
            num_gpt_extracts -= 1
    return num_gpt_extracts


class BatchInProgressException(Exception):
    pass


def handle_batch(approach: Approach, batch_id, wait_for_batch_completion, approach_file_path):
    client = OpenAI()
    batch: Batch = client.batches.retrieve(approach.pending_batch_id)
    waiting_statuses = ["validating", "in_progress", "finalizing"]
    if batch.status in waiting_statuses:
        if wait_for_batch_completion:
            print(
                f"Waiting for batch completion for approach {approach.id} (step '{approach.pending_batch_goal}', batch_id: '{approach.pending_batch_id}')")
            print("You can wait, or re-start the script at a later time to check the progress.")
            print("The script will check the status every 30 seconds, and continue once the batch is completed.")
            in_progress = True
            while in_progress:
                batch: Batch = client.batches.retrieve(approach.pending_batch_id)
                if batch.status not in waiting_statuses:
                    in_progress = False
                else:
                    request_count_string = ""
                    if batch.request_counts and batch.request_counts.total:
                        request_count_string = f"{batch.request_counts.completed}/{batch.request_counts.total} completed, {batch.request_counts.failed} failed"
                    print(f"Batch {approach.pending_batch_id} status: {batch.status} {request_count_string}")
                    time.sleep(30)
        else:
            print(
                f"Batch {approach.pending_batch_id} in progress for approach {approach.id} (step '{approach.pending_batch_goal}', batch_id: '{approach.pending_batch_id}'). Re-run the script at a later time.")
            print("An overview of all pending batches is available at https://platform.openai.com/batches.")
            raise BatchInProgressException()

    if batch.status != "completed":
        raise Exception(
            f"There is a problem with the batch {approach.pending_batch_id}. Please check the status on https://platform.openai.com/batches/{batch_id}.")
    else:
        print(f"Batch {approach.pending_batch_id} completed.")
        if approach.pending_batch_goal == "response_generation":
            add_generated_responses_from_batch(batch, approach)
            approach.pending_batch_id = None
            approach.pending_batch_goal = None
            utils.write_approaches_file(approach_file_path, approach)

        elif approach.pending_batch_goal == "response_extraction":
            add_extracted_code_from_batch(batch, approach)
            approach.pending_batch_id = None
            approach.pending_batch_goal = None
            utils.write_approaches_file(approach_file_path, approach)
        else:
            raise ValueError(f"Invalid batch goal {approach.pending_batch_goal}")


def process_file(data_file_path, wait_for_batch_completion: bool,
                 semgrep_result_filters: List[Callable[[Task, Sample, dict], bool]] = None,
                 codeql_result_filters: List[Callable[[Task, Sample, dict], bool]] = None):
    load_dotenv()
    print(f"Processing file {data_file_path}")
    samples_per_task = int(os.getenv('SAMPLES_PER_TASK'))

    file_name, file_extension = os.path.splitext(data_file_path)
    with open(f"{file_name}{file_extension}", 'r') as file:
        data = json.load(file)

    approach = Approach(**data)
    previous_approach_dict = approach.dict(exclude_defaults=True)

    batch_id = approach.pending_batch_id
    if (batch_id):
        handle_batch(approach, batch_id, wait_for_batch_completion, data_file_path)

    num_responses_to_generate = sum(
        1 for task in approach.tasks for sample in task.samples if not sample.generated_response)
    if len(approach.tasks[0].samples) < samples_per_task:
        num_responses_to_generate += (samples_per_task - len(approach.tasks[-1].samples)) * len(approach.tasks)

    if num_responses_to_generate > int(os.getenv('BATCH_THRESHOLD')):
        batch_id = create_response_generation_batch(approach)
        approach.pending_batch_id = batch_id
        approach.pending_batch_goal = "response_generation"
        utils.write_approaches_file(f"{file_name}{file_extension}", approach)
        handle_batch(approach, batch_id, wait_for_batch_completion, data_file_path)

    samples_to_extract = [sample for task in approach.tasks for sample in task.samples if
                          sample.generated_response and not sample.extracted_code]
    num_gpt_extracts = get_num_gpt_extracts(samples_to_extract)
    if num_gpt_extracts > int(os.getenv('BATCH_THRESHOLD')):
        batch_id = create_response_extraction_batch(approach)
        approach.pending_batch_id = batch_id
        approach.pending_batch_goal = "response_extraction"
        utils.write_approaches_file(f"{file_name}{file_extension}", approach)
        handle_batch(approach, batch_id, wait_for_batch_completion, data_file_path)

    if not approach.pending_batch_id:
        generation_or_extraction_necessary = (
                any(
                    task for task in approach.tasks if not task.samples or len(task.samples) < samples_per_task)
                or any(
            not sample.generated_response or not sample.extracted_code for task in approach.tasks for sample in
            task.samples))
        if generation_or_extraction_necessary:
            for i in range(samples_per_task):
                print(f"Starting execution for sample {i}")

                print(f"Starting response generation for sample {i}")
                st = time.time()
                response_generator = ResponseGenerator()
                retry_on_rate_limit(response_generator.generate_missing, approach, i)
                et = time.time()
                previous_approach_dict = save_if_changed(f"{file_name}{file_extension}", approach,
                                                         previous_approach_dict)
                print(f"Response generation for sample {i} finished, time: {(et - st):.2f}s")

                print()

                print(f"Starting response extraction for sample {i}: {(et - st):.2f}s")
                st = time.time()
                code_extractor = CodeExtractor()
                retry_on_rate_limit(code_extractor.extract_missing, approach, i)
                et = time.time()
                previous_approach_dict = save_if_changed(f"{file_name}{file_extension}", approach,
                                                         previous_approach_dict)
                print(f"Response extraction for sample {i} finished, time: {(et - st):.2f}s")

                print()

                print(f"Starting semgrep scan for sample {i}")
                st = time.time()

                semgrep_scanner = SemgrepScanner()
                semgrep_scanner.scan_samples(approach, i)

                et = time.time()
                previous_approach_dict = save_if_changed(f"{file_name}{file_extension}", approach,
                                                         previous_approach_dict)
                print(f"Semgrep scan for sample {i} finished, time: {(et - st):.1f}s")

                print()

        else:
            print(f"Starting semgrep scan for approach")
            st = time.time()
            semgrep_scanner = SemgrepScanner()
            semgrep_scanner.scan_samples(approach)
            previous_approach_dict = save_if_changed(f"{file_name}{file_extension}", approach, previous_approach_dict)
            et = time.time()
            print(f"Semgrep scan finished, time: {(et - st):.1f}s")

    print(f"Starting codeql scan")
    st = time.time()

    codeql_scanner = CodeQLScanner()
    codeql_scanner.scan_samples(approach)

    previous_approach_dict = save_if_changed(f"{file_name}{file_extension}", approach, previous_approach_dict)
    et = time.time()

    print(f"Codeql scan finished, time: {(et - st):.1f}s")

    # if errors were found by the scanner, re-extract and re-scan the affected sample
    # if the issue persists, re-generate the response and re-scan the affected sample
    # abort after 4 unsuccessful regenerations

    relevant_scan_errors = get_relevant_scan_errors(approach)
    if relevant_scan_errors:
        num_regenerations = 0
        while num_regenerations < 4:

            num_regenerations += 1

            for i in range(samples_per_task):

                relevant_scan_errors = get_relevant_scan_errors(approach, i)
                if relevant_scan_errors:
                    logging.info(
                        f"Syntax errors found in {len(set([(error.sample_index, error.task_id) for error in relevant_scan_errors]))} samples at index {i}.")

                    re_extract(relevant_scan_errors, num_regenerations, approach, i)

            semgrep_scanner = SemgrepScanner()
            semgrep_scanner.scan_samples(approach)
            codeql_scanner = CodeQLScanner()
            codeql_scanner.scan_samples(approach)
            previous_approach_dict = save_if_changed(f"{file_name}{file_extension}", approach, previous_approach_dict)

    relevant_scan_errors = get_relevant_scan_errors(approach)

    if relevant_scan_errors:
        print(
            f"""Failed to resolve syntax errors in {len(set([error.task_id + "-" + str(error.sample_index) for error in relevant_scan_errors]))} samples after 3 attempts.
                    Check the error field in data file for more information.""")

    previous_approach_dict = save_if_changed(f"{file_name}{file_extension}", approach, previous_approach_dict)

    analyze_scan_results.analyze(approach, semgrep_result_filters, codeql_result_filters)
    previous_approach_dict = save_if_changed(f"{file_name}{file_extension}", approach, previous_approach_dict)


def get_relevant_scan_errors(approach, i=-1):
    if approach.errors and "semgrep_scan" in approach.errors:
        semgrep_scan_errors = [error for error in approach.errors["semgrep_scan"]]
        if i > -1:
            semgrep_scan_errors = [error for error in semgrep_scan_errors if error.sample_index == i]
    else:
        semgrep_scan_errors = []

    relevant_scan_errors = [error for error in semgrep_scan_errors if
                            error.error.startswith("Syntax error at")
                            or error.error.startswith("Lexical error at")]

    if approach.errors and "codeql_scan" in approach.errors:
        codeql_scan_errors = [error for error in approach.errors["codeql_scan"]]
        if i > -1:
            codeql_scan_errors = [error for error in codeql_scan_errors if error.sample_index == i]
    else:
        codeql_scan_errors = []
    relevant_scan_errors += [error for error in codeql_scan_errors if
                             error.error.startswith("Extraction failed in")]

    return relevant_scan_errors


def main():
    load_dotenv()
    data_file_path = utils.relative_path_from_root(os.getenv('DATA_FILE_PATH'))
    process_file(data_file_path, True, SEMGREP_SCAN_RESULT_FILTERS, CODEQL_SCAN_RESULT_FILTERS)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    st = time.time()
    load_dotenv()
    main()
    et = time.time()
    print(f"Total execution time: {(et - st):.2f}s")
