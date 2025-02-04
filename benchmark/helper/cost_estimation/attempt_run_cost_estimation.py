import csv
import logging
import os
import re
from typing import List

import pandas as pd
import tiktoken
from dotenv import load_dotenv

import utils
from project_types.custom_types import Approach, Task, language_extensions

pricing_per_1m_tokens = {
    'gpt-3.5-turbo-0125-in': 0.50,
    'gpt-3.5-turbo-0125-out': 1.50,
    'gpt-4-in': 30.00,
    'gpt-4-out': 60.00,
    'gpt-4-turbo-in': 10.00,
    'gpt-4-turbo-out': 30.00,
    'gpt-4o-in': 5.00,
    'gpt-4o-out': 15.00,
    'gpt-4o-2024-08-06-in': 2.50,
    'gpt-4o-2024-08-06-out': 10,
    'gpt-4o-mini-in': 0.15,
    'gpt-4o-mini-out': 0.60,
}


def get_costs(data_folder_path: str, margin_factor: float, using_batch_api: bool):
    matrix = []

    for file in os.listdir(data_folder_path):
        data_file_path = os.path.join(data_folder_path, file)
        # checking if it is a file
        if os.path.isfile(data_file_path):
            approach = utils.read_approaches_file(data_file_path)
            if (
                    not approach.tasks is None
                    and not any(task.samples is None for task in approach.tasks)
                    and not any(sample.generated_response is None for task in approach.tasks for sample in task.samples)
            ):
                results = {"Filename": file}
                matrix.append(results)
                analyze(approach, results, margin_factor, using_batch_api)
            else:
                logging.error(
                    f"{data_file_path} is not generated yet, generate it first"
                )

    sort_column = "Filename"
    matrix.sort(key=lambda row: row[sort_column])

    print_matrix = pd.DataFrame.from_records(
        matrix,
        columns=[
            "Filename",
            "Total Tasks",
            "Total Samples",
            "Total Input Characters",
            "Total Output Characters",
            "GPT-3.5-turbo Cost",
            "GPT-4 Cost",
            "GPT-4-turbo Cost",
            "GPT-4o Cost",
            "GPT-4o-2024-08-06 Cost",
            "GPT-4o-mini Cost"
        ],
    ).to_string(index=False, header=True)

    print()
    print(print_matrix)

    with open("attempt_execution_cost.csv", "w+") as output:
        if matrix:
            csvWriter = csv.DictWriter(output, matrix[0].keys(), quoting=csv.QUOTE_ALL)
            csvWriter.writeheader()
            csvWriter.writerows(matrix)


def requires_re_extraction(sample):
    code_blocks = utils.get_code_blocks(sample.generated_response)

    code = ""
    if len(code_blocks) == 0:
        code = sample.generated_response
    elif len(code_blocks) == 1:
        code = code_blocks[0][1]

    if code and utils.is_complex_code(code):
        return False
    else:
        return True


def get_no_tokens(tasks, samples_requiring_re_extraction, encoding):
    re_extraction_in_tokens = sum(len(encoding.encode(
        (sample.modified_prompt
         if sample.modified_prompt else task.modified_prompt)
        + sample.generated_response
        + f"Only output the {language_extensions.get(task.language)} code and nothing else, so that when I copy your answer into a file, "
          f"it will be a valid {language_extensions.get(task.language)} file."
    )) for task in tasks for sample in task.samples if sample in samples_requiring_re_extraction)

    re_extraction_out_tokens = sum(
        len(encoding.encode(sample.extracted_code)) for sample in samples_requiring_re_extraction)

    if any(task.modified_prompt for task in tasks):
        return (
            re_extraction_in_tokens + sum(
                len(encoding.encode(task.modified_prompt)) * len(task.samples) for task in tasks),
            sum(len(encoding.encode(sample.generated_response)) for task in tasks for sample in task.samples))
    else:
        return (
            re_extraction_out_tokens + sum(len(encoding.encode(sample.modified_prompt)) for task in tasks for sample in task.samples),
            sum(len(encoding.encode(sample.generated_response)) for task in tasks for sample in task.samples))


def get_cost_for_model(model, total_input_tokens, total_output_tokens):
    input_cost_per_million_tokens = pricing_per_1m_tokens[f"{model}-in"]
    output_cost_per_million_tokens = pricing_per_1m_tokens[f"{model}-out"]

    total_cost = ((total_input_tokens / 1_000_000) * input_cost_per_million_tokens) + ((total_output_tokens / 1_000_000) * output_cost_per_million_tokens)

    return total_cost


def analyze(approach: Approach, results, margin_factor, using_batch_api):
    tasks: List[Task] = approach.tasks

    if any(task.modified_prompt for task in tasks):
        total_input_characters = sum(len(task.modified_prompt) * len(task.samples) for task in tasks)
    else:
        total_input_characters = sum(len(sample.modified_prompt) for task in tasks for sample in task.samples)

    total_output_characters = sum(len(sample.generated_response) for task in tasks for sample in task.samples)

    samples_requiring_re_extraction = [sample for task in tasks for sample in task.samples if
                                       requires_re_extraction(sample)]

    model = "gpt-3.5-turbo-0125"
    encoding = tiktoken.encoding_for_model(model)
    total_3_5_input_tokens, total_3_5_output_tokens = get_no_tokens(tasks, samples_requiring_re_extraction, encoding)
    total_3_5_cost = get_cost_for_model(model, total_3_5_input_tokens, total_3_5_output_tokens)

    model = "gpt-4"
    encoding = tiktoken.encoding_for_model(model)
    total_4_input_tokens, total_4_output_tokens = get_no_tokens(tasks, samples_requiring_re_extraction, encoding)
    total_4_cost = get_cost_for_model(model, total_4_input_tokens, total_4_output_tokens)

    model = "gpt-4-turbo"
    encoding = tiktoken.encoding_for_model(model)
    total_4_turbo_input_tokens, total_4_turbo_output_tokens = get_no_tokens(tasks, samples_requiring_re_extraction,
                                                                            encoding)
    total_4_turbo_cost = get_cost_for_model(model, total_4_turbo_input_tokens, total_4_turbo_output_tokens)

    model = "gpt-4o"
    encoding = tiktoken.encoding_for_model(model)
    total_4o_input_tokens, total_4o_output_tokens = get_no_tokens(tasks, samples_requiring_re_extraction, encoding)
    total_4o_cost = get_cost_for_model(model, total_4o_input_tokens, total_4o_output_tokens)

    model = "gpt-4o-2024-08-06"
    total_4o_2024_08_06_cost = get_cost_for_model(model, total_4o_input_tokens, total_4o_output_tokens)

    model = "gpt-4o-mini"
    encoding = tiktoken.encoding_for_model(model)
    total_4o_mini_input_tokens, total_4o_mini_output_tokens = get_no_tokens(tasks, samples_requiring_re_extraction,
                                                                            encoding)
    total_4o_mini_cost = get_cost_for_model(model, total_4o_mini_input_tokens, total_4o_mini_output_tokens)

    if using_batch_api:
        total_3_5_cost = total_3_5_cost * 0.5
        total_4_cost = total_4_cost * 0.5
        total_4_turbo_cost = total_4_turbo_cost * 0.5
        total_4o_cost = total_4o_cost * 0.5
        total_4o_mini_cost = total_4o_mini_cost * 0.5
        total_4o_2024_08_06_cost = total_4o_2024_08_06_cost * 0.5

    vat_factor = 1.081
    total_3_5_cost = round(total_3_5_cost * margin_factor * vat_factor, 4)
    total_4_cost = round(total_4_cost * margin_factor * vat_factor, 4)
    total_4_turbo_cost = round(total_4_turbo_cost * margin_factor * vat_factor, 4)
    total_4o_cost = round(total_4o_cost * margin_factor * vat_factor, 4)
    total_4o_mini_cost = round(total_4o_mini_cost * margin_factor * vat_factor, 4)
    total_4o_2024_08_06_cost = round(total_4o_2024_08_06_cost * margin_factor * vat_factor, 4)

    results.update(
        {
            "Filename": approach.id,
            "Total Tasks": len(tasks),
            "Total Samples": sum(len(task.samples) for task in tasks),
            "Total Input Characters": total_input_characters,
            "Total Output Characters": total_output_characters,
            "GPT-3.5-turbo Cost": total_3_5_cost,
            "GPT-4 Cost": total_4_cost,
            "GPT-4-turbo Cost": total_4_turbo_cost,
            "GPT-4o Cost": total_4o_cost,
            "GPT-4o-2024-08-06 Cost": total_4o_2024_08_06_cost,
            "GPT-4o-mini Cost": total_4o_mini_cost,
        })


if __name__ == "__main__":
    load_dotenv()
    data_folder_path = os.path.dirname(utils.relative_path_from_root(os.getenv("DATA_FILE_PATH")))

    logging.basicConfig(level=logging.INFO)

    margin_factor = 1.2
    using_batch_api = False
    get_costs(data_folder_path, margin_factor, using_batch_api)
